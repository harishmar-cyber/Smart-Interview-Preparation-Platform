from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, HRQuestion, HRPractice, ActivityLog
from services.recommendation_service import generate_recommendations

hr_bp = Blueprint('hr', __name__)

@hr_bp.route('/hr-practice')
@login_required
def index():
    category = request.args.get('category', '')
    status = request.args.get('status', '')

    query = HRQuestion.query

    if category:
        query = query.filter_by(category=category)

    questions = query.order_by(HRQuestion.id.asc()).all()

    # User's practice records
    user_practices = {
        p.hr_question_id: p for p in HRPractice.query.filter_by(user_id=current_user.id).all()
    }

    if status == 'practiced':
        questions = [q for q in questions if q.id in user_practices and user_practices[q.id].is_practiced]
    elif status == 'pending':
        questions = [q for q in questions if q.id not in user_practices or not user_practices[q.id].is_practiced]

    total_count = HRQuestion.query.count()
    practiced_count = HRPractice.query.filter_by(user_id=current_user.id, is_practiced=True).count()
    completion_percentage = round((practiced_count / max(1, total_count)) * 100, 1)

    categories = [
        'Introduction & Background',
        'Strengths & Weaknesses',
        'Behavioral & STAR',
        'Company & Career Goals',
        'Situational & Pressure Handling'
    ]

    return render_template(
        'hr_practice.html',
        questions=questions,
        user_practices=user_practices,
        total_count=total_count,
        practiced_count=practiced_count,
        completion_percentage=completion_percentage,
        categories=categories,
        selected_category=category,
        selected_status=status
    )

@hr_bp.route('/hr-practice/<int:question_id>/save', methods=['POST'])
@login_required
def save_practice(question_id):
    question = HRQuestion.query.get_or_404(question_id)
    data = request.get_json() or {}
    personal_answer = data.get('personal_answer', '').strip()
    is_practiced = bool(data.get('is_practiced', True))
    confidence_level = data.get('confidence_level', 'Medium')

    practice = HRPractice.query.filter_by(user_id=current_user.id, hr_question_id=question_id).first()

    if not practice:
        practice = HRPractice(
            user_id=current_user.id,
            hr_question_id=question_id,
            personal_answer=personal_answer,
            is_practiced=is_practiced,
            confidence_level=confidence_level,
            updated_at=datetime.utcnow()
        )
        db.session.add(practice)
    else:
        practice.personal_answer = personal_answer
        practice.is_practiced = is_practiced
        practice.confidence_level = confidence_level
        practice.updated_at = datetime.utcnow()

    # Log activity if marked practiced
    if is_practiced:
        activity = ActivityLog(
            user_id=current_user.id,
            activity_type='hr_practice',
            title=f"Practiced HR Question: {question.question_text[:40]}...",
            description=f"Confidence: {confidence_level}",
            reference_id=question.id
        )
        db.session.add(activity)

    db.session.commit()

    # Refresh recommendations
    generate_recommendations(current_user.id)

    return jsonify({
        'success': True,
        'message': 'Your personal response has been saved.',
        'is_practiced': practice.is_practiced,
        'updated_at': practice.updated_at.strftime('%b %d, %Y %H:%M')
    })
