# accounts/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    StudentProfileView,
)

urlpatterns = [
    # JWT Authentication Endpoints
    path("register/", RegisterView.as_view(), name="auth_register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="auth_login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="auth_token_refresh"),

    # Profile Endpoint. Weekly availability lives at /api/scheduling/slots/
    path("profile/", StudentProfileView.as_view(), name="student_profile"),
]