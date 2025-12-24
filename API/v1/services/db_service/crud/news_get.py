from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
from sqlalchemy import func
from ORM.userFeedORM import UserFeedORM
from ORM.newsArticleORM import NewsArticleORM
import re


def normalize_source_name(source_name: str) -> Optional[str]:
    """Remove special characters and convert to uppercase"""
    if not source_name:
        return None
    return re.sub(r'[^a-zA-Z0-9]', '', source_name.upper().strip())


def get_news_for_feed(feed_id: int, db: Session) -> List[NewsArticleORM]:
    feed: UserFeedORM = db.query(UserFeedORM).filter(
        UserFeedORM.id == feed_id).first()
    if not feed:
        raise HTTPException(
            status_code=404, detail=f"Feed with id {feed_id} not found")

    results: List[NewsArticleORM] = []

    symbols = feed.stocks or []
    sources = feed.sources or []

    for symbol in symbols:
        query = db.query(NewsArticleORM).filter(
            NewsArticleORM.symbols.contains([symbol])
        )

        if sources:
            normalized_sources = [normalize_source_name(s) for s in sources]
            query = query.filter(
                NewsArticleORM.sourcename.in_(normalized_sources))

        articles = query.order_by(
            NewsArticleORM.pubdate.desc()).limit(10).all()

        results.extend(articles)

    return results
