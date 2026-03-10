from datetime import datetime

from pydantic import BaseModel

from models.newsArticle import NewsArticle


class NewsResponse(BaseModel):
    status: str
    total_results: int
    results: list[NewsArticle]


class PaginatedNewsResponse(BaseModel):
    articles: list[NewsArticle]
    next_cursor: datetime | None  # pubdate of last article for pagination
    has_more: bool
    total_returned: int
