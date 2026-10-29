from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.question import Category, Question, Bookmark, QuestionAttempt
from models.test_models import MockTest, TestQuestion, TestAttempt, AttemptAnswer
from models.coding import CodingProblem, CodingSubmission
from models.hr import HRQuestion, HRPractice
from models.recommendation import Recommendation
from models.activity import ActivityLog

__all__ = [
    'db',
    'User',
    'Category',
    'Question',
    'Bookmark',
    'QuestionAttempt',
    'MockTest',
    'TestQuestion',
    'TestAttempt',
    'AttemptAnswer',
    'CodingProblem',
    'CodingSubmission',
    'HRQuestion',
    'HRPractice',
    'Recommendation',
    'ActivityLog'
]
