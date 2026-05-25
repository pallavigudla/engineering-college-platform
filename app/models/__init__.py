"""
app/models/__init__.py
Cleaned Models File
"""

from datetime import datetime

from app import db, login_manager

from flask_login import UserMixin

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# ═══════════════════════════════════════════════════════════════
# USER LOADER
# ═══════════════════════════════════════════════════════════════

@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


# ═══════════════════════════════════════════════════════════════
# ASSOCIATION TABLES
# ═══════════════════════════════════════════════════════════════

college_branch = db.Table(

    "college_branch",

    db.Column(
        "college_id",
        db.Integer,
        db.ForeignKey("colleges.id"),
        primary_key=True
    ),

    db.Column(
        "branch_id",
        db.Integer,
        db.ForeignKey("branches.id"),
        primary_key=True
    ),
)

college_facility = db.Table(

    "college_facility",

    db.Column(
        "college_id",
        db.Integer,
        db.ForeignKey("colleges.id"),
        primary_key=True
    ),

    db.Column(
        "facility_id",
        db.Integer,
        db.ForeignKey("facilities.id"),
        primary_key=True
    ),
)


# ═══════════════════════════════════════════════════════════════
# USER MODEL
# ═══════════════════════════════════════════════════════════════

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(256),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="student"
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    last_login = db.Column(
        db.DateTime,
        nullable=True
    )

    def set_password(self, password):

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):

        return check_password_hash(
            self.password_hash,
            password
        )

    @property
    def is_admin(self):

        return self.role == "admin"

    def __repr__(self):

        return f"<User {self.email}>"


# ═══════════════════════════════════════════════════════════════
# STATE MODEL
# ═══════════════════════════════════════════════════════════════

class State(db.Model):

    __tablename__ = "states"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    code = db.Column(
        db.String(5),
        unique=True,
        nullable=True
    )

    cities = db.relationship(
        "City",
        backref="state",
        lazy="dynamic"
    )

    colleges = db.relationship(
        "College",
        backref="state",
        lazy="dynamic"
    )

    def __repr__(self):

        return f"<State {self.name}>"


# ═══════════════════════════════════════════════════════════════
# CITY MODEL
# ═══════════════════════════════════════════════════════════════

class City(db.Model):

    __tablename__ = "cities"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    state_id = db.Column(
        db.Integer,
        db.ForeignKey("states.id"),
        nullable=False
    )

    colleges = db.relationship(
        "College",
        backref="city",
        lazy="dynamic"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "name",
            "state_id",
            name="uq_city_state"
        ),
    )

    def __repr__(self):

        return f"<City {self.name}>"


# ═══════════════════════════════════════════════════════════════
# BRANCH MODEL
# ═══════════════════════════════════════════════════════════════

