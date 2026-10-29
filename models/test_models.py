from datetime import datetime
from models import db

class MockTest(db.Model):
    __tablename__ = 'mock_tests'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True, index=True)
    duration_minutes = db.Column(db.Integer, default=30, nullable=False)
    total_marks = db.Column(db.Integer, default=20, nullable=False)
    passing_percentage = db.Column(db.Float, default=60.0, nullable=False)
    difficulty = db.Column(db.String(20), default='Medium', nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    test_questions = db.relationship('TestQuestion', backref='mock_test', lazy='dynamic', cascade='all, delete-orphan')
    attempts = db.relationship('TestAttempt', backref='mock_test', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def question_count(self):
        return self.test_questions.count()

    def __repr__(self):
        return f"<MockTest {self.title}>"

class TestQuestion(db.Model):
    __tablename__ = 'test_questions'
    __table_args__ = (db.UniqueConstraint('test_id', 'question_id', name='uq_test_question'),)

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('mock_tests.id', ondelete='CASCADE'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False, index=True)
    marks = db.Column(db.Integer, default=1, nullable=False)

    def __repr__(self):
        return f"<TestQuestion Test:{self.test_id} Q:{self.question_id}>"

class TestAttempt(db.Model):
    __tablename__ = 'test_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    test_id = db.Column(db.Integer, db.ForeignKey('mock_tests.id', ondelete='CASCADE'), nullable=False, index=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Float, default=0.0, nullable=False)
    percentage = db.Column(db.Float, default=0.0, nullable=False)
    status = db.Column(db.String(20), default='in_progress', nullable=False)  # 'in_progress', 'submitted', 'evaluated', 'expired'
    time_taken_seconds = db.Column(db.Integer, default=0, nullable=False)

    # Relationships
    answers = db.relationship('AttemptAnswer', backref='attempt', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def is_passed(self):
        passing = self.mock_test.passing_percentage if self.mock_test else 60.0
        return self.percentage >= passing

    @property
    def correct_count(self):
        return self.answers.filter_by(is_correct=True).count()

    @property
    def incorrect_count(self):
        return self.answers.filter(AttemptAnswer.is_correct == False, AttemptAnswer.selected_answer != None, AttemptAnswer.selected_answer != '').count()

    @property
    def unanswered_count(self):
        total = self.mock_test.question_count if self.mock_test else 0
        answered = self.answers.filter(AttemptAnswer.selected_answer != None, AttemptAnswer.selected_answer != '').count()
        return max(0, total - answered)

    def __repr__(self):
        return f"<TestAttempt {self.id}: User:{self.user_id} Test:{self.test_id} Score:{self.score}>"

class AttemptAnswer(db.Model):
    __tablename__ = 'attempt_answers'
    __table_args__ = (db.UniqueConstraint('attempt_id', 'question_id', name='uq_attempt_question'),)

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('test_attempts.id', ondelete='CASCADE'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False, index=True)
    selected_answer = db.Column(db.String(10), nullable=True)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    marks_awarded = db.Column(db.Float, default=0.0, nullable=False)

    # Relationship to Question
    question = db.relationship('Question')

    def __repr__(self):
        return f"<AttemptAnswer Attempt:{self.attempt_id} Q:{self.question_id} Ans:{self.selected_answer} Correct:{self.is_correct}>"
