"""
app/blueprints/main/__init__.py — Main Blueprint
Home page, dashboard, favorites, comparison.
"""

import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func

from app import db
from app.models import College, Favorite, Comparison, State, Branch

main_bp = Blueprint("main", __name__, template_folder="../../templates/main")


# ─── HOME PAGE ─────────────────────────────────────────────────

@main_bp.route("/")
def index():
    """Landing page with stats and featured colleges."""
    # Aggregate stats for hero section
    stats = {
        "total_colleges": College.query.filter_by(is_active=True).count(),
        "total_states": State.query.count(),
        "total_branches": Branch.query.count(),
    }

    # Top ranked colleges (NIRF)
    top_colleges = (
        College.query
        .filter(College.is_active == True, College.nirf_rank != None)
        .order_by(College.nirf_rank.asc())
        .limit(6)
        .all()
    )

    # High placement colleges
    top_placement = (
        College.query
        .filter(College.is_active == True, College.placement_percentage != None)
        .order_by(College.placement_percentage.desc())
        .limit(6)
        .all()
    )

    states = State.query.order_by(State.name).all()
    branches = Branch.query.order_by(Branch.name).all()

    return render_template(
        "main/index.html",
        stats=stats,
        top_colleges=top_colleges,
        top_placement=top_placement,
        states=states,
        branches=branches,
        title="Home",
    )


# ─── STUDENT DASHBOARD ─────────────────────────────────────────

@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Student personal dashboard."""
    favorites = (
        Favorite.query
        .filter_by(user_id=current_user.id)
        .order_by(Favorite.saved_at.desc())
        .all()
    )
    fav_colleges = [f.college for f in favorites]

    return render_template(
        "main/dashboard.html",
        fav_colleges=fav_colleges,
        title="My Dashboard",
    )


# ─── FAVORITES ─────────────────────────────────────────────────

@main_bp.route("/favorites")
@login_required
def favorites():
    """View all saved colleges."""
    favs = (
        Favorite.query
        .filter_by(user_id=current_user.id)
        .order_by(Favorite.saved_at.desc())
        .all()
    )
    return render_template(
        "main/favorites.html",
        favorites=favs,
        title="My Favorites",
    )


@main_bp.route("/favorites/toggle/<int:college_id>", methods=["POST"])
@login_required
def toggle_favorite(college_id):
    """Add or remove a college from favorites (AJAX-friendly)."""
    college = College.query.get_or_404(college_id)
    existing = Favorite.query.filter_by(
        user_id=current_user.id, college_id=college_id
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"status": "removed", "message": "Removed from favorites"})
    else:
        fav = Favorite(user_id=current_user.id, college_id=college_id)
        db.session.add(fav)
        db.session.commit()
        return jsonify({"status": "added", "message": "Added to favorites"})


# ─── COMPARISON ────────────────────────────────────────────────

@main_bp.route("/compare")
@login_required
def compare():
    """Compare multiple colleges side by side."""
    college_ids_raw = request.args.getlist("ids")

    # Validate and cap at 4 colleges
    try:
        college_ids = [int(cid) for cid in college_ids_raw[:4]]
    except (ValueError, TypeError):
        flash("Invalid comparison request.", "warning")
        return redirect(url_for("colleges.search"))

    if len(college_ids) < 2:
        flash("Please select at least 2 colleges to compare.", "warning")
        return redirect(url_for("colleges.search"))

    colleges = College.query.filter(College.id.in_(college_ids)).all()

    # All unique branches across compared colleges
    all_branches = set()
    for c in colleges:
        all_branches.update([b.name for b in c.branches])

    return render_template(
        "main/compare.html",
        colleges=colleges,
        all_branches=sorted(all_branches),
        title="Compare Colleges",
    )
