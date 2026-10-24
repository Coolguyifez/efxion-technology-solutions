import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


class Config:

    # =====================================================
    # APPLICATION
    # =====================================================

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "efxion-development-secret-key"
    )

    # =====================================================
    # DATABASE
    # =====================================================

    INSTANCE_DIR = BASE_DIR / "instance"

    INSTANCE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    DATABASE_URL = os.environ.get(
        "DATABASE_URL"
    )

    if DATABASE_URL:

        # Supabase / Render may provide postgres://
        # SQLAlchemy uses postgresql://
        if DATABASE_URL.startswith(
            "postgres://"
        ):
            DATABASE_URL = DATABASE_URL.replace(
                "postgres://",
                "postgresql://",
                1
            )

        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    else:

        # Local fallback only.
        SQLALCHEMY_DATABASE_URI = (
            f"sqlite:///"
            f"{INSTANCE_DIR / 'efxion.db'}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =====================================================
    # DATABASE ENGINE SETTINGS
    # =====================================================

    if SQLALCHEMY_DATABASE_URI.startswith(
        "sqlite"
    ):

        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {
                "timeout": 30
            },
            "pool_pre_ping": True
        }

    else:

        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True
        }

    # =====================================================
    # RESUME UPLOADS
    # =====================================================

    UPLOAD_FOLDER = (
        INSTANCE_DIR
        / "uploads"
        / "resumes"
    )

    MAX_CONTENT_LENGTH = (
        5 * 1024 * 1024
    )

    ALLOWED_RESUME_EXTENSIONS = {
        "pdf",
        "doc",
        "docx"
    }

    # =====================================================
    # RESEND
    # =====================================================

    RESEND_API_KEY = os.environ.get(
        "RESEND_API_KEY"
    )

    RESEND_FROM_EMAIL = os.environ.get(
        "RESEND_FROM_EMAIL",
        "Efxion Technology Solutions <onboarding@resend.dev>"
    )

    ADMIN_RESET_TOKEN_EXPIRY_MINUTES = 60

    # =====================================================
    # INITIAL ADMIN SETUP
    # =====================================================

    ADMIN_SETUP_KEY = os.environ.get(
        "ADMIN_SETUP_KEY"
    )