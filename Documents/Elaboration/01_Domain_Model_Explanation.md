# Elaboration — Conceptual Domain Model

## 1. Purpose

The domain model is a conceptual view of the problem domain, not a software class diagram. It identifies important concepts, attributes and associations without placing controller/service methods into the model.

This follows the distinction emphasized by Craig Larman: a domain model should represent conceptual classes from the domain rather than software artifacts.

## 2. Conceptual classes

### Student
Represents the university student using the application.

### StudentProfile
Stores student number, programme and year of study associated one-to-one with a user.

### Subject
Represents a course/subject in the catalogue.

### SelfAssessment
Represents the student's perceived strength and weakness in one subject. The implementation constrains both scores to 1–5 and permits at most one assessment per student/subject.

### ScheduleSlot
Represents a recurring weekly availability block.

### StudySession
Represents an individual personal study session linked to a subject.

### Match
Represents the persisted result of a matching request, with a relevance score.

### MatchParticipant
Represents participation of a Student in a Match. It is a persistence association/junction concept needed to represent the many-to-many relationship.

### GroupStudySession
Represents a scheduled collaborative session created from a Match. Its status can be scheduled, completed or cancelled.

### Feedback
Represents post-session feedback submitted by a participating student.

## 3. Important associations

- Student 1 — 1 StudentProfile
- Student 1 — 0..* SelfAssessment
- Subject 1 — 0..* SelfAssessment
- Student 1 — 0..* ScheduleSlot
- Student 1 — 0..* StudySession
- Subject 1 — 0..* StudySession
- Student 0..* — 0..* Match through MatchParticipant
- Match 1 — 0..1 GroupStudySession
- Student 1 — 0..* Feedback
- GroupStudySession 1 — 0..* Feedback

## 4. Domain-model observations

The current implementation does **not** contain a separate `StudyTimetable` class. A timetable is effectively represented by the collection of `StudySession` objects belonging to a student.

Likewise, the AI matching engine is intentionally excluded from the conceptual domain model. It is a software responsibility rather than a conceptual entity in the student's study-planning domain.

