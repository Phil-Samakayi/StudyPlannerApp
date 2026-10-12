# StudyPlannerApp — Larman/RUP Documentation Package

**Prepared from the uploaded StudyPlannerApp implementation.**

This package is deliberately **documentation-only**. It contains no application source code, database, node modules, Python environment, Git metadata, or project assets.

## Documentation approach

The package uses a Rational Unified Process (RUP)-style lifecycle and Craig Larman's iterative, use-case-driven approach:

1. **Inception** — establish vision, scope, actors, major use cases, risks and success criteria.
2. **Elaboration** — stabilize the architecturally significant use cases, domain model, system sequence diagrams, operation contracts and design decisions.
3. **Construction** — implement and refine prioritized use cases through iterations, with design/testing documentation kept synchronized with the implementation.
4. **Transition** — validate the integrated system, complete acceptance testing and prepare delivery.

The diagrams distinguish a **conceptual domain model** from a **software design class diagram**. The domain model intentionally avoids controller/service methods; those appear only in the design view.

## Important implementation-grounding note

The original project vision/SRS contained several planned features that are **not present in the uploaded implementation**. This package therefore documents the current implementation as the primary source of truth and identifies planned-but-unimplemented features separately rather than presenting them as completed functionality.

Examples:
- Present: registration, JWT login, profile, subject catalogue, self-assessment, weekly availability, personal study sessions, AI peer matching, group-study session scheduling/completion, feedback and feedback metrics.
- Not evidenced in the current code: transcript upload/parsing, transcript-derived academic profile confirmation, invitation accept/decline workflow, explicit GroupStudy opt-in, LMS integration, chat/video, GPA calculation.

## Main artifacts

- `01_Inception/01_Vision_and_Scope.md`
- `01_Inception/02_Use_Case_Model.md`
- `01_Inception/03_Risk_and_Iteration_Plan.md`
- `02_Elaboration/01_Domain_Model_Explanation.md`
- `02_Elaboration/02_System_Sequence_Diagrams.md`
- `02_Elaboration/03_Operation_Contracts.md`
- `02_Elaboration/04_Design_Class_View.md`
- `02_Elaboration/05_Architecture_and_Design_Rationale.md`
- `02_Elaboration/06_Traceability_Matrix.md`
- `03_Construction/01_Iteration_Plan.md`
- `03_Construction/02_Implementation_Traceability.md`
- `04_Transition/01_Transition_and_Acceptance_Plan.md`
- `05_UML_Diagrams/*.png` and corresponding `.dot` source files

## Diagram set

1. Use Case Model
2. Conceptual Domain Model
3. Entity Relationship Model
4. SSD — AI Peer Match
5. SSD — Availability / Schedule Update
6. SSD — Post-Session Feedback
7. Design Class Diagram
8. System Architecture
