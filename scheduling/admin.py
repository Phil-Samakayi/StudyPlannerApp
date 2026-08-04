# scheduling/admin.py
from django.contrib import admin
from .models import ScheduleSlot, StudySession


@admin.register(ScheduleSlot)
class ScheduleSlotAdmin(admin.ModelAdmin):
    list_display = ["student", "day_of_week", "start_time", "end_time"]
    list_filter = ["day_of_week"]


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ["student", "subject", "start_time", "end_time"]
    list_filter = ["subject"]
