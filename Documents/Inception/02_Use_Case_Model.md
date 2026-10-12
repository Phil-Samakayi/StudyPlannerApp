# Inception — Use Case Model

## 1. Use-case identification

The following use cases are grounded in the uploaded implementation.

| ID | Use Case | Primary Actor | Status |
|---|---|---|---|
| UC-01 | Register Account | Student | Implemented |
| UC-02 | Log In | Student | Implemented |
| UC-03 | Manage Profile | Student | Implemented |
| UC-04 | View Subject Catalogue | Student/Admin | Implemented |
| UC-05 | Manage Self-Assessment | Student | Implemented |
| UC-06 | Manage Weekly Availability | Student | Implemented |
| UC-07 | Manage Personal Study Session | Student | Implemented |
| UC-08 | Request AI Peer Match | Student | Implemented |
| UC-09 | View My Matches | Student | Implemented |
| UC-10 | Schedule Group Study Session | Student | Implemented |
| UC-11 | Complete Group Study Session | Student | Implemented |
| UC-12 | Submit Post-Session Feedback | Student | Implemented |
| UC-13 | View Feedback Metrics | Admin/Staff | Implemented |
| UC-14 | Upload Transcript | Student | Planned / not evidenced |
| UC-15 | Review Academic Profile | Student | Planned / not evidenced |
| UC-16 | Accept/Decline GroupStudy Invitation | Student | Planned / not evidenced |

## 2. Core use-case priorities

### Highest priority
- UC-02 Log In
- UC-05 Manage Self-Assessment
- UC-06 Manage Weekly Availability
- UC-08 Request AI Peer Match
- UC-09 View My Matches
- UC-10 Schedule Group Study Session
- UC-12 Submit Post-Session Feedback

These represent the core differentiating workflow.

### Supporting priority
- UC-01 Register Account
- UC-03 Manage Profile
- UC-04 View Subject Catalogue
- UC-07 Manage Personal Study Session
- UC-11 Complete Group Study Session
- UC-13 View Feedback Metrics

## 3. Use-case relationships

Keep UML relationships deliberately limited, consistent with Larman's advice not to replace useful use-case text with excessive `include`/`extend` relationships.

- **Schedule Group Study Session** requires the student to have a match, so viewing/selecting an existing match is a prerequisite.
- **Submit Post-Session Feedback** requires a completed session.
- **Request AI Peer Match** results in a match being available for later viewing.

The detailed behavioural rules belong in the use-case descriptions and operation contracts, not only in the diagram.

## 4. Fully dressed core use case — Request AI Peer Match

**Goal:** Find a suitable study peer for a selected subject.

**Preconditions**
1. Student is authenticated.
2. Student has a self-assessment for the selected subject.
3. The subject exists.

**Main success scenario**
1. Student selects a subject.
2. Student requests a peer match.
3. System retrieves the student's self-assessment.
4. System finds candidate self-assessments for the same subject.
5. System obtains recurring availability for the requesting student and candidates.
6. Matching engine constructs the comparison vectors.
7. Matching engine calculates cosine similarity.
8. Matching engine applies the availability factor.
9. Candidates are sorted by final relevance score.
10. System selects the highest-ranked candidate.
11. System creates a Match.
12. System creates MatchParticipant records for the requesting student and selected peer.
13. System returns the created Match.

**Alternative**
- If no self-assessment or candidates exist, the system returns no match rather than creating a Match record.

## 5. Fully dressed core use case — Submit Post-Session Feedback

**Preconditions**
1. Student is authenticated.
2. Student participated in the referenced group-study session.
3. The session is completed.
4. Student has not already submitted feedback for that session.

**Main success scenario**
1. Student selects a completed session.
2. Student submits a rating and optional comment.
3. System validates the session status.
4. System validates participation.
5. System validates that duplicate feedback does not exist.
6. System persists the feedback.
7. System returns confirmation.

