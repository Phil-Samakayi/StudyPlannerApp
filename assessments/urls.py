# assessments/urls.py
from django.urls import path
from .views import (
    AssessmentListCreateView,
    AssessmentDetailView,
    BulkAssessmentSubmitView,
)

urlpatterns = [
    path("", AssessmentListCreateView.as_view(), name="assessment_list_create"),
    path("bulk_submit/", BulkAssessmentSubmitView.as_view(), name="assessment_bulk_submit"),
    path("<int:pk>/", AssessmentDetailView.as_view(), name="assessment_detail"),
]