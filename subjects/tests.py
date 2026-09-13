# subjects/tests.py
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from .models import Subject

SUBJECTS_URL = "/api/subjects/"


class SubjectPermissionTests(APITestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email="student@unza.zm", password="strongpass123", full_name="Student One", role="STUDENT"
        )
        self.admin = CustomUser.objects.create_user(
            email="admin@unza.zm", password="strongpass123", full_name="Admin One",
            role="ADMIN", is_staff=True,
        )
        self.subject = Subject.objects.create(code="CSC301", name="Data Structures")

    def test_list_requires_authentication(self):
        response = self.client.get(SUBJECTS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_student_can_read(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get(SUBJECTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["code"], "CSC301")

    def test_student_cannot_create_subject(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(SUBJECTS_URL, {"code": "CSC302", "name": "Algorithms"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Subject.objects.filter(code="CSC302").exists())

    def test_admin_can_create_subject(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(SUBJECTS_URL, {"code": "CSC302", "name": "Algorithms"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(Subject.objects.filter(code="CSC302").exists())

    def test_admin_can_delete_subject(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f"{SUBJECTS_URL}{self.subject.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Subject.objects.filter(id=self.subject.id).exists())

    def test_duplicate_subject_code_is_rejected(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(SUBJECTS_URL, {"code": "CSC301", "name": "Different Name"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subject_name_is_stripped_of_whitespace(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(SUBJECTS_URL, {"code": "CSC303", "name": "  Networks  "})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data["name"], "Networks")
