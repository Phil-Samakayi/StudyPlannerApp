# matching/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MatchViewSet, GroupStudySessionViewSet, FeedbackViewSet

router = DefaultRouter()
router.register(r"matches", MatchViewSet, basename="match")
router.register(r"sessions", GroupStudySessionViewSet, basename="group-study-session")
router.register(r"feedback", FeedbackViewSet, basename="feedback")

urlpatterns = [
    path("", include(router.urls)),
]