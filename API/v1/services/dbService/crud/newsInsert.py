from sqlalchemy.orm import Session

from ORM.newsArticleORM import NewsArticleORM


def create_news_article(article: NewsArticleORM, db: Session) -> NewsArticleORM:
    db.add(article)
    db.commit()
    db.refresh(article)
    return article
