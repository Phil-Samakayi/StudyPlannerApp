# Elaboration — System Sequence Diagrams

The SSDs show system events at the boundary of the system. They are intentionally less detailed than a design sequence diagram.

## SSD-01 — Request AI Peer Match

**Actor:** Student

1. `requestMatch(subjectId)`
2. System authenticates the request.
3. System retrieves the student's assessment for the subject.
4. System retrieves candidate assessments.
5. System retrieves recurring availability.
6. Matching engine scores candidates.
7. System persists the highest-ranked Match and its participants.
8. System returns the Match.

**Alternative:** no assessment/candidates → return no-match response.

### Matching rule currently implemented

Request vector:
`[requesting weakness score, 6 - requesting strength score]`

Candidate vector:
`[candidate strength score, 6 - candidate weakness score]`

Compatibility:
`cosine_similarity(request_vector, candidate_vector)`

Availability:
- overlapping exact recurring `(day, start, end)` slot → factor `1.0`
- no overlap → factor `0.75`
- if either side has no slots → treated as overlapping by the current implementation

Final relevance:
`round(similarity × availability_factor, 2)`

The top candidate is persisted as the Match.

## SSD-02 — Update Weekly Availability

1. Student selects weekly slots.
2. UI sends bulk update.
3. System authenticates the student.
4. Existing slots for that student are deleted.
5. Submitted slots are validated.
6. New slots are created.
7. System returns the saved slots.

## SSD-03 — Submit Post-Session Feedback

1. Student submits session, rating and comment.
2. System verifies the session is completed.
3. System verifies the student participated.
4. System verifies duplicate feedback does not already exist.
5. System creates Feedback.
6. System returns confirmation.

## SSD-04 — Schedule Group Study Session

1. Student selects a Match.
2. Student supplies scheduled time.
3. System verifies the student is a participant in the Match.
4. System creates the GroupStudySession.
5. System returns the scheduled session.

