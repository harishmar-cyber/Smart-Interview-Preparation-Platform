from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Recommendation
from services.recommendation_service import generate_recommendations

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/recommendations')
@login_required
def index():
    status = request.args.get('status', 'active')
    priority = request.args.get('priority', '')

    query = Recommendation.query.filter_by(user_id=current_user.id)

    if status == 'active':
        query = query.filter_by(is_completed=False)
    elif status == 'completed':
        query = query.filter_by(is_completed=True)

    if priority in ['High', 'Moderate', 'Steady', 'Advanced']:
        query = query.filter_by(priority=priority)

    recommendations = query.order_by(
        db_case_priority(),
        Recommendation.created_at.desc()
    ).all()

    # Generate if none exist
    if not recommendations and status == 'active':
        recommendations = generate_recommendations(current_user.id)

    active_count = Recommendation.query.filter_by(user_id=current_user.id, is_completed=False).count()
    completed_count = Recommendation.query.filter_by(user_id=current_user.id, is_completed=True).count()

    return render_template(
        'recommendations.html',
        recommendations=recommendations,
        active_count=active_count,
        completed_count=completed_count,
        current_status=status,
        current_priority=priority
    )

@recommendations_bp.route('/recommendations/<int:rec_id>/toggle', methods=['POST'])
@login_required
def toggle_complete(rec_id):
    rec = Recommendation.query.filter_by(id=rec_id, user_id=current_user.id).first_or_404()
    rec.is_completed = not rec.is_completed
    db.session.commit()

    if request.is_json:
        return jsonify({
            'success': True,
            'is_completed': rec.is_completed,
            'message': 'Recommendation marked as completed!' if rec.is_completed else 'Recommendation marked as active.'
        })

    flash("Recommendation updated.", "info")
    return redirect(url_for('recommendations.index'))

@recommendations_bp.route('/recommendations/refresh', methods=['POST'])
@login_required
def refresh():
    generate_recommendations(current_user.id)
    flash("Recommendations successfully updated based on your latest activity!", "success")
    return redirect(url_for('recommendations.index'))

def db_case_priority():
    from sqlalchemy import case
    return case(
        (Recommendation.priority == 'High', 1),
        (Recommendation.priority == 'Moderate', 2),
        (Recommendation.priority == 'Steady', 3),
        else_=4
    )
