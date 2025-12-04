from pydantic import BaseModel, Field
from src.utils.enums import RecurrenceFrequency

class RecurrentTransactionBase(BaseModel):
    recurrence_day: int = Field(..., ge=1, le=31, description="Day of the month to execute")
    frequency: RecurrenceFrequency = RecurrenceFrequency.MONTHLY

class RecurrentTransactionCreate(RecurrentTransactionBase):
    base_transaction_id: int

class RecurrentTransactionRead(RecurrentTransactionBase):
    id: int
    user_id: int
    base_transaction_id: int
    is_active: bool

    class Config:
        from_attributes = True