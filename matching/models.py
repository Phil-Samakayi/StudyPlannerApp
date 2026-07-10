"""
matching/models.py

Maps to the MATCH, MATCH_PARTICIPANT, GROUP_STUDY_SESSION, and FEEDBACK
tables in the ER diagram (Figure 4, v1.0).

This app is the "in-process matching app" shown in the system
architecture diagram (Figure 5): it lives in the same Django project
and database as the other apps, but keeps the AI matching concerns
(scikit-learn scoring, ranked results, GroupStudy lifecycle) isolated
behind its own models and, later, its own REST endpoint
(/api/matches/...).
"""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Match(models.Model):
    """
    The result of one AI matching run: a relevance-scored pairing.
    Always involves 2 or more students, linked via MatchParticipant
    (Student "2..*" -- "0..*" Match in the domain model).
    """
    relevance_score = models.FloatField(
        help_text="Model-computed compatibility score for this pairing, 0.0-1.0."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "match"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Match #{self.pk} (relevance={self.relevance_score:.2f})"


class MatchParticipant(models.Model):
    """Junction table resolving the many-to-many Student <-> Match relationship."""

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="participants")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="match_participations",
    )

    class Meta:
        db_table = "match_participant"
        # Composite UNIQUE constraint on (match_id, student_id) -- prevents
        # duplicate pairings (ER diagram notes).
        constraints = [
            models.UniqueConstraint(fields=["match", "student"], name="uq_matchparticipant_match_student"),
        ]

    def __str__(self):
        return f"{self.student} in {self.match}"


class GroupStudySessionStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class GroupStudySession(models.Model):
    """
    A GroupStudy session produced by a Match (Match "1" -- "0..1"
    GroupStudySession : produces). Not every match necessarily
    proceeds to a scheduled session, hence the 0..1.
    """
    match = models.OneToOneField(
        Match,
        on_delete=models.CASCADE,
        related_name="group_study_session",
    )
    scheduled_time = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=GroupStudySessionStatus.choices,
        default=GroupStudySessionStatus.SCHEDULED,
    )

    class Meta:
        db_table = "group_study_session"
        ordering = ["scheduled_time"]

    def __str__(self):
        return f"GroupStudySession #{self.pk} ({self.status})"

    @property
    def participants(self):
        """Students in this session, via the parent Match's participants."""
        return [mp.student for mp in self.match.participants.select_related("student")]


class Feedback(models.Model):
    """Post-session feedback, used to evaluate match relevance (US-8)."""

    RATING_MIN = 1
    RATING_MAX = 5

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedback_given",
    )
    session = models.ForeignKey(
        GroupStudySession,
        on_delete=models.CASCADE,
        related_name="feedback",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(RATING_MIN), MaxValueValidator(RATING_MAX)]
    )
    comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "feedback"
        # One feedback entry per student per session.
        constraints = [
            models.UniqueConstraint(fields=["student", "session"], name="uq_feedback_student_session"),
        ]
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"Feedback by {self.student} on {self.session} ({self.rating}/5)"
