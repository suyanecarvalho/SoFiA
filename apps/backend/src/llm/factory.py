from .DummyLLM.dummy_llm import DummyLLM
from .LocalLLM.local_llm import LocalLLM
from .RemoteLLM.remote_llm import RemoteLLM
from .interface import LLMInterface
import os

def get_llm() -> LLMInterface:
    """
    Factory function to get the configured LLM instance.
    Reads the configuration from environment variables or a config file.
    """
    llm_type = os.getenv("LLM_TYPE", "dummy")

    if llm_type == "local":
        #TODO fix this after true implementation
        return LocalLLM()
    elif llm_type == "remote":
        #TODO fix this after true implementation
        return RemoteLLM()
    elif llm_type == "dummy":
        return DummyLLM()
    else:
        raise ValueError(f"Unknown LLM_TYPE: {llm_type}")
