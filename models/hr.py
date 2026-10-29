from datetime import datetime
from models import db

class HRQuestion(db.Model):
    __tablename__ = 'hr_questions'

    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(60), default='Behavioral', nullable=False)  # Behavioral, Situational, Career Goals, Strengths & Weaknesses
    answer_tips = db.Column(db.Text, nullable=True)
    example_answer = db.Column(db.Text, nullable=True)
    star_framework_guide = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    practices = db.relationship('HRPractice', backref='question', lazy='dynamic', cascade='all, delete-orphan')

    def get_user_practice(self, user_id):
        if not user_id:
            return None
        return self.practices.filter_by(user_id=user_id).first()

    def __repr__(self):
        return f"<HRQuestion {self.id}: {self.question_text[:30]}...>"

class HRPractice(db.Model):
    __tablename__ = 'hr_practices'
    __table_args__ = (db.UniqueConstraint('user_id', 'hr_question_id', name='uq_user_hr_practice'),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    hr_question_id = db.Column(db.Integer, db.ForeignKey('hr_questions.id', ondelete='CASCADE'), nullable=False, index=True)
    personal_answer = db.Column(db.Text, nullable=True)
    is_practiced = db.Column(db.Boolean, default=False, nullable=False)
    confidence_level = db.Column(db.String(20), default='Medium', nullable=False)  # 'Low', 'Medium', 'High'
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<HRPractice User:{self.user_id} HR_Q:{self.hr_question_id} Practiced:{self.is_practiced}>"
