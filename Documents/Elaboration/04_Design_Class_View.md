# Elaboration — Design Class View

## 1. Purpose

Unlike the domain model, this design view represents software responsibilities. It therefore contains controllers/viewsets, the matching service, repositories/data-access responsibilities and domain/data classes.

## 2. Controller responsibilities

### AccountController
- register
- login/token issuance
- refresh token
- retrieve/update authenticated profile

### AssessmentController
- list/create own assessments
- retrieve/update/delete own assessment
- bulk submit assessments

### SchedulingController
- list/manage own recurring availability
- bulk update availability
- manage own personal study sessions

### MatchController
- request a match
- list matches belonging to the authenticated student

### GroupStudySessionController
- schedule group session for a participant's match
- list sessions for participant
- mark session completed

### FeedbackController
- create/read/update/delete feedback within authorization rules
- calculate aggregate feedback metrics

## 3. MatchingService

The current `matching.engine.generate_peer_matches()` is the most important application-service responsibility.

It:
1. retrieves the requester's assessment;
2. builds the requester vector;
3. retrieves candidate assessments for the same subject;
4. obtains availability;
5. calculates cosine similarity;
6. applies the availability factor;
7. sorts results;
8. returns the top N candidates.

Keeping this responsibility outside the controller follows the principle of assigning a complex domain/application responsibility to a focused service rather than making the controller perform the algorithm.

## 4. Design principles visible in the implementation

- **Controller:** Django REST viewsets coordinate requests and delegate work.
- **Information Expert:** models/serializers validate and expose information they own.
- **Protected Variations:** the matching algorithm is isolated in `matching.engine`, making changes to scoring less likely to affect the API controller.
- **Creator:** the matching controller creates the Match and MatchParticipant records as part of the match-request use case.
- **Low Coupling:** matching, scheduling, assessments and accounts are separated into Django apps.

