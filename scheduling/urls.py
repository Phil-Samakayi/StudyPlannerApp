# scheduling/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScheduleSlotViewSet, StudySessionViewSet

router = DefaultRouter()
router.register(r"slots", ScheduleSlotViewSet, basename="schedule-slot")
router.register(r"sessions", StudySessionViewSet, basename="study-session")

urlpatterns = [
    path("", include(router.urls)),
]