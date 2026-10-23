# StudyPlannerApp

A web-based study planner for University of Zambia students that matches students for GroupStudy sessions based on complementary strengths and weaknesses.

Final Year Project, Department of Computing and Informatics, University of Zambia (2026).

- **Team:** Phil Samakayi (2021439488) and Blessing Yabe (2021417034)
- **Supervisor:** Mr. Martin Phiri

## Features

- **Accounts:** registration and login with university email; JWT access and refresh tokens; student profile (student number, programme, year of study). New accounts are always students; administrators are created with `createsuperuser`.
- **Subject catalogue:** courses readable by every logged-in user, editable only by administrators.
- **Self-assessment:** each student rates their strength and need for support (1–5) in each subject.
- **Weekly availability:** recurring free-time slots, with overlapping slots rejected.
- **Personal study planner:** study sessions per subject (no double-booking) and subject goals with target dates.
- **Reminders:** a dashboard banner for personal and group sessions starting in the next 24 hours.
- **AI peer matching:** proposes the student whose strengths best cover your needs in a chosen subject, with a penalty when you share no free time.
- **GroupStudy sessions:** schedule a session for a match, mark it complete (not before its start time) or cancel it, then rate it 1–5.
- **Feedback metrics:** the share of ratings of 4 or more, compared with the 75% match-relevance target.

## Tech stack

| Layer | Technology |
|---|---|
| Front end | React 18, React Router 6, Axios, Vite 5 |
| Back end | Python 3.12, Django 6, Django REST Framework, SimpleJWT |
| Matching | NumPy, scikit-learn (cosine similarity) |
| Database | PostgreSQL |

## Project structure

```
accounts/      Custom user (email login, role), student profile, registration, JWT login
subjects/      Course catalogue
assessments/   Self-assessment scores per student and subject
scheduling/    Weekly availability, personal study sessions, subject goals,
               availability.py (shared free-time calculation)
matching/      engine.py (peer matching), matches, GroupStudy sessions, feedback, metrics
config/        Settings and URL routing
src/           React front end (components/ and services/)
Documents/     Unified Process documentation (Inception, Elaboration, Construction,
               Transition) and UML diagrams
```

## How matching works

For the requesting student *r* and each candidate *c* who has assessed the same subject:

- need(r) = [weakness_r, 6 − strength_r]
- offer(c) = [strength_c, 6 − weakness_c]
- relevance = cosine_similarity(need, offer) × (1.0 if they share a weekly slot, otherwise 0.75)

The highest-scoring candidate becomes the match. See `matching/engine.py`.

## Setup (local development)

### Prerequisites

- Python 3.12 (on Windows, Smart App Control may block scikit-learn under Python 3.14)
- Node.js LTS and npm
- PostgreSQL (pgAdmin is optional but useful)
- Git

### 1. Clone and install the back end

```bash
git clone https://github.com/Phil-Samakayi/StudyPlannerApp.git
cd StudyPlannerApp
python -m venv venv
venv\Scripts\activate            # macOS/Linux: source venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. Create the database and set the password

Create an empty PostgreSQL database called `study_planner_db` (for example in pgAdmin), then set your PostgreSQL password for the terminal session:

```powershell
# Windows PowerShell (current terminal only)
$env:DB_PASSWORD = "your-postgres-password"

# or permanently (open a new terminal afterwards)
setx DB_PASSWORD "your-postgres-password"
```

```bash
# macOS/Linux
export DB_PASSWORD="your-postgres-password"
```

### 3. Migrate and create an administrator

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Add courses

Sign in at http://127.0.0.1:8000/admin/ with the administrator account and add a few subjects (for example code `CSC4004`, name `Projects`). Students need courses before they can self-assess or request a match.

### 5. Run the app (two terminals)

```bash
# Terminal 1: back end, http://127.0.0.1:8000/api/
python manage.py runserver

# Terminal 2: front end, http://localhost:5173/
npm install
npm run dev
```

Open http://localhost:5173/, sign up as a student and follow the dashboard.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `DB_NAME` | `study_planner_db` | PostgreSQL database name |
| `DB_USER` | `postgres` | PostgreSQL user |
| `DB_PASSWORD` | (empty) | PostgreSQL password; must be set |
| `DB_HOST` / `DB_PORT` | `127.0.0.1` / `5432` | Database server |
| `DATABASE_URL` | (not set) | Full database URL; overrides the `DB_*` settings |
| `SECRET_KEY` | insecure development key | Must be set to a secret value outside local development |
| `DEBUG` | `True` | Set to `False` outside local development |
| `ALLOWED_HOSTS`, `CORS_ORIGINS` | (empty) | Extra hosts and front-end origins, comma-separated |

Never commit passwords, keys or database dumps.

## Running the tests

```bash
python manage.py test
```

The back-end suite has 92 tests covering all five apps. To run the tests without PostgreSQL, point Django at a throwaway SQLite file:

```powershell
$env:DATABASE_URL = "sqlite:///test.sqlite3"; python manage.py test
```

## Main API endpoints

All paths start with `/api/`. Every endpoint except registration and login needs an `Authorization: Bearer <access token>` header.

| Endpoint | Purpose |
|---|---|
| `accounts/register/` | Register a student |
| `auth/token/`, `auth/token/refresh/` | Log in, refresh the access token |
| `accounts/profile/` | Read or update your profile |
| `subjects/` | Course catalogue |
| `assessments/`, `assessments/bulk_submit/` | Self-assessments |
| `scheduling/slots/`, `scheduling/sessions/`, `scheduling/goals/` | Availability, study sessions, goals |
| `matching/matches/request-match/` | Request a peer match (`{"subject_id": 1}`) |
| `matching/sessions/`, `.../<id>/complete/`, `.../<id>/cancel/` | GroupStudy sessions |
| `matching/feedback/`, `matching/feedback/metrics/` | Ratings and relevance metrics |

## Known limitations

- Cosine similarity ignores how strong a candidate is, so candidates with proportional ratings can tie (see `test_known_limitation_cosine_similarity_ties_on_proportional_profiles`).
- The matching availability check compares slots for exact equality rather than overlap.
- A match does not record its subject, and there is no accept/decline step for a proposed partner.
- The React front end has no automated tests.

## Future work

- Deployment to a hosting platform (the settings already read `DATABASE_URL`, `SECRET_KEY`, `DEBUG` and `ALLOWED_HOSTS`, and Gunicorn and WhiteNoise are installed for this).
- Suggested GroupStudy meeting times in the interface, using `scheduling/availability.py`.
- Accept/decline invitations for proposed partners.
- Transcript upload with OCR as an alternative to self-assessment.
- Email or SMS notifications, and continuous integration.

## Troubleshooting

- **`fe_sendauth: no password supplied`:** set `DB_PASSWORD` in the same terminal before `runserver`.
- **scikit-learn fails to import on Windows:** use Python 3.12.
- **`npm` or `node` not found:** install Node.js LTS and reopen the terminal.
- **No courses in the drop-downs:** add subjects in the admin site (step 4).
