# Construction — Implementation Traceability

This artifact connects the design responsibilities to the current project modules.

| Design responsibility | Current implementation |
|---|---|
| Account registration | `accounts.views.RegisterView` |
| JWT login | `accounts.views.CustomTokenObtainPairView` |
| Profile | `accounts.views.StudentProfileView` |
| Subject catalogue | `subjects.views.SubjectViewSet` |
| Self-assessment | `assessments.views` + `SelfAssessment` |
| Availability | `scheduling.views.ScheduleSlotViewSet` + `ScheduleSlot` |
| Personal study | `scheduling.views.StudySessionViewSet` + `StudySession` |
| Match request | `matching.views.MatchViewSet.request_match()` |
| Matching algorithm | `matching.engine.generate_peer_matches()` |
| Match persistence | `Match` + `MatchParticipant` |
| Group study | `matching.views.GroupStudySessionViewSet` |
| Completion | `GroupStudySessionViewSet.mark_completed()` |
| Feedback | `matching.views.FeedbackViewSet` + `FeedbackSerializer` |
| Metrics | `FeedbackViewSet.metrics()` |

## Important design-to-code discrepancy

Earlier UML material in the project describes an AI service and some planned entities/features that are more elaborate than the uploaded code. The current implementation should be used when defending the project in a presentation.

For example, the current matching request creates the **top match directly**. It does not persist a list of all five ranked candidates as Match objects.

Similarly, the current implementation does not implement transcript parsing or an invitation state machine.

