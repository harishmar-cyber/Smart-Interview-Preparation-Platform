from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from models import db, CodingProblem, CodingSubmission, ActivityLog
from services.code_runner import execute_coding_submission
from services.recommendation_service import generate_recommendations

coding_bp = Blueprint('coding', __name__)

@coding_bp.route('/coding')
@login_required
def index():
    difficulty = request.args.get('difficulty', '')
    category = request.args.get('category', '')
    status = request.args.get('status', '')

    query = CodingProblem.query

    if difficulty and difficulty in ['Easy', 'Medium', 'Hard']:
        query = query.filter_by(difficulty=difficulty)

    if category:
        query = query.filter_by(category=category)

    problems = query.order_by(CodingProblem.id.asc()).all()

    # Get solved problem IDs for current user
    solved_problem_ids = set(
        s[0] for s in db.session.query(CodingSubmission.problem_id)
        .filter_by(user_id=current_user.id, result_status='Accepted').distinct().all()
    )

    # Filter by solved status if requested
    if status == 'solved':
        problems = [p for p in problems if p.id in solved_problem_ids]
    elif status == 'unsolved':
        problems = [p for p in problems if p.id not in solved_problem_ids]

    categories = db.session.query(CodingProblem.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]

    total_problems = CodingProblem.query.count()
    solved_count = len(solved_problem_ids)
    progress_percentage = round((solved_count / max(1, total_problems)) * 100, 1)

    return render_template(
        'coding.html',
        problems=problems,
        solved_problem_ids=solved_problem_ids,
        categories=categories,
        selected_difficulty=difficulty,
        selected_category=category,
        selected_status=status,
        total_problems=total_problems,
        solved_count=solved_count,
        progress_percentage=progress_percentage
    )

@coding_bp.route('/coding/<slug>')
@login_required
def detail(slug):
    problem = CodingProblem.query.filter_by(slug=slug).first_or_404()

    # User's recent submissions
    submissions = CodingSubmission.query.filter_by(
        user_id=current_user.id,
        problem_id=problem.id
    ).order_by(CodingSubmission.submitted_at.desc()).limit(10).all()

    is_solved = problem.is_solved_by(current_user.id)

    # Get user's last submitted code or default starter code
    last_submission = submissions[0] if submissions else None
    current_code = last_submission.submitted_code if last_submission else problem.starter_code

    test_cases = problem.get_test_cases()
    visible_test_cases = [tc for tc in test_cases if not tc.get('is_hidden', False)]

    return render_template(
        'coding_detail.html',
        problem=problem,
        submissions=submissions,
        is_solved=is_solved,
        current_code=current_code,
        visible_test_cases=visible_test_cases
    )

@coding_bp.route('/coding/<int:problem_id>/run', methods=['POST'])
@login_required
def run_sample_code(problem_id):
    problem = CodingProblem.query.get_or_404(problem_id)
    data = request.get_json() or {}
    code = data.get('code', '')

    if not code.strip():
        return jsonify({'success': False, 'message': 'Code cannot be empty.'}), 400

    # Run only against visible (sample) test cases
    test_cases = problem.get_test_cases()
    sample_cases = [tc for tc in test_cases if not tc.get('is_hidden', False)]
    if not sample_cases:
        sample_cases = test_cases[:2]

    result = execute_coding_submission(code, sample_cases, timeout_sec=3.0)
    return jsonify({
        'success': True,
        'result': result
    })

@coding_bp.route('/coding/<int:problem_id>/submit', methods=['POST'])
@login_required
def submit_code(problem_id):
    problem = CodingProblem.query.get_or_404(problem_id)
    data = request.get_json() or {}
    code = data.get('code', '')

    if not code.strip():
        return jsonify({'success': False, 'message': 'Code cannot be empty.'}), 400

    # Run against all test cases (both visible and hidden)
    all_test_cases = problem.get_test_cases()
    result = execute_coding_submission(code, all_test_cases, timeout_sec=3.0)

    # Save submission
    submission = CodingSubmission(
        user_id=current_user.id,
        problem_id=problem.id,
        submitted_code=code,
        language='python',
        result_status=result['result_status'],
        test_cases_passed=result['test_cases_passed'],
        test_cases_total=result['test_cases_total'],
        runtime_ms=result['runtime_ms'],
        error_message=result.get('error_message')
    )
    db.session.add(submission)

    # If accepted, log activity and refresh recommendations
    if result['result_status'] == 'Accepted':
        activity = ActivityLog(
            user_id=current_user.id,
            activity_type='coding_submission',
            title=f"Solved Coding Challenge: {problem.title}",
            description=f"Passed {result['test_cases_passed']}/{result['test_cases_total']} test cases in {result['runtime_ms']}ms",
            reference_id=problem.id
        )
        db.session.add(activity)

    db.session.commit()

    if result['result_status'] == 'Accepted':
        generate_recommendations(current_user.id)

    return jsonify({
        'success': True,
        'result': result,
        'submission_id': submission.id
    })
