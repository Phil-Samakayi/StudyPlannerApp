# scheduling/serializers.py
from rest_framework import serializers
from .models import ScheduleSlot, StudySession, DayOfWeek


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
