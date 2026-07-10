"""
accounts/tests.py

Covers US-1 (register/login) and US-2 (manage profile / opt-in) end to end
through the actual REST API, using DRF's test client.
"""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

Student = get_user_model()


class RegistrationTests(APITestCase):
    def test_register_creates_student(self):
        response = self.client.post("/api/auth/register/", {
            "username": "student1",
            "email": "student1@example.com",
            "password": "a-strong-password-123",
            "password2": "a-strong-password-123",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Student.objects.filter(username="student1").exists())
        # password must never be echoed back
        self.assertNotIn("password", response.data)

    def test_register_rejects_mismatched_passwords(self):
        response = self.client.post("/api/auth/register/", {
            "username": "student2",
            "email": "student2@example.com",
            "password": "a-strong-password-123",
            "password2": "different-password-456",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_rejects_duplicate_email(self):
        Student.objects.create_user(username="existing", email="dupe@example.com", password="x")
        response = self.client.post("/api/auth/register/", {
            "username": "student3",
            "email": "dupe@example.com",
            "password": "a-strong-password-123",
            "password2": "a-strong-password-123",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAndProfileTests(APITestCase):
    def setUp(self):
        self.student = Student.objects.create_user(
            username="loginuser", email="login@example.com", password="a-strong-password-123"
        )

    def test_login_returns_jwt_tokens(self):
        response = self.client.post("/api/auth/login/", {
            "username": "loginuser",
            "password": "a-strong-password-123",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_rejects_wrong_password(self):
        response = self.client.post("/api/auth/login/", {
            "username": "loginuser",
            "password": "wrong-password",
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_authentication(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_own_profile_when_authenticated(self):
        login = self.client.post("/api/auth/login/", {
            "username": "loginuser",
            "password": "a-strong-password-123",
        })
        access = login.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "loginuser")
        self.assertEqual(response.data["groupstudy_opt_in"], False)

    def test_me_can_update_opt_in(self):
        login = self.client.post("/api/auth/login/", {
            "username": "loginuser",
            "password": "a-strong-password-123",
        })
        access = login.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.patch("/api/auth/me/", {"groupstudy_opt_in": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertTrue(self.student.groupstudy_opt_in)
