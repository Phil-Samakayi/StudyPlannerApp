# assessments/admin.py
from django.contrib import admin
from .models import SelfAssessment


@admin.register(SelfAssessment)
class SelfAssessmentAdmin(admin.ModelAdmin):
    list_display = ["student", "subject", "strength_score", "weakness_score", "updated_at"]
    list_filter = ["subject"]
    search_fields = ["student__email", "subject__name", "subject__code"]
