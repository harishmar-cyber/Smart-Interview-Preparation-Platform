from models import Recommendation, db
from services.recommendation_service import generate_recommendations


def test_new_user_receives_onboarding_recommendations(app, student):
    with app.app_context():
        recommendations = generate_recommendations(student)

        assert recommendations
        assert any("Diagnostic" in item.title for item in recommendations)
        assert all(item.priority in {"High", "Moderate", "Steady", "Advanced"} for item in recommendations)
        assert Recommendation.query.filter_by(user_id=student, is_completed=False).count() == len(recommendations)
