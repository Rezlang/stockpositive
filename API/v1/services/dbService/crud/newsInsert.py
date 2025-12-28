from sqlalchemy.orm import Session
from ORM.newsArticleORM import NewsArticleORM
from services.dbService.database import get_db
from fastapi import Depends


def create_news_article(article: NewsArticleORM, db: Session) -> NewsArticleORM:
    db.add(article)
    db.commit()
    db.refresh(article)
    return article
