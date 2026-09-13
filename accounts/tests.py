# accounts/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CustomUser, StudentProfile

REGISTER_URL = "/api/accounts/register/"
LOGIN_URL = "/api/auth/token/"
REFRESH_URL = "/api/auth/token/refresh/"
PROFILE_URL = "/api/accounts/profile/"


class RegistrationTests(APITestCase):
    def test_register_creates_user_and_student_profile(self):
        response = self.client.post(REGISTER_URL, {
            "email": "new.student@unza.zm",
            "full_name": "New Student",
            "password": "strongpass123",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        user = CustomUser.objects.get(email="new.student@unza.zm")
        self.assertEqual(user.full_name, "New Student")
        self.assertEqual(user.role, "STUDENT")
        # Registering should not leak the raw password back to the client.
        self.assertNotIn("password", response.data)

        # A STUDENT registration auto-creates a pending StudentProfile.
        profile = StudentProfile.objects.get(user=user)
        self.assertTrue(profile.student_number.startswith("PENDING-"))

    def test_register_rejects_duplicate_email(self):
        CustomUser.objects.create_user(email="dupe@unza.zm", password="strongpass123", full_name="First")
        response = self.client.post(REGISTER_URL, {
            "email": "dupe@unza.zm",
            "full_name": "Second",
            "password": "strongpass123",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_rejects_short_password(self):
        response = self.client.post(REGISTER_URL, {
            "email": "short.pass@unza.zm",
            "full_name": "Short Pass",
            "password": "short1",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(CustomUser.objects.filter(email="short.pass@unza.zm").exists())

    def test_register_rejects_missing_email(self):
        response = self.client.post(REGISTER_URL, {
            "full_name": "No Email",
            "password": "strongpass123",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="login.user@unza.zm", password="correcthorse123", full_name="Login User"
        )

    def test_login_with_valid_credentials_returns_tokens_and_user(self):
        response = self.client.post(LOGIN_URL, {
            "email": "login.user@unza.zm",
            "password": "correcthorse123",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "login.user@unza.zm")

    def test_login_with_wrong_password_is_rejected(self):
        response = self.client.post(LOGIN_URL, {
            "email": "login.user@unza.zm",
            "password": "wrong-password",
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_unknown_email_is_rejected(self):
        response = self.client.post(LOGIN_URL, {
            "email": "nobody@unza.zm",
            "password": "correcthorse123",
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_issues_new_access_token(self):
        login_response = self.client.post(LOGIN_URL, {
            "email": "login.user@unza.zm",
            "password": "correcthorse123",
        })
        refresh_token = login_response.data["refresh"]

        refresh_response = self.client.post(REFRESH_URL, {"refresh": refresh_token})
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)


class ProfileTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="profile.user@unza.zm", password="correcthorse123", full_name="Profile User"
        )

    def test_profile_requires_authentication(self):
        response = self.client.get(PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_is_auto_created_on_first_fetch(self):
        self.assertFalse(StudentProfile.objects.filter(user=self.user).exists())
        self.client.force_authenticate(user=self.user)

        response = self.client.get(PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(StudentProfile.objects.filter(user=self.user).exists())
        self.assertEqual(response.data["user"]["email"], "profile.user@unza.zm")

    def test_profile_update_persists_program_and_year(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(PROFILE_URL, {
            "program": "BSc Computing and Informatics",
            "year_of_study": 4,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        profile = StudentProfile.objects.get(user=self.user)
        self.assertEqual(profile.program, "BSc Computing and Informatics")
        self.assertEqual(profile.year_of_study, 4)

    def test_profile_update_rejects_year_out_of_range(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(PROFILE_URL, {"year_of_study": 9})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_only_returns_the_authenticated_students_own_data(self):
        other_user = CustomUser.objects.create_user(
            email="other.user@unza.zm", password="correcthorse123", full_name="Other User"
        )
        StudentProfile.objects.create(user=other_user, student_number="SN-OTHER", program="Law")

        self.client.force_authenticate(user=self.user)
        response = self.client.get(PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], "profile.user@unza.zm")
        self.assertNotEqual(response.data["user"]["email"], "other.user@unza.zm")
