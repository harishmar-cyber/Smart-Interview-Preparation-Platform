import json
from datetime import datetime
from models import db

class CodingProblem(db.Model):
    __tablename__ = 'coding_problems'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, unique=True)
    slug = db.Column(db.String(160), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='Easy', nullable=False)  # 'Easy', 'Medium', 'Hard'
    category = db.Column(db.String(50), default='Basic Programming', nullable=False)
    input_format = db.Column(db.Text, nullable=True)
    output_format = db.Column(db.Text, nullable=True)
    sample_input = db.Column(db.Text, nullable=True)
    sample_output = db.Column(db.Text, nullable=True)
    constraints = db.Column(db.Text, nullable=True)
    hints = db.Column(db.Text, nullable=True)
    solution_explanation = db.Column(db.Text, nullable=True)
    starter_code = db.Column(db.Text, nullable=True)
    test_cases_json = db.Column(db.Text, nullable=False, default='[]')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    submissions = db.relationship('CodingSubmission', backref='problem', lazy='dynamic', cascade='all, delete-orphan')

    def get_test_cases(self):
        try:
            return json.loads(self.test_cases_json)
        except Exception:
            return []

    def set_test_cases(self, test_cases_list):
        self.test_cases_json = json.dumps(test_cases_list)

    def is_solved_by(self, user_id):
        if not user_id:
            return False
        return self.submissions.filter_by(user_id=user_id, result_status='Accepted').count() > 0

    def __repr__(self):
        return f"<CodingProblem {self.title}>"

class CodingSubmission(db.Model):
    __tablename__ = 'coding_submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('coding_problems.id', ondelete='CASCADE'), nullable=False, index=True)
    submitted_code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(30), default='python', nullable=False)
    result_status = db.Column(db.String(40), default='Pending', nullable=False)  # 'Accepted', 'Wrong Answer', 'Time Limit Exceeded', 'Runtime Error'
    test_cases_passed = db.Column(db.Integer, default=0, nullable=False)
    test_cases_total = db.Column(db.Integer, default=0, nullable=False)
    runtime_ms = db.Column(db.Float, default=0.0, nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<CodingSubmission {self.id}: User:{self.user_id} Problem:{self.problem_id} Status:{self.result_status}>"
