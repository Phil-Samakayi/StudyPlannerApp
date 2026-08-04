# accounts/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, StudentProfile


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for User display and detail representation.
    """
    class Meta:
        model = CustomUser
        fields = ["id", "email", "full_name", "first_name", "last_name", "role", "date_joined"]
        read_only_fields = ["id", "date_joined"]


# Backwards-compatible alias; matching/serializers.py imports this name.
UserSerializer = CustomUserSerializer


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ["id", "email", "full_name", "first_name", "last_name", "password", "role"]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            full_name=validated_data.get("full_name", ""),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            role=validated_data.get("role", "STUDENT"),
        )
        # Create an associated student profile automatically
        if user.role == "STUDENT":
            StudentProfile.objects.get_or_create(user=user, defaults={"student_number": f"PENDING-{user.pk}"})
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT Token serializer to include additional user details in token payload response.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "full_name": self.user.full_name,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "role": self.user.role,
        }
        return data


class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Student Profile details.
    """
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            "id",
            "user",
            "student_number",
            "program",
            "year_of_study",
        ]
        read_only_fields = ["id"]