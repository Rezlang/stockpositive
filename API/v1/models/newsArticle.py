from datetime import datetime

from pydantic import BaseModel


class NewsArticle(BaseModel):
    id: int | None
    title: str | None
    description: str | None
    content: str | None
    link: str | None
    imagelink: str | None
    keywords: list[str] | None
    creator: list[str] | None
    symbols: list[str] | None
    pubdate: datetime | None
    sourcename: str | None
    sentiment: str | None
    aisummary: str | None

    model_config = {"from_attributes": True}
