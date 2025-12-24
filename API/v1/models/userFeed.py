from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class UserFeedCreate(BaseModel):
    feedname: str
    stocks: List[str]
    sources: List[str]


class UserFeedUpdate(BaseModel):
    feedname: Optional[str] = None
    stocks: Optional[List[str]] = None
    sources: Optional[List[str]] = None


class UserFeedResponse(BaseModel):
    id: int
    user_id: int
    feedname: str
    stocks: List[str]
    sources: List[str]
    created_at: datetime

    class Config:
        from_atributes = True
