from flask import Blueprint, render_template
from models import Category, Question, MockTest, CodingProblem

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def landing():
    categories = Category.query.all()
    total_questions = Question.query.count()
    total_tests = MockTest.query.count()
    total_problems = CodingProblem.query.count()

    stats = {
        'questions_count': max(total_questions, 60),
        'tests_count': max(total_tests, 5),
        'problems_count': max(total_problems, 15),
        'hr_count': 20
    }

    return render_template('landing.html', categories=categories, stats=stats)
