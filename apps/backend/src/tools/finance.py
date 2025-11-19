from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from pydantic import TypeAdapter

from src.tools.base import BaseTool
from src.services.transaction_service import TransactionService
from src.db.crud import crud_category
from src.db.schemas import transaction as transaction_schema
from src.utils.enums import UserIntent
from src.core.logger import logger

class ExpenseTool(BaseTool):
    def __init__(self, db: Session, service: TransactionService):
        self.db = db
        self.service = service

    @property
    def name(self) -> str:
        return UserIntent.EXPENSE.value

    @property
    def schema(self) -> Dict[str, Any]:
        db_categories = crud_category.get_categories(self.db, limit=100)
        category_names = [c.name for c in db_categories] if db_categories else []

        return {
            "type": "object",
            "properties": {
                "amount": {"type": "integer", "description": "The expense amount in CENTS. E.g., 1050."},
                "description": {"type": "string", "description": "What was bought?"},
                "category_name": {"type": "string", "enum": category_names, "description": "Select the closest existing category."},
                "is_superfluous": {"type": "boolean", "description": "Is this a need (False) or a want (True)?"},
            },
            "required": ["amount", "description", "category_name"],
        }

    def execute(self, params: Dict[str, Any], user_id: int) -> Tuple[str, str]:
        params["transaction_type"] = "expense"
        cat_name = params.pop("category_name", None)
        if cat_name:
            categories = crud_category.get_categories(self.db, name_contains=cat_name)
            for cat in categories:
                if cat.name.lower() == cat_name.lower():
                    params["category_id"] = cat.id
                    break
            if "category_id" not in params and categories:
                params["category_id"] = categories[0].id
        logger.info(f"Tool Executing: Expense", extra={"payload": params})
        adapter = TypeAdapter(transaction_schema.TransactionCreate)
        validated_data = adapter.validate_python(params)
        tx = self.service.create_transaction(user_id=user_id, transaction_data=validated_data)

        return (
            f"System: Successfully created expense ID {tx.id}.",
            f"Created Expense: {tx.description} (R$ {tx.amount / 100:.2f})"
        )


class IncomeTool(BaseTool):
    def __init__(self, service: TransactionService):
        self.service = service

    @property
    def name(self) -> str:
        return UserIntent.INCOME.value

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "amount": {"type": "integer", "description": "Income amount in CENTS."},
                "description": {"type": "string", "description": "Source of income."},
            },
            "required": ["amount", "description"],
        }

    def execute(self, params: Dict[str, Any], user_id: int) -> Tuple[str, str]:
        params["transaction_type"] = "income"
        params["category_id"] = None
        params["is_superfluous"] = None

        logger.info(f"Tool Executing: Income", extra={"payload": params})

        adapter = TypeAdapter(transaction_schema.TransactionCreate)
        validated_data = adapter.validate_python(params)
        tx = self.service.create_transaction(user_id=user_id, transaction_data=validated_data)

        return (
            f"System: Successfully created income ID {tx.id}.",
            f"Created Income: {tx.description} (R$ {tx.amount / 100:.2f})"
        )


class QueryTool(BaseTool):
    def __init__(self, service: TransactionService):
        self.service = service

    @property
    def name(self) -> str:
        return UserIntent.QUERY.value

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "date_from": {"type": "string", "format": "date"},
                "date_to": {"type": "string", "format": "date"},
                "limit": {"type": "integer"},
            },
        }

    def execute(self, params: Dict[str, Any], user_id: int) -> Tuple[str, str]:
        logger.info(f"Tool Executing: Query", extra={"payload": params})
        results = self.service.get_transactions(filters=params)

        if not results:
            return "System: No transactions found.", "Query executed (0 results)"

        summary_lines = []
        for tx in results:
            t_type = getattr(tx, "transaction_type", "transaction")
            summary_lines.append(f"- {tx.created_at}: {tx.description} (R$ {tx.amount / 100:.2f}) [{t_type}]")

        return (
            "System: Found the following transactions:\n" + "\n".join(summary_lines),
            f"Retrieved {len(results)} transactions"
        )