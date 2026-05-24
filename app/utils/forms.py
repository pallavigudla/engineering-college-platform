"""
app/utils/forms.py — WTForms definitions with CSRF protection
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, IntegerField, FloatField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange, ValidationError
from flask_wtf.file import FileField, FileAllowed


# ═══════════════════════════════════════════════════════════════
# AUTH FORMS
# ═══════════════════════════════════════════════════════════════

class SignupForm(FlaskForm):
    """Student registration form."""
    full_name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(min=2, max=120)]
    )
    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email(), Length(max=150)]
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8, max=128)]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")]
    )

    def validate_email(self, field):
        from app.models import User
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("This email is already registered. Please login.")


class LoginForm(FlaskForm):
    """Login form."""
    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )
    remember_me = BooleanField("Remember Me")


# ═══════════════════════════════════════════════════════════════
# SEARCH FORM
# ═══════════════════════════════════════════════════════════════

class CollegeSearchForm(FlaskForm):
    """College search and filter form."""
    class Meta:
        csrf = False  # GET form — CSRF not needed

    query       = StringField("Search by name", validators=[Optional()])
    state       = SelectField("State", choices=[("", "All States")], validators=[Optional()])
    branch      = SelectField("Branch", choices=[("", "All Branches")], validators=[Optional()])
    college_type = SelectField(
        "Type",
        choices=[
            ("", "All Types"),
            ("Government", "Government"),
            ("Private", "Private"),
            ("Deemed", "Deemed"),
            ("Autonomous", "Autonomous"),
        ],
        validators=[Optional()],
    )
    nirf_rank_max   = IntegerField("NIRF Rank (up to)", validators=[Optional(), NumberRange(min=1)])
    fees_max        = IntegerField("Max Annual Fees (₹)", validators=[Optional(), NumberRange(min=0)])
    placement_min   = FloatField("Min Placement %", validators=[Optional(), NumberRange(min=0, max=100)])
    hostel          = BooleanField("Hostel Available")
    sort_by         = SelectField(
        "Sort By",
        choices=[
            ("nirf_rank", "NIRF Rank"),
            ("placement_percentage", "Placement %"),
            ("annual_fees_min", "Fees (Low to High)"),
            ("name", "Name A-Z"),
        ],
        validators=[Optional()],
    )


# ═══════════════════════════════════════════════════════════════
# ADMIN FORMS
# ═══════════════════════════════════════════════════════════════

class CSVUploadForm(FlaskForm):
    """CSV dataset upload form for admin."""
    csv_file = FileField(
        "CSV Dataset File",
        validators=[
            DataRequired(),
            FileAllowed(["csv"], "Only .csv files are allowed!"),
        ],
    )
    source = SelectField(
        "Data Source",
        choices=[
            ("NIRF", "NIRF Rankings"),
            ("AICTE", "AICTE Approved List"),
            ("JOSAA", "JoSAA Counseling Data"),
            ("AP_EAMCET", "AP EAMCET Data"),
            ("TS_EAMCET", "TS EAMCET Data"),
            ("MANUAL", "Manual Dataset"),
        ],
        validators=[DataRequired()],
    )
    mode = SelectField(
        "Import Mode",
        choices=[
            ("upsert", "Insert & Update (Recommended)"),
            ("insert_only", "Insert New Only"),
        ],
        validators=[DataRequired()],
    )
