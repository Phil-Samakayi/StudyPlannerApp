# StudyPlannerApp

An AI-assisted study planner for university students. StudyPlannerApp helps
students track their coursework, self-assess their strengths and weaknesses
per subject, and get matched with complementary peers for GroupStudy
sessions — replacing the "form a group with whoever's in your class" status
quo with a data-informed match.

Built as a final-year Computing & Informatics project at the University of
Zambia.

## Core Features

- **Accounts** — student registration/login with JWT authentication
  (`accounts`), custom user model + student profile.
- **Subjects** — a course catalog students enroll against (`subjects`).
- **Self-Assessments** — students rate their strength/weakness (1–5) per
  subject (`assessments`), which feeds the matching engine.
- **AI Peer Matching** — a cosine-similarity engine over self-assessment
  vectors recommends complementary study partners for a subject
  (`matching`), so a student strong in a topic is matched with one who
  needs help in it, and vice versa.
- **GroupStudy Sessions** — once matched, students schedule a study session
  for a specific date/time, mark it complete, and leave feedback/ratings
  afterwards (`matching`).
- **Scheduling** — weekly recurring availability slots and personal study
  sessions (`scheduling`).

## Tech Stack

- **Backend:** Django + Django REST Framework, JWT auth via
  `djangorestframework-simplejwt`, SQLite (dev), scikit-learn for the
  matching engine.
- **Frontend:** React (Vite), `react-router-dom`, `axios`.

## Project Structure

```
accounts/      Custom user + student profile, JWT auth, registration
subjects/      Course catalog
assessments/   Self-assessment scores (strength/weakness per subject)
matching/      Peer matching engine, GroupStudy sessions, feedback
scheduling/    Weekly availability slots, personal study sessions
config/        Project settings, root URL routing
src/           React frontend (components, services, routing)
```

## API Overview

All endpoints are rooted at `/api/`:

| Prefix | Purpose |
|---|---|
| `/api/auth/token/`, `/api/auth/token/refresh/` | JWT login/refresh |
| `/api/accounts/register/`, `/api/accounts/login/`, `/api/accounts/profile/` | Registration & profile |
| `/api/subjects/` | Course catalog (read for students, write for staff) |
| `/api/assessments/`, `/api/assessments/bulk_submit/` | Self-assessment CRUD |
| `/api/matching/matches/`, `/api/matching/matches/request-match/` | Request/view peer matches |
| `/api/matching/sessions/`, `/api/matching/sessions/<id>/complete/` | Schedule & complete GroupStudy sessions |
| `/api/matching/feedback/` | Post-session feedback & ratings |
| `/api/scheduling/slots/`, `/api/scheduling/sessions/` | Weekly availability & personal study sessions |

## Setup & Running Locally

### Backend (Django)

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py createsuperuser   # optional, for /admin/ and creating Subjects
python3 manage.py runserver
```

API will be available at http://localhost:8000/api/

### Frontend (React + Vite)

```bash
npm install
npm run dev
```

App will be available at http://localhost:5173/

> **Note:** Subjects (course catalog) can currently only be created by an
> admin/staff user, via Django admin (`/admin/`) or the API with a staff
> account. Seed a few subjects (e.g. `code="CSC301"`, `name="Data
> Structures"`) before registering students, so the Self-Assessment and
> Peer Match screens have data to show.

## Running the Test Suite

```bash
python3 manage.py test
```

55 tests across all five apps (accounts, subjects, assessments, scheduling,
matching), covering models, serializers, permissions, and the matching
engine.

## Contributors

- Blessing Yabe
- Phil Samakayi
