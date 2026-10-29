from datetime import datetime
from models import db

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    activity_type = db.Column(db.String(50), nullable=False)  # 'mock_test', 'question_practice', 'coding_submission', 'hr_practice'
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    reference_id = db.Column(db.Integer, nullable=True)
    score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    @property
    def icon(self):
        icons = {
            'mock_test': 'fa-stopwatch text-indigo',
            'question_practice': 'fa-check-circle text-success',
            'coding_submission': 'fa-code text-cyan',
            'hr_practice': 'fa-user-tie text-warning'
        }
        return icons.get(self.activity_type, 'fa-bolt text-primary')

    def __repr__(self):
        return f"<ActivityLog {self.user_id}: {self.activity_type} - {self.title}>"
