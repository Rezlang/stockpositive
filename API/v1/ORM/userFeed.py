from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from typing import List, Optional
from datetime import datetime


class UserFeed(SQLModel, table=True):
    __tablename__ = "userfeeds"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(sa_column=Column("user_id", Integer, nullable=False))
    feedname: str = Field(sa_column=Column(
        "feedname", String(100), nullable=False))
    stocks: List[str] = Field(sa_column=Column("stocks", JSON, nullable=False))
    sources: List[str] = Field(
        sa_column=Column("sources", JSON, nullable=False))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            "created_at", DateTime, server_default=func.now(), nullable=False
        ),
    )
