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

        Args:
            message: User's input message
            partial: Previously collected parameters (for multi-turn)
        """
        categories = self.service.get_all_category_names()
        cat_list = "\n".join(f"  - {cat}" for cat in categories)
        partial_section = ""
        if partial:
            partial_section = f"\n\nALREADY COLLECTED IN PREVIOUS MESSAGES:\n{json.dumps(partial, indent=2, ensure_ascii=False)}\n"
        return f"""You are extracting structured data for an EXPENSE transaction (money spent).
            USER MESSAGE: "{message}"{partial_section}
            
            AVAILABLE CATEGORIES (you MUST choose exactly one from this list):
            {cat_list}
            
            REQUIRED FIELDS:
            - amount (integer, in cents): Must be explicitly stated by user. 
              Conversion examples: R$119.99 → 11999, R$50 → 5000, 150 reais → 15000
            - description (string): What was purchased or paid for
            - category_name (string): MUST be one of the categories listed above (exact match)
            - is_superfluous (boolean): Only true if user explicitly indicates this is unnecessary/impulsive/a want
            
            STRICT EXTRACTION RULES:
            1. If amount is NOT explicitly stated or unclear → {{"refusal_reason": "missing_amount"}}
            2. If you cannot confidently map to a category from the list → {{"refusal_reason": "missing_category"}}
            3. If description is missing or unclear → {{"refusal_reason": "missing_description"}}
            4. NEVER guess or estimate values
            5. If already collected data exists, extract ONLY the new fields from current message
            
            EXAMPLES:
            
            Input: "Bought a dress for R$120 at Shein"
            Output: {{"amount": 12000, "description": "dress", "category_name": "Lazer & Entretenimento", "is_superfluous": false}}
            
            Input: "It was at Shein and I feel bad because I have too many"
            Output: {{"refusal_reason": "missing_amount"}}
            
            Input: "120 reais" (with partial context: {{"description": "dress", "is_superfluous": true}})
            Output: {{"amount": 12000}}
            
            Input: "Yesterday I bought makeup"
            Output: {{"refusal_reason": "missing_amount"}}
            
            OUTPUT ONLY VALID JSON (no markdown, no explanations):"""

    def execute(self, params: Dict[str, Any], user_id: int) -> Tuple[str, str]:
        params["transaction_type"] = "expense"
        logger.info(f"Tool Executing: Expense", extra={"payload": params})
        cat_name = params.pop("category_name", None)
        if cat_name:
            category = self.service.get_category_by_name(cat_name)
            if category:
                params["category_id"] = category.id
            else:
                raise ValueError(f"Category '{cat_name}' not found.")
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
        """
        Generate extraction prompt for income data.

        Args:
            message: User's input message
            partial: Previously collected parameters (for multi-turn)
        """
        partial_section = ""
        if partial:
            partial_section = f"\n\nALREADY COLLECTED IN PREVIOUS MESSAGES:\n{json.dumps(partial, indent=2, ensure_ascii=False)}\n"

        return f"""You are extracting structured data for an INCOME transaction (money received).

        USER MESSAGE: "{message}"{partial_section}
        
        REQUIRED FIELDS:
        - amount (integer, in cents): Must be explicitly stated by user.
          Conversion examples: R$4500 → 450000, R$150 → 15000, 1000 reais → 100000
        - description (string): Source of the money (salary, payment, gift, sale, etc)
        
        STRICT EXTRACTION RULES:
        1. If amount is NOT explicitly stated or unclear → {{"refusal_reason": "missing_amount"}}
        2. If description is missing or unclear → {{"refusal_reason": "missing_description"}}
        3. NEVER guess or estimate values
        4. If already collected data exists, extract ONLY the new fields from current message
        
        EXAMPLES:
        
        Input: "Received my salary of R$4500"
        Output: {{"amount": 450000, "description": "salary"}}
        
        Input: "Got a birthday gift"
        Output: {{"refusal_reason": "missing_amount"}}
        
        Input: "4500 reais" (with partial context: {{"description": "salary"}})
        Output: {{"amount": 450000}}
        
        Input: "I received money yesterday"
        Output: {{"refusal_reason": "missing_amount"}}
        
        OUTPUT ONLY VALID JSON (no markdown, no explanations):"""

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
        """Query tool doesn't need extraction - just passes through the message."""
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