# subjects/serializers.py
from rest_framework import serializers
from .models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "code", "name"]
        read_only_fields = ["id"]

    def validate_name(self, value):
        """
        Clean and strip trailing/leading whitespace from subject name.
        """
        cleaned_name = value.strip()
        if not cleaned_name:
            raise serializers.ValidationError("Subject name cannot be empty.")
        return cleaned_name