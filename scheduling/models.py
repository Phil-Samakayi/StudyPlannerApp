"""
scheduling/models.py

Maps to the SCHEDULE_SLOT and STUDY_SESSION tables in the ER diagram
(Figure 4, v1.0).

ScheduleSlot represents a student's *recurring weekly availability*
(e.g. "Free Tuesdays 14:00-16:00") and is what the matching app queries
to find common free time between matched students -- it is separate
from StudySession, which represents an actual booked study session
against a subject.
"""
from django.conf import settings
from django.db import models


class DayOfWeek(models.IntegerChoices):
    MONDAY = 0, "Monday"
    TUESDAY = 1, "Tuesday"
    WEDNESDAY = 2, "Wednesday"
    THURSDAY = 3, "Thursday"
    FRIDAY = 4, "Friday"
    SATURDAY = 5, "Saturday"
    SUNDAY = 6, "Sunday"


class ScheduleSlot(models.Model):
    """A block of recurring weekly availability for a student."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="schedule_slots",
    )
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        db_table = "schedule_slot"
        # Index on ScheduleSlot(student_id, day_of_week) -- per ER diagram
        # notes, this speeds up availability look-ups during match scheduling.
        indexes = [
            models.Index(fields=["student", "day_of_week"], name="idx_slot_student_day"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="schedule_slot_end_after_start",
            ),
        ]
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.student} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class StudySession(models.Model):
    """A booked personal study session against a subject."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="study_sessions",
    )
    subject = models.ForeignKey(
        "subjects.Subject",
        on_delete=models.PROTECT,
        related_name="study_sessions",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    goal = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "study_session"
        indexes = [
            models.Index(fields=["student", "start_time"], name="idx_session_student_start"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="study_session_end_after_start",
            ),
        ]
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.student} - {self.subject} ({self.start_time:%Y-%m-%d %H:%M})"
