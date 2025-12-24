from sqlalchemy import Column, Text, DateTime, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class NewsArticleORM(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    link = Column(Text, nullable=True)
    imagelink = Column(Text, nullable=True)
    keywords = Column(ARRAY(Text), nullable=True)
    creator = Column(ARRAY(Text), nullable=True)
    symbols = Column(ARRAY(Text), nullable=True)
    pubdate = Column(DateTime, nullable=True)
    sourcename = Column(Text, nullable=True)
    sentiment = Column(Text, nullable=True)
    aisummary = Column(Text, nullable=True)
