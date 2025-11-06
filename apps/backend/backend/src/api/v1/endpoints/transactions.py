from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import datetime

from ....db.crud import crud_transaction
from ....db.schemas import transaction as transaction_schema
from ....db.database.connection import get_db

router = APIRouter()


@router.post("/", response_model=transaction_schema.Transaction)
def create_new_transaction(
    transaction: transaction_schema.TransactionCreate, db: Session = Depends(get_db)
):
    """
    Create a new transaction.
    """
    return crud_transaction.create_transaction(db=db, transaction=transaction)


@router.get("/", response_model=List[transaction_schema.Transaction])
def read_transactions(
    skip: int = 0,
    limit: int = 100,
    date_from: Optional[datetime.date] = None,
    date_to: Optional[datetime.date] = None,
    category_id: Optional[int] = None,
    is_superfluous: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """
    Retrieve transactions.
    """
    transactions = crud_transaction.get_transactions(
        db,
        skip=skip,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
        category_id=category_id,
        is_superfluous=is_superfluous,
    )
    return transactions
