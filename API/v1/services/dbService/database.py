import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from sqlmodel import Session, create_engine, text


# Load environment variables
# Try to find .env file, but don't fail if it doesn't exist (for CI/testing)
# Go up from database.py -> dbService -> services -> v1 -> API -> project root -> API/.env
env_path = Path(__file__).parent.parent.parent.parent.parent / "API" / ".env"
if env_path.exists():
    print(env_path)
    load_dotenv(dotenv_path=env_path)
else:
    # For CI or other environments, just load from environment
    load_dotenv()

# Check TEST_DATABASE_URL first (for tests), then DATABASE_URL
DATABASE_URL = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL or TEST_DATABASE_URL must be set in environment variables or .env file"
    )

# Create SQLModel engine (compatible with SQLAlchemy)
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=True)


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI routes - returns SQLModel Session"""
    with Session(engine) as session:
        yield session


def test_connection():
    """Test database connection"""
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
        print("DATABASE CONNECTION OK")
    except Exception as e:
        print(f"DATABASE CONNECTION WARNING: {e}")
        # Don't fail on import if DB is not available (e.g., during CI setup)


# Run test on import (optional, won't fail if DB unavailable)
test_connection()
