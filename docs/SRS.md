# Software Requirements Specification

## Document Metadata

| Field | Value |
|---|---|
| Project | Smart Interview Preparation Platform (SmartPrep) |
| Version | 1.0 |
| Status | Academic project specification and implementation snapshot |
| Prepared | 2026-10-29 |
| Platform | Local Flask web application with SQLite |
| Audience | Students, evaluators, administrators, and maintainers |

## 1. Introduction

### 1.1 Purpose
This SRS describes the intended users, behavior, interfaces, data, constraints, and acceptance conditions for SmartPrep. It also distinguishes implemented behavior from requested or future work so evaluators can verify the current code without assuming unimplemented functionality.

### 1.2 Scope and Objectives
SmartPrep consolidates placement preparation into one locally hosted web application. A student can review categorized interview questions, take timed tests, practice coding and HR responses, inspect stored progress, and receive rules-based study suggestions. An administrator can manage selected shared content and inspect platform summaries.

Objectives are to persist preparation activity, compute test outcomes on the server, present relevant recommendations from recorded activity, and provide an understandable demonstration suitable for an undergraduate software engineering project.

### 1.3 Intended Audience
Students use practice and progress features. Administrators maintain content and view platform activity. Developers and evaluators use this document, the pytest suite, and the diagrams to understand and verify the system.

### 1.4 Definitions and Abbreviations

| Term | Definition |
|---|---|
| Admin | User with the `admin` role and permission to access `/admin` routes |
| Attempt | One student's persisted session for a mock test |
| CSRF | Cross-site request forgery protection for state-changing requests |
| HR | Human resources / behavioral interview preparation |
| ORM | Object-relational mapping through SQLAlchemy |
| Recommendation | A persisted rule-based practice suggestion |
| SRS | Software Requirements Specification |
| Student | Authenticated user with the `student` role |

## 2. Overall Product Description

### 2.1 Product Perspective
The system is a standalone Flask MVC-inspired web application. Jinja templates form the presentation layer; blueprints handle HTTP routes; SQLAlchemy models persist data in SQLite; service modules calculate scores, progress, and recommendations. Bootstrap, Chart.js, Font Awesome, and fonts are loaded by browser clients from CDNs.

### 2.2 User Classes

| User class | Characteristics | Main permissions |
|---|---|---|
| Student | Placement candidate using an individual account | Practice, test, submit code, save HR drafts, review progress/recommendations, update profile |
| Admin | Content manager using an administrator account | Student operations plus selected admin content CRUD and platform summaries |

### 2.3 Operating Environment
Python 3.10+, Flask 3, a modern browser, and a writable local filesystem are required. The default database is a SQLite file under `instance/`. A network connection is needed for CDN-hosted frontend libraries unless they are vendored locally.

### 2.4 Assumptions and Dependencies
The operator installs packages from `requirements.txt`, protects `.env`, and uses the seed script only for a local demonstration reset. Flask-WTF, Flask-Login, Flask-SQLAlchemy, Werkzeug, and the SQLite driver are the key runtime dependencies. No external AI service is configured.

### 2.5 Constraints
The Flask development server and SQLite configuration are for a small local demo, not a production workload. The coding runner's AST checks and child-process timeout are not an OS security sandbox. Seed data includes development-only demonstration credentials. The current schema is initialized by `db.create_all()` and has no migration history.

## 3. Functional Requirements

Status refers to the current repository snapshot.

| ID | Requirement | Acceptance condition | Status |
|---|---|---|---|
| FR-001 | The system shall register a student with a unique email and hashed password. | A valid registration persists one student and the plaintext password is not stored. | Implemented |
| FR-002 | The system shall authenticate users and support logout. | Valid credentials create an authenticated session; invalid credentials do not. | Implemented |
| FR-003 | The system shall authorize admin operations on the server. | A student cannot access `/admin`; an admin can. | Implemented |
| FR-004 | The system shall let authenticated students browse, search, filter, and paginate questions. | Query terms and category/difficulty filters affect the returned list. | Implemented |
| FR-005 | The system shall let a student bookmark and practice a question. | Bookmark and latest answer outcome persist for that student. | Implemented |
| FR-006 | The system shall start and resume timed mock-test attempts. | Attempt status, start time, and remaining time are derived on the server. | Implemented |
| FR-007 | The system shall omit answer keys from the active test page and grade submitted choices on the server. | Result records contain the server-computed score and per-question correctness. | Implemented |
| FR-008 | The system shall prevent access to another student's attempt and result. | A non-owner receives HTTP 403. | Implemented |
| FR-009 | The system shall provide Python coding submissions and persist result summaries. | Submission records contain status and test-case counts. | Implemented with security limitation |
| FR-010 | The system shall allow a student to save HR answer drafts and mark questions practiced. | Saved content is associated with the authenticated user and HR question. | Implemented |
| FR-011 | The system shall provide progress summaries and charts based on stored activity. | Analytics endpoint data is derived from the user's records. | Implemented; analytics breadth is limited |
| FR-012 | The system shall generate onboarding suggestions when there is no performance history. | New accounts receive suggestions without invented scores. | Implemented |
| FR-013 | The system shall generate score-band recommendations from stored activity. | Recommendation priority and text reflect calculated performance. | Implemented |
| FR-014 | The system shall let administrators create, edit, and delete questions and mock tests. | Changes persist and are visible in student content routes. | Implemented |
| FR-015 | The system shall let administrators manage coding problems and HR questions. | Admin changes persist and are reflected in corresponding practice routes. | Implemented |
| FR-016 | The system shall provide an admin view of student and platform activity summaries. | The dashboard displays counts and recent records from the database. | Implemented |
| FR-017 | The system shall let students update profile details and change passwords after verifying the current password. | Valid updates persist; invalid password changes are rejected. | Implemented |
| FR-018 | The system shall protect state-changing requests against CSRF. | Requests without a valid token are rejected outside test configuration. | Implemented |
| FR-019 | The system shall allow administrators to manage category records and category metadata. | Admin can create, edit, and delete categories. | Not implemented; seeded categories are used |
| FR-020 | The system shall provide a persisted daily preparation streak and date/category analytics filters. | Streaks and filters are computed from dated activity. | Not implemented |

