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
