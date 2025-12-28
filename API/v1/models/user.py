from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import re


class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone_number: Optional[str]


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('password must be at least 8 characters long')
        if not any(c.isdigit() for c in v):
            raise ValueError('password must contain at least one digit')
        if not any(c.isupper() for c in v):
            raise ValueError('password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('password must contain at least one lowercase letter')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('password must contain at least one special character')
        return v


class UserUpdate(BaseModel):
    usergroup_id: int
    username: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]
    password: Optional[str]


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usergroup_id: int
    is_active: bool
    created_at: datetime
    permissions: dict[str, Optional[int]]
