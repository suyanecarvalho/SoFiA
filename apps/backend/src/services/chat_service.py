from sqlalchemy.orm import Session
from src.llm.factory import get_llm_instance
from src.llm.interface import LLMInterface


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.llm: LLMInterface = get_llm_instance("dummy")

    def process_user_message(self, message: str, model_preference: str = "dummy") -> str:
        """
        Core business logic for handling chat messages.

        Args:
            message: The raw user input.
            model_preference: Specific model strategy to use.

        Returns:
            str: The final response to show the user.
        """
        if model_preference != "dummy":
            self.llm = get_llm_instance(model_preference, identifier="placeholder_key_or_name")

        # 2. TODO: Intent Classification & Execution Logic
        # (This is where the logic explained below will be implemented)

        return "This is a stub response from the ChatService."