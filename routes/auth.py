from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, ActivityLog
from services.recommendation_service import generate_recommendations

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        preferred_job_role = request.form.get('preferred_job_role', 'Software Engineer').strip()
        education = request.form.get('education', 'Computer Science').strip()

        # Validation
        if not full_name or not email or not password:
            flash("All required fields must be filled out.", "danger")
            return render_template('register.html')

        if len(full_name) < 2:
            flash("Full name must be at least 2 characters long.", "danger")
            return render_template('register.html')

        if '@' not in email or '.' not in email:
            flash("Please enter a valid email address.", "danger")
            return render_template('register.html')

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('register.html')

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')

        # Check existing user
        if User.query.filter_by(email=email).first():
            flash("An account with this email address already exists.", "warning")
            return render_template('register.html')

        # Create user
        new_user = User(
            full_name=full_name,
            email=email,
            role='student',
            preferred_job_role=preferred_job_role or 'Software Engineer',
            education=education or 'Computer Science',
            is_active=True,
            created_at=datetime.utcnow()
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Log registration activity
        act = ActivityLog(
            user_id=new_user.id,
            activity_type='login',
            title='Account Created',
            description='Welcome to Smart Interview Preparation Platform!'
        )
        db.session.add(act)
        db.session.commit()

        # Generate onboarding recommendations
        generate_recommendations(new_user.id)

        # Log in user
        login_user(new_user)
        flash(f"Welcome to Smart Prep, {new_user.full_name}! Your preparation journey starts now.", "success")
        return redirect(url_for('student.dashboard'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template('login.html')

        if not user.is_active:
            flash("Your account has been deactivated. Please contact support.", "danger")
            return render_template('login.html')

        login_user(user, remember=remember)
        flash(f"Welcome back, {user.full_name}!", "success")

        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)

        if user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    return render_template('login.html')

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for('main.landing'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        preferred_job_role = request.form.get('preferred_job_role', '').strip()
        education = request.form.get('education', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not full_name:
            flash("Full name cannot be empty.", "danger")
            return render_template('profile.html')

        current_user.full_name = full_name
        current_user.preferred_job_role = preferred_job_role
        current_user.education = education

        # Password update if requested
        if new_password:
            if not current_password:
                flash("Please enter your current password to set a new password.", "danger")
                return render_template('profile.html')
            if not current_user.check_password(current_password):
                flash("Current password entered is incorrect.", "danger")
                return render_template('profile.html')
            if len(new_password) < 6:
                flash("New password must be at least 6 characters long.", "danger")
                return render_template('profile.html')
            if new_password != confirm_password:
                flash("New passwords do not match.", "danger")
                return render_template('profile.html')

            current_user.set_password(new_password)
            flash("Profile details and password updated successfully!", "success")
        else:
            flash("Profile details updated successfully!", "success")

        db.session.commit()
        return redirect(url_for('auth.profile'))

    return render_template('profile.html')
