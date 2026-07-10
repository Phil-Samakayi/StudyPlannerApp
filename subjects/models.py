"""
subjects/models.py

Maps to the SUBJECT table in the ER diagram (Figure 4, v1.0).
"""
from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "subject"
        ordering = ["name"]
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    def __str__(self):
        return self.name
