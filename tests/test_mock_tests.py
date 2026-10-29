from models import AttemptAnswer, MockTest, TestAttempt, TestQuestion, User, db

from services.scoring_service import grade_test_attempt
from tests.conftest import add_question, login


def _create_test(app, question_id, user_id):
    with app.app_context():
        mock_test = MockTest(
            title="Python Basics",
            description="A short test",
            duration_minutes=30,
            total_marks=1,
            passing_percentage=60,
            is_published=True,
        )
        db.session.add(mock_test)
        db.session.flush()
        db.session.add(TestQuestion(test_id=mock_test.id, question_id=question_id, marks=1))
        attempt = TestAttempt(user_id=user_id, test_id=mock_test.id, status="in_progress")
        db.session.add(attempt)
        db.session.commit()
        return attempt.id


def test_test_delivery_does_not_render_correct_answer(app, client, student, category):
    question_id = add_question(app, category)
    attempt_id = _create_test(app, question_id, student)
    login(client)

    response = client.get(f"/mock-tests/attempt/{attempt_id}/take")

    assert response.status_code == 200
    assert b"correct_answer" not in response.data
    assert b"Lists can be changed after creation." not in response.data


def test_submission_is_scored_and_persisted(app, client, student, category):
    question_id = add_question(app, category)
    attempt_id = _create_test(app, question_id, student)
    login(client)

    response = client.post(
        f"/mock-tests/attempt/{attempt_id}/submit",
        json={"answers": {str(question_id): "B"}, "time_taken_seconds": 30},
    )

    assert response.status_code == 200
    assert response.json["summary"]["percentage"] == 100
    with app.app_context():
        attempt = db.session.get(TestAttempt, attempt_id)
        answer = AttemptAnswer.query.filter_by(attempt_id=attempt_id).one()
        assert attempt.status == "evaluated"
        assert attempt.score == 1
        assert answer.is_correct is True


def test_submission_rejects_question_not_in_test(app, client, student, category):
    question_id = add_question(app, category)
    attempt_id = _create_test(app, question_id, student)
    login(client)

    response = client.post(
        f"/mock-tests/attempt/{attempt_id}/submit",
        json={"answers": {"999999": "A"}},
    )

    assert response.status_code == 400
    with app.app_context():
        assert db.session.get(TestAttempt, attempt_id).status == "in_progress"


def test_user_cannot_view_another_users_result(app, client, student, category):
    question_id = add_question(app, category)
    with app.app_context():
        other_user = User(full_name="Other Student", email="other@example.test", role="student")
        other_user.set_password("SecurePass123")
        db.session.add(other_user)
        db.session.commit()
        other_user_id = other_user.id
    attempt_id = _create_test(app, question_id, other_user_id)
    login(client)

    response = client.get(f"/mock-tests/attempt/{attempt_id}/result")

    assert response.status_code == 403
