"""
app/blueprints/colleges/__init__.py — College Search, Filter, Detail
"""

from flask import Blueprint, render_template, request
from sqlalchemy import or_

from app import db
from app.models import (
    College,
    Favorite,
    Branch,
    State,
    City
)
from app.utils.forms import CollegeSearchForm
from flask_login import current_user

colleges_bp = Blueprint(
    "colleges",
    __name__,
    template_folder="../../templates/colleges"
)


# ─────────────────────────────────────────────────────────────
# BUILD SEARCH QUERY
# ─────────────────────────────────────────────────────────────

def build_college_query(form):

    query = College.query.filter_by(is_active=True)

    # ── Text search ─────────────────────────────────────────
    if form.query.data:

        search_term = f"%{form.query.data.strip()}%"

        query = query.filter(
            or_(
                College.name.ilike(search_term),
                College.short_name.ilike(search_term),

                # Search by city relationship
                College.city.has(
                    City.name.ilike(search_term)
                ),

                # Search by state relationship
                College.state.has(
                    State.name.ilike(search_term)
                ),

                # Search by branches relationship
                College.branches.any(
                    Branch.name.ilike(search_term)
                ),

                # Search by branch codes
                College.branches.any(
                    Branch.code.ilike(search_term)
                ),
            )
        )
    # ── College type ───────────────────────────────────────
    if form.college_type.data:
        query = query.filter(
            College.college_type == form.college_type.data
        )

    # ── NIRF rank filter ───────────────────────────────────
    if form.nirf_rank_max.data:
        query = query.filter(
            College.nirf_rank != None,
            College.nirf_rank <= form.nirf_rank_max.data
        )

    # ── Fees filter ────────────────────────────────────────
    if form.fees_max.data:
        query = query.filter(
            or_(
                College.annual_fees_min <= form.fees_max.data,
                College.annual_fees_min == None
            )
        )

    # ── Placement filter ───────────────────────────────────
    if form.placement_min.data:
        query = query.filter(
            College.placement_percentage != None,
            College.placement_percentage >= form.placement_min.data
        )

    # ── Hostel filter ──────────────────────────────────────
    if form.hostel.data:
        query = query.filter(
            College.hostel_available == True
        )
     # ── State filter ──────────────────────────────────────
    if form.state.data and form.state.data.strip():

        query = query.join(State).filter(
            State.name.ilike(form.state.data)
        )

    # ── Branch filter ─────────────────────────────────────
    if form.branch.data and form.branch.data.strip():

        query = query.join(
            College.branches
        ).filter(
            Branch.name.ilike(f"%{form.branch.data}%")
        )

    # ── Sorting ────────────────────────────────────────────
    sort_column_map = {
        "nirf_rank": College.nirf_rank.asc(),
        "placement_percentage": College.placement_percentage.desc(),
        "annual_fees_min": College.annual_fees_min.asc(),
        "name": College.name.asc(),
    }

    sort_key = form.sort_by.data or "nirf_rank"

    query = query.order_by(
        sort_column_map.get(
            sort_key,
            College.nirf_rank.asc()
        )
    )

    return query


# ─────────────────────────────────────────────────────────────
# SEARCH PAGE
# ─────────────────────────────────────────────────────────────

@colleges_bp.route("/search")
def search():

    form = CollegeSearchForm(request.args)

    # ── Dynamic states dropdown ────────────────────────────
    states = [("", "All States")]

    all_states = State.query.order_by(State.name).all()

    for state in all_states:
        states.append((state.name, state.name))
    # ── Branch dropdown ────────────────────────────────────
    branches = [
    ("", "All Branches"),
    ("CSE", "CSE"),
    ("AI", "AI"),
    ("DS", "DS"),
    ("ECE", "ECE"),
    ("EEE", "EEE"),
    ("ME", "ME"),
    ]

    form.state.choices = states
    form.branch.choices = branches

    page = request.args.get("page", 1, type=int)

    per_page = 12

    # ── Build query ────────────────────────────────────────
    college_query = build_college_query(form)

    pagination = college_query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    colleges = pagination.items

    # ── Favorites ──────────────────────────────────────────
    fav_ids = set()

    if current_user.is_authenticated:
        fav_ids = {
            f.college_id
            for f in Favorite.query.filter_by(
                user_id=current_user.id
            ).all()
        }

    return render_template(
        "colleges/search.html",
        form=form,
        colleges=colleges,
        pagination=pagination,
        fav_ids=fav_ids,
        total=pagination.total,
        title="Search Colleges",
    )


# ─────────────────────────────────────────────────────────────
# COLLEGE DETAIL PAGE
# ─────────────────────────────────────────────────────────────

@colleges_bp.route("/<int:college_id>")
def detail(college_id):

    college = College.query.filter_by(
        id=college_id,
        is_active=True
    ).first_or_404()

    is_favorite = False

    if current_user.is_authenticated:
        is_favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            college_id=college_id
        ).first() is not None

    similar = (
        College.query
        .filter(
            College.id != college.id,
            College.state == college.state,
            College.is_active == True
        )
        .limit(4)
        .all()
    )

    return render_template(
        "colleges/detail.html",
        college=college,
        is_favorite=is_favorite,
        similar=similar,
        title=college.name,
    )
@colleges_bp.route("/compare")
def compare():

    ids = request.args.getlist("ids")

    colleges = []

    if ids:
        colleges = College.query.filter(
            College.id.in_(ids)
        ).all()

    all_colleges = College.query.order_by(
        College.name
    ).all()

    return render_template(
        "colleges/compare.html",
        colleges=colleges,
        all_colleges=all_colleges
    )