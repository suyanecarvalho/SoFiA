from pydantic import BaseModel, Field
from typing import Optional
import datetime

class TransactionBase(BaseModel):
    amount: int = Field(..., description="The transaction amount in cents")
    description: str
    category_id: int
    is_superfluous: bool = False

class TransactionCreate(TransactionBase):
    user_id: int = 1

class Transaction(TransactionBase):
    id: int
    user_id: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True