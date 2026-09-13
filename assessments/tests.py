# assessments/tests.py
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from subjects.models import Subject
from .models import SelfAssessment

ASSESSMENTS_URL = "/api/assessments/"
BULK_SUBMIT_URL = "/api/assessments/bulk_submit/"


class SelfAssessmentTests(APITestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email="assess.me@unza.zm", password="strongpass123", full_name="Assess Me"
        )
        self.other_student = CustomUser.objects.create_user(
            email="assess.other@unza.zm", password="strongpass123", full_name="Assess Other"
        )
        self.subject = Subject.objects.create(code="CSC301", name="Data Structures")
        self.other_subject = Subject.objects.create(code="CSC302", name="Algorithms")
        self.client.force_authenticate(user=self.student)

    def test_create_assessment(self):
        response = self.client.post(ASSESSMENTS_URL, {
            "subject": self.subject.id,
            "strength_score": 4,
            "weakness_score": 2,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(SelfAssessment.objects.count(), 1)
        saved = SelfAssessment.objects.get()
        self.assertEqual(saved.student, self.student)

    def test_resubmitting_same_subject_updates_instead_of_duplicating(self):
        self.client.post(ASSESSMENTS_URL, {
            "subject": self.subject.id, "strength_score": 3, "weakness_score": 3,
        })
        response = self.client.post(ASSESSMENTS_URL, {
            "subject": self.subject.id, "strength_score": 5, "weakness_score": 1,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        # Still exactly one row for this student/subject pair (US-04).
        self.assertEqual(SelfAssessment.objects.filter(student=self.student, subject=self.subject).count(), 1)
        updated = SelfAssessment.objects.get(student=self.student, subject=self.subject)
        self.assertEqual(updated.strength_score, 5)
        self.assertEqual(updated.weakness_score, 1)

    def test_score_above_max_is_rejected(self):
        response = self.client.post(ASSESSMENTS_URL, {
            "subject": self.subject.id, "strength_score": 6, "weakness_score": 2,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_score_below_min_is_rejected(self):
        response = self.client.post(ASSESSMENTS_URL, {
            "subject": self.subject.id, "strength_score": 3, "weakness_score": 0,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_only_returns_own_assessments(self):
        SelfAssessment.objects.create(
            student=self.student, subject=self.subject, strength_score=4, weakness_score=2
        )
        SelfAssessment.objects.create(
            student=self.other_student, subject=self.subject, strength_score=2, weakness_score=4
        )
        response = self.client.get(ASSESSMENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["student"], self.student.id)

    def test_cannot_retrieve_another_students_assessment(self):
        other_assessment = SelfAssessment.objects.create(
            student=self.other_student, subject=self.subject, strength_score=2, weakness_score=4
        )
        response = self.client.get(f"{ASSESSMENTS_URL}{other_assessment.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_bulk_submit_creates_multiple_assessments(self):
        response = self.client.post(BULK_SUBMIT_URL, {
            "assessments": [
                {"subject": self.subject.id, "strength_score": 4, "weakness_score": 2},
                {"subject": self.other_subject.id, "strength_score": 2, "weakness_score": 5},
            ]
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(SelfAssessment.objects.filter(student=self.student).count(), 2)

    def test_assessment_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(ASSESSMENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
