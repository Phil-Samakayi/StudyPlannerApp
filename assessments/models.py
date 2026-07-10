"""
assessments/models.py

Maps to the SELF_ASSESSMENT table in the ER diagram (Figure 4, v1.0).

This is the input data for the AI matching model (Objective 3): each
row is one student's self-rated strength/weakness on one subject.
"""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class SelfAssessment(models.Model):
    SCORE_MIN = 1
    SCORE_MAX = 5

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="self_assessments",
    )
    subject = models.ForeignKey(
        "subjects.Subject",
        on_delete=models.CASCADE,
        related_name="self_assessments",
    )
    strength_score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(SCORE_MIN), MaxValueValidator(SCORE_MAX)]
    )
    weakness_score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(SCORE_MIN), MaxValueValidator(SCORE_MAX)]
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "self_assessment"
        # A student has at most one assessment per subject -- resubmitting
        # updates the existing row rather than creating a duplicate (US-4).
        constraints = [
            models.UniqueConstraint(fields=["student", "subject"], name="uq_assessment_student_subject"),
        ]
        # Index on SelfAssessment(subject_id, strength_score, weakness_score)
        # -- the columns the matching query filters/sorts on when finding
        # complementary peers (ER diagram notes).
        indexes = [
            models.Index(
                fields=["subject", "strength_score", "weakness_score"],
                name="idx_assessment_matching",
            ),
        ]

    def __str__(self):
        return f"{self.student} / {self.subject}: +{self.strength_score} -{self.weakness_score}"
