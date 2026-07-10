"""
accounts/serializers.py
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

Student = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Used by POST /api/auth/register/ (US-1: "As a student, I want to
    register and log in, so that my schedule and assessment data are
    private to me.")
    """
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm password")

    class Meta:
        model = Student
        fields = ("username", "email", "first_name", "last_name", "password", "password2")
        extra_kwargs = {
            "email": {"required": True},
        }

    def validate_email(self, value):
        if Student.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A student with this email already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        student = Student(**validated_data)
        student.set_password(password)
        student.save()
        return student


class StudentSerializer(serializers.ModelSerializer):
    """
    Used by GET/PATCH /api/auth/me/ (US-2: manage profile, including
    GroupStudy opt-in).
    """

    class Meta:
        model = Student
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "groupstudy_opt_in",
            "date_joined",
        )
        read_only_fields = ("id", "username", "date_joined")
