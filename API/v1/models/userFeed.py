from pydantic import BaseModel
from typing import List
from datetime import datetime


class UserFeed(BaseModel):
    id: int
    user_id: int
    feedname: str
    stocks: List[str]
    sources: List[str]
    created_at: datetime

    class Config:
        from_atributes = True
