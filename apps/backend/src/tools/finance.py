import json
from typing import Dict, Any, Tuple, Optional
from pydantic import TypeAdapter
from src.core.logger import logger
from src.services.transaction_service import TransactionService
from src.tools.base import BaseTool
from src.utils.enums import UserIntent
from src.db.schemas import transaction as transaction_schema


class ExpenseTool(BaseTool):
    """Tool for creating expense transactions."""
    name = "expense"
    def __init__(self, service: TransactionService):
        self.service = service

    @property
    def schema(self) -> Dict[str, Any]:
        categories = self.service.get_all_category_names()
        return {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "integer",
                    "description": "The expense amount in CENTS. E.g., R$119.99 → 11999"
                },
                "description": {
                    "type": "string",
                    "description": "What was bought or paid for"
                },
                "category_name": {
                    "type": "string",
                    "enum": categories,
                    "description": "The expense category - must match one from the enum list"
                },
                "is_superfluous": {
                    "type": "boolean",
                    "description": "Is this a want/luxury (true) or a need (false)?"
                }
            },
            "required": ["amount", "description", "category_name"]
        }

    def get_extraction_prompt(
            self,
            message: str,
            partial: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate extraction prompt for expense data.
        Allows partial extraction without refusal logic.
        """
        categories = self.service.get_all_category_names()
        cat_list = "\n".join(f"  - {cat}" for cat in categories)
        partial_section = ""
        if partial:
            partial_section = f"\n\nALREADY COLLECTED DATA (Do not change these unless the user explicitly corrects them):\n{json.dumps(partial, indent=2, ensure_ascii=False)}\n"

        return f"""You are extracting structured data for an EXPENSE transaction.
            USER MESSAGE: "{message}"{partial_section}

            AVAILABLE CATEGORIES (Try to map to one of these, otherwise omit category):
            {cat_list}

            FIELDS TO EXTRACT:
            - amount (integer, in cents): E.g., R$119.99 → 11999.
            - description (string): What was bought.
            - category_name (string): Must match the list above exactly.
            - is_superfluous (boolean): True if the user implies it was unnecessary/impulsive ("didn't need it", "guilty", "expensive").

            INSTRUCTIONS:
            1. Extract ANY fields explicitly stated in the message.
            2. If a field is missing or unclear, OMIT it from the JSON.
            3. DO NOT return an error or refusal. Return partial JSON if necessary.
            4. If data was already collected, merge it with new info (new info takes precedence).

            EXAMPLES:

            Input: "Bought a dress for R$120 at Shein"
            Output: {{"amount": 12000, "description": "dress", "category_name": "Lazer & Entretenimento", "is_superfluous": false}}

            Input: "120 reais" (Context: description=makeup was already known)
            Output: {{"amount": 12000}}

            OUTPUT ONLY VALID JSON:"""

    def execute(self, params: Dict[str, Any], user_id: int) -> Tuple[str, str]:
        params["transaction_type"] = "expense"
        logger.info(f"Tool Executing: Expense", extra={"payload": params})
        cat_name = params.pop("category_name", None)
        if cat_name:
            category = self.service.get_category_by_name(cat_name)
            if category:
                params["category_id"] = category.id
            else:
                raise ValueError(f"Category '{cat_name}' not found in database.")
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
            "required": ["amount", "description"]
        }

    def get_extraction_prompt(
            self,
            message: str,
            partial: Optional[Dict[str, Any]] = None
    ) -> str:
        partial_section = ""
        if partial:
            partial_section = f"\n\nALREADY COLLECTED DATA:\n{json.dumps(partial, indent=2, ensure_ascii=False)}\n"

        return f"""You are extracting structured data for an INCOME transaction.
        USER MESSAGE: "{message}"{partial_section}

        FIELDS TO EXTRACT:
        - amount (integer, in cents): E.g., R$100.00 → 10000
        - description (string): Source (salary, gift, etc)

        INSTRUCTIONS:
        1. Extract ANY fields explicitly stated.
        2. If a field is missing, OMIT it from the JSON.
        3. DO NOT return an error or refusal. Return partial JSON.

        EXAMPLES:
        Input: "Received my salary"
        Output: {{"description": "salary"}}

        Input: "4500 reais"
        Output: {{"amount": 450000}}

        OUTPUT ONLY VALID JSON:"""

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
            "required": ["query"]
        }

    def get_extraction_prompt(self, message: str, **kwargs) -> str:
        return f"""Simple extraction - just return the query as-is.
        USER MESSAGE: "{message}"
        OUTPUT: {{"query": "{message}"}}"""

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