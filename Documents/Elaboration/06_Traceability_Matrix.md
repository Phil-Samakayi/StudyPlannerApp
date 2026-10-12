# Elaboration — Requirements / Design Traceability

| Requirement / Goal | Implementation evidence | Main diagram/artifact |
|---|---|---|
| Authenticate students | accounts views/serializers + SimpleJWT | Use Case, Architecture |
| Manage profile | StudentProfileView | Use Case, Design Class |
| Maintain subjects | SubjectViewSet | Use Case, ER |
| Record strength/weakness | SelfAssessment + validators | Domain, ER, Use Case |
| Maintain weekly availability | ScheduleSlot + bulk-update | Domain, SSD, ER |
| Personal study planning | StudySession | Domain, ER |
| AI peer matching | `generate_peer_matches()` | SSD, Design Class |
| Persist match | Match + MatchParticipant | Domain, ER |
| Schedule group study | GroupStudySessionViewSet | SSD, Domain |
| Complete session | `mark_completed()` | SSD, Operation Contract |
| Submit feedback | FeedbackViewSet/Serializer | SSD, Operation Contract |
| Evaluate perceived relevance | feedback metrics endpoint | Use Case, Transition |
| Transcript parsing | No corresponding uploaded implementation found | Future scope |
| Invitation accept/decline | No corresponding implementation found | Future scope |

## Larman/RUP artifact trace

| Artifact | Purpose | Package location |
|---|---|---|
| Vision | Why/what/scope | Inception |
| Use Case Model | Functional behaviour | Inception |
| Domain Model | Conceptual structure | Elaboration |
| SSDs | System events for important use cases | Elaboration |
| Operation Contracts | State changes and postconditions | Elaboration |
| Design Class Diagram | Software responsibilities | Elaboration |
| Architecture | Major technical structure | Elaboration |
| Iteration Plan | Incremental development | Construction |
| Acceptance Plan | Transition readiness | Transition |