### 3.1 Use Case Descriptions

| Use case | Primary actor | Preconditions | Main outcome |
|---|---|---|---|
| Register and sign in | Student | Application available | Student account and authenticated session exist |
| Practice a question | Student | Authenticated; content exists | Answer outcome and optional bookmark are recorded |
| Take a mock test | Student | Authenticated; published test exists | Attempt is submitted, scored, and stored |
| Submit coding work | Student | Authenticated; coding problem exists | Submission result and status are stored |
| Practice HR response | Student | Authenticated; HR question exists | Draft and practice state are stored |
| Review progress | Student | Authenticated | Analytics and recommendations are displayed |
| Maintain content | Admin | Authenticated admin session | Selected shared content is updated |
| Review platform activity | Admin | Authenticated admin session | Aggregate counts and recent activity are displayed |

## 4. Non-Functional Requirements

| ID | Requirement | Verification / current note |
|---|---|---|
| NFR-001 | Passwords shall be stored using a password-hashing function. | Verify through `User.set_password` and registration test. |
| NFR-002 | Admin authorization shall be enforced server-side. | Student/admin route tests. |
| NFR-003 | State-changing requests shall require valid CSRF tokens in normal configuration. | Flask-WTF middleware is enabled; testing config disables it. |
| NFR-004 | Correct test answers shall not be included in the active-test response. | Route test inspects returned HTML. |
| NFR-005 | Submitted code shall not be evaluated through unrestricted `exec` or `eval` in the Flask process. | Current implementation uses a child process and static AST checks; this does not provide robust isolation. |
| NFR-006 | Ordinary local operations should complete within two seconds for a small demo dataset, excluding code evaluation. | Target only; no formal load test has been run. |
| NFR-007 | Large question lists should be paginated. | Student and admin question routes use pagination. |
| NFR-008 | Forms and pages should remain usable at desktop and mobile widths. | Responsive CSS is present; no formal cross-device audit is recorded. |
| NFR-009 | Missing records should return an HTTP error rather than an unhandled lookup result. | Routes use `get_or_404` in major detail workflows. |
| NFR-010 | User progress shall persist between requests using the database. | SQLAlchemy persistence; restart scenario remains a manual test. |
| NFR-011 | Deployment secrets shall be configurable outside source. | Environment variables are supported; checked-in `.env.example` contains demo-only values. |
| NFR-012 | The application shall separate route handling, persistence, templates, and business logic. | Blueprints, models, services, and Jinja templates are separated. |

## 5. External Interface Requirements

### 5.1 User Interface
The browser UI uses Jinja-rendered pages, Bootstrap 5, custom CSS/JavaScript, Chart.js visualizations, and accessible labels where present. Authenticated navigation exposes student or admin workflows. The active test interface displays answer options and a countdown; answer keys are presented only after evaluation or explicit question practice.

### 5.2 Software Interfaces
Flask route handlers call SQLAlchemy models and service functions. SQLite stores relational records. Flask-Login maintains authenticated session identity. Flask-WTF validates CSRF tokens. Frontend libraries currently load from public CDNs.

### 5.3 Communication Interfaces
The browser communicates with the Flask server over local HTTP during development. JSON requests are used for selected practice and test interactions. Production HTTPS and hardened cookie deployment are outside the current local-demo configuration.

## 6. Data Requirements

The data store uses SQLAlchemy entities and foreign-key relationships. Exact fields are defined in `models/`; the following is the logical entity summary.

