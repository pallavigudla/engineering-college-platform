"""
app/blueprints/auth/__init__.py — Authentication Blueprint
Handles signup, login, logout with secure session management.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

from app import db
from app.models import User
from app.utils.forms import SignupForm, LoginForm

auth_bp = Blueprint("auth", __name__, template_folder="../../templates/auth")


# ─── SIGNUP ────────────────────────────────────────────────────

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """Student registration endpoint."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = SignupForm()
    if form.validate_on_submit():
        print("SIGNUP FORM SUBMITTED")
        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower(),
            role="student",
        )
        user.set_password(form.password.data)

        try:
            db.session.add(user)
            db.session.commit()
            print("USER CREATED SUCCESSFULLY")
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash("Registration failed. Please try again.", "danger")

    return render_template("auth/signup.html", form=form, title="Sign Up")


# ─── LOGIN ─────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Student/Admin login endpoint."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash("Your account has been deactivated. Contact support.", "danger")
                return render_template("auth/login.html", form=form, title="Login")

            # Update last login timestamp
            user.last_login = datetime.utcnow()
            db.session.commit()

            login_user(user, remember=form.remember_me.data)
            flash(f"Welcome back, {user.full_name}!", "success")

            # Redirect to admin if admin role
            if user.is_admin:
                return redirect(url_for("admin.dashboard"))

            # Redirect to originally requested page (safe redirect)
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):  # security: relative URLs only
                return redirect(next_page)
            return redirect(url_for("main.index"))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("auth/login.html", form=form, title="Login")


# ─── LOGOUT ────────────────────────────────────────────────────

@auth_bp.route("/logout")
@login_required
def logout():
    """Logout current user."""
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))
