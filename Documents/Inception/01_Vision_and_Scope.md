# Inception — Vision and Scope

## 1. Product vision

StudyPlannerApp is a web-based study management application intended to help university students organize individual study time and find academically complementary peers for collaborative study.

The implemented core idea is:

> A student records subject-specific strengths and weaknesses, provides recurring weekly availability, and requests an AI-assisted peer match for a selected subject.

The matching implementation uses a vector representation of the requesting student's weakness/strength profile and candidate students' complementary profile, computes cosine similarity, applies an availability penalty when weekly slots do not overlap, ranks the candidates, and persists the highest-ranked pairing.

## 2. Primary stakeholders

| Stakeholder | Interest |
|---|---|
| Student | Personal study planning, self-assessment, peer matching and feedback |
| Administrator | Maintaining the subject catalogue and supporting system administration |
| Development team | Feasible implementation, maintainability and project completion |
| Project supervisor | Technical quality, appropriate software-engineering process and documentation |

## 3. Current actors

### Student
The primary actor. A student can authenticate, manage profile information, read subjects, maintain self-assessments and availability, create personal study sessions, request/view matches, schedule and complete group-study sessions, and submit feedback.

### Administrator
An administrative user/staff member can manage the subject catalogue. The feedback metrics endpoint is also accessible to administrators/staff.

### Matching engine
The matching engine is **not** modelled as a domain actor in the domain model. It is an internal application/service component invoked by the matching controller.

## 4. Current functional scope

- Account registration and JWT authentication
- Student profile retrieval/update
- Subject catalogue
- Self-assessment CRUD and bulk submission
- Weekly recurring availability
- Personal study sessions
- AI peer matching
- Match history for the authenticated student
- Group-study session scheduling
- Group-study session completion
- Post-session feedback
- Aggregated feedback metrics

## 5. Planned features not evidenced as implemented

These remain future scope unless the implementation is extended:

- Transcript upload
- Automatic transcript parsing
- Academic profile generation from transcript grades
- Manual confirmation/correction of extracted transcript data
- Explicit opt-in/opt-out workflow for GroupStudy
- Invitation lifecycle with accept/decline
- Real-time chat/video
- LMS integration
- GPA calculation
- Payment functionality

## 6. Key quality concerns

1. **Security** — authenticated access and ownership restrictions must remain enforced.
2. **Matching quality** — recommendations should be useful and should be evaluated through feedback.
3. **Data integrity** — assessment uniqueness, valid 1–5 ratings, valid time ranges and participant restrictions are important.
4. **Maintainability** — the matching algorithm should remain isolated from controllers so it can evolve independently.
5. **Usability** — the core student workflow should be understandable without developer assistance.

## 7. Success criteria for the current implementation

A practical acceptance baseline is:

- Student can register and log in.
- Student can maintain profile, subjects, self-assessments and weekly availability.
- Student can create personal study sessions.
- Student can request a subject-specific peer match.
- The system returns a persisted match when a candidate exists.
- Student can schedule and complete a matched group-study session.
- Feedback is only accepted for completed sessions and only from participants.
- Feedback metrics can be calculated from submitted ratings.

