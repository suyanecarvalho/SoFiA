from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.backend.src.db.crud import crud_transaction
from apps.backend.src.db.schemas import transaction as transaction_schema
from apps.backend.src.db.database.connection import get_db

router = APIRouter()


@router.post("/", response_model=transaction_schema.Transaction)
def create_new_transaction(
        transaction: transaction_schema.TransactionCreate,
        db: Session = Depends(get_db)
):
    """
    Create a new transaction.
    """
    return crud_transaction.create_transaction(db=db, transaction=transaction)


@router.get("/", response_model=List[transaction_schema.Transaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all transactions.
    """
    transactions = crud_transaction.get_transactions(db, skip=skip, limit=limit)
    return transactions
