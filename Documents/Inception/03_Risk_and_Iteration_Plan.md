# Inception — Risks and Initial Iteration Plan

## 1. Major risks

| Risk | Impact | Mitigation |
|---|---|---|
| Poor match quality | High | Use feedback metrics and refine scoring rules |
| Sparse candidate data | High | Make assessment and availability workflows easy to complete |
| Invalid/duplicate assessment data | Medium | 1–5 validators and unique student/subject constraint |
| Scheduling inconsistencies | Medium | Validate end time > start time |
| Unauthorized access | High | JWT authentication and per-user queryset restrictions |
| Over-expansion of scope | High | Separate implemented features from planned transcript/invitation features |
| Tight coupling of AI logic | Medium | Keep matching algorithm in `matching.engine` |
| Database migration differences | Medium | Maintain explicit model constraints/indexes and test migrations |

## 2. RUP-style iteration strategy

### Inception iteration
Establish:
- vision
- actors
- use cases
- major risks
- initial architecture
- success criteria

### Elaboration iteration
Prove the architecture through the architecturally significant scenario:
**Request AI Peer Match**.

Deliver:
- domain model
- SSD
- operation contracts
- design class view
- architecture
- persistence model

### Construction iteration 1
Implement and stabilize:
- registration/login
- profile
- subjects
- self-assessment

### Construction iteration 2
Implement and stabilize:
- availability
- personal study sessions
- AI matching

### Construction iteration 3
Implement and stabilize:
- match persistence/history
- group-study session scheduling/completion
- feedback

### Transition
Run integrated acceptance tests, verify security/ownership rules, collect match-quality feedback, fix defects and prepare the final release.

