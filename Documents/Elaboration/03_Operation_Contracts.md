# Elaboration — Operation Contracts

Operation contracts describe important system operations in terms of preconditions, postconditions and system state changes.

## OC-01 — requestMatch(subjectId)

**Cross-reference:** UC-08 / SSD-01

**Preconditions**
- Current user is authenticated.
- `subjectId` identifies an existing Subject.
- Current user has a SelfAssessment for that subject.

**Postconditions on success**
- A Match is created.
- Match.relevance_score equals the selected candidate's final relevance score.
- Two MatchParticipant associations exist: requesting student and selected candidate.
- Match is retrievable through the requesting student's match list.

**Postconditions when no candidate exists**
- No Match is created.
- A no-candidate response is returned.

## OC-02 — bulkUpdateSlots(slots)

**Cross-reference:** UC-06 / SSD-02

**Preconditions**
- Current user is authenticated.
- `slots` is a list.
- Every slot has a valid day/time combination.
- `end_time > start_time`.

**Postconditions**
- All previous ScheduleSlot rows for the current student are removed.
- One ScheduleSlot is created for each valid submitted slot.
- Returned collection contains the student's new availability.

## OC-03 — scheduleGroupStudySession(match, scheduledTime)

**Cross-reference:** UC-10 / SSD-04

**Preconditions**
- Current user is authenticated.
- Current user participates in the supplied Match.

**Postconditions**
- A GroupStudySession is created for the Match.
- Scheduled time is stored.
- Initial status is `scheduled`.

## OC-04 — completeGroupStudySession(session)

**Cross-reference:** UC-11

**Preconditions**
- Current user can retrieve the session through their participating Match.

**Postconditions**
- Session.status becomes `completed`.
- Feedback becomes eligible for that session.

## OC-05 — submitFeedback(session, rating, comment)

**Cross-reference:** UC-12 / SSD-03

**Preconditions**
- Current user is authenticated.
- Session status is `completed`.
- Current user is a participant in the session's Match.
- Current user has not already submitted feedback for that session.
- Rating is 1–5.

**Postconditions**
- A Feedback record exists linked to the student and session.
- Feedback contains the supplied rating and optional comment.

