from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models.userFeed import UserFeed


class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone_number: Optional[str]


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    usergroup_id: int
    username: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]
    password: Optional[str]


class UserResponse(UserBase):
    id: int
    usergroup_id: int
    is_active: bool
    created_at: datetime
    permissions: List[str]

    class Config:
        from_atributes = True
