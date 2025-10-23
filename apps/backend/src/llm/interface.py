from abc import ABC, abstractmethod
from typing import List
from apps.backend.src.db.schemas.transaction import Transaction

class LLMInterface(ABC):
    """
    An abstract interface for a self-contained LLM service.

    """

    @abstractmethod
    def get_nl_answer(self, prompt: str) -> str:
        """
        Processes a prompt and returns a complete, natural language answer.

        Args:
            prompt: The raw question from the user.

        Returns:
            A final, natural language string to be shown to the user.
        """
        pass

    @abstractmethod
    def get_structured_answer(self, prompt: str) -> List[Transaction]:
        """
        Processes a prompt to retrieve structured data from the database.
        This is the core data retrieval engine for benchmarking.

        Args:
            prompt: The raw question from the user.

        Returns:
            A list of Pydantic Transaction objects.
        """
        pass

    @abstractmethod
    def create_transaction_from_prompt(self, prompt: str) -> Transaction:
        """
        Parses a prompt, creates a new transaction, and saves it to the database.

        Args:
            prompt: The user's description of a transaction.

        Returns:
            The newly created Pydantic Transaction object, including its database-generated ID.
        """
        pass