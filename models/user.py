from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student' or 'admin'
    preferred_job_role = db.Column(db.String(100), nullable=True, default='Software Engineer')
    education = db.Column(db.String(150), nullable=True, default='Computer Science & Engineering')
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    test_attempts = db.relationship('TestAttempt', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    coding_submissions = db.relationship('CodingSubmission', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    hr_practices = db.relationship('HRPractice', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    recommendations = db.relationship('Recommendation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    activities = db.relationship('ActivityLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    question_attempts = db.relationship('QuestionAttempt', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
