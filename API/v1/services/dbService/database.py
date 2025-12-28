import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from sqlmodel import Session, create_engine, text


# Load environment variables
env_path = Path("/Users/joshmoskoff/Desktop/stockpositive/API/.env")
print(env_path)
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLModel engine (compatible with SQLAlchemy)
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=True)


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI routes - returns SQLModel Session"""
    with Session(engine) as session:
        yield session


def test_connection():
    """Test database connection"""
    with Session(engine) as session:
        session.exec(text("SELECT 1"))
    print("DATABASE CONNECTION OK")


# Run test on import (optional)
test_connection()
