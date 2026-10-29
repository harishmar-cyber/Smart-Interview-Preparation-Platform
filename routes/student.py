from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Recommendation, MockTest, Category
from services.progress_service import get_student_dashboard_metrics

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@login_required
def dashboard():
    metrics = get_student_dashboard_metrics(current_user.id)
    recommendations = Recommendation.query.filter_by(user_id=current_user.id, is_completed=False)\
        .order_by(
            db_case_priority(),
            Recommendation.created_at.desc()
        ).limit(3).all()

    # If no recommendations yet, generate onboarding ones
    if not recommendations:
        from services.recommendation_service import generate_recommendations
        recommendations = generate_recommendations(current_user.id)[:3]

    suggested_tests = MockTest.query.filter_by(is_published=True).limit(3).all()
    categories = Category.query.limit(6).all()

    return render_template(
        'dashboard.html',
        metrics=metrics,
        recommendations=recommendations,
        suggested_tests=suggested_tests,
        categories=categories
    )

def db_case_priority():
    from sqlalchemy import case
    return case(
        (Recommendation.priority == 'High', 1),
        (Recommendation.priority == 'Moderate', 2),
        (Recommendation.priority == 'Steady', 3),
        else_=4
    )
