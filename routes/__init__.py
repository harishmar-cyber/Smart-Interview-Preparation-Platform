from routes.main import main_bp
from routes.auth import auth_bp
from routes.student import student_bp
from routes.questions import questions_bp
from routes.mock_tests import mock_tests_bp
from routes.coding import coding_bp
from routes.hr import hr_bp
from routes.analytics import analytics_bp
from routes.recommendations import recommendations_bp
from routes.admin import admin_bp

def register_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(mock_tests_bp)
    app.register_blueprint(coding_bp)
    app.register_blueprint(hr_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(admin_bp)
