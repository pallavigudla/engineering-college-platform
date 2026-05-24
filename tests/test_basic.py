"""
tests/test_basic.py — Basic unit tests for EduRank
Run: python -m pytest tests/ -v
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app, db
from app.models import User, College, State


@pytest.fixture
def app():
    """Create test app with in-memory SQLite database."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_state(app):
    """Create a sample state."""
    with app.app_context():
        state = State(name="Test State", code="TS")
        db.session.add(state)
        db.session.commit()
        return state.id


# ─── AUTH TESTS ────────────────────────────────────────────────

class TestAuth:

    def test_signup_page_loads(self, client):
        """Signup page should return 200."""
        res = client.get("/auth/signup")
        assert res.status_code == 200

    def test_login_page_loads(self, client):
        """Login page should return 200."""
        res = client.get("/auth/login")
        assert res.status_code == 200

    def test_signup_creates_user(self, client, app):
        """Valid signup should create a new user."""
        with app.app_context():
            res = client.post("/auth/signup", data={
                "full_name": "Test Student",
                "email": "test@example.com",
                "password": "TestPass123!",
                "confirm_password": "TestPass123!",
                "csrf_token": "test"  # CSRF disabled in testing
            }, follow_redirects=True)
            user = User.query.filter_by(email="test@example.com").first()
            assert user is not None
            assert user.full_name == "Test Student"
            assert user.role == "student"

    def test_password_is_hashed(self, client, app):
        """Password should never be stored in plaintext."""
        with app.app_context():
            user = User(full_name="Test", email="hash@test.com")
            user.set_password("MyPassword123")
            db.session.add(user)
            db.session.commit()
            assert user.password_hash != "MyPassword123"
            assert user.check_password("MyPassword123") is True
            assert user.check_password("WrongPassword") is False

    def test_duplicate_email_rejected(self, client, app):
        """Duplicate email signup should be rejected."""
        with app.app_context():
            user = User(full_name="Existing", email="dup@test.com")
            user.set_password("pass12345")
            db.session.add(user)
            db.session.commit()

            res = client.post("/auth/signup", data={
                "full_name": "New User",
                "email": "dup@test.com",
                "password": "TestPass123!",
                "confirm_password": "TestPass123!",
            })
            # Should stay on signup page (not redirect to login)
            assert b"already registered" in res.data or res.status_code == 200


# ─── COLLEGE MODEL TESTS ───────────────────────────────────────

class TestCollegeModel:

    def test_college_creation(self, app, sample_state):
        """College should be creatable with required fields."""
        with app.app_context():
            college = College(
                name="Test Institute of Technology",
                state_id=sample_state,
                nirf_rank=1,
                annual_fees_min=250000,
                placement_percentage=95.5,
            )
            db.session.add(college)
            db.session.commit()
            fetched = College.query.filter_by(name="Test Institute of Technology").first()
            assert fetched is not None
            assert fetched.nirf_rank == 1

    def test_fees_display(self, app, sample_state):
        """fees_display() should return formatted string."""
        with app.app_context():
            college = College(
                name="Fee Test College",
                state_id=sample_state,
                annual_fees_min=100000,
                annual_fees_max=200000,
            )
            display = college.fees_display()
            assert "₹" in display
            assert "1,00,000" in display or "100,000" in display

    def test_to_dict(self, app, sample_state):
        """to_dict() should return a dictionary with expected keys."""
        with app.app_context():
            college = College(name="Dict Test", state_id=sample_state)
            db.session.add(college)
            db.session.commit()
            d = college.to_dict()
            assert "id" in d
            assert "name" in d
            assert d["name"] == "Dict Test"


# ─── ROUTE TESTS ───────────────────────────────────────────────

class TestRoutes:

    def test_home_page(self, client):
        """Home page should return 200."""
        res = client.get("/")
        assert res.status_code == 200

    def test_search_page(self, client):
        """College search page should return 200."""
        res = client.get("/colleges/search")
        assert res.status_code == 200

    def test_api_colleges(self, client):
        """API colleges endpoint should return JSON."""
        res = client.get("/api/v1/colleges")
        assert res.status_code == 200
        data = res.get_json()
        assert "data" in data
        assert "meta" in data

    def test_api_states(self, client):
        """API states endpoint should return JSON."""
        res = client.get("/api/v1/states")
        assert res.status_code == 200
        data = res.get_json()
        assert "data" in data

    def test_dashboard_requires_login(self, client):
        """Dashboard should redirect to login if not authenticated."""
        res = client.get("/dashboard", follow_redirects=False)
        assert res.status_code in (302, 301)
        assert "/auth/login" in res.headers.get("Location", "")

    def test_admin_requires_login(self, client):
        """Admin panel should redirect to login if not authenticated."""
        res = client.get("/admin/", follow_redirects=False)
        assert res.status_code in (302, 301)

    def test_404_returns_error_page(self, client):
        """Unknown URL should return 404."""
        res = client.get("/this-page-does-not-exist-at-all")
        assert res.status_code == 404
