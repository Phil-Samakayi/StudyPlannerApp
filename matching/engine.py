# matching/engine.py (Updated to query scheduling.ScheduleSlot)
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from assessments.models import SelfAssessment
from scheduling.models import ScheduleSlot
from .models import Match, MatchParticipant


def generate_peer_matches(requesting_student, subject_id, top_n=5):
    try:
        user_assess = SelfAssessment.objects.get(student=requesting_student, subject_id=subject_id)
    except SelfAssessment.DoesNotExist:
        return []

    req_vector = np.array([[user_assess.weakness_score, 6 - user_assess.strength_score]])

    candidates = SelfAssessment.objects.filter(subject_id=subject_id).exclude(student=requesting_student)
    if not candidates.exists():
        return []

    # Get requesting student's weekly availability slots
    req_slots = set(
        ScheduleSlot.objects.filter(student=requesting_student).values_list("day_of_week", "start_time", "end_time")
    )

    results = []
    for cand in candidates:
        cand_vector = np.array([[cand.strength_score, 6 - cand.weakness_score]])
        similarity = float(cosine_similarity(req_vector, cand_vector)[0][0])

        # Get candidate student's weekly availability slots
        cand_slots = set(
            ScheduleSlot.objects.filter(student=cand.student).values_list("day_of_week", "start_time", "end_time")
        )
        has_overlap = len(req_slots.intersection(cand_slots)) > 0 if (req_slots and cand_slots) else True

        final_relevance = round(similarity * (1.0 if has_overlap else 0.75), 2)

        results.append({
            "candidate": cand.student,
            "relevance_score": final_relevance,
        })

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:top_n]