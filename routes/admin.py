import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import (
    db, User, Category, Question, MockTest, TestQuestion,
    CodingProblem, CodingSubmission, HRQuestion, TestAttempt, ActivityLog
)
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def check_admin():
    if not current_user.is_admin:
        flash("Unauthorized: Admin privileges required.", "danger")
        return redirect(url_for('student.dashboard'))

@admin_bp.route('/dashboard')
def dashboard():
    total_students = User.query.filter_by(role='student').count()
    total_questions = Question.query.count()
    total_tests = MockTest.query.count()
    total_problems = CodingProblem.query.count()
    total_hr = HRQuestion.query.count()
    total_attempts = TestAttempt.query.count()
    total_submissions = CodingSubmission.query.count()

    recent_users = User.query.filter_by(role='student').order_by(User.created_at.desc()).limit(5).all()
    recent_attempts = TestAttempt.query.order_by(TestAttempt.started_at.desc()).limit(6).all()
    recent_activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(8).all()

    stats = {
        'total_students': total_students,
        'total_questions': total_questions,
        'total_tests': total_tests,
        'total_problems': total_problems,
        'total_hr': total_hr,
        'total_attempts': total_attempts,
        'total_submissions': total_submissions
    }

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_users=recent_users,
        recent_attempts=recent_attempts,
        recent_activities=recent_activities
    )

# ==================== QUESTIONS CRUD ====================

@admin_bp.route('/questions')
def questions_list():
    category_id = request.args.get('category', type=int)
    search_q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Question.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search_q:
        query = query.filter(Question.question_text.ilike(f"%{search_q}%"))

    pagination = query.order_by(Question.id.desc()).paginate(page=page, per_page=15, error_out=False)
    categories = Category.query.all()

    return render_template(
        'admin/questions.html',
        questions=pagination.items,
        pagination=pagination,
        categories=categories,
        selected_category=category_id,
        search_query=search_q
    )

@admin_bp.route('/questions/create', methods=['GET', 'POST'])
def question_create():
    categories = Category.query.all()
    if request.method == 'POST':
        category_id = request.form.get('category_id', type=int)
        question_text = request.form.get('question_text', '').strip()
        difficulty = request.form.get('difficulty', 'Medium')
        question_type = request.form.get('question_type', 'mcq')
        option_a = request.form.get('option_a', '').strip()
        option_b = request.form.get('option_b', '').strip()
        option_c = request.form.get('option_c', '').strip()
        option_d = request.form.get('option_d', '').strip()
        correct_answer = request.form.get('correct_answer', '').strip().upper()
        explanation = request.form.get('explanation', '').strip()

        if not category_id or not question_text or not correct_answer:
            flash("Category, question text, and correct answer are required.", "danger")
            return render_template('admin/question_form.html', categories=categories, question=None)

        q = Question(
            category_id=category_id,
            question_text=question_text,
            difficulty=difficulty,
            question_type=question_type,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer,
            explanation=explanation,
            created_at=datetime.utcnow()
        )
        db.session.add(q)
        db.session.commit()
        flash("Question added successfully!", "success")
        return redirect(url_for('admin.questions_list'))

    return render_template('admin/question_form.html', categories=categories, question=None)

@admin_bp.route('/questions/<int:id>/edit', methods=['GET', 'POST'])
def question_edit(id):
    question = Question.query.get_or_404(id)
    categories = Category.query.all()

    if request.method == 'POST':
        question.category_id = request.form.get('category_id', type=int)
        question.question_text = request.form.get('question_text', '').strip()
        question.difficulty = request.form.get('difficulty', 'Medium')
        question.question_type = request.form.get('question_type', 'mcq')
        question.option_a = request.form.get('option_a', '').strip()
        question.option_b = request.form.get('option_b', '').strip()
        question.option_c = request.form.get('option_c', '').strip()
        question.option_d = request.form.get('option_d', '').strip()
        question.correct_answer = request.form.get('correct_answer', '').strip().upper()
        question.explanation = request.form.get('explanation', '').strip()

        db.session.commit()
        flash("Question updated successfully!", "success")
        return redirect(url_for('admin.questions_list'))

    return render_template('admin/question_form.html', categories=categories, question=question)

@admin_bp.route('/questions/<int:id>/delete', methods=['POST'])
def question_delete(id):
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully.", "info")
    return redirect(url_for('admin.questions_list'))

# ==================== MOCK TESTS CRUD ====================

@admin_bp.route('/tests')
def tests_list():
    tests = MockTest.query.order_by(MockTest.id.desc()).all()
    return render_template('admin/tests.html', tests=tests)

