from .DummyLLM.dummy_llm import DummyLLM
from .LocalLLM.local_llm import LocalLLM
from .RemoteLLM.remote_llm import RemoteLLM
from .interface import LLMInterface


def get_llm_instance(model_type: str, identifier: str = None) -> LLMInterface:
    """
    Factory function to create an instance of an LLM based on its type and an identifier.

    Args:
        model_type (str): The type of model, e.g., 'local', 'remote', 'dummy'.
        identifier (str, optional): The specific model name for local LLMs,
                                    or the API key for remote LLMs.

    Returns:
        LLMInterface: An instantiated LLM class.
    """
    if model_type == "local":
        if not identifier:
            raise ValueError("A model name is required for local LLMs.")
        return LocalLLM(model_name=identifier)

    elif model_type == "remote":
        if not identifier:
            raise ValueError("An API key is required for remote LLMs.")
        return RemoteLLM(api_key=identifier)

    elif model_type == "dummy":
        return DummyLLM()

    else:
        raise ValueError(f"Unknown model type specified: {model_type}")
