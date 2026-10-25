# scheduling/tests.py
import datetime

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from subjects.models import Subject
from .availability import common_weekly_windows, has_common_availability, suggest_session_times
from .models import ScheduleSlot, StudySession, SubjectGoal

SLOTS_URL = "/api/scheduling/slots/"
BULK_UPDATE_URL = "/api/scheduling/slots/bulk-update/"
SESSIONS_URL = "/api/scheduling/sessions/"
GOALS_URL = "/api/scheduling/goals/"


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

    def test_list_only_returns_own_study_sessions(self):
        other = CustomUser.objects.create_user(
            email="session.other@unza.zm", password="strongpass123", full_name="Session Other"
        )
        StudySession.objects.create(
            student=other, subject=self.subject,
            start_time="2026-09-20T14:00:00Z", end_time="2026-09-20T16:00:00Z", goal="Private plan",
        )
        response = self.client.get(SESSIONS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

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


class SubjectGoalTests(APITestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email="goal.me@unza.zm", password="strongpass123", full_name="Goal Me"
        )
        self.other_student = CustomUser.objects.create_user(
            email="goal.other@unza.zm", password="strongpass123", full_name="Goal Other"
        )
        self.subject = Subject.objects.create(code="CSC301", name="Data Structures")
        self.client.force_authenticate(user=self.student)
        self.future_date = (datetime.date.today() + datetime.timedelta(days=14)).isoformat()

    def test_create_goal(self):
        response = self.client.post(GOALS_URL, {
            "subject": self.subject.id,
            "description": "Master linked lists",
            "target_date": self.future_date,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        goal = SubjectGoal.objects.get()
        self.assertEqual(goal.student, self.student)
        self.assertFalse(goal.achieved)

    def test_goal_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(GOALS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_only_returns_own_goals(self):
        SubjectGoal.objects.create(
            student=self.student, subject=self.subject, description="Mine", target_date=self.future_date
        )
        SubjectGoal.objects.create(
            student=self.other_student, subject=self.subject, description="Not mine", target_date=self.future_date
        )
        response = self.client.get(GOALS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["description"], "Mine")

    def test_empty_description_is_rejected(self):
        response = self.client.post(GOALS_URL, {
            "subject": self.subject.id, "description": "   ", "target_date": self.future_date,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_target_date_in_the_past_is_rejected_on_create(self):
        past_date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        response = self.client.post(GOALS_URL, {
            "subject": self.subject.id, "description": "Too late", "target_date": past_date,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_goal_independent_of_any_study_session(self):
        # The whole point of FR-026: a goal exists without a StudySession.
        response = self.client.post(GOALS_URL, {
            "subject": self.subject.id, "description": "No session needed", "target_date": self.future_date,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(StudySession.objects.count(), 0)

    def test_mark_achieved(self):
        goal = SubjectGoal.objects.create(
            student=self.student, subject=self.subject, description="Finish", target_date=self.future_date
        )
        response = self.client.post(f"{GOALS_URL}{goal.id}/mark-achieved/")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        goal.refresh_from_db()
        self.assertTrue(goal.achieved)

    def test_cannot_mark_an_already_achieved_goal_achieved_again(self):
        goal = SubjectGoal.objects.create(
            student=self.student, subject=self.subject, description="Finish",
            target_date=self.future_date, achieved=True,
        )
        response = self.client.post(f"{GOALS_URL}{goal.id}/mark-achieved/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_outsider_cannot_mark_someone_elses_goal_achieved(self):
        goal = SubjectGoal.objects.create(
            student=self.student, subject=self.subject, description="Finish", target_date=self.future_date
        )
        self.client.force_authenticate(user=self.other_student)
        response = self.client.post(f"{GOALS_URL}{goal.id}/mark-achieved/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_can_edit_a_goal_whose_target_date_has_passed(self):
        # Editing an overdue goal (e.g. to mark achieved) should not be
        # blocked by the "not in the past" check -- that only applies on create.
        past_date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        goal = SubjectGoal.objects.create(
            student=self.student, subject=self.subject, description="Overdue", target_date=past_date
        )
        response = self.client.patch(f"{GOALS_URL}{goal.id}/", {"description": "Still overdue, updated"})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)


class SharedAvailabilityTests(APITestCase):
    """
    Exercises scheduling/availability.py directly. A fixed "now" keeps the
    concrete-date assertions stable: Tuesday 13 October 2026, 09:00 local.
    """

    def setUp(self):
        self.tz = timezone.get_current_timezone()
        self.now = timezone.make_aware(datetime.datetime(2026, 10, 13, 9, 0), self.tz)
        self.alice = CustomUser.objects.create_user(
            email="avail.alice@unza.zm", password="strongpass123", full_name="Alice"
        )
        self.bob = CustomUser.objects.create_user(
            email="avail.bob@unza.zm", password="strongpass123", full_name="Bob"
        )
        self.cara = CustomUser.objects.create_user(
            email="avail.cara@unza.zm", password="strongpass123", full_name="Cara"
        )

    def slot(self, student, day, start, end):
        ScheduleSlot.objects.create(
            student=student, day_of_week=day,
            start_time=datetime.time(*start), end_time=datetime.time(*end),
        )

    def local(self, *args):
        return timezone.make_aware(datetime.datetime(*args), self.tz).isoformat()

    def test_partial_overlap_is_found(self):
        # The case exact slot matching misses: 14-16 and 15-17 share 15-16.
        self.slot(self.alice, 1, (14, 0), (16, 0))
        self.slot(self.bob, 1, (15, 0), (17, 0))
        self.assertEqual(common_weekly_windows([self.alice, self.bob]), {1: [(15 * 60, 16 * 60)]})

    def test_no_overlap_gives_no_windows(self):
        self.slot(self.alice, 1, (8, 0), (10, 0))
        self.slot(self.bob, 1, (10, 0), (12, 0))  # touching, not overlapping
        self.assertEqual(common_weekly_windows([self.alice, self.bob]), {})
        self.assertFalse(has_common_availability([self.alice, self.bob]))

    def test_adjacent_slots_are_merged_before_intersecting(self):
        self.slot(self.alice, 2, (14, 0), (15, 0))
        self.slot(self.alice, 2, (15, 0), (16, 0))
        self.slot(self.bob, 2, (14, 30), (16, 0))
        self.assertEqual(common_weekly_windows([self.alice, self.bob]), {2: [(14 * 60 + 30, 16 * 60)]})

    def test_three_students_must_all_be_free(self):
        self.slot(self.alice, 3, (9, 0), (17, 0))
        self.slot(self.bob, 3, (10, 0), (14, 0))
        self.slot(self.cara, 3, (13, 0), (18, 0))
        self.assertEqual(common_weekly_windows([self.alice, self.bob, self.cara]), {3: [(13 * 60, 14 * 60)]})

    def test_suggestions_are_concrete_upcoming_datetimes(self):
        self.slot(self.alice, 1, (14, 0), (16, 0))  # Tuesday
        self.slot(self.bob, 1, (15, 0), (17, 0))
        result = suggest_session_times([self.alice, self.bob], now=self.now)
        self.assertEqual(result["suggestions"], [{
            "start": self.local(2026, 10, 13, 15, 0),
            "end": self.local(2026, 10, 13, 16, 0),
            "day_name": "Tuesday",
            "duration_minutes": 60,
        }])
        self.assertEqual(result["students_without_availability"], [])

    def test_windows_earlier_in_the_week_roll_over_to_next_week(self):
        self.slot(self.alice, 0, (10, 0), (12, 0))  # Monday -- already past on Tuesday
        self.slot(self.bob, 0, (10, 0), (12, 0))
        result = suggest_session_times([self.alice, self.bob], now=self.now)
        self.assertEqual(len(result["suggestions"]), 1)
        self.assertEqual(result["suggestions"][0]["start"], self.local(2026, 10, 19, 10, 0))

    def test_window_in_progress_starts_from_next_quarter_hour(self):
        self.slot(self.alice, 1, (14, 0), (17, 0))
        self.slot(self.bob, 1, (14, 0), (17, 0))
        now = timezone.make_aware(datetime.datetime(2026, 10, 13, 15, 7), self.tz)
        first = suggest_session_times([self.alice, self.bob], now=now)["suggestions"][0]
        self.assertEqual(first["start"], self.local(2026, 10, 13, 15, 15))
        self.assertEqual(first["duration_minutes"], 105)

    def test_windows_shorter_than_minimum_are_skipped(self):
        self.slot(self.alice, 1, (14, 0), (16, 0))
        self.slot(self.bob, 1, (15, 30), (17, 0))  # only 30 minutes shared
        self.assertEqual(suggest_session_times([self.alice, self.bob], now=self.now)["suggestions"], [])
        relaxed = suggest_session_times([self.alice, self.bob], now=self.now, min_minutes=30)
        self.assertEqual(len(relaxed["suggestions"]), 1)

    def test_student_without_slots_is_reported(self):
        self.slot(self.alice, 1, (14, 0), (16, 0))
        result = suggest_session_times([self.alice, self.bob], now=self.now)
        self.assertEqual(result["suggestions"], [])
        self.assertEqual(result["students_without_availability"], [self.bob])
