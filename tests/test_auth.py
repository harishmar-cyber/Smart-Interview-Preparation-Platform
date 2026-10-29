import re

from models import User, db


def test_registration_hashes_password_and_logs_in(app, client):
    response = client.post(
        "/register",
        data={
            "full_name": "New Student",
            "email": "NEW@example.test",
            "password": "SecurePass123",
            "confirm_password": "SecurePass123",
        },
    )

    assert response.status_code == 302
    with app.app_context():
        user = User.query.filter_by(email="new@example.test").one()
        assert user.check_password("SecurePass123")
        assert user.password_hash != "SecurePass123"


def test_registration_rejects_duplicate_email(app, client, student):
    response = client.post(
        "/register",
        data={
            "full_name": "Another Student",
            "email": "student@example.test",
            "password": "SecurePass123",
            "confirm_password": "SecurePass123",
        },
    )

    assert response.status_code == 200
    with app.app_context():
        assert User.query.filter_by(email="student@example.test").count() == 1


def test_login_rejects_wrong_password(client, student):
    response = client.post(
        "/login",
        data={"email": "student@example.test", "password": "wrong-password"},
    )

    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_csrf_rejects_missing_token_and_accepts_valid_token(app, client, student):
    app.config["WTF_CSRF_ENABLED"] = True
    login_page = client.get("/login")
    token_match = re.search(rb'<meta name="csrf-token" content="([^"]+)"', login_page.data)

    assert token_match is not None
    rejected = client.post(
        "/login",
        data={"email": "student@example.test", "password": "SecurePass123"},
    )
    accepted = client.post(
        "/login",
        data={
            "email": "student@example.test",
            "password": "SecurePass123",
            "csrf_token": token_match.group(1).decode(),
        },
    )

    assert rejected.status_code == 400
    assert accepted.status_code == 302
