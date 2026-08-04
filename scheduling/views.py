# scheduling/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ScheduleSlot, StudySession
from .serializers import ScheduleSlotSerializer, StudySessionSerializer


class ScheduleSlotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for students to manage their recurring weekly availability slots (ScheduleSlot).
    Maps to SCHEDULE_SLOT table.
    """
    serializer_class = ScheduleSlotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ScheduleSlot.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=False, methods=["post"], url_path="bulk-update")
    def bulk_update_slots(self, request):
        """
        POST /api/scheduling/slots/bulk-update/
        Allows updating multiple recurring slots at once from the timetable frontend.
        """
        slots_data = request.data.get("slots", [])
        if not isinstance(slots_data, list):
            return Response({"detail": "Expected a list of slots under key 'slots'."}, status=status.HTTP_400_BAD_REQUEST)

        # Re-populate availability slots
        ScheduleSlot.objects.filter(student=request.user).delete()
        created_slots = []
        for slot in slots_data:
            serializer = ScheduleSlotSerializer(data=slot)
            serializer.is_valid(raise_exception=True)
            created_slots.append(serializer.save(student=request.user))

        return Response(
            ScheduleSlotSerializer(created_slots, many=True).data,
            status=status.HTTP_201_CREATED
        )


class StudySessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for individual personal study sessions (StudySession).
    Maps to STUDY_SESSION table.
    """
    serializer_class = StudySessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StudySession.objects.filter(student=self.request.user).select_related("subject")

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)