| Entity | Important fields and relationships |
|---|---|
| User | id, full_name, unique email, password_hash, role, preferred_job_role, education, is_active, created_at; owns attempts, submissions, HR practice, bookmarks, recommendations, activity, and question attempts |
| Category | id, unique name, description, icon, color; has questions, mock tests, recommendations |
| Question | id, category_id, question_text, type, difficulty, options, correct_answer, explanation; belongs to category |
| Bookmark | user_id, question_id, created_at; unique per user/question |
| QuestionAttempt | user_id, question_id, selected_answer, is_correct, attempted_at |
| MockTest | title, category_id, duration, marks, pass percentage, difficulty, published flag |
| TestQuestion | test_id, question_id, marks; unique per test/question |
| TestAttempt | user_id, test_id, started/submitted times, score, percentage, status, time_taken |
| AttemptAnswer | attempt_id, question_id, selected_answer, correctness, marks_awarded; unique per attempt/question |
| CodingProblem | title, slug, statement, format, samples, constraints, hints, explanation, test cases |
| CodingSubmission | user_id, problem_id, source, status, case totals, runtime, error, submitted_at |
| HRQuestion | question, example, tips, category |
| HRPractice | user_id, question_id, draft, practiced flag, updated_at |
| Recommendation | user_id, optional category, explanation, priority, action, target URL, completion, created_at |
| ActivityLog | user_id, activity type, optional reference/score, title, description, created_at |

Foreign keys and relationship cascades are defined in the model modules. The database is initialized through `db.create_all()`; no schema migration framework is configured.

## 7. Business Rules

1. New registrations always receive the `student` role.
2. A student's email address is unique and case-normalized during registration.
3. A test's percentage is computed from marks awarded divided by possible marks; incorrect answers have no negative marking in the current scoring service.
4. Test scores are calculated on the server using stored question answer keys.
5. A user may view only their own attempt and result, except an administrator.
6. Recommendations use stored performance; a user without recorded performance receives onboarding recommendations.
7. Recommendation rules use bands `<50`, `50–<70`, `70–<85`, and `>=85` percent.
8. The seed operation deletes current application records before inserting demo data.
9. The coding runner's result is based on configured test cases, but its process isolation is not production-grade.

## 8. Requirement Traceability

| Requirement group | Implementing area | Automated coverage |
|---|---|---|
| FR-001–003 | `routes/auth.py`, `utils/decorators.py`, `routes/admin.py` | `tests/test_auth.py`, `tests/test_admin.py` |
| FR-004–005 | `routes/questions.py`, `models/question.py` | `tests/test_questions.py` |
| FR-006–008 | `routes/mock_tests.py`, `services/scoring_service.py` | `tests/test_mock_tests.py` |
| FR-009 | `routes/coding.py`, `services/code_runner.py` | Manual scenarios listed; automated route coverage remains limited |
| FR-010 | `routes/hr.py`, `models/hr.py` | Manual scenarios listed |
| FR-011 | `routes/analytics.py`, `services/progress_service.py` | Manual scenarios listed |
| FR-012–013 | `services/recommendation_service.py` | `tests/test_recommendations.py` covers onboarding |
| FR-014–016 | `routes/admin.py` | Admin authorization automated; CRUD scenarios remain pending |
| FR-017–018 | `routes/auth.py`, `app.py`, `templates/base.html` | Profile/CSRF manual cases remain pending |

## 9. Acceptance Criteria

The local demo is acceptable when the documented setup initializes the app, seed data is present, student/admin authentication works, protected routes enforce roles, mock-test scoring is server-side, student records persist, recommendations are generated without inventing performance, the pytest suite passes, and documented limitations are visible to the evaluator. The current automated suite verifies core flows but does not exhaustively verify every requirement.

## 10. Risks and Limitations

- Coding execution must not be exposed to untrusted users without stronger OS/container isolation.
- The checked-in demo credential values and development secret are unsuitable for deployment.
- Seed resets all records and sample student history is demonstrative.
- The daily streak, category CRUD, rendered diagrams, screenshots, and several analytics filters are not implemented.
- CDN dependencies can prevent full UI rendering offline.
- Tests currently emit SQLAlchemy deprecation and collection warnings; these are not test failures.

## 11. UML Diagram Guide

PlantUML sources are in `docs/diagrams/`. The use-case diagram shows student and admin goals; the class diagram captures current core entities and associations; the sequence diagram follows a test attempt from browser request through grading and persistence; the activity diagram models a student preparation loop; the state diagram models attempt lifecycle transitions. PNG/SVG rendering was unavailable during this pass, so source files are the deliverable.

## 12. References

- Flask documentation: <https://flask.palletsprojects.com/>
- Flask-SQLAlchemy documentation: <https://flask-sqlalchemy.palletsprojects.com/>
- Flask-Login documentation: <https://flask-login.readthedocs.io/>
- Flask-WTF documentation: <https://flask-wtf.readthedocs.io/>
- SQLAlchemy documentation: <https://docs.sqlalchemy.org/>
- PlantUML language reference: <https://plantuml.com/>
