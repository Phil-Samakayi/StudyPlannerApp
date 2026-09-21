# scheduling/tests.py
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from subjects.models import Subject
from .models import ScheduleSlot, StudySession

SLOTS_URL = "/api/scheduling/slots/"
BULK_UPDATE_URL = "/api/scheduling/slots/bulk-update/"
SESSIONS_URL = "/api/scheduling/sessions/"


class ScheduleSlotTests(APITestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email="slots.me@unza.zm", password="strongpass123", full_name="Slots Me"
        )
        self.other_student = CustomUser.objects.create_user(
            email="slots.other@unza.zm", password="strongpass123", full_name="Slots Other"
        )
        self.client.force_authenticate(user=self.student)

    def test_create_slot(self):
        response = self.client.post(SLOTS_URL, {
            "day_of_week": 1, "start_time": "14:00:00", "end_time": "16:00:00",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(ScheduleSlot.objects.get().student, self.student)

    def test_end_before_start_is_rejected(self):
        response = self.client.post(SLOTS_URL, {
            "day_of_week": 1, "start_time": "16:00:00", "end_time": "14:00:00",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_end_equal_to_start_is_rejected(self):
        response = self.client.post(SLOTS_URL, {
            "day_of_week": 1, "start_time": "14:00:00", "end_time": "14:00:00",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_only_returns_own_slots(self):
        ScheduleSlot.objects.create(
            student=self.student, day_of_week=1, start_time="14:00:00", end_time="16:00:00"
        )
        ScheduleSlot.objects.create(
            student=self.other_student, day_of_week=2, start_time="09:00:00", end_time="10:00:00"
        )
        response = self.client.get(SLOTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_bulk_update_replaces_existing_slots(self):
        ScheduleSlot.objects.create(
            student=self.student, day_of_week=0, start_time="08:00:00", end_time="09:00:00"
        )
        response = self.client.post(BULK_UPDATE_URL, {
            "slots": [
                {"day_of_week": 1, "start_time": "14:00:00", "end_time": "16:00:00"},
                {"day_of_week": 3, "start_time": "10:00:00", "end_time": "11:00:00"},
            ]
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        remaining = ScheduleSlot.objects.filter(student=self.student)
        self.assertEqual(remaining.count(), 2)
        self.assertFalse(remaining.filter(day_of_week=0).exists())

    def test_bulk_update_does_not_touch_another_students_slots(self):
        ScheduleSlot.objects.create(
            student=self.other_student, day_of_week=0, start_time="08:00:00", end_time="09:00:00"
        )
        self.client.post(BULK_UPDATE_URL, {
            "slots": [{"day_of_week": 1, "start_time": "14:00:00", "end_time": "16:00:00"}]
        }, format="json")
        self.assertTrue(ScheduleSlot.objects.filter(student=self.other_student, day_of_week=0).exists())

    def test_overlapping_slot_on_same_day_is_rejected(self):
        ScheduleSlot.objects.create(
            student=self.student, day_of_week=1, start_time="14:00:00", end_time="16:00:00"
        )
        response = self.client.post(SLOTS_URL, {
            "day_of_week": 1, "start_time": "15:00:00", "end_time": "17:00:00",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ScheduleSlot.objects.filter(student=self.student).count(), 1)

    def test_back_to_back_slots_on_same_day_are_allowed(self):
        ScheduleSlot.objects.create(
            student=self.student, day_of_week=1, start_time="14:00:00", end_time="16:00:00"
        )
        response = self.client.post(SLOTS_URL, {
            "day_of_week": 1, "start_time": "16:00:00", "end_time": "17:00:00",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_overlapping_slot_on_a_different_day_is_allowed(self):
        ScheduleSlot.objects.create(
            student=self.student, day_of_week=1, start_time="14:00:00", end_time="16:00:00"
        )
        response = self.client.post(SLOTS_URL, {
            "day_of_week": 2, "start_time": "14:00:00", "end_time": "16:00:00",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_overlapping_slot_from_another_student_is_allowed(self):
        ScheduleSlot.objects.create(
            student=self.other_student, day_of_week=1, start_time="14:00:00", end_time="16:00:00"
        )
        response = self.client.post(SLOTS_URL, {
            "day_of_week": 1, "start_time": "14:00:00", "end_time": "16:00:00",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_updating_a_slot_does_not_conflict_with_itself(self):
        slot = ScheduleSlot.objects.create(
            student=self.student, day_of_week=1, start_time="14:00:00", end_time="16:00:00"
        )
        response = self.client.patch(f"{SLOTS_URL}{slot.id}/", {"end_time": "16:30:00"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def test_bulk_update_rejects_internally_overlapping_slots(self):
        response = self.client.post(BULK_UPDATE_URL, {
            "slots": [
                {"day_of_week": 1, "start_time": "14:00:00", "end_time": "16:00:00"},
                {"day_of_week": 1, "start_time": "15:00:00", "end_time": "17:00:00"},
            ]
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class StudySessionTests(APITestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email="session.me@unza.zm", password="strongpass123", full_name="Session Me"
        )
        self.subject = Subject.objects.create(code="CSC301", name="Data Structures")
        self.client.force_authenticate(user=self.student)

    def test_create_study_session(self):
        response = self.client.post(SESSIONS_URL, {
            "subject": self.subject.id,
            "start_time": "2026-09-20T14:00:00Z",
            "end_time": "2026-09-20T16:00:00Z",
            "goal": "Revise linked lists",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(StudySession.objects.get().student, self.student)

    def test_session_end_before_start_is_rejected(self):
        response = self.client.post(SESSIONS_URL, {
            "subject": self.subject.id,
            "start_time": "2026-09-20T16:00:00Z",
            "end_time": "2026-09-20T14:00:00Z",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sessions_require_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(SESSIONS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_overlapping_study_session_is_rejected(self):
        StudySession.objects.create(
            student=self.student, subject=self.subject,
            start_time="2026-09-20T14:00:00Z", end_time="2026-09-20T16:00:00Z",
        )
        response = self.client.post(SESSIONS_URL, {
            "subject": self.subject.id,
            "start_time": "2026-09-20T15:00:00Z",
            "end_time": "2026-09-20T17:00:00Z",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(StudySession.objects.filter(student=self.student).count(), 1)

    def test_back_to_back_study_sessions_are_allowed(self):
        StudySession.objects.create(
            student=self.student, subject=self.subject,
            start_time="2026-09-20T14:00:00Z", end_time="2026-09-20T16:00:00Z",
        )
        response = self.client.post(SESSIONS_URL, {
            "subject": self.subject.id,
            "start_time": "2026-09-20T16:00:00Z",
            "end_time": "2026-09-20T17:00:00Z",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_overlapping_study_session_from_another_student_is_allowed(self):
        other_student = CustomUser.objects.create_user(
            email="session.other@unza.zm", password="strongpass123", full_name="Session Other"
        )
        StudySession.objects.create(
            student=other_student, subject=self.subject,
            start_time="2026-09-20T14:00:00Z", end_time="2026-09-20T16:00:00Z",
        )
        response = self.client.post(SESSIONS_URL, {
            "subject": self.subject.id,
            "start_time": "2026-09-20T14:00:00Z",
            "end_time": "2026-09-20T16:00:00Z",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_updating_a_study_session_does_not_conflict_with_itself(self):
        session = StudySession.objects.create(
            student=self.student, subject=self.subject,
            start_time="2026-09-20T14:00:00Z", end_time="2026-09-20T16:00:00Z",
        )
        response = self.client.patch(f"{SESSIONS_URL}{session.id}/", {"end_time": "2026-09-20T16:30:00Z"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
