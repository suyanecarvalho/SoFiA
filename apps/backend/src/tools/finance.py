import json
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from pydantic import TypeAdapter
from src.core.logger import logger
from src.services.transaction_service import TransactionService
from src.tools.base import BaseTool
from src.utils.enums import UserIntent
from src.db.schemas import transaction as transaction_schema


class ExpenseTool(BaseTool):
    name = "expense"
    def __init__(self, service: TransactionService):
        self.service = service

    @property
    def schema(self) -> Dict[str, Any]:
        categories = self.service.get_all_category_names()
        return {
            "type": "object",
            "properties": {
                "amount": {"type": "integer", "description": "Amount in CENTS"},
                "description": {"type": "string"},
                "category_name": {"type": "string", "enum": categories},
                "is_superfluous": {"type": "boolean"}
            },
            "required": ["amount", "description", "category_name"]
        }

    def get_extraction_prompt(self, message: str, partial: Optional[Dict[str, Any]] = None) -> str:
        categories = self.service.get_all_category_names()
        cat_list = "\n".join(f"  - {cat}" for cat in categories)
        partial_str = f"\nPrevious data: {json.dumps(partial)}" if partial else ""

        return f"""Extract EXPENSE data. User: "{message}"{partial_str}

        AVAILABLE CATEGORIES:
        {cat_list}

        Schema:
        - amount (int cents)
        - description (string)
        - category_name (exact match)
        - is_superfluous (bool)

        Extract known fields. Omit unknown. No JSON markdown.
        """

    def execute(self, params: Dict[str, Any], user_id: int) -> Tuple[str, str]:
        params["transaction_type"] = "expense"
        logger.info(f"Tool Executing: Expense", extra={"payload": params})

        cat_name = params.pop("category_name", None)
        if cat_name:
            category = self.service.get_category_by_name(cat_name)
            if category:
                params["category_id"] = category.id

        adapter = TypeAdapter(transaction_schema.TransactionCreate)
        validated_data = adapter.validate_python(params)
        tx = self.service.create_transaction(user_id=user_id, transaction_data=validated_data)
        return (
            f"Expense created: {tx.description} (R$ {tx.amount / 100:.2f})",
            f"Created Expense: {tx.description}"
        )


class IncomeTool(BaseTool):
    name = "income"
    def __init__(self, service: TransactionService):
        self.service = service

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "amount": {"type": "integer"},
                "description": {"type": "string"},
            },
            "required": ["amount", "description"]
        }

    def get_extraction_prompt(self, message: str, partial: Optional[Dict[str, Any]] = None) -> str:
        partial_str = f"\nPrevious data: {json.dumps(partial)}" if partial else ""
        return f"""Extract INCOME data. User: "{message}"{partial_str}
        Schema: amount (int cents), description (string).
        Extract known fields. Omit unknown. No JSON markdown."""

    def execute(self, params: Dict[str, Any], user_id: int) -> Tuple[str, str]:
        params["transaction_type"] = "income"
        params["category_id"] = None
        params["is_superfluous"] = None
        logger.info(f"Tool Executing: Income", extra={"payload": params})
        adapter = TypeAdapter(transaction_schema.TransactionCreate)
        validated_data = adapter.validate_python(params)
        tx = self.service.create_transaction(user_id=user_id, transaction_data=validated_data)
        return (
            f"Income created: {tx.description} (R$ {tx.amount / 100:.2f})",
            f"Created Income: {tx.description}"
        )


class QueryTool(BaseTool):
    """Smart Query Tool that filters transactions."""
    def __init__(self, service: TransactionService):
        self.service = service

    @property
    def name(self) -> str:
        return UserIntent.QUERY.value

    @property
    def schema(self) -> Dict[str, Any]:
        categories = self.service.get_all_category_names()
        return {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "format": "date", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "format": "date", "description": "YYYY-MM-DD"},
                "is_superfluous": {"type": "boolean"},
                "category_name": {"type": "string", "enum": categories},
                "limit": {"type": "integer"},
                "transaction_type": {"type": "string", "enum": ["expense", "income"]}
            },
            "required": []
        }

    def get_extraction_prompt(self, message: str, partial: Optional[Dict[str, Any]] = None) -> str:
        """
        Instructs LLM to convert natural language time and categories into filters.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        categories = self.service.get_all_category_names()
        cat_list = "\n".join(f"  - {cat}" for cat in categories)
        partial_str = f"\nPrevious data: {json.dumps(partial)}" if partial else ""

        return f"""You are a query parser for a finance DB.
        TODAY IS: {today}

        USER QUERY: "{message}"{partial_str}

        AVAILABLE CATEGORIES (Exact match required):
        {cat_list}

        YOUR TASK: Convert natural language requirements into JSON filters.

        FIELDS:
        - start_date (YYYY-MM-DD): derived from "this month", "last week".
        - end_date (YYYY-MM-DD): derived from "until now", "yesterday".
        - category_name (string): MUST be one of the available categories.
        - is_superfluous (boolean): true if user asks for "unnecessary" money.
        - transaction_type (string): 'expense' or 'income' if specified.
        - limit (int): default 5 if unspecified.

        EXAMPLES:
        "How much spent on Food this month?" -> {{"start_date": "2024-05-01", "end_date": "2024-05-15", "category_name": "Alimentação", "transaction_type": "expense"}}
        "Show superfluous expenses" -> {{"is_superfluous": true, "transaction_type": "expense"}}

        OUTPUT VALID JSON ONLY. Omit keys if not mentioned.
        """

    def execute(self, params: Dict[str, Any], user_id: int) -> Tuple[str, str]:
        logger.info(f"QueryTool executing with params: {json.dumps(params, ensure_ascii=False)}")
        filters = {}
        if "start_date" in params:
            try:
                filters["date_from"] = datetime.strptime(params["start_date"], "%Y-%m-%d").date()
            except ValueError:
                logger.warning(f"Invalid start_date format: {params['start_date']}")

        if "end_date" in params:
            try:
                filters["date_to"] = datetime.strptime(params["end_date"], "%Y-%m-%d").date()
            except ValueError:
                logger.warning(f"Invalid end_date format: {params['end_date']}")
        if "is_superfluous" in params: filters["is_superfluous"] = params["is_superfluous"]
        if "transaction_type" in params: filters["transaction_type"] = params["transaction_type"]
        cat_name = params.get("category_name")
        if cat_name:
            category = self.service.get_category_by_name(cat_name)
            if category:
                filters["category_id"] = category.id
                logger.info(f"Mapped category '{cat_name}' to ID {category.id}")
        logger.info(f"🔎 DB Filters: {filters}")
        results = self.service.get_transactions(filters=filters)
        if not results:
            return "No transactions found matching those criteria.", "Query (0 results)"
        total = sum(t.amount for t in results)
        summary_lines = []
        for tx in results:
            summary_lines.append(f"- {tx.created_at.strftime('%d/%m')}: {tx.description} (R$ {tx.amount / 100:.2f})")
        full_text = f"Found {len(results)} transactions. Total: R$ {total/100:.2f}.\nDetails:\n" + "\n".join(summary_lines)
        return full_text, f"Query ({len(results)} results)"