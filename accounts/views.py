# accounts/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import StudentProfile
from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    StudentProfileSerializer,
)


class RegisterView(generics.CreateAPIView):
    """
    Handles student registration.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Handles login and JWT token retrieval.
    """
    serializer_class = CustomTokenObtainPairSerializer


class StudentProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieves or updates the profile of the authenticated student.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StudentProfileSerializer

    def get_object(self):
        profile, _ = StudentProfile.objects.get_or_create(
            user=self.request.user,
            defaults={"student_number": f"PENDING-{self.request.user.pk}"},
        )
        return profile