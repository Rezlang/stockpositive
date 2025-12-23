from sqlalchemy.orm import Session
from ORM.newsArticle import NewsArticle
from services.db_service.database import get_db
from fastapi import Depends


def create_news_article(article: NewsArticle, db: Session) -> NewsArticle:
    db.add(article)
    db.commit()
    db.refresh(article)
    return article
