"""
Centralized database configuration.

Why this exists:
- Single source of truth for connection details
- Easy to swap between local Postgres and cloud (GCP CloudSQL, AWS RDS) later
- All scripts import from here instead of duplicating connection logic
- Connection pooling configured once, used everywhere
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

load_dotenv(override=False)


def get_database_url() -> str:
    """Build the PostgreSQL connection URL from environment variables."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")

    if not user or not db_name:
        raise EnvironmentError(
            "DB_USER and DB_NAME must be set in .env file"
        )

    if password:
        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    return f"postgresql://{user}@{host}:{port}/{db_name}"


def get_engine() -> Engine:
    """Return a SQLAlchemy engine with connection pooling."""
    return create_engine(
        get_database_url(),
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=False,
    )
