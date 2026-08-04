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
        start = data.get("start_time")
        end = data.get("end_time")
        if start and end and end <= start:
            raise serializers.ValidationError({"end_time": "end_time must be strictly after start_time."})
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
        start = data.get("start_time")
        end = data.get("end_time")
        if start and end and end <= start:
            raise serializers.ValidationError({"end_time": "end_time must be strictly after start_time."})
        return data