# database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path("/Users/joshmoskoff/Desktop/stockpositive/API/.env")
print(env_path)
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for ORM models
Base = declarative_base()

# Dependency for FastAPI routes


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test database connection


def test_connection():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("DATABASE CONNECTION OK")


# Run test on import (optional)
test_connection()
