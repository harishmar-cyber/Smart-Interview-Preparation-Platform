from models import CodingProblem, User, db

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


def test_admin_coding_pages_and_problem_crud(app, client):
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

    assert client.get("/admin/coding").status_code == 200
    assert client.get("/admin/coding/create").status_code == 200
    response = client.post(
        "/admin/coding/create",
        data={
            "title": "Sum a Number",
            "slug": "sum-a-number",
            "description": "Read and print one integer.",
            "difficulty": "Easy",
            "category": "Basic Programming",
            "test_cases_json": '[{"input": "1", "expected": "1"}]',
            "solution_explanation": "Read the input and print it.",
        },
    )

    assert response.status_code == 302
    with app.app_context():
        problem = CodingProblem.query.filter_by(slug="sum-a-number").one()
        problem_id = problem.id
        assert problem.solution_explanation == "Read the input and print it."

    assert client.get(f"/admin/coding/{problem_id}/edit").status_code == 200
    edit_response = client.post(
        f"/admin/coding/{problem_id}/edit",
        data={
            "title": "Sum One Number",
            "slug": "sum-one-number",
            "description": "Read and print one integer.",
            "difficulty": "Easy",
            "category": "Basic Programming",
            "test_cases_json": '[{"input": "2", "expected": "2"}]',
            "solution_explanation": "Read and return the input value.",
        },
    )

    assert edit_response.status_code == 302
    with app.app_context():
        updated = db.session.get(CodingProblem, problem_id)
        assert updated.slug == "sum-one-number"
        assert updated.solution_explanation == "Read and return the input value."
