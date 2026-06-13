import os
from dotenv import load_dotenv

load_dotenv()


def normalize_database_url(database_url: str) -> str:
    """
    Render and some other hosts may provide postgres:// URLs.
    SQLAlchemy expects postgresql://.
    """
    if database_url and database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    return database_url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    raw_database_url = os.getenv("DATABASE_URL", "sqlite:///billchill.db")
    SQLALCHEMY_DATABASE_URI = normalize_database_url(raw_database_url)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "uploads"
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024