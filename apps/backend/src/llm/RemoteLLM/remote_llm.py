import json
from typing import List, Dict, Any
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from src.llm.interface import LLMInterface, LLMMessage
from src.core.logger import logger


class RemoteLLM(LLMInterface):
    """
    An interface for the Google Gemini API.
    """

    def __init__(
        self, api_key: str, model_name: str = "gemini-1.5-flash-latest", **kwargs
    ):
        self.api_key = api_key
        self.model_name = model_name
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            logger.error("Failed to configure Gemini client", exc_info=True)
            raise ValueError(f"Failed to configure Gemini client: {e}")

    def _convert_to_gemini_history(
        self, messages: List[LLMMessage]
    ) -> List[Dict[str, Any]]:
        """
        Converts our internal message format to the Gemini format.
        """
        gemini_history = []
        for msg in messages:
            role = "model" if msg["role"] == "assistant" else msg["role"]
            if role in ["user", "model"]:
                gemini_history.append({"role": role, "parts": [msg["content"]]})
        return gemini_history

    def get_chat_response(self, messages: List[LLMMessage]) -> str:
        """
        Generates a natural language response using the Gemini API.
        """
        system_prompt = next(
            (m["content"] for m in messages if m["role"] == "system"), None
        )
        chat_history = self._convert_to_gemini_history(messages)

        if not chat_history:
            return "Error: No user prompt provided."

        prompt = chat_history.pop()  # The last message is the prompt

        try:
            model_instance = self.model
            if system_prompt:
                model_instance = genai.GenerativeModel(
                    self.model_name, system_instruction=system_prompt
                )

            chat_session = model_instance.start_chat(history=chat_history)
            response = chat_session.send_message(prompt["parts"])
            return response.text
        except (google_exceptions.GoogleAPICallError, ValueError) as e:
            logger.error("Error communicating with Gemini API", exc_info=True)
            return f"Error communicating with Gemini API: {e}"
        except Exception as e:
            logger.error("Unexpected error in get_chat_response", exc_info=True)
            return f"An unexpected error occurred: {e}"

    def extract_structured_data(
        self, prompt: str, output_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Uses Gemini's JSON mode to extract structured data.
        """
        logger.debug(
            "Starting Structured Data Extraction",
            extra={"payload": {"schema_keys": list(output_schema.keys())}},
        )

        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )

        # We make the prompt more explicit to help the model
        extraction_prompt = f"""
        Analyze the following user text and extract information according to the provided JSON schema.

        CRITICAL INSTRUCTIONS:
        1. You MUST output valid JSON.
        2. If the user text implies a transaction (spending or receiving money), set intent to 'create_transaction'.
        3. Map the values to the schema strictly.

        USER TEXT: "{prompt}"

        JSON SCHEMA: {json.dumps(output_schema)}
        """

        try:
            response = self.model.generate_content(
                extraction_prompt, generation_config=generation_config
            )

            logger.info(
                "Raw Gemini JSON Response", extra={"payload": {"text": response.text}}
            )

            return json.loads(response.text)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(
                "JSON Decode Error from LLM",
                extra={
                    "payload": {
                        "response_text": response.text
                        if "response" in locals()
                        else "No response"
                    }
                },
            )
            return {}
        except google_exceptions.GoogleAPICallError as e:
            logger.error("Gemini API Call Error in extraction", exc_info=True)
            return {}
        except Exception as e:
            logger.error("Unexpected error in extract_structured_data", exc_info=True)
            return {}
