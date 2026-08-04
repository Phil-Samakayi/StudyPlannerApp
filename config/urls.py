"""
URL Configuration for StudyPlannerApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from accounts.views import CustomTokenObtainPairView

urlpatterns = [
    # Django Admin Panel
    path("admin/", admin.site.urls),

    # Authentication Endpoints (SimpleJWT)
    path("api/auth/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # Application Modules
    path("api/accounts/", include("accounts.urls")),
    path("api/subjects/", include("subjects.urls")),
    path("api/assessments/", include("assessments.urls")),
    path("api/matching/", include("matching.urls")),
    path("api/scheduling/", include("scheduling.urls")),
]