class Branch(db.Model):

    __tablename__ = "branches"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    code = db.Column(
        db.String(20),
        unique=True,
        nullable=True
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    def __repr__(self):

        return f"<Branch {self.name}>"


# ═══════════════════════════════════════════════════════════════
# FACILITY MODEL
# ═══════════════════════════════════════════════════════════════

class Facility(db.Model):

    __tablename__ = "facilities"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    icon = db.Column(
        db.String(50),
        nullable=True
    )

    def __repr__(self):

        return f"<Facility {self.name}>"


# ═══════════════════════════════════════════════════════════════
# COLLEGE MODEL
# ═══════════════════════════════════════════════════════════════

class College(db.Model):

    __tablename__ = "colleges"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # Identity
    name = db.Column(
        db.String(250),
        nullable=False,
        index=True
    )

    short_name = db.Column(
        db.String(50),
        nullable=True
    )

    college_type = db.Column(
        db.String(50),
        nullable=True
    )

    establishment_year = db.Column(
        db.Integer,
        nullable=True
    )

    aicte_id = db.Column(
        db.String(50),
        unique=True,
        nullable=True,
        index=True
    )

    nirf_id = db.Column(
        db.String(50),
        nullable=True
    )

    # Location
    address = db.Column(
        db.Text,
        nullable=True
    )

    city_id = db.Column(
        db.Integer,
        db.ForeignKey("cities.id"),
        nullable=True
    )

    state_id = db.Column(
        db.Integer,
        db.ForeignKey("states.id"),
        nullable=False
    )

    pincode = db.Column(
        db.String(10),
        nullable=True
    )

    latitude = db.Column(
        db.Float,
        nullable=True
    )

    longitude = db.Column(
        db.Float,
        nullable=True
    )

    # Contact
    official_website = db.Column(
        db.String(250),
        nullable=True
    )

    email = db.Column(
        db.String(150),
        nullable=True
    )

    phone = db.Column(
        db.String(20),
        nullable=True
    )

    # Rankings
    nirf_rank = db.Column(
        db.Integer,
        nullable=True,
        index=True
    )

    nirf_score = db.Column(
        db.Float,
        nullable=True
    )

    nirf_year = db.Column(
        db.Integer,
        nullable=True
    )

    state_rank = db.Column(
        db.Integer,
        nullable=True
    )

    naac_grade = db.Column(
        db.String(5),
        nullable=True
    )

    # Fees
    annual_fees_min = db.Column(
        db.Integer,
        nullable=True,
        index=True
    )

    annual_fees_max = db.Column(
        db.Integer,
        nullable=True
    )

    # Placements
    placement_percentage = db.Column(
        db.Float,
        nullable=True,
        index=True
    )

    avg_package_lpa = db.Column(
        db.Float,
        nullable=True
    )

    highest_package_lpa = db.Column(
        db.Float,
        nullable=True
    )

    top_recruiters = db.Column(
        db.Text,
        nullable=True
    )

    # Capacity
    total_seats = db.Column(
        db.Integer,
        nullable=True
    )

    intake_capacity = db.Column(
        db.Integer,
        nullable=True
    )

    # Hostel
    hostel_available = db.Column(
        db.Boolean,
        default=False
    )

    boys_hostel = db.Column(
        db.Boolean,
        default=False
    )

    girls_hostel = db.Column(
        db.Boolean,
        default=False
    )

    # Affiliation
    affiliated_university = db.Column(
        db.String(250),
        nullable=True
    )

    autonomous = db.Column(
        db.Boolean,
        default=False
    )

    # Media
    logo_url = db.Column(
        db.String(500),
        nullable=True
    )

    image_url = db.Column(
        db.String(500),
        nullable=True
    )

    # Meta
    description = db.Column(
        db.Text,
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    data_source = db.Column(
        db.String(50),
        nullable=True
    )

    last_updated = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # Relationships
    branches = db.relationship(
        "Branch",
        secondary=college_branch,
        backref="colleges",
        lazy="subquery"
    )

    facilities = db.relationship(
        "Facility",
        secondary=college_facility,
        backref="colleges",
        lazy="subquery"
    )

    courses = db.relationship(
        "Course",
        backref="college",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    def fees_display(self):

        if self.annual_fees_min and self.annual_fees_max:

            return f"₹{self.annual_fees_min:,} – ₹{self.annual_fees_max:,}/yr"

        elif self.annual_fees_min:

            return f"₹{self.annual_fees_min:,}/yr"

        return "Fee info not available"

    def to_dict(self):

        return {

            "id": self.id,

            "name": self.name,

            "short_name": self.short_name,

            "college_type": self.college_type,

            "state": self.state.name if self.state else None,

            "city": self.city.name if self.city else None,

            "nirf_rank": self.nirf_rank,

            "annual_fees_min": self.annual_fees_min,

            "annual_fees_max": self.annual_fees_max,

            "placement_percentage": self.placement_percentage,

            "avg_package_lpa": self.avg_package_lpa,

            "naac_grade": self.naac_grade,

            "hostel_available": self.hostel_available,

            "official_website": self.official_website,

            "branches": [
                b.name for b in self.branches
            ],
        }

    def __repr__(self):

        return f"<College {self.name}>"


# ═══════════════════════════════════════════════════════════════
# COURSE MODEL
# ═══════════════════════════════════════════════════════════════

class Course(db.Model):

    __tablename__ = "courses"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    college_id = db.Column(
        db.Integer,
        db.ForeignKey("colleges.id"),
        nullable=False
    )

    branch_id = db.Column(
        db.Integer,
        db.ForeignKey("branches.id"),
        nullable=True
    )

    name = db.Column(
        db.String(200),
        nullable=False
    )

    degree = db.Column(
        db.String(50),
        nullable=True
    )

    duration_years = db.Column(
        db.Integer,
        nullable=True
    )

    seats = db.Column(
        db.Integer,
        nullable=True
    )

    annual_fees = db.Column(
        db.Integer,
        nullable=True
    )

    cutoff_rank = db.Column(
        db.Integer,
        nullable=True
    )

    branch = db.relationship(
        "Branch",
        backref="courses"
    )

    def __repr__(self):

        return f"<Course {self.name}>"


# ═══════════════════════════════════════════════════════════════
# IMPORT LOG MODEL
# ═══════════════════════════════════════════════════════════════

class ImportLog(db.Model):

    __tablename__ = "import_logs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    filename = db.Column(
        db.String(250),
        nullable=False
    )

    source = db.Column(
        db.String(50),
        nullable=True
    )

    records_total = db.Column(
        db.Integer,
        default=0
    )

    records_added = db.Column(
        db.Integer,
        default=0
    )

    records_updated = db.Column(
        db.Integer,
        default=0
    )

    records_failed = db.Column(
        db.Integer,
        default=0
    )

    status = db.Column(
        db.String(20),
        default="pending"
    )

    error_message = db.Column(
        db.Text,
        nullable=True
    )

    imported_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    started_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    def __repr__(self):

        return f"<ImportLog {self.filename}>"