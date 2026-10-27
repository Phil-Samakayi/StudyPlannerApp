# matching/engine.py
"""
Deterministic peer-matching engine.

For a requesting student and a subject, every other student who has assessed
the same subject is scored on two things:

1. Coverage (magnitude-aware). Strength and need for support are both on a
   1-5 scale. Forward coverage is how much of the requester's need the
   candidate's strength can cover, min(need_r, strength_c) / need_r.
   Reciprocal coverage is the same in the other direction,
   min(need_c, strength_r) / need_c. Coverage is the mean of the two, so it
   lies in (0, 1] and, unlike cosine similarity, a weak candidate can no
   longer score as highly as a strong one.

2. Availability. Using scheduling.availability (interval overlap, not exact
   slot equality):
     - "shared":  the two students share at least one weekly window -> x 1.0
     - "unknown": either student has not set any availability      -> x 0.9
     - "none":    both have availability but it never overlaps      -> x 0.75
   Missing availability is therefore treated as unknown, not as confirmed
   compatibility.

Ties are broken by the total support exchanged,
min(need_r, strength_c) + min(need_c, strength_r), so pairs in which more
help can flow are preferred.

This is a rule-based recommender: it is not trained and does not learn from
feedback.
"""
from assessments.models import SelfAssessment
from scheduling.availability import has_common_availability
from scheduling.models import ScheduleSlot

AVAILABILITY_FACTORS = {"shared": 1.0, "unknown": 0.9, "none": 0.75}


def coverage_score(requester_strength, requester_need, candidate_strength, candidate_need):
    """Mean of forward and reciprocal coverage, in (0, 1]."""
    forward = min(requester_need, candidate_strength) / requester_need
    reciprocal = min(candidate_need, requester_strength) / candidate_need
    return (forward + reciprocal) / 2


def support_exchanged(requester_strength, requester_need, candidate_strength, candidate_need):
    """Total support that can flow between the two students (tie-breaker)."""
    return min(requester_need, candidate_strength) + min(candidate_need, requester_strength)


def availability_status(student_a, student_b, students_with_slots):
    """'shared', 'none' or 'unknown' for two students, using interval overlap."""
    if student_a.pk not in students_with_slots or student_b.pk not in students_with_slots:
        return "unknown"
    return "shared" if has_common_availability([student_a, student_b]) else "none"


def generate_peer_matches(requesting_student, subject_id, top_n=5):
    try:
        user_assess = SelfAssessment.objects.get(student=requesting_student, subject_id=subject_id)
    except SelfAssessment.DoesNotExist:
        return []

    candidates = list(
        SelfAssessment.objects.filter(subject_id=subject_id)
        .exclude(student=requesting_student)
        .select_related("student")
    )
    if not candidates:
        return []

    student_ids = [requesting_student.pk] + [c.student_id for c in candidates]
    students_with_slots = set(
        ScheduleSlot.objects.filter(student_id__in=student_ids).values_list("student_id", flat=True)
    )

    results = []
    for cand in candidates:
        coverage = coverage_score(
            user_assess.strength_score, user_assess.weakness_score,
            cand.strength_score, cand.weakness_score,
        )
        availability = availability_status(requesting_student, cand.student, students_with_slots)
        results.append({
            "candidate": cand.student,
            "relevance_score": round(coverage * AVAILABILITY_FACTORS[availability], 2),
            "coverage": round(coverage, 3),
            "availability": availability,
            "support_exchanged": support_exchanged(
                user_assess.strength_score, user_assess.weakness_score,
                cand.strength_score, cand.weakness_score,
            ),
        })

    results.sort(key=lambda r: (r["relevance_score"], r["support_exchanged"]), reverse=True)
    return results[:top_n]
