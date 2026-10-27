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
MATCHES_URL = "/api/matching/matches/"
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

    def test_complementary_profile_ranked_above_similar_profile(self):
        # Both candidates fully cover the requester's low need (2), so coverage ties at 1.0;
        # the mirror-image profile is ranked first because more support can flow between them.
        results = generate_peer_matches(self.requester, self.subject.id)
        self.assertEqual(results[0]["candidate"], self.complementary)
        self.assertEqual(results[1]["candidate"], self.similar)
        self.assertGreater(results[0]["support_exchanged"], results[1]["support_exchanged"])

    def _profiles(self, requester, candidates):
        """Create a requester and candidates as (label, strength, need) and return the results by label."""
        req = make_student(f"req.{requester[0]}@unza.zm", "Requester")
        SelfAssessment.objects.create(
            student=req, subject=self.subject, strength_score=requester[1], weakness_score=requester[2]
        )
        by_id = {}
        for label, strength, need in candidates:
            student = make_student(f"cand.{label}@unza.zm", label)
            SelfAssessment.objects.create(
                student=student, subject=self.subject, strength_score=strength, weakness_score=need
            )
            by_id[student.id] = label
        results = generate_peer_matches(req, self.subject.id, top_n=50)
        return {by_id[r["candidate"].id]: r for r in results if r["candidate"].id in by_id}

    def test_strong_candidate_outranks_weak_candidates_for_balanced_requester(self):
        # The case that cosine similarity could not separate (all of these scored 1.00 before).
        r = self._profiles(("bal", 2, 4), [
            ("strong", 5, 1), ("strong_gaps", 5, 2), ("average", 3, 3),
            ("as_weak", 2, 4), ("weaker", 1, 5),
        ])
        self.assertEqual(r["strong"]["coverage"], 1.0)
        self.assertEqual(r["strong_gaps"]["coverage"], 1.0)
        self.assertGreater(r["strong"]["coverage"], r["average"]["coverage"])
        self.assertGreater(r["average"]["coverage"], r["as_weak"]["coverage"])
        self.assertGreater(r["as_weak"]["coverage"], r["weaker"]["coverage"])

    def test_unsuitable_candidate_scores_low(self):
        # Two students who both need a lot of help and offer little.
        r = self._profiles(("weak", 1, 5), [("unsuitable", 1, 5), ("helper", 5, 1)])
        self.assertAlmostEqual(r["unsuitable"]["coverage"], 0.2, places=3)
        self.assertGreater(r["helper"]["coverage"], r["unsuitable"]["coverage"])

    def test_similar_strong_profiles_score_full_coverage_for_low_need(self):
        # A requester who needs little help is fully covered by an equally strong peer.
        r = self._profiles(("strong_req", 5, 1), [("same", 5, 1)])
        self.assertEqual(r["same"]["coverage"], 1.0)

    def test_relevance_scores_always_between_0_and_1(self):
        from .engine import coverage_score
        for rs in range(1, 6):
            for rn in range(1, 6):
                for cs in range(1, 6):
                    for cn in range(1, 6):
                        score = coverage_score(rs, rn, cs, cn)
                        self.assertGreater(score, 0)
                        self.assertLessEqual(score, 1)

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


class MatchingAvailabilityTests(APITestCase):
    """The five availability cases from the supervisor's review, checked through the engine."""

    def setUp(self):
        self.subject = Subject.objects.create(code="CSC302", name="Algorithms")
        self.a = make_student("avail.a@unza.zm", "Student A")
        self.b = make_student("avail.b@unza.zm", "Student B")
        SelfAssessment.objects.create(student=self.a, subject=self.subject, strength_score=2, weakness_score=4)
        SelfAssessment.objects.create(student=self.b, subject=self.subject, strength_score=5, weakness_score=1)

    def slot(self, student, start, end, day=2):
        ScheduleSlot.objects.create(student=student, day_of_week=day, start_time=start, end_time=end)

    def result(self):
        return generate_peer_matches(self.a, self.subject.id)[0]

    def test_partial_overlap_counts_as_shared(self):
        self.slot(self.a, "10:00", "12:00")
        self.slot(self.b, "11:00", "13:00")
        self.assertEqual(self.result()["availability"], "shared")
        self.assertEqual(self.result()["relevance_score"], 1.0)

    def test_exact_overlap_counts_as_shared(self):
        self.slot(self.a, "10:00", "12:00")
        self.slot(self.b, "10:00", "12:00")
        self.assertEqual(self.result()["availability"], "shared")

    def test_adjacent_intervals_are_not_shared(self):
        self.slot(self.a, "10:00", "11:00")
        self.slot(self.b, "11:00", "12:00")
        self.assertEqual(self.result()["availability"], "none")
        self.assertEqual(self.result()["relevance_score"], 0.75)

    def test_no_overlap_is_penalised(self):
        self.slot(self.a, "10:00", "11:00")
        self.slot(self.b, "12:00", "13:00")
        self.assertEqual(self.result()["availability"], "none")
        self.assertEqual(self.result()["relevance_score"], 0.75)

    def test_missing_availability_is_unknown_not_compatible(self):
        self.slot(self.a, "10:00", "12:00")  # B has no availability at all
        result = self.result()
        self.assertEqual(result["availability"], "unknown")
        self.assertEqual(result["relevance_score"], 0.9)
        self.assertLess(result["relevance_score"], 1.0)


