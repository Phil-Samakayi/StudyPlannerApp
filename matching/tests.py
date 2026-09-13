# matching/tests.py
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from subjects.models import Subject
from assessments.models import SelfAssessment
from scheduling.models import ScheduleSlot
from .engine import generate_peer_matches
from .models import Match, MatchParticipant, GroupStudySession, GroupStudySessionStatus, Feedback

REQUEST_MATCH_URL = "/api/matching/matches/request-match/"
SESSIONS_URL = "/api/matching/sessions/"
FEEDBACK_URL = "/api/matching/feedback/"
FEEDBACK_METRICS_URL = "/api/matching/feedback/metrics/"


def make_student(email, full_name):
    return CustomUser.objects.create_user(email=email, password="strongpass123", full_name=full_name)


class MatchingEngineTests(APITestCase):
    """Directly exercises matching/engine.py's generate_peer_matches()."""

    def setUp(self):
        self.subject = Subject.objects.create(code="CSC301", name="Data Structures")
        self.requester = make_student("engine.requester@unza.zm", "Requester")
        self.complementary = make_student("engine.complementary@unza.zm", "Complementary")
        self.similar = make_student("engine.similar@unza.zm", "Similar")

        # Requester is strong (5) but weak (2) -- needs a peer strong where they're weak.
        SelfAssessment.objects.create(
            student=self.requester, subject=self.subject, strength_score=5, weakness_score=2
        )
        # Complementary profile: an exact swap -- weak where requester is strong,
        # strong where requester is weak.
        SelfAssessment.objects.create(
            student=self.complementary, subject=self.subject, strength_score=2, weakness_score=5
        )
        # Identical profile to requester -- not complementary at all.
        SelfAssessment.objects.create(
            student=self.similar, subject=self.subject, strength_score=5, weakness_score=2
        )

    def test_returns_empty_when_requester_has_no_assessment(self):
        no_assessment_student = make_student("engine.none@unza.zm", "No Assessment")
        results = generate_peer_matches(no_assessment_student, self.subject.id)
        self.assertEqual(results, [])

    def test_returns_empty_when_no_candidates(self):
        SelfAssessment.objects.filter(student__in=[self.complementary, self.similar]).delete()
        results = generate_peer_matches(self.requester, self.subject.id)
        self.assertEqual(results, [])

    def test_ranks_complementary_profile_above_similar_profile(self):
        results = generate_peer_matches(self.requester, self.subject.id)
        candidate_ids = [r["candidate"].id for r in results]
        self.assertIn(self.complementary.id, candidate_ids)
        self.assertIn(self.similar.id, candidate_ids)

        complementary_score = next(r["relevance_score"] for r in results if r["candidate"].id == self.complementary.id)
        similar_score = next(r["relevance_score"] for r in results if r["candidate"].id == self.similar.id)
        self.assertGreater(complementary_score, similar_score)

    def test_known_limitation_cosine_similarity_ties_on_proportional_profiles(self):
        """
        Documents a real limitation, not an assertion of correct behavior:
        because the engine scores pairs with plain cosine similarity, any two
        profile vectors that are positive scalar multiples of each other tie
        at 1.0 -- including a candidate who merely *scales* the requester's
        profile rather than truly complementing it. Example: requester
        (strength=5, weakness=1) has vector [1, 1]; a same-profile peer
        (strength=5, weakness=1) has vector [5, 5] -- parallel to [1, 1], so
        cosine similarity can't tell them apart from a perfect complement.
        Worth revisiting for the AI matching sprint (e.g. weight in raw
        score magnitude, not just direction).
        """
        same_profile_peer = make_student("engine.tie@unza.zm", "Tie Case")
        tie_requester = make_student("engine.tie.requester@unza.zm", "Tie Requester")
        for student in (tie_requester, same_profile_peer):
            SelfAssessment.objects.create(
                student=student, subject=self.subject, strength_score=5, weakness_score=1
            )
        results = generate_peer_matches(tie_requester, self.subject.id)
        self.assertEqual(results[0]["relevance_score"], 1.0)

    def test_overlapping_availability_outranks_no_overlap(self):
        # Two otherwise-identical complementary candidates; only one shares a free slot.
        overlapping = make_student("engine.overlap@unza.zm", "Overlap")
        no_overlap = make_student("engine.nooverlap@unza.zm", "No Overlap")
        for student in (overlapping, no_overlap):
            SelfAssessment.objects.create(
                student=student, subject=self.subject, strength_score=1, weakness_score=5
            )

        ScheduleSlot.objects.create(student=self.requester, day_of_week=1, start_time="14:00", end_time="16:00")
        ScheduleSlot.objects.create(student=overlapping, day_of_week=1, start_time="14:00", end_time="16:00")
        ScheduleSlot.objects.create(student=no_overlap, day_of_week=3, start_time="09:00", end_time="10:00")

        results = generate_peer_matches(self.requester, self.subject.id)
        overlap_score = next(r["relevance_score"] for r in results if r["candidate"].id == overlapping.id)
        no_overlap_score = next(r["relevance_score"] for r in results if r["candidate"].id == no_overlap.id)
        self.assertGreater(overlap_score, no_overlap_score)


