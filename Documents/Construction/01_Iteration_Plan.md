# Construction — Iteration Plan

Construction should proceed in short, use-case-driven iterations rather than implementing the entire system in one pass.

## Iteration C1 — Accounts and Catalogue

**Goal:** Establish the authenticated student foundation.

Scope:
- registration
- login/token handling
- profile
- subject catalogue
- authorization

Exit criteria:
- student can register/login;
- authenticated profile can be retrieved;
- subjects can be listed;
- only authorized staff/admin users can modify subjects.

## Iteration C2 — Academic Self-Assessment

Scope:
- list/create/update/delete assessments
- bulk submission
- validation
- one assessment per student/subject

Exit criteria:
- invalid scores are rejected;
- duplicate student/subject assessment is prevented;
- student cannot access another student's assessment.

## Iteration C3 — Scheduling

Scope:
- weekly recurring availability
- personal study sessions

Exit criteria:
- availability can be replaced through bulk update;
- invalid time ranges are rejected;
- personal sessions are isolated to the authenticated student.

## Iteration C4 — AI Matching

Scope:
- subject-specific candidate selection
- cosine similarity
- availability factor
- ranking
- Match persistence
- participant associations

Exit criteria:
- a valid request returns the best available candidate;
- no-candidate path is handled cleanly;
- match is persisted;
- only the student's own matches are returned.

## Iteration C5 — Group Study and Feedback

Scope:
- schedule session
- complete session
- feedback
- metrics

Exit criteria:
- only match participants can schedule;
- completed status is required for feedback;
- only participants can submit feedback;
- duplicate feedback is rejected;
- metrics are calculated.

