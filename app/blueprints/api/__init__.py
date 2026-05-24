"""
app/blueprints/api/__init__.py — REST API v1 Blueprint
JSON API for search, college details, favorites.
Future-ready for mobile apps or SPA frontends.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from app.models import College, State, Branch, Favorite
from app import db

api_bp = Blueprint("api", __name__)


@api_bp.route("/colleges")
def list_colleges():
    """
    GET /api/v1/colleges
    Query params: q, state, branch, nirf_max, fees_max, placement_min, page, per_page
    """
    q          = request.args.get("q", "")
    state_name = request.args.get("state", "")
    branch_name = request.args.get("branch", "")
    nirf_max   = request.args.get("nirf_max", type=int)
    fees_max   = request.args.get("fees_max", type=int)
    placement_min = request.args.get("placement_min", type=float)
    page       = request.args.get("page", 1, type=int)
    per_page   = min(request.args.get("per_page", 20, type=int), 100)

    query = College.query.filter_by(is_active=True)

    if q:
        query = query.filter(College.name.ilike(f"%{q}%"))
    if state_name:
        state = State.query.filter_by(name=state_name).first()
        if state:
            query = query.filter(College.state_id == state.id)
    if branch_name:
        branch = Branch.query.filter_by(name=branch_name).first()
        if branch:
            query = query.filter(College.branches.any(id=branch.id))
    if nirf_max:
        query = query.filter(College.nirf_rank <= nirf_max)
    if fees_max:
        query = query.filter(College.annual_fees_min <= fees_max)
    if placement_min:
        query = query.filter(College.placement_percentage >= placement_min)

    paginated = query.order_by(College.nirf_rank.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "data": [c.to_dict() for c in paginated.items],
        "meta": {
            "total": paginated.total,
            "page": page,
            "per_page": per_page,
            "pages": paginated.pages,
        },
    })


@api_bp.route("/colleges/<int:college_id>")
def get_college(college_id):
    """GET /api/v1/colleges/<id> — Full college detail."""
    college = College.query.filter_by(id=college_id, is_active=True).first_or_404()
    data = college.to_dict()
    data["courses"] = [
        {
            "name": c.name,
            "degree": c.degree,
            "duration": c.duration_years,
            "seats": c.seats,
            "fees": c.annual_fees,
        }
        for c in college.courses
    ]
    data["facilities"] = [f.name for f in college.facilities]
    return jsonify({"data": data})


@api_bp.route("/states")
def list_states():
    """GET /api/v1/states — All states."""
    states = State.query.order_by(State.name).all()
    return jsonify({"data": [{"id": s.id, "name": s.name} for s in states]})


@api_bp.route("/branches")
def list_branches():
    """GET /api/v1/branches — All branches."""
    branches = Branch.query.order_by(Branch.name).all()
    return jsonify({
        "data": [{"id": b.id, "name": b.name, "code": b.code} for b in branches]
    })


@api_bp.route("/favorites", methods=["GET"])
@login_required
def list_favorites():
    """GET /api/v1/favorites — Current user's favorites."""
    favs = Favorite.query.filter_by(user_id=current_user.id).all()
    return jsonify({"data": [f.college.to_dict() for f in favs]})
