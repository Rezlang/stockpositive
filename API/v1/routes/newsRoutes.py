from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from models.newsArticle import NewsArticle
from models.newsResponse import PaginatedNewsResponse
from ORM.newsArticleORM import NewsArticleORM
from ORM.userORM import UserORM
from services.authService.authService import get_current_active_user
from services.authService.permissionCheckers import require_permissions
from services.dbService.crud.newsGet import get_news_for_feed
from services.dbService.crud.newsInsert import create_news_article
from services.dbService.database import get_db
from services.retrieveNews import retrieve_news


router = APIRouter()


@router.get(
    "/load-news",
    response_model=list[NewsArticle],
    dependencies=[require_permissions(["LOAD.NEWS"])],
)
def load_market_news(
    source: str = "market",
    symbols: list[str] | None = Query(default=None),
    db: Session = Depends(get_db),
):
    articles: list[NewsArticleORM] = retrieve_news(source, symbols)

    for article in articles:
        create_news_article(article, db)

    articles = [NewsArticle.model_validate(a, from_attributes=True) for a in articles]

    return articles


@router.get(
    "/get-news",
    response_model=PaginatedNewsResponse,
    dependencies=[require_permissions(["GET.NEWS"])],
)
def get_market_news(
    feedId: int,
    beforeDate: datetime | None = None,
    db: Session = Depends(get_db),
    currentUser: UserORM = Depends(get_current_active_user),
):
    return get_news_for_feed(feedId, db, currentUser.id, beforeDate)
