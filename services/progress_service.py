from datetime import datetime, date, timedelta
from sqlalchemy import func
from models import (
    db, User, TestAttempt, AttemptAnswer, Question, CodingProblem,
    CodingSubmission, HRQuestion, HRPractice, ActivityLog, Category, QuestionAttempt
)

def calculate_user_streak(user_id: int):
    """Calculates consecutive days of preparation activity up to today/yesterday."""
    activities = ActivityLog.query.filter_by(user_id=user_id)\
        .order_by(ActivityLog.created_at.desc()).all()

    if not activities:
        return 0

    activity_dates = sorted({a.created_at.date() for a in activities}, reverse=True)
    if not activity_dates:
        return 0

    today = date.today()
    current_date = today
    streak = 0

    # If no activity today, check if active yesterday
    if activity_dates[0] < today - timedelta(days=1):
        return 0

    if activity_dates[0] == today:
        check_date = today
    else:
        check_date = today - timedelta(days=1)

    for act_date in activity_dates:
        if act_date == check_date:
            streak += 1
            check_date -= timedelta(days=1)
        elif act_date < check_date:
            break

    return max(1, streak) if (activity_dates[0] in [today, today - timedelta(days=1)]) else 0

def get_student_dashboard_metrics(user_id: int):
    """
    Computes all dynamic metrics for the student dashboard.
    Ensures 100% genuine database metrics without hardcoded numbers.
    """
    # 1. Tests Completed & Average Score
    attempts = TestAttempt.query.filter_by(user_id=user_id, status='evaluated').all()
    tests_completed = len(attempts)
    avg_score = round(sum(a.percentage for a in attempts) / tests_completed, 1) if tests_completed > 0 else 0.0

    # 2. Coding Problems Solved
    coding_solved = db.session.query(CodingSubmission.problem_id)\
        .filter(CodingSubmission.user_id == user_id, CodingSubmission.result_status == 'Accepted')\
        .distinct().count()
    total_coding = CodingProblem.query.count()

    # 3. Questions Attempted (unique questions through test attempts and direct practice)
    test_q_ids = db.session.query(AttemptAnswer.question_id)\
        .join(TestAttempt, AttemptAnswer.attempt_id == TestAttempt.id)\
        .filter(TestAttempt.user_id == user_id).distinct().all()
    direct_q_ids = db.session.query(QuestionAttempt.question_id)\
        .filter(QuestionAttempt.user_id == user_id).distinct().all()

    all_attempted_q_ids = set([q[0] for q in test_q_ids] + [q[0] for q in direct_q_ids])
    questions_attempted = len(all_attempted_q_ids)
    total_questions = Question.query.count()

    # 4. HR Questions Practiced
    hr_practiced = HRPractice.query.filter_by(user_id=user_id, is_practiced=True).count()
    total_hr = HRQuestion.query.count()

    # 5. Streak
    streak = calculate_user_streak(user_id)

    # 6. Overall Preparation Progress %
    # Weighted: Mock Tests (35%), Coding (35%), Questions (15%), HR (15%)
    test_metric = min(100.0, avg_score) if tests_completed > 0 else 0.0
    coding_metric = min(100.0, (coding_solved / max(1, total_coding)) * 100)
    question_metric = min(100.0, (questions_attempted / max(1, total_questions)) * 100)
    hr_metric = min(100.0, (hr_practiced / max(1, total_hr)) * 100)

    overall_progress = round(
        (test_metric * 0.35) +
        (coding_metric * 0.35) +
        (question_metric * 0.15) +
        (hr_metric * 0.15),
        1
    )

    # 7. Category-wise Breakdown for Chart.js
    categories = Category.query.all()
    cat_names = []
    cat_scores = []
    cat_accuracies = {}

    for cat in categories:
        answers = db.session.query(AttemptAnswer)\
            .join(TestAttempt, AttemptAnswer.attempt_id == TestAttempt.id)\
            .join(Question, AttemptAnswer.question_id == Question.id)\
            .filter(TestAttempt.user_id == user_id, Question.category_id == cat.id)\
            .all()
        if answers:
            correct = sum(1 for a in answers if a.is_correct)
            acc = round((correct / len(answers)) * 100, 1)
            cat_names.append(cat.name)
            cat_scores.append(acc)
            cat_accuracies[cat.name] = acc

    strongest_subject = max(cat_accuracies.items(), key=lambda x: x[1])[0] if cat_accuracies else None
    weakest_subject = min(cat_accuracies.items(), key=lambda x: x[1])[0] if cat_accuracies else None

    # 8. Recent Activity
    recent_activities = ActivityLog.query.filter_by(user_id=user_id)\
        .order_by(ActivityLog.created_at.desc()).limit(8).all()

    # 9. Recent Test Results
    recent_tests = TestAttempt.query.filter_by(user_id=user_id, status='evaluated')\
        .order_by(TestAttempt.submitted_at.desc()).limit(5).all()

    return {
        'tests_completed': tests_completed,
        'avg_score': avg_score,
        'coding_solved': coding_solved,
        'total_coding': total_coding,
        'questions_attempted': questions_attempted,
        'total_questions': total_questions,
        'hr_practiced': hr_practiced,
        'total_hr': total_hr,
        'streak': streak,
        'overall_progress': overall_progress,
        'strongest_subject': strongest_subject,
        'weakest_subject': weakest_subject,
        'category_names': cat_names,
        'category_scores': cat_scores,
        'recent_activities': recent_activities,
        'recent_tests': recent_tests
    }
