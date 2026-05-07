import os
from dotenv import load_dotenv
from datetime import timedelta, timezone

load_dotenv()

class DefaultConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_TIME_LIMIT = None

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=int(os.getenv("SESSION_LIFETIME_MINUTES", 2))
    )

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"
    SESSION_COOKIE_SAMESITE = "Lax"

    TIMEZONE = timezone(timedelta(hours=int(os.getenv("TIMEZONE_OFFSET", -4))))

    IGNORED_ROUTES = [
        "auth.session_status",
        "auth.refresh_session",
        "auth.auto_logout"
    ]