@admin_bp.route('/tests/create', methods=['GET', 'POST'])
def test_create():
    categories = Category.query.all()
    all_questions = Question.query.all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id', type=int)
        duration_minutes = request.form.get('duration_minutes', 30, type=int)
        passing_percentage = request.form.get('passing_percentage', 60.0, type=float)
        difficulty = request.form.get('difficulty', 'Medium')
        is_published = bool(request.form.get('is_published'))
        selected_q_ids = request.form.getlist('questions', type=int)

        if not title:
            flash("Test title is required.", "danger")
            return render_template('admin/test_form.html', categories=categories, all_questions=all_questions, test=None)

        mock_test = MockTest(
            title=title,
            description=description,
            category_id=category_id if category_id else None,
            duration_minutes=duration_minutes,
            passing_percentage=passing_percentage,
            difficulty=difficulty,
            is_published=is_published,
            total_marks=len(selected_q_ids) if selected_q_ids else 20
        )
        db.session.add(mock_test)
        db.session.flush()

        for q_id in selected_q_ids:
            tq = TestQuestion(test_id=mock_test.id, question_id=q_id, marks=1)
            db.session.add(tq)

        db.session.commit()
        flash("Mock Test created successfully!", "success")
        return redirect(url_for('admin.tests_list'))

    return render_template('admin/test_form.html', categories=categories, all_questions=all_questions, test=None)

@admin_bp.route('/tests/<int:id>/edit', methods=['GET', 'POST'])
def test_edit(id):
    test = MockTest.query.get_or_404(id)
    categories = Category.query.all()
    all_questions = Question.query.all()
    current_q_ids = set(tq.question_id for tq in test.test_questions.all())

    if request.method == 'POST':
        test.title = request.form.get('title', '').strip()
        test.description = request.form.get('description', '').strip()
        cat_id = request.form.get('category_id', type=int)
        test.category_id = cat_id if cat_id else None
        test.duration_minutes = request.form.get('duration_minutes', 30, type=int)
        test.passing_percentage = request.form.get('passing_percentage', 60.0, type=float)
        test.difficulty = request.form.get('difficulty', 'Medium')
        test.is_published = bool(request.form.get('is_published'))

        selected_q_ids = request.form.getlist('questions', type=int)

        # Update test questions
        TestQuestion.query.filter_by(test_id=test.id).delete()
        for q_id in selected_q_ids:
            tq = TestQuestion(test_id=test.id, question_id=q_id, marks=1)
            db.session.add(tq)

        test.total_marks = len(selected_q_ids)
        db.session.commit()
        flash("Mock test updated successfully!", "success")
        return redirect(url_for('admin.tests_list'))

    return render_template(
        'admin/test_form.html',
        categories=categories,
        all_questions=all_questions,
        test=test,
        current_q_ids=current_q_ids
    )

@admin_bp.route('/tests/<int:id>/delete', methods=['POST'])
def test_delete(id):
    test = MockTest.query.get_or_404(id)
    db.session.delete(test)
    db.session.commit()
    flash("Mock test deleted successfully.", "info")
    return redirect(url_for('admin.tests_list'))

# ==================== CODING PROBLEMS CRUD ====================

@admin_bp.route('/coding')
def coding_list():
    problems = CodingProblem.query.order_by(CodingProblem.id.asc()).all()
    return render_template('admin/coding.html', problems=problems)

@admin_bp.route('/coding/create', methods=['GET', 'POST'])
def coding_create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip().lower().replace(' ', '-')
        description = request.form.get('description', '').strip()
        difficulty = request.form.get('difficulty', 'Easy')
        category = request.form.get('category', 'Basic Programming').strip()
        input_format = request.form.get('input_format', '')
        output_format = request.form.get('output_format', '')
        sample_input = request.form.get('sample_input', '')
        sample_output = request.form.get('sample_output', '')
        constraints = request.form.get('constraints', '')
        hints = request.form.get('hints', '')
        starter_code = request.form.get('starter_code', '')
        test_cases_raw = request.form.get('test_cases_json', '[]')

        # Validate JSON
        try:
            json.loads(test_cases_raw)
        except Exception:
            flash("Invalid JSON format for test cases.", "danger")
            return render_template('admin/coding_form.html', problem=None)

        problem = CodingProblem(
            title=title,
            slug=slug,
            description=description,
            difficulty=difficulty,
            category=category,
            input_format=input_format,
            output_format=output_format,
            sample_input=sample_input,
            sample_output=sample_output,
            constraints=constraints,
            hints=hints,
            starter_code=starter_code,
            test_cases_json=test_cases_raw,
            created_at=datetime.utcnow()
        )
        db.session.add(problem)
        db.session.commit()
        flash("Coding problem added successfully!", "success")
        return redirect(url_for('admin.coding_list'))

    return render_template('admin/coding_form.html', problem=None)