class RequestMatchViewTests(APITestCase):
    def setUp(self):
        self.subject = Subject.objects.create(code="CSC301", name="Data Structures")
        self.requester = make_student("view.requester@unza.zm", "Requester")
        self.peer = make_student("view.peer@unza.zm", "Peer")
        SelfAssessment.objects.create(
            student=self.requester, subject=self.subject, strength_score=5, weakness_score=1
        )
        SelfAssessment.objects.create(
            student=self.peer, subject=self.subject, strength_score=1, weakness_score=5
        )
        self.client.force_authenticate(user=self.requester)

    def test_request_match_creates_match_with_both_participants(self):
        response = self.client.post(REQUEST_MATCH_URL, {"subject_id": self.subject.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        match = Match.objects.get(id=response.data["id"])
        participant_ids = set(MatchParticipant.objects.filter(match=match).values_list("student_id", flat=True))
        self.assertEqual(participant_ids, {self.requester.id, self.peer.id})

    def test_request_match_with_no_candidates_returns_200_with_no_match_created(self):
        SelfAssessment.objects.filter(student=self.peer).delete()
        response = self.client.post(REQUEST_MATCH_URL, {"subject_id": self.subject.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Match.objects.count(), 0)

    def test_request_match_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(REQUEST_MATCH_URL, {"subject_id": self.subject.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GroupStudySessionTests(APITestCase):
    def setUp(self):
        self.student_a = make_student("session.a@unza.zm", "Student A")
        self.student_b = make_student("session.b@unza.zm", "Student B")
        self.outsider = make_student("session.outsider@unza.zm", "Outsider")

        self.match = Match.objects.create(relevance_score=0.9)
        MatchParticipant.objects.create(match=self.match, student=self.student_a)
        MatchParticipant.objects.create(match=self.match, student=self.student_b)

    def test_participant_can_schedule_a_session_for_their_match(self):
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(SESSIONS_URL, {
            "match": self.match.id,
            "scheduled_time": timezone.now().isoformat(),
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(GroupStudySession.objects.filter(match=self.match).exists())

    def test_non_participant_cannot_schedule_a_session_for_someone_elses_match(self):
        self.client.force_authenticate(user=self.outsider)
        response = self.client.post(SESSIONS_URL, {
            "match": self.match.id,
            "scheduled_time": timezone.now().isoformat(),
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertFalse(GroupStudySession.objects.filter(match=self.match).exists())

    def test_participant_can_mark_session_completed(self):
        session = GroupStudySession.objects.create(match=self.match, scheduled_time=timezone.now())
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(f"{SESSIONS_URL}{session.id}/complete/")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        session.refresh_from_db()
        self.assertEqual(session.status, GroupStudySessionStatus.COMPLETED)

    def test_outsider_cannot_mark_someone_elses_session_completed(self):
        session = GroupStudySession.objects.create(match=self.match, scheduled_time=timezone.now())
        self.client.force_authenticate(user=self.outsider)
        response = self.client.post(f"{SESSIONS_URL}{session.id}/complete/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FeedbackTests(APITestCase):
    def setUp(self):
        self.student_a = make_student("feedback.a@unza.zm", "Student A")
        self.student_b = make_student("feedback.b@unza.zm", "Student B")
        self.outsider = make_student("feedback.outsider@unza.zm", "Outsider")

        self.match = Match.objects.create(relevance_score=0.9)
        MatchParticipant.objects.create(match=self.match, student=self.student_a)
        MatchParticipant.objects.create(match=self.match, student=self.student_b)

    def test_feedback_rejected_before_session_completed(self):
        session = GroupStudySession.objects.create(match=self.match, scheduled_time=timezone.now())
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(FEEDBACK_URL, {
            "session": session.id, "rating": 5, "comment": "Great session",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_participant_can_submit_feedback_after_completion(self):
        session = GroupStudySession.objects.create(
            match=self.match, scheduled_time=timezone.now(), status=GroupStudySessionStatus.COMPLETED
        )
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(FEEDBACK_URL, {
            "session": session.id, "rating": 5, "comment": "Great session",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Feedback.objects.get().student, self.student_a)

    def test_non_participant_cannot_submit_feedback(self):
        session = GroupStudySession.objects.create(
            match=self.match, scheduled_time=timezone.now(), status=GroupStudySessionStatus.COMPLETED
        )
        self.client.force_authenticate(user=self.outsider)
        response = self.client.post(FEEDBACK_URL, {
            "session": session.id, "rating": 5, "comment": "Not really there",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_feedback_for_same_session_is_rejected(self):
        session = GroupStudySession.objects.create(
            match=self.match, scheduled_time=timezone.now(), status=GroupStudySessionStatus.COMPLETED
        )
        self.client.force_authenticate(user=self.student_a)
        self.client.post(FEEDBACK_URL, {"session": session.id, "rating": 5, "comment": "First"})
        response = self.client.post(FEEDBACK_URL, {"session": session.id, "rating": 3, "comment": "Second"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Feedback.objects.filter(session=session, student=self.student_a).count(), 1)


class FeedbackMetricsTests(APITestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user(
            email="metrics.admin@unza.zm", password="strongpass123", full_name="Metrics Admin",
            role="ADMIN", is_staff=True,
        )
        self.student_a = make_student("metrics.a@unza.zm", "Student A")
        self.student_b = make_student("metrics.b@unza.zm", "Student B")
        self.student_c = make_student("metrics.c@unza.zm", "Student C")

        match1 = Match.objects.create(relevance_score=0.9)
        MatchParticipant.objects.create(match=match1, student=self.student_a)
        MatchParticipant.objects.create(match=match1, student=self.student_b)
        session1 = GroupStudySession.objects.create(
            match=match1, scheduled_time=timezone.now(), status=GroupStudySessionStatus.COMPLETED
        )
        Feedback.objects.create(student=self.student_a, session=session1, rating=5)

        match2 = Match.objects.create(relevance_score=0.4)
        MatchParticipant.objects.create(match=match2, student=self.student_a)
        MatchParticipant.objects.create(match=match2, student=self.student_c)
        session2 = GroupStudySession.objects.create(
            match=match2, scheduled_time=timezone.now(), status=GroupStudySessionStatus.COMPLETED
        )
        Feedback.objects.create(student=self.student_c, session=session2, rating=2)

    def test_metrics_computes_relevance_rate_against_75_percent_objective(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(FEEDBACK_METRICS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_reviews"], 2)
        # 1 of 2 reviews is >=4 (rating>=4 counts as "positive") => 50%, below the 75% objective.
        self.assertEqual(response.data["perceived_relevance_rate"], "50.0%")
        self.assertFalse(response.data["meets_objective_3"])

    def test_metrics_with_no_feedback_reports_zero_without_error(self):
        Feedback.objects.all().delete()
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(FEEDBACK_METRICS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_reviews"], 0)
        self.assertFalse(response.data["meets_objective_3"])
