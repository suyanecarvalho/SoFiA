from src.utils.enums import UserIntent

INTENT_DETECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": [e.value for e in UserIntent],
            "description": "Classify the user text. 'expense' for spending money, 'income' for receiving money, 'query' for asking about past data, 'chat' for everything else.",
        }
    },
    "required": ["intent"],
}

def get_expense_schema(category_names: list[str]) -> dict:
    return {
        "type": "object",
        "properties": {
            "amount": {
                "type": "integer",
                "description": "The expense amount in CENTS (integer). E.g., R$ 10,50 -> 1050. R$ 50 -> 5000.",
            },
            "description": {
                "type": "string",
                "description": "What was bought?",
            },
            "category_name": {
                "type": "string",
                "enum": category_names,
                "description": "Select the closest existing category.",
            },
            "is_superfluous": {
                "type": "boolean",
                "description": "Is this a need (False) or a want (True)?",
            },
        },
        "required": ["amount", "description", "category_name"],
    }

INCOME_SCHEMA = {
    "type": "object",
    "properties": {
        "amount": {
            "type": "integer",
            "description": "The income amount in CENTS (integer). E.g., R$ 100,00 -> 10000.",
        },
        "description": {
            "type": "string",
            "description": "Source of income.",
        },
    },
    "required": ["amount", "description"],
}

QUERY_SCHEMA = {
    "type": "object",
    "properties": {
        "date_from": {
            "type": "string",
            "format": "date",
            "description": "YYYY-MM-DD",
        },
        "date_to": {
            "type": "string",
            "format": "date",
            "description": "YYYY-MM-DD",
        },
        "limit": {
            "type": "integer",
            "description": "Number of items to retrieve",
        },
    },
}