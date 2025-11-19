from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from src.db.crud import crud_transaction, crud_category
from src.db.schemas import transaction as transaction_schema
from src.db.models import models


class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.category_crud = crud_category

    def create_transaction(
            self, user_id: int, transaction_data: transaction_schema.TransactionCreate
    ) -> models.Transaction:
        return crud_transaction.create_transaction(
            db=self.db, transaction=transaction_data, user_id=user_id
        )

    def get_transactions(
            self, filters: Dict[str, Any]
    ) -> List[models.Transaction]:
        """
        Maps dynamic filters from the LLM to the specific arguments
        required by the crud_transaction layer.
        """
        return crud_transaction.get_transactions(
            db=self.db,
            date_from=filters.get("date_from"),
            date_to=filters.get("date_to"),
            limit=filters.get("limit"),
            category_id=filters.get("category_id"),
            is_superfluous=filters.get("is_superfluous"),
            transaction_type=filters.get("transaction_type")
        )

    def get_category_by_name(self, name: str) -> Optional[models.Category]:
        """Finds a category by its exact name (case-insensitive)."""
        return self.category_crud.get_category_by_name(self.db, name)

    def get_all_category_names(self) -> List[str]:
        """Returns a list of all category names."""
        categories = self.category_crud.get_categories(self.db)
        return [cat.name for cat in categories]