from typing import Optional
from pydantic import BaseModel
import datetime


class UserBase(BaseModel):
    name: str
    profile_pic: Optional[str] = None
    api_key: Optional[str] = None
    salary: Optional[int] = None
    payday: Optional[int] = None


class UserCreate(UserBase):
    """Schema for creating a user."""

    pass


class UserUpdate(BaseModel):
    """Schema for updating a user (all fields optional)."""

    name: Optional[str] = None
    profile_pic: Optional[str] = None
    api_key: Optional[str] = None
    salary: Optional[int] = None
    payday: Optional[int] = None


class User(UserBase):
    """Schema for reading a user."""

    id: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True
