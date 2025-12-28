
from pydantic import BaseModel

from models.newsArticle import NewsArticle


class NewsResponse(BaseModel):
    status: str
    total_results: int
    results: list[NewsArticle]
