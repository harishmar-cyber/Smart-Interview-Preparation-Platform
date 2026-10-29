from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import (
    db, TestAttempt, AttemptAnswer, Question, CodingSubmission,
    CodingProblem, HRPractice, HRQuestion, Category
)
from services.progress_service import get_student_dashboard_metrics

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/progress')
@login_required
def index():
    metrics = get_student_dashboard_metrics(current_user.id)

    # Detailed test attempts history
    test_history = TestAttempt.query.filter_by(user_id=current_user.id, status='evaluated')\
        .order_by(TestAttempt.submitted_at.desc()).all()

    # Coding submissions history
    coding_submissions = CodingSubmission.query.filter_by(user_id=current_user.id)\
        .order_by(CodingSubmission.submitted_at.desc()).limit(15).all()

    # Category performance breakdown
    categories = Category.query.all()
    cat_stats = []
    for cat in categories:
        answers = db.session.query(AttemptAnswer)\
            .join(TestAttempt, AttemptAnswer.attempt_id == TestAttempt.id)\
            .join(Question, AttemptAnswer.question_id == Question.id)\
            .filter(TestAttempt.user_id == current_user.id, Question.category_id == cat.id)\
            .all()

        total = len(answers)
        correct = sum(1 for a in answers if a.is_correct)
        acc = round((correct / total) * 100, 1) if total > 0 else 0.0
        cat_stats.append({
            'name': cat.name,
            'icon': cat.icon,
            'color': cat.color,
            'total_attempted': total,
            'correct': correct,
            'accuracy': acc
        })

    return render_template(
        'progress.html',
        metrics=metrics,
        test_history=test_history,
        coding_submissions=coding_submissions,
        cat_stats=cat_stats
    )

@analytics_bp.route('/api/analytics-data')
@login_required
def get_chart_data():
    """Provides dynamic JSON data for all charts on Progress and Dashboard."""
    # 1. Performance Over Time (Test Attempt Dates vs Percentage)
    attempts = TestAttempt.query.filter_by(user_id=current_user.id, status='evaluated')\
        .order_by(TestAttempt.submitted_at.asc()).all()

    time_labels = [a.submitted_at.strftime('%b %d') for a in attempts]
    time_scores = [a.percentage for a in attempts]

    # 2. Category Accuracy
    categories = Category.query.all()
    cat_labels = []
    cat_accuracies = []

    for cat in categories:
        answers = db.session.query(AttemptAnswer)\
            .join(TestAttempt, AttemptAnswer.attempt_id == TestAttempt.id)\
            .join(Question, AttemptAnswer.question_id == Question.id)\
            .filter(TestAttempt.user_id == current_user.id, Question.category_id == cat.id)\
            .all()
        if answers:
            correct = sum(1 for a in answers if a.is_correct)
            acc = round((correct / len(answers)) * 100, 1)
            cat_labels.append(cat.name)
            cat_accuracies.append(acc)

    # 3. Module Completion Breakdown (Radar / Doughnut)
    total_q = max(1, Question.query.count())
    attempted_q = len(set(
        a[0] for a in db.session.query(AttemptAnswer.question_id)
        .join(TestAttempt, AttemptAnswer.attempt_id == TestAttempt.id)
        .filter(TestAttempt.user_id == current_user.id).all()
    ))

    total_coding = max(1, CodingProblem.query.count())
    solved_coding = db.session.query(CodingSubmission.problem_id)\
        .filter(CodingSubmission.user_id == current_user.id, CodingSubmission.result_status == 'Accepted')\
        .distinct().count()

    total_hr = max(1, HRQuestion.query.count())
    practiced_hr = HRPractice.query.filter_by(user_id=current_user.id, is_practiced=True).count()

    return jsonify({
        'trend': {
            'labels': time_labels,
            'data': time_scores
        },
        'categories': {
            'labels': cat_labels,
            'data': cat_accuracies
        },
        'distribution': {
            'labels': ['Question Bank', 'Coding Problems', 'HR Preparation', 'Mock Tests'],
            'data': [
                round((attempted_q / total_q) * 100, 1),
                round((solved_coding / total_coding) * 100, 1),
                round((practiced_hr / total_hr) * 100, 1),
                round(sum(time_scores) / len(time_scores), 1) if time_scores else 0.0
            ]
        }
    })
