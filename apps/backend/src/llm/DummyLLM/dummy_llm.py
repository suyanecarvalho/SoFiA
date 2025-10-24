from typing import List

from apps.backend.src.llm.interface import LLMInterface
from apps.backend.src.db.models import models

class DummyLLM(LLMInterface):
    """
    A minimal placeholder LLM for testing the benchmark.
    """
    def get_structured_answer(self, prompt: str) -> List[models.Transaction]:
        return []

    def create_transaction_from_prompt(self, prompt: str) -> None:
        return None

    def get_nl_answer(self, prompt: str) -> str:
        return ""