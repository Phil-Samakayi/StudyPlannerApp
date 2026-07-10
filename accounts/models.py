from django.contrib.auth.models import AbstractUser
from django.db import models


class Student(AbstractUser):
    """
    A registered student. `email` is enforced unique at the DB level.

    groupstudy_opt_in defaults to False. The matching app must exclude
    any student with opt_in=False from candidate pools, regardless of
    their self-assessment data (informed-consent principle, proposal
    Section 3.2).
    """
    email = models.EmailField(unique=True)
    groupstudy_opt_in = models.BooleanField(
        default=False,
        help_text="Whether this student has opted in to GroupStudy matching.",
    )

    class Meta:
        db_table = "student"
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return self.get_full_name() or self.username
