from models import User, db

from tests.conftest import login


def test_student_is_denied_admin_dashboard(client, student):
    login(client)

    response = client.get("/admin/dashboard")

    assert response.status_code == 302
    assert "/dashboard" in response.headers["Location"]


def test_admin_can_open_admin_dashboard(app, client):
    with app.app_context():
        admin = User(
            full_name="Test Administrator",
            email="admin@example.test",
            role="admin",
            is_active=True,
        )
        admin.set_password("SecurePass123")
        db.session.add(admin)
        db.session.commit()

    response = login(client, email="admin@example.test")
    assert response.status_code == 302
    dashboard_response = client.get("/admin/dashboard")

    assert dashboard_response.status_code == 200


def test_admin_pages_render(app, client):
    with app.app_context():
        admin = User(
            full_name="Test Administrator",
            email="admin@example.test",
            role="admin",
            is_active=True,
        )
        admin.set_password("SecurePass123")
        db.session.add(admin)
        db.session.commit()
    login(client, email="admin@example.test")

    hr_response = client.get("/admin/hr")
    users_response = client.get("/admin/users")

    assert hr_response.status_code == 200
    assert b"HR question bank" in hr_response.data
    assert users_response.status_code == 200
    assert b"Create administrator account" in users_response.data


def test_admin_can_create_another_admin(app, client):
    with app.app_context():
        admin = User(
            full_name="Test Administrator",
            email="admin@example.test",
            role="admin",
            is_active=True,
        )
        admin.set_password("SecurePass123")
        db.session.add(admin)
        db.session.commit()
    login(client, email="admin@example.test")

    response = client.post(
        "/admin/users/admin/create",
        data={
            "full_name": "Second Administrator",
            "email": "SECOND@example.test",
            "password": "NewAdminPass123",
            "confirm_password": "NewAdminPass123",
        },
    )

    assert response.status_code == 302
    with app.app_context():
        created = User.query.filter_by(email="second@example.test").one()
        assert created.role == "admin"
        assert created.check_password("NewAdminPass123")


def test_student_cannot_create_an_admin(app, client, student):
    login(client)

    response = client.post(
        "/admin/users/admin/create",
        data={
            "full_name": "Unauthorized Admin",
            "email": "unauthorized@example.test",
            "password": "NewAdminPass123",
            "confirm_password": "NewAdminPass123",
        },
    )

    assert response.status_code == 302
    with app.app_context():
        assert User.query.filter_by(email="unauthorized@example.test").first() is None
