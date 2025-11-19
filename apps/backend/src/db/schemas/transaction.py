import datetime

from pydantic import BaseModel, Field
from typing import Optional, Union, Literal, Annotated
from src.utils.enums import TransactionType


class TransactionCore(BaseModel):
    amount: Annotated[
        int,
        Field(gt=0, description="The transaction amount in cents (always positive)"),
    ]
    description: str


class ExpenseCreate(TransactionCore):
    transaction_type: Literal[TransactionType.EXPENSE] = TransactionType.EXPENSE
    category_id: int
    is_superfluous: bool = False


class IncomeCreate(TransactionCore):
    transaction_type: Literal[TransactionType.INCOME] = TransactionType.INCOME
    category_id: Literal[None] = None
    is_superfluous: Literal[None] = None


TransactionCreate = Annotated[
    Union[ExpenseCreate, IncomeCreate], Field(discriminator="transaction_type")
]


class Transaction(TransactionCore):
    id: int
    transaction_type: TransactionType
    category_id: Optional[int] = None
    is_superfluous: Optional[bool] = None
    user_id: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True
