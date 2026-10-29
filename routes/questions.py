from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Question, Category, Bookmark, QuestionAttempt, ActivityLog

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('/questions')
@login_required
def index():
    category_id = request.args.get('category', type=int)
    difficulty = request.args.get('difficulty', type=str)
    search_query = request.args.get('q', '').strip()
    bookmarked_only = request.args.get('bookmarked', type=int) == 1
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Question.query

    if category_id:
        query = query.filter_by(category_id=category_id)

    if difficulty and difficulty in ['Easy', 'Medium', 'Hard']:
        query = query.filter_by(difficulty=difficulty)

    if search_query:
        search_filter = f"%{search_query}%"
        query = query.filter(Question.question_text.ilike(search_filter) | Question.explanation.ilike(search_filter))

    if bookmarked_only:
        user_bookmark_qids = db.session.query(Bookmark.question_id).filter_by(user_id=current_user.id).all()
        q_ids = [b[0] for b in user_bookmark_qids]
        query = query.filter(Question.id.in_(q_ids))

    pagination = query.order_by(Question.id.asc()).paginate(page=page, per_page=per_page, error_out=False)
    questions = pagination.items

    categories = Category.query.all()

    # User's bookmarked questions map
    bookmarks = set(b.question_id for b in Bookmark.query.filter_by(user_id=current_user.id).all())

    # User's attempted questions map
    user_attempts = {
        qa.question_id: qa for qa in QuestionAttempt.query.filter_by(user_id=current_user.id).all()
    }

    selected_category = Category.query.get(category_id) if category_id else None

    return render_template(
        'questions.html',
        questions=questions,
        pagination=pagination,
        categories=categories,
        selected_category=selected_category,
        current_difficulty=difficulty,
        search_query=search_query,
        bookmarked_only=bookmarked_only,
        bookmarks=bookmarks,
        user_attempts=user_attempts,
        total_count=pagination.total
    )

@questions_bp.route('/questions/<int:question_id>')
@login_required
def detail(question_id):
    question = Question.query.get_or_404(question_id)
    is_bookmarked = Bookmark.query.filter_by(user_id=current_user.id, question_id=question_id).first() is not None
    attempt = QuestionAttempt.query.filter_by(user_id=current_user.id, question_id=question_id).first()

    return render_template(
        'question_detail.html',
        question=question,
        is_bookmarked=is_bookmarked,
        attempt=attempt
    )

@questions_bp.route('/questions/<int:question_id>/bookmark', methods=['POST'])
@login_required
def toggle_bookmark(question_id):
    question = Question.query.get_or_404(question_id)
    bookmark = Bookmark.query.filter_by(user_id=current_user.id, question_id=question_id).first()

    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        bookmarked = False
        message = "Removed from bookmarks."
    else:
        new_bm = Bookmark(user_id=current_user.id, question_id=question_id)
        db.session.add(new_bm)
        db.session.commit()
        bookmarked = True
        message = "Added to bookmarks."

    if request.is_json:
        return jsonify({'success': True, 'bookmarked': bookmarked, 'message': message})

    flash(message, "info")
    return redirect(request.referrer or url_for('questions.index'))

@questions_bp.route('/questions/<int:question_id>/attempt', methods=['POST'])
@login_required
def record_direct_attempt(question_id):
    question = Question.query.get_or_404(question_id)
    data = request.get_json() or {}
    selected_option = data.get('selected_option', '').strip().upper()

    if not selected_option:
        return jsonify({'success': False, 'message': 'No option selected.'}), 400

    is_correct = (selected_option == (question.correct_answer or '').strip().upper())

    attempt = QuestionAttempt.query.filter_by(user_id=current_user.id, question_id=question_id).first()
    if not attempt:
        attempt = QuestionAttempt(
            user_id=current_user.id,
            question_id=question_id,
            selected_answer=selected_option,
            is_correct=is_correct
        )
        db.session.add(attempt)
    else:
        attempt.selected_answer = selected_option
        attempt.is_correct = is_correct

    # Log practice activity
    act = ActivityLog(
        user_id=current_user.id,
        activity_type='question_practice',
        title=f"Practiced: {question.category.name if question.category else 'Technical'} Question",
        description=f"Outcome: {'Correct' if is_correct else 'Incorrect'}",
        reference_id=question.id
    )
    db.session.add(act)
    db.session.commit()

    return jsonify({
        'success': True,
        'is_correct': is_correct,
        'correct_answer': question.correct_answer,
        'explanation': question.explanation
    })
