# matching/serializers.py
from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Match, MatchParticipant, GroupStudySession, Feedback


class RequestMatchSerializer(serializers.Serializer):
    """Input serializer for POST /api/matching/matches/request-match/."""
    subject_id = serializers.IntegerField()


class MatchSerializer(serializers.ModelSerializer):
    """
    Read-only representation of a Match, including the resolved list of
    participating students (via the MatchParticipant junction table).
    """
    participants = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = ["id", "relevance_score", "participants", "created_at"]
        read_only_fields = fields

    def get_participants(self, obj):
        students = [mp.student for mp in obj.participants.select_related("student")]
        return UserSerializer(students, many=True).data


class GroupStudySessionSerializer(serializers.ModelSerializer):
    """
    Serializer for a GroupStudySession produced by a Match.
    `participants` is derived from the parent Match's participants.
    """
    participants = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GroupStudySession
        fields = ["id", "match", "scheduled_time", "status", "participants"]
        read_only_fields = ["id", "status", "participants"]

    def get_participants(self, obj):
        return UserSerializer(obj.participants, many=True).data

    def validate_match(self, value):
        """
        A student may only schedule a GroupStudySession for a Match they were
        actually paired into -- otherwise any authenticated user could create
        a session (and later mark it completed) for someone else's match.
        """
        request = self.context.get("request")
        if request and request.user and not value.participants.filter(student=request.user).exists():
            raise serializers.ValidationError(
                "You can only schedule sessions for matches you participated in."
            )
        return value


class FeedbackSerializer(serializers.ModelSerializer):
    """Post-session feedback submitted by a participating student."""

    class Meta:
        model = Feedback
        fields = ["id", "student", "session", "rating", "comment", "submitted_at"]
        read_only_fields = ["id", "student", "submitted_at"]

    def validate_session(self, value):
        """
        Enforce US-08: feedback can only be left once a session is COMPLETED.
        """
        from .models import GroupStudySessionStatus
        if value.status != GroupStudySessionStatus.COMPLETED:
            raise serializers.ValidationError(
                "Feedback is only enabled for sessions that have been marked as COMPLETED."
            )
        return value

    def validate(self, data):
        """Ensure the submitting student actually participated in this session."""
        request = self.context.get("request")
        session = data.get("session")
        if request and request.user and session:
            if not session.match.participants.filter(student=request.user).exists():
                raise serializers.ValidationError(
                    "You cannot submit feedback for a session you did not participate in."
                )
            # Model has a DB-level UniqueConstraint on (student, session), but
            # that isn't a `unique_together` Meta option, so DRF doesn't
            # auto-generate a validator for it -- without this check, a
            # resubmission crashes with an unhandled IntegrityError (500)
            # instead of a normal 400 validation error.
            if Feedback.objects.filter(session=session, student=request.user).exists():
                raise serializers.ValidationError(
                    "You have already submitted feedback for this session."
                )
        return data
