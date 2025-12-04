from typing import Optional
from pydantic import BaseModel, Field
import datetime


class UserBase(BaseModel):
    name: str
    profile_pic: Optional[str] = None
    api_key: Optional[str] = None


class UserCreate(UserBase):
    salary: Optional[int] = Field(None, description="Monthly salary in cents")
    payday: Optional[int] = Field(None, ge=1, le=31, description="Day of the month for salary receipt")


class UserUpdate(BaseModel):
    name: Optional[str] = None
    profile_pic: Optional[str] = None
    api_key: Optional[str] = None


class User(UserBase):
    id: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    salary_recurrence_id: Optional[int] = None

    class Config:
        from_attributes = True