"""
accounts/views.py

Login itself is handled by simplejwt's built-in TokenObtainPairView /
TokenRefreshView, wired up directly in accounts/urls.py -- no custom
view needed for that part.
"""
from rest_framework import generics, permissions
from rest_framework.response import Response

from .serializers import RegisterSerializer, StudentSerializer


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ -- open to anyone, no auth required."""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/auth/me/  -- view own profile
    PATCH /api/auth/me/ -- update own profile, including groupstudy_opt_in

    Deliberately scoped to the requesting user only: get_object() ignores
    any pk in the URL and always returns request.user, so a student can
    never view or edit another student's profile through this endpoint.
    """
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
