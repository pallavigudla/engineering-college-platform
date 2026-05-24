"""
config.py — Application configuration classes
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:

    # Security
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-fallback-key"
    )

    WTF_CSRF_ENABLED = False
    WTF_CSRF_TIME_LIMIT = int(
        os.environ.get(
            "WTF_CSRF_TIME_LIMIT",
            3600
        )
    )

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20,
    }

    # Session
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SAMESITE = "Lax"

    REMEMBER_COOKIE_SECURE = False

    REMEMBER_COOKIE_DURATION = 86400 * 7

    # Uploads
    MAX_CONTENT_LENGTH = int(
        os.environ.get(
            "MAX_CONTENT_LENGTH",
            16 * 1024 * 1024
        )
    )

    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER",
        "uploads"
    )

    ALLOWED_EXTENSIONS = {"csv"}

    # Pagination
    COLLEGES_PER_PAGE = 12
    ADMIN_PER_PAGE = 20


class DevelopmentConfig(Config):

    DEBUG = True
    FLASK_ENV = "development"


class ProductionConfig(Config):

    DEBUG = False
    FLASK_ENV = "production"

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

    @classmethod
    def init_app(cls, app):

        db_url = os.environ.get(
            "DATABASE_URL",
            ""
        )

        if db_url.startswith("postgres://"):
            db_url = db_url.replace(
                "postgres://",
                "postgresql://",
                1
            )

        app.config[
            "SQLALCHEMY_DATABASE_URI"
        ] = db_url


class TestingConfig(Config):

    TESTING = True

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///:memory:"
    )

    WTF_CSRF_ENABLED = False

    SECRET_KEY = "test-secret-key"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}