# schedule/apps.py
from django.apps import AppConfig


class ScheduleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduling'
    verbose_name = 'Study Timetable & Session Coordination'