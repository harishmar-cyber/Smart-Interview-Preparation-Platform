from datetime import datetime
from models import db

class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True, index=True)
    title = db.Column(db.String(200), nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='Moderate', nullable=False)  # 'High', 'Moderate', 'Steady', 'Advanced'
    suggested_action = db.Column(db.String(255), nullable=False)
    target_url = db.Column(db.String(255), nullable=True)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def badge_color(self):
        mapping = {
            'High': 'danger',
            'Moderate': 'warning',
            'Steady': 'info',
            'Advanced': 'success'
        }
        return mapping.get(self.priority, 'primary')

    def __repr__(self):
        return f"<Recommendation {self.id}: User:{self.user_id} {self.priority} - {self.title}>"
