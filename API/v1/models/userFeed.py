from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class UserFeedCreate(BaseModel):
    feedname: str
    stocks: list[str]
    sources: list[str]

    @field_validator("feedname")
    @classmethod
    def feedname_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("feedname cannot be empty")
        return v

    @field_validator("stocks")
    @classmethod
    def stocks_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("stocks list cannot be empty")
        return v

    @field_validator("sources")
    @classmethod
    def sources_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("sources list cannot be empty")
        return v


class UserFeedUpdate(BaseModel):
    feedname: str | None = None
    stocks: list[str] | None = None
    sources: list[str] | None = None


class UserFeedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    feedname: str
    stocks: list[str]
    sources: list[str]
    created_at: datetime
