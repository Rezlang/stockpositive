from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String, DateTime
from sqlalchemy.sql import func
from pydantic import EmailStr
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column(
        "username", String(100), nullable=False, unique=True))
    email: EmailStr = Field(sa_column=Column(
        "email", String(255), nullable=False, unique=True))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column("created_at", DateTime,
                         server_default=func.now(), nullable=False)
    )
