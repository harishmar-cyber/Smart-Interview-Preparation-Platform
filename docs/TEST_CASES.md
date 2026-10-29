# Test Case Register

**Project:** Smart Interview Preparation Platform
**Document status:** Initial execution record for this repository snapshot
**Automated command:** `python -m pytest -q`
**Execution note:** The automated suite was run locally on 2026-10-29. Cases marked Pass below map to assertions exercised by that run. All other cases remain Pending; no result is inferred for an unexecuted case.

| ID | Req. | Objective | Preconditions | Steps | Input / data | Expected result | Actual result | Status | Remarks |
|---|---|---|---|---|---|---|---|---|---|
| TC-001 | FR-001 | Register a valid student | Empty test database | Open registration; submit valid fields | Name `New Student`, unique email, matching valid password | Student persists, password is hashed, session redirects to dashboard | Automated pytest observed redirect and verified stored hash | Pass | `tests/test_auth.py` |
| TC-002 | FR-001 | Reject duplicate email | Student with test email exists | Submit registration with same email | Existing email, otherwise valid fields | Registration rejected; one account remains | Automated pytest observed response and one stored account | Pass | `tests/test_auth.py` |
| TC-003 | FR-001 | Reject malformed email | Registration page available | Submit malformed email | `not-an-email` | Validation message; no user persisted | Not executed | Pending | Manual/API validation case |
| TC-004 | FR-001 | Reject weak password | Registration page available | Submit password shorter than supported minimum | `abc` | Validation message; no user persisted | Not executed | Pending | Verify documented minimum policy |
| TC-005 | FR-001 | Reject password mismatch | Registration page available | Submit different password and confirmation | `SecurePass123` / `Mismatch123` | Registration rejected; no user persisted | Not executed | Pending | Boundary/security case |
| TC-006 | FR-002 | Log in with valid credentials | Student account exists | Submit correct email/password; request protected page | `student@example.test` / valid password | Authenticated session reaches student area | Authenticated requests succeeded in the automated protected-route flows | Pass | Covered as a shared test precondition |
| TC-007 | FR-002 | Reject invalid credentials | Student account exists | Submit correct email and wrong password | `wrong-password` | Login remains unauthenticated and shows safe error | Automated pytest observed error response | Pass | `tests/test_auth.py` |
| TC-008 | FR-002 | Logout invalidates session | Student is logged in | Request logout; then protected dashboard | Valid session | Session ends and protected route redirects to login | Not executed | Pending | Manual route test |
| TC-009 | FR-017 | Update profile details | Student is logged in | Submit profile with new name/role/education | Non-empty valid values | Updated profile persists | Not executed | Pending | Manual form test |
| TC-010 | FR-003 | Block unauthenticated student route | No active session | Request `/dashboard` | No cookies | Redirect to login | Not executed | Pending | Manual/API test |
| TC-011 | FR-003 | Block student from admin dashboard | Student is logged in | Request `/admin/dashboard` | Student role | Student is redirected or denied; no admin content returned | Automated pytest observed redirect to student dashboard | Pass | `tests/test_admin.py` |
| TC-012 | FR-003 | Allow admin dashboard | Admin account exists | Log in as admin; request admin dashboard | Admin role | Dashboard returns HTTP 200 | Automated pytest observed HTTP 200 | Pass | `tests/test_admin.py` |
| TC-013 | FR-004 | Search and open question detail | Student and question exist | Search by keyword; open question detail | `mutable` | Matching question appears and detail renders explanation | Automated pytest observed both responses and question text | Pass | `tests/test_questions.py` |
| TC-014 | FR-004 | Handle nonexistent question | Student is logged in | Request a question ID not in database | Large unused integer ID | HTTP 404; no server traceback exposed | Not executed | Pending | Missing-record case |
| TC-015 | FR-005 | Bookmark question | Student and question exist | POST bookmark toggle; query persisted relation | Existing question ID | Response indicates bookmarked; one row persists | Automated pytest observed JSON and database row | Pass | `tests/test_questions.py` |
| TC-016 | FR-005 | Reject empty practice answer | Student and question exist | POST attempt with no selected option | Empty JSON object | HTTP 400 and no false attempt is stored | Not executed | Pending | Negative input case |
| TC-017 | FR-007 | Hide answer key during active test | Student has in-progress attempt | GET active test page; inspect returned HTML | Question has answer `B` and explanation | Correct answer/explanation absent before submission | Automated pytest confirmed answer-key fields and explanation are absent | Pass | `tests/test_mock_tests.py` |
| TC-018 | FR-007 | Score a correct submitted answer | Student has an in-progress one-question test | Submit answer and inspect result/records | Answer `B` for correct choice | 100% score, evaluated status, correct answer row persisted | Automated pytest observed 100%, evaluated state, and persisted answer | Pass | `tests/test_mock_tests.py` |
| TC-019 | FR-007 | Score all questions unanswered | Student has an in-progress test | Submit empty answer map | `{}` | Zero marks; all questions counted unanswered | Not executed | Pending | Boundary case |
| TC-020 | FR-007 | Prevent repeat grading | Attempt has already been evaluated | Submit a second answer payload | Different answer after first submission | Existing result is returned unchanged | Not executed | Pending | Idempotency case |
| TC-021 | FR-008 | Deny another student's result access | Attempt belongs to a different student | Log in as first student; request result URL | Foreign attempt ID | HTTP 403; result data not disclosed | Automated pytest observed HTTP 403 | Pass | `tests/test_mock_tests.py` |
| TC-022 | FR-006 | Automatically submit expired test | Attempt duration has elapsed | Open take page after timer expiry | Expired attempt | Attempt is graded/submitted and result is shown | Not executed | Pending | Timer boundary integration case |
| TC-023 | FR-009 | Reject empty coding submission | Student and coding problem exist | Submit whitespace-only source | Empty source | HTTP 400 and no accepted submission | Not executed | Pending | Manual/API test |
| TC-024 | FR-009 | Persist accepted coding submission | Student and problem with known tests exist | Submit a known passing solution | Valid Python solution | All configured cases pass; accepted submission and solved status persist | Not executed | Pending | Do not expose public runner without sandbox controls |
| TC-025 | FR-010 | Save HR draft answer | Student and HR question exist | Save a personal answer; reload page | Non-empty personal answer | Draft is associated with student and reloads | Not executed | Pending | Manual integration case |
| TC-026 | FR-012 | Generate onboarding recommendations | Student has no performance activity | Invoke recommendation generation | New student ID | Non-score onboarding suggestions persist | Automated pytest observed diagnostic suggestion and stored records | Pass | `tests/test_recommendations.py` |
| TC-027 | FR-013 | Recommend weak performance area | Student has recorded low score | Generate recommendations after low result | Category performance below 50% | High-priority targeted suggestion reflects current score | Not executed | Pending | Data-driven recommendation case |
| TC-028 | FR-011 | View progress for empty history | Student has no attempts/submissions | Open progress and analytics endpoint | Empty activity set | Useful empty state and no fabricated performance values | Not executed | Pending | Empty-history boundary case |
| TC-029 | FR-014 | Create an admin question | Admin and category exist | Submit valid question in admin form | Valid category, choices, answer, explanation | Question persists and becomes browseable | Not executed | Pending | CRUD integration case |
| TC-030 | FR-014 | Reject invalid admin question | Admin account exists | Submit question with missing required fields | Missing category or answer | Validation error; no malformed record persists | Not executed | Pending | Server-side validation case |
| TC-031 | FR-014 | Create an admin mock test | Admin and questions exist | Configure test and attach questions | Positive duration and marks | Test persists and appears in published test list | Not executed | Pending | CRUD integration case |
| TC-032 | FR-015 | Manage coding and HR content | Admin account exists | Create/edit/delete one coding item and HR item | Valid and invalid boundary values | Valid changes persist; invalid values are rejected | Not executed | Pending | Manual admin CRUD test |
| TC-033 | FR-017 | Reject invalid password change | Student is logged in | Submit new password with wrong current password | Wrong current password | Password remains unchanged and safe validation appears | Not executed | Pending | Negative profile case |
| TC-034 | FR-010, FR-011 | Persist progress across restart | Local SQLite file contains practice records | Record practice; stop/restart server; reopen dashboard | Existing seeded database | Previously committed records remain available | Not executed | Pending | Database persistence integration case |
| TC-035 | FR-018 | Reject state change without CSRF token | Normal non-testing configuration | POST state-changing endpoint without token | Missing/invalid token | HTTP 400; database state is unchanged | Not executed | Pending | Current pytest config disables CSRF; production-mode check required |
| TC-036 | FR-021 | Provision an additional admin | Admin is logged in | Submit the admin creation form with valid details | Unique email and matching password of at least 8 characters | New account has admin role and hashed password | Targeted pytest observed redirect, admin role, and verified password hash | Pass | `tests/test_admin.py` |
| TC-037 | FR-003, FR-021 | Deny student admin provisioning | Student is logged in | POST the admin creation endpoint | Valid-looking admin details | Request is denied and no admin account is created | Targeted pytest observed redirect and no account | Pass | `tests/test_admin.py` |
| TC-038 | FR-015 | Render HR administration pages | Admin is logged in | Open `/admin/hr` and `/admin/users` | Empty test database | Both pages render with their forms and empty states | Targeted pytest observed HTTP 200 for both pages | Pass | `tests/test_admin.py` |

## Automated Test Mapping

| Test module | Verified behavior |
|---|---|
| `tests/test_auth.py` | Registration stores a password hash, duplicate registration is rejected, wrong-password login is rejected |
| `tests/test_questions.py` | Search/detail rendering and bookmark persistence |
| `tests/test_mock_tests.py` | Answer-key omission, server-side score persistence, owner authorization |
| `tests/test_recommendations.py` | Onboarding recommendations are stored without performance history |
| `tests/test_admin.py` | Student denial and admin dashboard access |

Latest executed command: `.venv\Scripts\python.exe -m pytest -q` (**16 passed**). Pytest emitted SQLAlchemy deprecation and model-name collection warnings; they did not fail the run. Pending cases have not been claimed as passed.
