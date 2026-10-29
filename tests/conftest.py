import pytest

from app import create_app
from models import Category, Question, User, db


@pytest.fixture

def app():
    application = create_app("testing")
    with application.app_context():
        db.drop_all()
        db.create_all()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture

def client(app):
    return app.test_client()


@pytest.fixture

def student(app):
    with app.app_context():
        user = User(
            full_name="Test Student",
            email="student@example.test",
            role="student",
            is_active=True,
        )
        user.set_password("SecurePass123")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture

def category(app):
    with app.app_context():
        item = Category(name="Python", description="Python fundamentals")
        db.session.add(item)
        db.session.commit()
        return item.id


def login(client, email="student@example.test", password="SecurePass123"):
    return client.post("/login", data={"email": email, "password": password})


def add_question(app, category_id, *, answer="B"):
    with app.app_context():
        question = Question(
            category_id=category_id,
            question_text="Which collection is mutable?",
            question_type="mcq",
            difficulty="Easy",
            option_a="Tuple",
            option_b="List",
            option_c="String",
            option_d="Integer",
            correct_answer=answer,
            explanation="Lists can be changed after creation.",
        )
        db.session.add(question)
        db.session.commit()
        return question.id
