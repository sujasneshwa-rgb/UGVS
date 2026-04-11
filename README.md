# University Grievance Voting System (UGVS)

A web application where **students** can submit grievances (college or university level), **vote** to support issues that matter, and **track** status updates. **Administrators** manage grievances through Django’s admin interface. Email notifications are sent to students when grievance status changes.

## Features

- **Student portal:** registration, login (with CAPTCHA), submit grievances with optional evidence files, vote on grievances, separate views for college- and university-level voting.
- **Admin workflow:** review grievances, set status (Pending → In Progress → Resolved / Rejected).
- **Voting:** one vote per user per grievance; grievances can be ordered by vote count.
- **Notifications:** email alerts when status changes (configure SMTP in settings).
- **Security basics:** Django authentication, CSRF protection, custom user model.

## System architecture

Three-tier layout:

| Layer | Role |
|--------|------|
| **Client** | Browser UI for **students** and **admins** (HTML templates). Users interact with forms and pages; the browser sends HTTP requests. |
| **Application** | **Django** (Python): URL routing, views, authentication, business rules (grievance CRUD, voting rules, status updates, email triggers). |
| **Database** | **SQLite** (default) via Django ORM: users, grievances, votes, and related data persisted in `db.sqlite3`. Uploaded files stored under `media/`. |

## Tech stack

- **Backend:** Python, Django
- **Database:** SQLite (`db.sqlite3`)
- **Frontend:** Django templates, HTML/CSS
- **Extras:** `django-simple-captcha`, Pillow (CAPTCHA images), optional SMTP for email

## Project structure (high level)

```
UGVS/                 # Django project settings & root URLs
accounts/             # Custom user, registration, login, home
grievances/           # Grievance & Vote models, views, URLs
templates/            # HTML templates
static/               # Static assets
media/                # User uploads (evidence) — created at runtime
```

## Prerequisites

- Python 3.10+ (recommended)
- pip

## Setup

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd UGVS
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv env
   # Windows
   env\Scripts\activate
   # macOS / Linux
   source env/bin/activate
   ```

3. **Install dependencies** (install Django and the packages your project uses; for example):

   ```bash
   pip install django django-simple-captcha pillow
   ```

   *Tip: generate a `requirements.txt` with `pip freeze > requirements.txt` after installing everything.*

4. **Configure environment-sensitive settings**

   Before pushing to GitHub or deploying, **do not commit real secrets**. Set `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and email credentials via environment variables or a local `.env` file (and add `.env` to `.gitignore`). Rotate any keys that were ever committed in plain text.

5. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create an admin user**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**

   ```bash
   python manage.py runserver
   ```

   Open `http://127.0.0.1:8000/` in your browser. Use `/admin/` for the Django admin panel.

## Usage overview

- **Students:** register → log in → submit grievances → vote on open grievances → receive emails when an admin updates status (if email is configured).
- **Admins:** log in to Django admin → manage `Grievance` records and statuses.

