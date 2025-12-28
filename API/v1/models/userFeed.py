from pydantic import BaseModel, field_validator, ConfigDict
from typing import List, Optional
from datetime import datetime


class UserFeedCreate(BaseModel):
    feedname: str
    stocks: List[str]
    sources: List[str]

    @field_validator('feedname')
    @classmethod
    def feedname_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('feedname cannot be empty')
        return v

    @field_validator('stocks')
    @classmethod
    def stocks_not_empty(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError('stocks list cannot be empty')
        return v

    @field_validator('sources')
    @classmethod
    def sources_not_empty(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError('sources list cannot be empty')
        return v


class UserFeedUpdate(BaseModel):
    feedname: Optional[str] = None
    stocks: Optional[List[str]] = None
    sources: Optional[List[str]] = None


class UserFeedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    feedname: str
    stocks: List[str]
    sources: List[str]
    created_at: datetime
