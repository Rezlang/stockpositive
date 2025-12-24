from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from ORM.newsArticleORM import NewsArticleORM


class NewsArticle(BaseModel):
    id: Optional[int]
    title: Optional[str]
    description: Optional[str]
    content: Optional[str]
    link: Optional[str]
    imagelink: Optional[str]
    keywords: Optional[List[str]]
    creator: Optional[List[str]]
    symbols: Optional[List[str]]
    pubdate: Optional[datetime]
    sourcename: Optional[str]
    sentiment: Optional[str]
    aisummary: Optional[str]

    model_config = {
        "from_attributes": True
    }
