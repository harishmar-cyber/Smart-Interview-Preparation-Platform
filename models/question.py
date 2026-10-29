from datetime import datetime
from models import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), default='fa-code')
    color = db.Column(db.String(20), default='#6366F1')

    # Relationships
    questions = db.relationship('Question', backref='category', lazy='dynamic', cascade='all, delete-orphan')
    mock_tests = db.relationship('MockTest', backref='category', lazy='dynamic')
    recommendations = db.relationship('Recommendation', backref='category', lazy='dynamic')

    def __repr__(self):
        return f"<Category {self.name}>"

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False, index=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(30), default='mcq', nullable=False)  # 'mcq', 'conceptual'
    difficulty = db.Column(db.String(20), default='Medium', nullable=False)  # 'Easy', 'Medium', 'Hard'
    option_a = db.Column(db.Text, nullable=True)
    option_b = db.Column(db.Text, nullable=True)
    option_c = db.Column(db.Text, nullable=True)
    option_d = db.Column(db.Text, nullable=True)
    correct_answer = db.Column(db.String(10), nullable=True)  # 'A', 'B', 'C', 'D'
    explanation = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    bookmarks = db.relationship('Bookmark', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    attempts = db.relationship('QuestionAttempt', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    test_questions = db.relationship('TestQuestion', backref='question', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_answer=False):
        data = {
            'id': self.id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else '',
            'question_text': self.question_text,
            'question_type': self.question_type,
            'difficulty': self.difficulty,
            'option_a': self.option_a,
            'option_b': self.option_b,
            'option_c': self.option_c,
            'option_d': self.option_d,
            'created_at': self.created_at.isoformat()
        }
        if include_answer:
            data['correct_answer'] = self.correct_answer
            data['explanation'] = self.explanation
        return data

    def __repr__(self):
        return f"<Question {self.id}: {self.question_text[:30]}...>"

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    __table_args__ = (db.UniqueConstraint('user_id', 'question_id', name='uq_user_question_bookmark'),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Bookmark User:{self.user_id} Q:{self.question_id}>"

class QuestionAttempt(db.Model):
    __tablename__ = 'question_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False, index=True)
    selected_answer = db.Column(db.String(10), nullable=True)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<QuestionAttempt User:{self.user_id} Q:{self.question_id} Correct:{self.is_correct}>"
