# Transition — Acceptance and Validation Plan

## 1. Purpose

Transition verifies that the integrated StudyPlannerApp satisfies the core use cases and that the architecturally significant matching workflow behaves correctly.

## 2. Acceptance scenarios

### AT-01 Registration/Login
**Given** a new student  
**When** valid registration data is submitted  
**Then** the account is created and the student can obtain JWT tokens.

### AT-02 Self-assessment
**Given** an authenticated student  
**When** the student submits strength and weakness values from 1 to 5  
**Then** the assessment is stored for that student and subject.

### AT-03 Availability
**Given** an authenticated student  
**When** weekly availability is saved  
**Then** the student's previous availability is replaced by the submitted slots.

### AT-04 Match success
**Given** two students with assessments for the same subject  
**When** one student requests a match  
**Then** a Match is created with two participants and a relevance score.

### AT-05 No-match path
**Given** a student with no assessment or no candidate  
**When** the student requests a match  
**Then** the system returns an informational no-match response and does not create an invalid Match.

### AT-06 Group study authorization
**Given** a Match  
**When** a participant schedules a session  
**Then** the GroupStudySession is created.

**When** a non-participant attempts the same action  
**Then** validation rejects the operation.

### AT-07 Feedback
**Given** a completed GroupStudySession  
**When** a participating student submits a rating from 1 to 5  
**Then** Feedback is created.

**When** the session is not completed  
**Then** feedback is rejected.

**When** the student already submitted feedback  
**Then** the duplicate is rejected.

## 3. Matching-quality validation

Collect post-session ratings and calculate:
- total reviews
- average rating
- positive reviews (`rating >= 4`)
- perceived relevance rate

The current metrics endpoint uses a 75% positive-review threshold as its objective indicator.

## 4. Transition checklist

- [ ] Run database migrations on clean environment.
- [ ] Verify registration/login.
- [ ] Verify per-user authorization.
- [ ] Verify subject administration.
- [ ] Verify assessment constraints.
- [ ] Verify availability validation.
- [ ] Verify matching success and no-match paths.
- [ ] Verify group-study participant restrictions.
- [ ] Verify completion and feedback rules.
- [ ] Verify feedback metrics.
- [ ] Verify frontend/API integration.
- [ ] Record known defects and limitations.
- [ ] Confirm future-scope features are not presented as implemented.

