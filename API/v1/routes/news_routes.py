from fastapi import APIRouter, Query
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from models.newsResponse import NewsResponse
from models.newsArticle import NewsArticle
from ORM.newsArticleORM import NewsArticleORM
from services.retrieve_news import retrieve_news
from services.db_service.crud.news_insert import create_news_article
from services.db_service.crud.news_get import get_news_for_feed
from services.db_service.database import get_db
from fastapi import Depends
from services.auth_service.permission_checkers import require_permissions

router = APIRouter()


@router.get("/load-news",
            response_model=List[NewsArticle],
            dependencies=[require_permissions(["LOAD.NEWS"])])
def load_market_news(
    source: str = "market",
    symbols: Optional[List[str]] = Query(default=None),
    db: Session = Depends(get_db)
):
    articles: List[NewsArticleORM] = retrieve_news(source, symbols)

    for article in articles:
        create_news_article(article, db)

    articles = [NewsArticle.model_validate(
        a, from_attributes=True) for a in articles]

    return articles


@router.get("/get-news", response_model=List[NewsArticle])
def get_market_news(
    feedId: int,
    db: Session = Depends(get_db)
):
    news = get_news_for_feed(feedId, db)

    return news
