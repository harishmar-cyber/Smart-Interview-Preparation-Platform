from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from models import db, MockTest, TestQuestion, TestAttempt, AttemptAnswer, Question, Category
from services.scoring_service import grade_test_attempt

mock_tests_bp = Blueprint('mock_tests', __name__)

@mock_tests_bp.route('/mock-tests')
@login_required
def index():
    tests = MockTest.query.filter_by(is_published=True).all()
    categories = Category.query.all()

    # User's past attempts
    attempts = TestAttempt.query.filter_by(user_id=current_user.id, status='evaluated')\
        .order_by(TestAttempt.submitted_at.desc()).all()

    # Best score per test
    best_scores = {}
    for att in attempts:
        if att.test_id not in best_scores or att.percentage > best_scores[att.test_id]:
            best_scores[att.test_id] = att.percentage

    return render_template(
        'mock_tests.html',
        tests=tests,
        categories=categories,
        attempts=attempts,
        best_scores=best_scores
    )

@mock_tests_bp.route('/mock-tests/<int:test_id>/start', methods=['POST'])
@login_required
def start_test(test_id):
    mock_test = MockTest.query.get_or_404(test_id)

    if not mock_test.is_published and not current_user.is_admin:
        flash("This test is not currently available.", "warning")
        return redirect(url_for('mock_tests.index'))

    # Check for an active in-progress attempt for this test
    existing_attempt = TestAttempt.query.filter_by(
        user_id=current_user.id,
        test_id=test_id,
        status='in_progress'
    ).first()

    if existing_attempt:
        # Check if expired
        elapsed = (datetime.utcnow() - existing_attempt.started_at).total_seconds()
        duration_sec = mock_test.duration_minutes * 60
        if elapsed > duration_sec + 60:  # Allow 60s grace
            # Auto-expire / evaluate with existing answers
            existing_attempt.status = 'expired'
            grade_test_attempt(existing_attempt.id, {}, int(duration_sec))
        else:
            return redirect(url_for('mock_tests.take_test', attempt_id=existing_attempt.id))

    # Create new attempt
    attempt = TestAttempt(
        user_id=current_user.id,
        test_id=test_id,
        started_at=datetime.utcnow(),
        status='in_progress'
    )
    db.session.add(attempt)
    db.session.commit()

    return redirect(url_for('mock_tests.take_test', attempt_id=attempt.id))

@mock_tests_bp.route('/mock-tests/attempt/<int:attempt_id>/take')
@login_required
def take_test(attempt_id):
    attempt = TestAttempt.query.get_or_404(attempt_id)

    # Security check: User must own the attempt
    if attempt.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    # If already evaluated, redirect to results
    if attempt.status in ['evaluated', 'expired']:
        return redirect(url_for('mock_tests.view_result', attempt_id=attempt.id))

    mock_test = attempt.mock_test
    duration_sec = mock_test.duration_minutes * 60
    elapsed_sec = int((datetime.utcnow() - attempt.started_at).total_seconds())
    remaining_sec = max(0, duration_sec - elapsed_sec)

    # If timer ran out completely before visiting page
    if remaining_sec <= 0:
        grade_test_attempt(attempt.id, {}, duration_sec)
        flash("Your test session timed out and was automatically submitted.", "info")
        return redirect(url_for('mock_tests.view_result', attempt_id=attempt.id))

    # Load test questions WITHOUT correct answers or explanations
    test_questions = mock_test.test_questions.all()
    questions_data = []

    for tq in test_questions:
        q = tq.question
        # Notice: correct_answer and explanation are deliberately omitted!
        questions_data.append({
            'id': q.id,
            'question_text': q.question_text,
            'option_a': q.option_a,
            'option_b': q.option_b,
            'option_c': q.option_c,
            'option_d': q.option_d,
            'difficulty': q.difficulty,
            'marks': tq.marks,
            'category_name': q.category.name if q.category else ''
        })

    # Saved partial answers if any
    saved_answers = {
        ans.question_id: ans.selected_answer
        for ans in attempt.answers.all()
    }

    return render_template(
        'take_test.html',
        attempt=attempt,
        mock_test=mock_test,
        questions=questions_data,
        remaining_seconds=remaining_sec,
        total_seconds=duration_sec,
        saved_answers=saved_answers
    )

@mock_tests_bp.route('/mock-tests/attempt/<int:attempt_id>/submit', methods=['POST'])
@login_required
def submit_test(attempt_id):
    attempt = TestAttempt.query.get_or_404(attempt_id)

    if attempt.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    if attempt.status in ['evaluated', 'expired']:
        return jsonify({
            'success': True,
            'redirect_url': url_for('mock_tests.view_result', attempt_id=attempt.id),
            'message': 'Test has already been submitted.'
        })

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'success': False, 'message': 'Invalid submission payload.'}), 400

    answers = data.get('answers', {})  # {str(q_id): 'A'}
    if not isinstance(answers, dict):
        return jsonify({'success': False, 'message': 'Answers must be an object.'}), 400

    allowed_question_ids = {
        str(test_question.question_id)
        for test_question in attempt.mock_test.test_questions.all()
    }
    for question_id, selected_answer in answers.items():
        if str(question_id) not in allowed_question_ids:
            return jsonify({'success': False, 'message': 'Submission contains an invalid question.'}), 400
        if selected_answer not in (None, '') and (
            not isinstance(selected_answer, str)
            or selected_answer.strip().upper() not in {'A', 'B', 'C', 'D'}
        ):
            return jsonify({'success': False, 'message': 'Submission contains an invalid answer choice.'}), 400

    max_duration = attempt.mock_test.duration_minutes * 60 + 60
    elapsed = int((datetime.utcnow() - attempt.started_at).total_seconds())
    time_taken = min(max(elapsed, 0), max_duration)

    graded_attempt, summary = grade_test_attempt(attempt.id, answers, time_taken)

    return jsonify({
        'success': True,
        'redirect_url': url_for('mock_tests.view_result', attempt_id=graded_attempt.id),
        'summary': summary
    })

@mock_tests_bp.route('/mock-tests/attempt/<int:attempt_id>/result')
@login_required
def view_result(attempt_id):
    attempt = TestAttempt.query.get_or_404(attempt_id)

    if attempt.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    mock_test = attempt.mock_test
    answers = attempt.answers.all()

    # Category performance breakdown for this test
    cat_breakdown = {}
    for ans in answers:
        cat_name = ans.question.category.name if ans.question.category else 'General'
        if cat_name not in cat_breakdown:
            cat_breakdown[cat_name] = {'total': 0, 'correct': 0}
        cat_breakdown[cat_name]['total'] += 1
        if ans.is_correct:
            cat_breakdown[cat_name]['correct'] += 1

    for cat, stats in cat_breakdown.items():
        stats['percentage'] = round((stats['correct'] / stats['total']) * 100, 1)

    return render_template(
        'test_result.html',
        attempt=attempt,
        mock_test=mock_test,
        answers=answers,
        cat_breakdown=cat_breakdown
    )
