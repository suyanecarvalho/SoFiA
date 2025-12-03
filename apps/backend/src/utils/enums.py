import enum


class TransactionType(str, enum.Enum):
    EXPENSE = "expense"
    INCOME = "income"


class ChatRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class UserIntent(str, enum.Enum):
    EXPENSE = "expense"
    INCOME = "income"
    QUERY = "query"
    CHAT = "chat"

class ToolName(str, enum.Enum):
    """Tools that support multi-turn parameter collection."""
    EXPENSE = "expense"
    INCOME = "income"
    QUERY = "query"