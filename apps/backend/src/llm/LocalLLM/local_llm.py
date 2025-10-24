from typing import List, Optional

from apps.backend.src.llm.interface import LLMInterface
from apps.backend.src.db.models import models

#TODO implement LocalLLM
class LocalLLM(LLMInterface):
    """
    An interface for a locally-run LLM (e.g., via Ollama).
    """
    def __init__(self, model_name: str):
        self.model_name = model_name

    def get_structured_answer(self, prompt: str) -> List[models.Transaction]:
        return []

    def create_transaction_from_prompt(self, prompt: str) -> None:
        return None

    def get_nl_answer(self, prompt: str) -> str:
        return ""