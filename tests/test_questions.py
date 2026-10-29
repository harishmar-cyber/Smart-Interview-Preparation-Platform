from models import Bookmark, db

from tests.conftest import add_question, login


def test_question_search_and_detail_render(app, client, student, category):
    question_id = add_question(app, category)
    login(client)

    search_response = client.get("/questions?q=mutable")
    detail_response = client.get(f"/questions/{question_id}")

    assert search_response.status_code == 200
    assert b"Which collection is mutable?" in search_response.data
    assert detail_response.status_code == 200
    assert b"Lists can be changed after creation." in detail_response.data


def test_question_bookmark_is_persisted(app, client, student, category):
    question_id = add_question(app, category)
    login(client)

    response = client.post(
        f"/questions/{question_id}/bookmark",
        json={"toggle": True},
    )

    assert response.status_code == 200
    assert response.json["bookmarked"] is True
    with app.app_context():
        assert Bookmark.query.filter_by(user_id=student, question_id=question_id).count() == 1


def test_wrong_answer_returns_incorrect_state_and_both_views_have_feedback_hooks(
    app, client, student, category
):
    question_id = add_question(app, category, answer="B")
    login(client)

    bank_page = client.get("/questions")
    detail_page = client.get(f"/questions/{question_id}")
    answer_response = client.post(
        f"/questions/{question_id}/attempt",
        json={"selected_option": "A"},
    )

    assert b"answer-choice-button" in bank_page.data
    assert b"question-answer-option" in detail_page.data
    assert answer_response.status_code == 200
    assert answer_response.json["is_correct"] is False
    assert answer_response.json["correct_answer"] == "B"
