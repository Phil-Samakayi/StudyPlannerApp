# StudyPlannerApp-
A Study planner that uses AI to match students in Group Studies based on complementary strengths and weaknesses.

===========================================================================================
B. YABE
Sprint 1
CORE USERS: Students
Admins exist to help guide the flow of student interactions as well as help improve the system.
=============================================================================================================================================================================================
created assessments/serializers.py and assessments/views.py
This serializer handles:

    Validation ensuring strength_score and weakness_score are within the valid 1–5 range.

    Nesting or referencing the Subject model.

    Clean bulk-upsert or individual updates using update_or_create logic.

This viewset implements:

    RESTful CRUD operations via Django REST Framework ModelViewSet.

    Security controls restricting students to reading and modifying only their own self-assessments (IsAuthenticated + queryset filtering).

    An extra endpoint (/api/assessments/bulk_submit/) allowing frontend React components to submit all subject ratings in a single HTTP POST request.

==============================================================================================================================================================================================
Key Backend Components Completedaccounts: Custom User authentication & Student Profile models, Views, Serializers, URLs.subjects: Course catalog model, views, and read/write permission router.assessments: Self-Assessment score model ($1\text{--}5$ strength/weakness ratings) & CRUD views.matching: Cosine similarity algorithm (scikit-learn), Match & Participant tracking, Group Sessions, Feedback ratings & AI metrics.scheduling: Weekly availability recurring slots (ScheduleSlot) and personal study sessions (StudySession).config: urls.py and settings.py routing, JWT settings, CORS, and auth overrides.
=============================================================================================================================================================================================
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

Note: Subjects (course catalog) can only be created by an admin/staff user, via
Django admin (`/admin/`) or the API with a staff account. Seed a few subjects
(e.g. code="CSC301", name="Data Structures") before registering students so
the Self-Assessment and Peer Match screens have data to show.
