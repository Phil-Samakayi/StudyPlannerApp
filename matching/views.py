# matching/views.py
from django.db.models import Avg, Count
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Match, MatchParticipant, GroupStudySession, GroupStudySessionStatus, Feedback
from .serializers import (
    MatchSerializer,
    GroupStudySessionSerializer,
    FeedbackSerializer,
    RequestMatchSerializer,
)
from .engine import generate_peer_matches


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for requesting and viewing AI-generated matches.
    """
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Match.objects.filter(participants__student=self.request.user).distinct()

    @action(detail=False, methods=["post"], url_path="request-match")
    def request_match(self, request):
        """
        POST /api/matches/request-match/
        Body: { "subject_id": 1 }
        Generates AI peer matches using scikit-learn scoring engine.
        """
        serializer = RequestMatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subject_id = serializer.validated_data["subject_id"]

        peer_results = generate_peer_matches(request.user, subject_id)
        if not peer_results:
            return Response(
                {"detail": "No candidate matches found for this subject."},
                status=status.HTTP_200_OK
            )

        top_peer = peer_results[0]

        # Create Match record
        match_obj = Match.objects.create(relevance_score=top_peer["relevance_score"])

        # Link both students as participants
        MatchParticipant.objects.create(match=match_obj, student=request.user)
        MatchParticipant.objects.create(match=match_obj, student=top_peer["candidate"])

        return Response(MatchSerializer(match_obj).data, status=status.HTTP_201_CREATED)


class GroupStudySessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing group study sessions produced by a Match.
    """
    serializer_class = GroupStudySessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GroupStudySession.objects.filter(
            match__participants__student=self.request.user
        ).distinct()

    @action(detail=True, methods=["post"], url_path="complete")
    def mark_completed(self, request, pk=None):
        """
        POST /api/sessions/{id}/complete/
        Marks session as COMPLETED, enabling feedback collection (US-08).
        """
        session = self.get_object()
        session.status = GroupStudySessionStatus.COMPLETED
        session.save()
        return Response(
            {"detail": "Session marked as completed. Feedback is now enabled.", "status": session.status},
            status=status.HTTP_200_OK
        )


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for submitting post-session feedback and evaluating Objective 3 (>= 75% target).
    """
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", None) == "ADMIN" or user.is_staff:
            return Feedback.objects.all().select_related("session", "student")
        return Feedback.objects.filter(session__match__participants__student=user).distinct()

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=False, methods=["get"], url_path="metrics")
    def metrics(self, request):
        """
        GET /api/feedback/metrics/
        Provides aggregated statistics evaluating Objective 3 (>= 75% match relevance target).
        """
        total = Feedback.objects.count()
        if total == 0:
            return Response({
                "total_reviews": 0,
                "average_rating": 0.0,
                "perceived_relevance_rate": "0%",
                "meets_objective_3": False
            })

        avg_rating = Feedback.objects.aggregate(Avg("rating"))["rating__avg"] or 0.0
        positive_reviews = Feedback.objects.filter(rating__gte=4).count()
        relevance_rate = (positive_reviews / total) * 100.0

        return Response({
            "total_reviews": total,
            "average_rating": round(avg_rating, 2),
            "positive_reviews_count": positive_reviews,
            "perceived_relevance_rate": f"{relevance_rate:.1f}%",
            "target_threshold": "75.0%",
            "meets_objective_3": relevance_rate >= 75.0
        }, status=status.HTTP_200_OK)