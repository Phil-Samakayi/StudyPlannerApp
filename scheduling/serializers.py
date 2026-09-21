# scheduling/serializers.py
from django.utils import timezone
from rest_framework import serializers
from .models import ScheduleSlot, StudySession, SubjectGoal, DayOfWeek


class ScheduleSlotSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source="get_day_of_week_display", read_only=True)

    class Meta:
        model = ScheduleSlot
        fields = ["id", "student", "day_of_week", "day_name", "start_time", "end_time"]
        read_only_fields = ["id", "student"]

    def validate(self, data):
        start = data.get("start_time", getattr(self.instance, "start_time", None))
        end = data.get("end_time", getattr(self.instance, "end_time", None))
        day = data.get("day_of_week", getattr(self.instance, "day_of_week", None))

        if start and end and end <= start:
            raise serializers.ValidationError({"end_time": "end_time must be strictly after start_time."})

        # Conflict check: reject a slot that overlaps another slot this same
        # student already has on the same day. Two ranges [start1,end1) and
        # [start2,end2) overlap iff start1 < end2 and start2 < end1.
        request = self.context.get("request")
        if request is not None and start and end and day is not None:
            conflicting = ScheduleSlot.objects.filter(
                student=request.user, day_of_week=day, start_time__lt=end, end_time__gt=start,
            )
            if self.instance is not None:
                conflicting = conflicting.exclude(pk=self.instance.pk)
            clash = conflicting.first()
            if clash:
                raise serializers.ValidationError(
                    f"This slot overlaps with an existing availability slot on "
                    f"{clash.get_day_of_week_display()} ({clash.start_time}-{clash.end_time})."
                )

        return data


class StudySessionSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = StudySession
        fields = [
            "id",
            "student",
            "subject",
            "subject_name",
            "start_time",
            "end_time",
            "goal",
        ]
        read_only_fields = ["id", "student"]

    def validate(self, data):
        start = data.get("start_time", getattr(self.instance, "start_time", None))
        end = data.get("end_time", getattr(self.instance, "end_time", None))

        if start and end and end <= start:
            raise serializers.ValidationError({"end_time": "end_time must be strictly after start_time."})

        # Conflict check: reject a session that overlaps another study session
        # this same student already has booked (regardless of subject).
        request = self.context.get("request")
        if request is not None and start and end:
            conflicting = StudySession.objects.filter(
                student=request.user, start_time__lt=end, end_time__gt=start,
            )
            if self.instance is not None:
                conflicting = conflicting.exclude(pk=self.instance.pk)
            clash = conflicting.first()
            if clash:
                raise serializers.ValidationError(
                    f"This session overlaps with an existing study session "
                    f"({clash.start_time:%Y-%m-%d %H:%M}-{clash.end_time:%H:%M})."
                )

        return data


class SubjectGoalSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = SubjectGoal
        fields = [
            "id",
            "student",
            "subject",
            "subject_name",
            "description",
            "target_date",
            "achieved",
            "created_at",
        ]
        read_only_fields = ["id", "student", "created_at"]

    def validate_description(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Goal description cannot be empty.")
        return cleaned

    def validate_target_date(self, value):
        # Only enforce "not in the past" on creation -- an existing goal
        # whose date has since passed should still be editable (e.g. to
        # mark it achieved), not locked out by this check.
        if self.instance is None and value < timezone.localdate():
            raise serializers.ValidationError("Target date cannot be in the past.")
        return value