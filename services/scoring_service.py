from datetime import datetime
from models import db, TestAttempt, AttemptAnswer, TestQuestion, Question, ActivityLog

def grade_test_attempt(attempt_id: int, user_answers: dict, time_taken_seconds: int = 0):
    """
    Grades an in-progress or submitted test attempt.
    user_answers: {str(question_id): 'A' | 'B' | 'C' | 'D'}
    Returns (TestAttempt, dict_summary)
    """
    attempt = db.session.get(TestAttempt, attempt_id)
    if not attempt:
        raise ValueError(f"Attempt ID {attempt_id} not found.")

    if attempt.status in ['evaluated', 'expired'] and attempt.submitted_at:
        # Already graded
        return attempt, {
            'score': attempt.score,
            'percentage': attempt.percentage,
            'status': attempt.status
        }

    test = attempt.mock_test
    test_questions = test.test_questions.all()
    q_map = {tq.question_id: tq for tq in test_questions}

    total_marks_possible = sum(tq.marks for tq in test_questions)
    if total_marks_possible == 0:
        total_marks_possible = test.total_marks or 20

    score_obtained = 0.0
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0

    # Delete any existing partial answers for this attempt
    AttemptAnswer.query.filter_by(attempt_id=attempt.id).delete()

    for tq in test_questions:
        q_id = tq.question_id
        q = db.session.get(Question, q_id)
        if not q:
            continue

        chosen_ans = user_answers.get(str(q_id), '').strip().upper()
        if not chosen_ans:
            chosen_ans = user_answers.get(q_id, '')
            if chosen_ans:
                chosen_ans = str(chosen_ans).strip().upper()

        if chosen_ans:
            is_correct = (chosen_ans == (q.correct_answer or '').strip().upper())
            marks_awarded = float(tq.marks) if is_correct else 0.0
            if is_correct:
                score_obtained += marks_awarded
                correct_count += 1
            else:
                incorrect_count += 1
        else:
            chosen_ans = None
            is_correct = False
            marks_awarded = 0.0
            unanswered_count += 1

        answer_record = AttemptAnswer(
            attempt_id=attempt.id,
            question_id=q_id,
            selected_answer=chosen_ans,
            is_correct=is_correct,
            marks_awarded=marks_awarded
        )
        db.session.add(answer_record)

    percentage = round((score_obtained / total_marks_possible) * 100, 2) if total_marks_possible > 0 else 0.0

    attempt.score = score_obtained
    attempt.percentage = percentage
    attempt.status = 'evaluated'
    attempt.submitted_at = datetime.utcnow()
    attempt.time_taken_seconds = time_taken_seconds

    # Log activity
    passed_str = "Passed" if attempt.is_passed else "Needs Improvement"
    activity = ActivityLog(
        user_id=attempt.user_id,
        activity_type='mock_test',
        title=f"Completed Mock Test: {test.title}",
        description=f"Scored {score_obtained}/{total_marks_possible} ({percentage}%) - {passed_str}",
        reference_id=test.id,
        score=percentage
    )
    db.session.add(activity)
    db.session.commit()

    # Trigger recommendation refresh
    from services.recommendation_service import generate_recommendations
    generate_recommendations(attempt.user_id)

    summary = {
        'total_questions': len(test_questions),
        'correct_count': correct_count,
        'incorrect_count': incorrect_count,
        'unanswered_count': unanswered_count,
        'score': score_obtained,
        'total_marks': total_marks_possible,
        'percentage': percentage,
        'is_passed': attempt.is_passed,
        'time_taken_seconds': time_taken_seconds
    }

    return attempt, summary
