from ORM.newsArticle import NewsArticle
from typing import List
from pydantic import BaseModel


class NewsResponse(BaseModel):
    status: str
    total_results: int
    results: List[NewsArticle]
