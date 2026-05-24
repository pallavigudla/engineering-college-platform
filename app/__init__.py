"""
app/__init__.py — Flask Application Factory
Uses the factory pattern for flexibility in testing and deployment.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

# ─── Extension instances (not yet bound to an app) ────────────
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()
migrate = Migrate()


def create_app(config_name="default"):
    """
    Application factory function.
    Creates and configures the Flask application.

    Args:
        config_name: One of 'development', 'production', 'testing', 'default'
    Returns:
        Configured Flask app instance
    """
    from config import config

    app = Flask(__name__)

    # ─── Load configuration ────────────────────────────────────
    app.config.from_object(config[config_name])

    # Run any class-level init (e.g. production URL fix)
    cfg = config[config_name]
    if hasattr(cfg, "init_app"):
        cfg.init_app(app)

    # ─── Initialize extensions ─────────────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    # ─── Register blueprints ───────────────────────────────────
    from app.blueprints.auth import auth_bp
    from app.blueprints.colleges import colleges_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.api import api_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(colleges_bp, url_prefix="/colleges")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    # ─── Register main routes ──────────────────────────────────
    from app.blueprints.main import main_bp
    app.register_blueprint(main_bp)

    # ─── Import models (ensures tables are registered) ─────────
    from app.models import (
        User, College, State, City, Branch,
        Facility, Course, Favorite, Comparison, ImportLog
    )

    # ─── Register template filters ─────────────────────────────
    from app.utils.helpers import register_template_filters
    register_template_filters(app)

    # ─── Register error handlers ───────────────────────────────
    register_error_handlers(app)

    # ─── Create DB tables if they don't exist ──────────────────
    with app.app_context():
        db.create_all()

    return app


def register_error_handlers(app):
    """Register custom error pages."""
    from flask import render_template

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500
