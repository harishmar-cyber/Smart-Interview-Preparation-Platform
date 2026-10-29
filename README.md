# Smart Interview Preparation Platform

A Flask and SQLite placement-preparation app for students and administrators. It combines a question bank, timed multiple-choice tests, Python coding practice, HR answer drafts, progress analytics, and rule-based recommendations.

## Problem and Objectives

Interview preparation material is usually scattered across services, while students have limited visibility into their progress and weak topics. SmartPrep brings these workflows into one locally runnable application and persists student activity in SQLite.

The project is designed as a Software Engineering microproject and IA3 academic demonstration. It is not a production assessment service.

## Features

- Student registration, login, logout, profile updates, and password hashing.
- Admin-only content management for questions, tests, coding problems, HR questions, and users.
- Searchable, filterable question bank with bookmarks and practice tracking.
- Timed mock tests; correct answers are omitted from the test page and scores are computed on the server.
- Python coding practice with time-limited subprocess execution and AST-based import/call filtering.
- HR practice drafts, progress analytics, and database-backed recommendations.
- SQLite models and a reset-and-seed demonstration script.
- CSRF protection for form and same-origin fetch requests.

Recommendations use configurable score bands and actual stored activity. They are rule-based, not machine learning.

## Technology

Python 3, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, SQLite, Jinja, Bootstrap 5, Chart.js, and pytest.

## Screenshots

No screenshots are included in this repository yet. Capture the landing page, student dashboard, test result, and admin dashboard after running the application if screenshots are required for submission.

## Layout

```text
app.py                 Flask app factory and extension setup
config.py              Development, testing, and production configuration
models/                SQLAlchemy entities
routes/                Student, admin, authentication, and practice routes
services/              Scoring, progress, coding, and recommendation logic
templates/             Jinja pages, including shared and admin views
static/                 CSS and JavaScript
instance/               Local SQLite database (ignored by Git)
seed.py                 Reset and populate demonstration data
tests/                  Automated pytest suite
docs/                   SRS, test-case register, and PlantUML sources
```

## Prerequisites

- Python 3.10 or later (tested locally with Python 3.13).
- Git, if cloning the repository.

## Install and Run: Windows PowerShell

```powershell
git clone https://github.com/harishmar-cyber/Smart-Interview-Preparation-Platform.git
cd Smart-Interview-Preparation-Platform
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python seed.py
python run.py
```

If PowerShell prevents environment activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal and activate again. Alternatively run `.venv\Scripts\python.exe` directly.

Open <http://127.0.0.1:5000>.

## Install and Run: Linux/macOS

```sh
git clone https://github.com/harishmar-cyber/Smart-Interview-Preparation-Platform.git
cd Smart-Interview-Preparation-Platform
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python seed.py
python run.py
```

## Configuration and Accounts

`config.py` reads `SECRET_KEY`, `DATABASE_URL`, and `FLASK_ENV`. `seed.py` reads `ADMIN_EMAIL` and `ADMIN_PASSWORD` from the process environment. Copy `.env.example` to `.env`; `python-dotenv` loads it when the application starts.

The checked-in values in `.env.example` are development-only demo credentials, not production secrets. The seed resets existing records, so use it only for a fresh demo database. Default demo accounts:

- Admin: `admin@smartprep.com` / `Admin@123`
- Student: `student@smartprep.com` / `Student@123`

Set a new `ADMIN_PASSWORD` before seeding if you need a different admin password. Never use these defaults outside a local demo. Set a long, unique `SECRET_KEY` and a protected database URL before deployment.

## Database and Demo Data

The app creates missing tables on startup. To initialize or reset all demonstration records:

```powershell
python seed.py
```

The script clears existing app data, then seeds categories, interview questions, mock tests, coding problems, HR questions, and demo accounts. The student data created by the script is demonstration data, not a real learner history. The SQLite database is stored under `instance/` and is not committed.

## Tests

Install dependencies, then run:

```powershell
python -m pytest -q
```

The suite uses an in-memory SQLite database. Detailed test coverage and not-yet-executed manual scenarios are listed in [docs/TEST_CASES.md](docs/TEST_CASES.md).

## Documentation and UML

- [Software Requirements Specification](docs/SRS.md)
- [Test case register](docs/TEST_CASES.md)
- Five PlantUML source files in [docs/diagrams](docs/diagrams)

To render a diagram when PlantUML is installed:

```sh
plantuml docs/diagrams/*.puml
```

Rendered images are intentionally not checked in because a PlantUML renderer was not available during this implementation pass.

## Security and Limitations

- Passwords are stored as Werkzeug hashes. Admin pages are protected by a server-side role check. State-changing requests use Flask-WTF CSRF tokens.
- Mock-test answers are scored server-side; correct answers and explanations are not passed to the active test template.
- The coding runner launches student code in a child Python process with a timeout and AST checks. This is **not a hardened sandbox**: AST filters can be bypassed and the child process does not have OS-level memory, filesystem, or network isolation. Use only with trusted local demo code. Do not expose coding execution to an untrusted public network; a production deployment needs an isolated container/worker with strict CPU, memory, filesystem, and network controls, or sample-only execution.
- The development server, built-in demo credentials, SQLite, and default development secret are not deployment-ready. Use a WSGI server, strong secrets, secure cookie settings, migrations, backups, and operational monitoring for production.
- External fonts, Bootstrap, Font Awesome, and Chart.js are loaded from CDNs; a network connection is needed for those assets.
- Some broad features described as future-oriented in the prompt, such as a persistent daily streak, date/category analytics filters, and rendered UML images, are not implemented in the current code.

## Common Issues

- **Import error for Flask packages:** activate the project virtual environment and run `pip install -r requirements.txt`.
- **PowerShell activation blocked:** use the process-scoped execution-policy command above or invoke the environment's Python executable directly.
- **Old or inconsistent demo data:** rerun `python seed.py`; this is destructive to current local app data.
- **Port 5000 is occupied:** stop the other process or change the `port` in `run.py`.
- **Charts or styling missing offline:** the relevant assets use CDNs; connect to the internet or vendor those assets locally.

## Future Enhancements

- A hardened isolated coding worker or a sample-only evaluator.
- Database migrations, pagination for all large admin lists, and broader input validation.
- More exhaustive route and integration tests, persistent streak logic, and filterable analytics.
- Rendered diagrams, screenshots, accessibility review, and offline frontend assets.
