import datetime
from typing import Optional

from sqlalchemy.orm import Session
from ..schemas import transaction as transaction_schema
from ..models import models


def get_transaction(db: Session, transaction_id: int):
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.id == transaction_id)
        .first()
    )


def get_transactions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    date_from: Optional[datetime.date] = None,
    date_to: Optional[datetime.date] = None,
    category_id: Optional[int] = None,
    is_superfluous: Optional[bool] = None,
):
    """
    Retrieve transactions with optional filtering.
    """
    query = db.query(models.Transaction)
    if date_from:
        query = query.filter(models.Transaction.created_at >= date_from)
    if date_to:
        query = query.filter(
            models.Transaction.created_at < (date_to + datetime.timedelta(days=1))
        )
    if category_id is not None:
        query = query.filter(models.Transaction.category_id == category_id)
    if is_superfluous is not None:
        query = query.filter(models.Transaction.is_superfluous == is_superfluous)

    return query.offset(skip).limit(limit).all()


def create_transaction(
    db: Session, transaction: transaction_schema.TransactionCreate
) -> models.Transaction:
    db_transaction = models.Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction
