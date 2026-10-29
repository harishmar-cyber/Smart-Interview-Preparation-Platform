import os
from flask import Flask, render_template
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from config import config_by_name
from models import db, User, Recommendation

login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_name=None):
    if not config_name:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Ensure instance directory exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from routes import register_routes
    register_routes(app)

    # Context processors
    @app.context_processor
    def inject_global_data():
        active_recs_count = 0
        if current_user.is_authenticated and not current_user.is_admin:
            active_recs_count = Recommendation.query.filter_by(
                user_id=current_user.id, is_completed=False
            ).count()
        return {
            'app_name': 'SmartPrep',
            'app_tagline': 'Smart Interview Preparation Platform',
            'active_recs_count': active_recs_count
        }

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('base.html', error_code=404, error_message="Page Not Found"), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('base.html', error_code=403, error_message="Access Forbidden"), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('base.html', error_code=500, error_message="Internal Server Error"), 500

    # Initialize database tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