@admin_bp.route('/coding/<int:id>/edit', methods=['GET', 'POST'])
def coding_edit(id):
    problem = CodingProblem.query.get_or_404(id)
    if request.method == 'POST':
        problem.title = request.form.get('title', '').strip()
        problem.slug = request.form.get('slug', '').strip().lower().replace(' ', '-')
        problem.description = request.form.get('description', '').strip()
        problem.difficulty = request.form.get('difficulty', 'Easy')
        problem.category = request.form.get('category', '').strip()
        problem.input_format = request.form.get('input_format', '')
        problem.output_format = request.form.get('output_format', '')
        problem.sample_input = request.form.get('sample_input', '')
        problem.sample_output = request.form.get('sample_output', '')
        problem.constraints = request.form.get('constraints', '')
        problem.hints = request.form.get('hints', '')
        problem.starter_code = request.form.get('starter_code', '')
        test_cases_raw = request.form.get('test_cases_json', '[]')

        try:
            json.loads(test_cases_raw)
            problem.test_cases_json = test_cases_raw
        except Exception:
            flash("Invalid JSON for test cases.", "danger")
            return render_template('admin/coding_form.html', problem=problem)

        db.session.commit()
        flash("Coding problem updated successfully!", "success")
        return redirect(url_for('admin.coding_list'))

    return render_template('admin/coding_form.html', problem=problem)

@admin_bp.route('/coding/<int:id>/delete', methods=['POST'])
def coding_delete(id):
    problem = CodingProblem.query.get_or_404(id)
    db.session.delete(problem)
    db.session.commit()
    flash("Coding problem deleted.", "info")
    return redirect(url_for('admin.coding_list'))

# ==================== HR QUESTIONS CRUD ====================

@admin_bp.route('/hr')
def hr_list():
    questions = HRQuestion.query.order_by(HRQuestion.id.asc()).all()
    return render_template('admin/hr.html', questions=questions)

@admin_bp.route('/hr/create', methods=['GET', 'POST'])
def hr_create():
    if request.method == 'POST':
        question_text = request.form.get('question_text', '').strip()
        category = request.form.get('category', 'Behavioral')
        answer_tips = request.form.get('answer_tips', '')
        example_answer = request.form.get('example_answer', '')
        star_guide = request.form.get('star_framework_guide', '')

        q = HRQuestion(
            question_text=question_text,
            category=category,
            answer_tips=answer_tips,
            example_answer=example_answer,
            star_framework_guide=star_guide,
            created_at=datetime.utcnow()
        )
        db.session.add(q)
        db.session.commit()
        flash("HR Question added successfully!", "success")
        return redirect(url_for('admin.hr_list'))

    return render_template('admin/hr_form.html', question=None)

@admin_bp.route('/hr/<int:id>/edit', methods=['GET', 'POST'])
def hr_edit(id):
    question = HRQuestion.query.get_or_404(id)
    if request.method == 'POST':
        question.question_text = request.form.get('question_text', '').strip()
        question.category = request.form.get('category', 'Behavioral')
        question.answer_tips = request.form.get('answer_tips', '')
        question.example_answer = request.form.get('example_answer', '')
        question.star_framework_guide = request.form.get('star_framework_guide', '')

        db.session.commit()
        flash("HR Question updated successfully!", "success")
        return redirect(url_for('admin.hr_list'))

    return render_template('admin/hr_form.html', question=question)

@admin_bp.route('/hr/<int:id>/delete', methods=['POST'])
def hr_delete(id):
    question = HRQuestion.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    flash("HR Question deleted.", "info")
    return redirect(url_for('admin.hr_list'))

# ==================== STUDENT USER MANAGEMENT ====================

@admin_bp.route('/users')
def users_list():
    search = request.args.get('q', '').strip()
    query = User.query.filter_by(role='student')
    if search:
        query = query.filter(User.full_name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))
    users = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users, search=search)

@admin_bp.route('/users/<int:id>/toggle-status', methods=['POST'])
def toggle_user_status(id):
    user = User.query.get_or_404(id)
    if user.is_admin:
        flash("Cannot deactivate an administrator account.", "danger")
        return redirect(url_for('admin.users_list'))

    user.is_active = not user.is_active
    db.session.commit()
    status_str = "activated" if user.is_active else "deactivated"
    flash(f"Student account {user.email} has been {status_str}.", "info")
    return redirect(url_for('admin.users_list'))
