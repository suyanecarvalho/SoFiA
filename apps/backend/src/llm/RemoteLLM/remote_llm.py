from typing import List, Optional

from apps.backend.src.llm.interface import LLMInterface
from apps.backend.src.db.models import models

#TODO implement RemoteLLM
class RemoteLLM(LLMInterface):
    """
    An interface for a remote, API-key based LLM (e.g., OpenAI, Groq).
    """
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_structured_answer(self, prompt: str) -> List[models.Transaction]:
        return []

    def create_transaction_from_prompt(self, prompt: str) -> None:
        return None

    def get_nl_answer(self, prompt: str) -> str:
        return ""