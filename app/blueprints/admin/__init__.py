"""
app/blueprints/admin/__init__.py — Admin Dashboard Blueprint
User management, analytics, CSV import system.
"""

import os
import json
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, current_app, jsonify
)
from flask_login import login_required, current_user
from sqlalchemy import func

from app import db
from app.models import User, College, Favorite, ImportLog, State, Branch
from app.utils.forms import CSVUploadForm

admin_bp = Blueprint("admin", __name__, template_folder="../../templates/admin")


# ─── ADMIN ACCESS DECORATOR ────────────────────────────────────

def admin_required(f):
    """Restricts route to admin users only."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated


# ─── DASHBOARD ─────────────────────────────────────────────────

@admin_bp.route("/")
@admin_required
def dashboard():
    """Admin analytics dashboard."""
    # Key metrics
    total_colleges  = College.query.filter_by(is_active=True).count()
    total_users     = User.query.filter_by(role="student").count()
    total_favorites = Favorite.query.count()
    total_imports   = ImportLog.query.count()

    # New users in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users_30d = User.query.filter(
        User.created_at >= thirty_days_ago,
        User.role == "student"
    ).count()

    # Colleges by state (for chart)
    colleges_by_state = (
        db.session.query(State.name, func.count(College.id))
        .join(College, College.state_id == State.id)
        .filter(College.is_active == True)
        .group_by(State.name)
        .order_by(func.count(College.id).desc())
        .limit(10)
        .all()
    )

    # Recent imports
    recent_imports = (
        ImportLog.query
        .order_by(ImportLog.started_at.desc())
        .limit(5)
        .all()
    )

    # Recent users
    recent_users = (
        User.query
        .filter_by(role="student")
        .order_by(User.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        total_colleges=total_colleges,
        total_users=total_users,
        total_favorites=total_favorites,
        total_imports=total_imports,
        new_users_30d=new_users_30d,
        colleges_by_state=colleges_by_state,
        recent_imports=recent_imports,
        recent_users=recent_users,
        title="Admin Dashboard",
    )


# ─── USER MANAGEMENT ───────────────────────────────────────────

@admin_bp.route("/users")
@admin_required
def users():
    """List all users with pagination."""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "")

    q = User.query
    if search:
        q = q.filter(
            User.full_name.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%")
        )
    pagination = q.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )

    return render_template(
        "admin/users.html",
        users=pagination.items,
        pagination=pagination,
        search=search,
        title="User Management",
    )


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@admin_required
def toggle_user(user_id):
    """Activate / deactivate a user account."""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot deactivate your own account.", "warning")
        return redirect(url_for("admin.users"))

    user.is_active = not user.is_active
    db.session.commit()
    status = "activated" if user.is_active else "deactivated"
    flash(f"User {user.email} has been {status}.", "success")
    return redirect(url_for("admin.users"))


# ─── CSV UPLOAD ────────────────────────────────────────────────

@admin_bp.route("/import", methods=["GET", "POST"])
@admin_required
def import_data():
    """CSV upload and import trigger."""
    form = CSVUploadForm()

    if form.validate_on_submit():
        file = form.csv_file.data
        source = form.source.data
        mode = form.mode.data

        # Save uploaded file temporarily
        upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
        os.makedirs(upload_folder, exist_ok=True)
        filename = f"{source}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # Create import log entry
        import_log = ImportLog(
            filename=filename,
            source=source,
            status="pending",
            imported_by=current_user.id,
        )
        db.session.add(import_log)
        db.session.commit()

        # Run import (inline for simplicity; use Celery for large files in prod)
        try:
            from scripts.import_colleges import import_csv
            result = import_csv(filepath, source=source, mode=mode, log_id=import_log.id)

            import_log.records_total   = result.get("total", 0)
            import_log.records_added   = result.get("added", 0)
            import_log.records_updated = result.get("updated", 0)
            import_log.records_failed  = result.get("failed", 0)
            import_log.status          = "success"
            import_log.completed_at    = datetime.utcnow()
            db.session.commit()

            flash(
                f"Import complete: {result.get('added', 0)} added, "
                f"{result.get('updated', 0)} updated, "
                f"{result.get('failed', 0)} failed.",
                "success",
            )
        except Exception as e:
            import_log.status = "failed"
            import_log.error_message = str(e)
            import_log.completed_at = datetime.utcnow()
            db.session.commit()
            flash(f"Import failed: {str(e)}", "danger")

        return redirect(url_for("admin.import_data"))

    # Show recent imports
    recent_logs = ImportLog.query.order_by(ImportLog.started_at.desc()).limit(10).all()

    return render_template(
        "admin/import.html",
        form=form,
        recent_logs=recent_logs,
        title="Dataset Import",
    )


# ─── IMPORT LOGS ───────────────────────────────────────────────

@admin_bp.route("/import/logs")
@admin_required
def import_logs():
    """Full import history."""
    page = request.args.get("page", 1, type=int)
    logs = ImportLog.query.order_by(ImportLog.started_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template(
        "admin/import_logs.html",
        logs=logs,
        title="Import History",
    )


# ─── ANALYTICS API (for charts) ────────────────────────────────

@admin_bp.route("/analytics/colleges-by-state")
@admin_required
def analytics_colleges_by_state():
    """JSON data for admin dashboard chart."""
    data = (
        db.session.query(State.name, func.count(College.id))
        .join(College, College.state_id == State.id)
        .filter(College.is_active == True)
        .group_by(State.name)
        .order_by(func.count(College.id).desc())
        .limit(15)
        .all()
    )
    return jsonify({
        "labels": [row[0] for row in data],
        "values": [row[1] for row in data],
    })
