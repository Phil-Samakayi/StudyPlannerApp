# Elaboration — Architecture and Design Rationale

## 1. Architectural style

The implementation is a web client + REST API architecture:

**React/Vite presentation → Django REST application → relational database**

The matching engine is an in-process application component inside the Django backend.

## 2. Presentation tier

React components provide:
- dashboard
- authentication screens
- self-assessment form
- availability grid
- peer-match request
- feedback interaction

The Axios API service attaches JWT access tokens to requests and attempts refresh on HTTP 401.

## 3. Application tier

Django REST Framework exposes endpoint groups for:
- `/api/accounts/`
- `/api/auth/`
- `/api/subjects/`
- `/api/assessments/`
- `/api/scheduling/`
- `/api/matching/`

## 4. Matching component

The matching engine is currently **in-process**, not a separate deployed microservice.

This is an important correction to the earlier conceptual documentation: the uploaded code imports the matching engine directly from `matching.engine`.

## 5. Data tier

The repository contains SQLite for local development. The project's earlier design material described MySQL as a production target, but the uploaded implementation/configuration should be treated as the current authority for what is actually deployed.

## 6. Security

- JWT authentication
- authenticated-only access for student data
- ownership filtering on assessments, schedules and personal sessions
- participant checks before scheduling group sessions
- participant and completion checks before feedback
- unique constraints for assessment and feedback duplication

## 7. Architectural risk

The matching engine currently performs database access itself. A future refinement could introduce explicit repository interfaces if the team needs easier unit testing or if the matching algorithm is extracted into a separate service.

