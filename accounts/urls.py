"""
accounts/urls.py

Included in config/urls.py under the 'api/auth/' prefix, so the full
paths are:

    POST /api/auth/register/
    POST /api/auth/login/
    POST /api/auth/login/refresh/
    GET/PATCH /api/auth/me/
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import MeView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
]
