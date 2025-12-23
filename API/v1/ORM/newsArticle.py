from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String, Text, DateTime
from pydantic import HttpUrl
from typing import List, Optional
from datetime import datetime


class NewsArticle(SQLModel, table=True):
    __tablename__ = "newsarticles"

    id: Optional[int] = Field(default=None, primary_key=True)

    title: Optional[str] = Field(
        default=None, sa_column=Column("title", Text, nullable=True))
    description: Optional[str] = Field(
        default=None, sa_column=Column("description", Text, nullable=True))
    content: Optional[str] = Field(
        default=None, sa_column=Column("content", Text, nullable=True))

    link: Optional[str] = Field(
        default=None, sa_column=Column("link", Text, nullable=True))
    imagelink: Optional[str] = Field(
        default=None, sa_column=Column("imagelink", Text, nullable=True))

    keywords: Optional[List[str]] = Field(
        default=None, sa_column=Column(ARRAY(Text), nullable=True))
    creator: Optional[List[str]] = Field(
        default=None, sa_column=Column(ARRAY(Text), nullable=True))
    symbol: Optional[List[str]] = Field(
        default=None, sa_column=Column(ARRAY(Text), nullable=True))

    pubdate: Optional[datetime] = Field(
        default=None, sa_column=Column("pubdate", DateTime, nullable=True))
    sourcename: Optional[str] = Field(
        default=None, sa_column=Column("sourcename", Text, nullable=True))
    sentiment: Optional[str] = Field(
        default=None, sa_column=Column("sentiment", Text, nullable=True))
    aisummary: Optional[str] = Field(
        default=None, sa_column=Column("aisummary", Text, nullable=True))