class MatchScoreValidationTests(APITestCase):
    def test_relevance_score_outside_0_to_1_is_rejected(self):
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            Match(relevance_score=3).full_clean()
        with self.assertRaises(ValidationError):
            Match(relevance_score=-0.1).full_clean()
        Match(relevance_score=0.85).full_clean()


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

    def test_cannot_complete_an_already_completed_session(self):
        session = GroupStudySession.objects.create(
            match=self.match, scheduled_time=timezone.now(), status=GroupStudySessionStatus.COMPLETED
        )
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(f"{SESSIONS_URL}{session.id}/complete/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_complete_a_session_before_its_scheduled_time(self):
        session = GroupStudySession.objects.create(
            match=self.match, scheduled_time=timezone.now() + timezone.timedelta(days=1)
        )
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(f"{SESSIONS_URL}{session.id}/complete/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        session.refresh_from_db()
        self.assertEqual(session.status, GroupStudySessionStatus.SCHEDULED)

    def test_cannot_complete_a_cancelled_session(self):
        session = GroupStudySession.objects.create(
            match=self.match, scheduled_time=timezone.now(), status=GroupStudySessionStatus.CANCELLED
        )
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(f"{SESSIONS_URL}{session.id}/complete/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_participant_can_cancel_a_scheduled_session(self):
        session = GroupStudySession.objects.create(match=self.match, scheduled_time=timezone.now())
        self.client.force_authenticate(user=self.student_b)
        response = self.client.post(f"{SESSIONS_URL}{session.id}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        session.refresh_from_db()
        self.assertEqual(session.status, GroupStudySessionStatus.CANCELLED)

    def test_cannot_cancel_an_already_cancelled_session(self):
        session = GroupStudySession.objects.create(
            match=self.match, scheduled_time=timezone.now(), status=GroupStudySessionStatus.CANCELLED
        )
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(f"{SESSIONS_URL}{session.id}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_cancel_an_already_completed_session(self):
        session = GroupStudySession.objects.create(
            match=self.match, scheduled_time=timezone.now(), status=GroupStudySessionStatus.COMPLETED
        )
        self.client.force_authenticate(user=self.student_a)
        response = self.client.post(f"{SESSIONS_URL}{session.id}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        session.refresh_from_db()
        self.assertEqual(session.status, GroupStudySessionStatus.COMPLETED)

    def test_outsider_cannot_cancel_someone_elses_session(self):
        session = GroupStudySession.objects.create(match=self.match, scheduled_time=timezone.now())
        self.client.force_authenticate(user=self.outsider)
        response = self.client.post(f"{SESSIONS_URL}{session.id}/cancel/")
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


class DataIsolationTests(APITestCase):
    """A student must not see another student's matches, GroupStudy sessions or feedback."""

    def setUp(self):
        self.a = make_student("iso.a@unza.zm", "Student A")
        self.b = make_student("iso.b@unza.zm", "Student B")
        self.outsider = make_student("iso.outsider@unza.zm", "Outsider")
        self.match = Match.objects.create(relevance_score=0.9)
        MatchParticipant.objects.create(match=self.match, student=self.a)
        MatchParticipant.objects.create(match=self.match, student=self.b)
        self.session = GroupStudySession.objects.create(
            match=self.match, scheduled_time=timezone.now(), status=GroupStudySessionStatus.COMPLETED
        )
        Feedback.objects.create(student=self.a, session=self.session, rating=5, comment="Private comment")
        self.client.force_authenticate(user=self.outsider)

    def test_outsider_cannot_list_or_retrieve_another_students_match(self):
        self.assertEqual(self.client.get(MATCHES_URL).data, [])
        self.assertEqual(self.client.get(f"{MATCHES_URL}{self.match.id}/").status_code, status.HTTP_404_NOT_FOUND)

    def test_outsider_cannot_list_another_students_group_sessions(self):
        self.assertEqual(self.client.get(SESSIONS_URL).data, [])

    def test_student_cannot_read_another_students_feedback(self):
        self.assertEqual(self.client.get(FEEDBACK_URL).data, [])

    def test_feedback_rating_outside_1_to_5_is_rejected(self):
        self.client.force_authenticate(user=self.b)
        for rating in (0, 6):
            response = self.client.post(FEEDBACK_URL, {"session": self.session.id, "rating": rating})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Feedback.objects.filter(student=self.b).exists())


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
