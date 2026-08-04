# assessments/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import SelfAssessment
from .serializers import (
    SelfAssessmentSerializer,
    BulkSelfAssessmentSerializer,
)


class AssessmentListCreateView(generics.ListCreateAPIView):
    """
    Lists and creates self-assessments for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SelfAssessmentSerializer  # <--- Updated serializer class reference

    def get_queryset(self):
        return SelfAssessment.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class AssessmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieves, updates, or deletes a specific self-assessment.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SelfAssessmentSerializer  # <--- Updated serializer class reference

    def get_queryset(self):
        return SelfAssessment.objects.filter(student=self.request.user)

class BulkAssessmentSubmitView(APIView):
    """
    POST /api/assessments/bulk_submit/
    Body: { "assessments": [ {"subject": 1, "strength_score": 4, "weakness_score": 2}, ... ] }
    Lets the frontend submit all subject ratings in a single request (US-04).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = BulkSelfAssessmentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        saved = serializer.save()
        return Response(
            SelfAssessmentSerializer(saved, many=True).data,
            status=status.HTTP_200_OK,
        )
