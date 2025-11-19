from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """The intent string this tool handles (must match UserIntent enum value)"""
        pass

    @property
    @abstractmethod
    def schema(self) -> Dict[str, Any]:
        """The JSON schema to guide the LLM extraction"""
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any], user_id: int) -> Tuple[str, str]:
        """
        Executes the business logic.
        Returns: (System Context for LLM, Human Readable Action Description)
        """
        pass