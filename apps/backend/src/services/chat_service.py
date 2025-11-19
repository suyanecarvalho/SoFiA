import json
import difflib
from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, Tuple, Any

from src.llm.factory import get_llm_instance
from src.llm.interface import LLMInterface, LLMMessage
from src.llm.schemas import get_intent_schema
from src.db.crud import crud_chat, crud_user
from src.tools.base import BaseTool
from src.db.models.models import ChatRole
from src.db.schemas.chat import ChatResponse
from src.core.logger import logger
from src.utils.constants import APPLICATION_USER_ID
from src.utils.enums import UserIntent


class ChatService:
    def __init__(self, db: Session, tools: list[BaseTool]):
        self.db = db
        self.llm: Optional[LLMInterface] = None
        self.tools: dict[str, BaseTool] = {t.name: t for t in tools}

    def _setup_llm(self, model_preference: str, model_name: str) -> None:
        logger.info(f"Initializing LLM: {model_preference} ({model_name})")
        match model_preference:
            case "remote":
                user = crud_user.get_user(self.db, user_id=APPLICATION_USER_ID)
                if not user or not user.api_key:
                    raise HTTPException(status_code=503, detail="Gemini API key not configured.")
                self.llm = get_llm_instance("remote", model_name=model_name, apiKey=user.api_key)
            case "local":
                self.llm = get_llm_instance("local", model_name=model_name)
            case _:
                self.llm = get_llm_instance("dummy")

    def _detect_intent(self, message: str) -> UserIntent:
        """Detects user intent using classification."""
        logger.debug(f"Detecting intent for: '{message}'")
        schema = get_intent_schema()

        prompt = f"""You are an intent classifier for SoFiA, a personal finance assistant.

        USER MESSAGE: "{message}"
        
        YOUR JOB:
        Classify the user's intent into ONE category:
        - "expense": User is talking about spending money.
        - "income": User received money.
        - "query": User is asking about past transactions.
        - "chat": General conversation.
        
        OUTPUT ONLY VALID JSON: {{"intent": "expense"}}"""

        result = self.llm.extract_structured_data(prompt, schema)
        intent_str = result.get("intent", UserIntent.CHAT.value)

        try:
            return UserIntent(intent_str.lower())
        except ValueError:
            return UserIntent.CHAT

    def _detect_cancellation(self, message: str) -> bool:
        """Use LLM to detect if user wants to cancel current flow."""
        schema = {
            "type": "object",
            "properties": {
                "wants_to_cancel": {
                    "type": "boolean",
                    "description": "Does the user want to cancel or stop the current action?"
                }
            },
            "required": ["wants_to_cancel"]
        }

        prompt = f"""Analyze this user message to detect cancellation intent.
        USER MESSAGE: "{message}"
        Does the user want to CANCEL, STOP, or DELETE the current action?
        Phrases: "não quero", "cancela", "deixa pra lá", "esquece", "pare".
        Output JSON:"""
        result = self.llm.extract_structured_data(prompt, schema)
        return result.get("wants_to_cancel", False)

    def _validate_and_clean_params(self, intent: UserIntent, params: dict[str, Any]) -> dict[str, Any]:
        """
        Validates extracted parameters against the tool's capabilities.
        Specifically handles Category Validation to prevent hallucinations.
        """
        cleaned = params.copy()
        if intent == UserIntent.EXPENSE and "category_name" in cleaned:
            extracted_cat = cleaned["category_name"]
            expense_tool = self.tools[UserIntent.EXPENSE.value]
            valid_categories = expense_tool.schema["properties"]["category_name"]["enum"]
            if extracted_cat in valid_categories:
                return cleaned
            matches = difflib.get_close_matches(extracted_cat, valid_categories, n=1, cutoff=0.6)
            if matches:
                logger.info(f"Auto-corrected category '{extracted_cat}' to '{matches[0]}'")
                cleaned["category_name"] = matches[0]
            else:
                logger.warning(f"LLM hallucinated category '{extracted_cat}'. Removing it to trigger user prompt.")
                del cleaned["category_name"]

        return cleaned

    def _check_missing_fields(self, params: dict[str, object], schema: dict) -> list[str]:
        """Checks which required fields are still missing."""
        required = schema.get("required", [])
        missing = []

        for field in required:
            if field == "is_superfluous":
                continue
            if field not in params or params[field] in (None, "", 0):
                missing.append(field)

        return missing

    def _execute_tool(self, intent: UserIntent, params: dict[str, object]) -> Tuple[Optional[str], Optional[str]]:
        """Execute the tool and return (description, action_type)."""
        if intent.value in self.tools:
            try:
                return self.tools[intent.value].execute(params, APPLICATION_USER_ID)
            except Exception as e:
                logger.error(f"Tool Execution Error ({intent.value})", exc_info=True)
                return f"System: Error executing tool: {e}", "System Error"
        return None, None

    def _generate_response_with_context(self, session_id: int, system_context: str) -> str:
        """Generate LLM response using conversation history and system context."""
        history = crud_chat.get_history(self.db, session_id, limit=10)
        current_date = datetime.now().strftime("%Y-%m-%d (%A)")

        system_message = f"""Today is {current_date}. You are SoFiA, a warm and friendly personal finance assistant.
        You speak Brazilian Portuguese.
        {system_context}
        Guidelines:
        - Be brief and clear
        - Use a warm tone
        - Ask questions naturally
        Respond in Portuguese:"""

        messages: list[LLMMessage] = [
            LLMMessage(role="system", content=system_message)
        ]
        messages.extend(
            [LLMMessage(role=m.role.value, content=m.content) for m in history]
        )

        response_text = self.llm.get_chat_response(messages)
        crud_chat.add_message(self.db, session_id, ChatRole.ASSISTANT, response_text)

        return response_text

    def _handle_conversation_flow(
            self, session_id: int, message: str
    ) -> tuple[str, Optional[str]]:
        session_state = crud_chat.get_session_state(self.db, session_id)
        pending_tool = session_state.get("pending_tool") if session_state else None
        collected_params = session_state.get("collected_params", {}) if session_state else {}
        logger.info(f"Session {session_id} state: pending_tool={pending_tool}, collected={collected_params}")
        crud_chat.add_message(
            self.db, session_id, ChatRole.USER, message, meta_data=collected_params
        )
        if pending_tool:
            logger.info(f"⏳ IN FLOW: {pending_tool} - continuing collection")

            if self._detect_cancellation(message):
                logger.info("❌ User canceled the flow")
                crud_chat.clear_session_state(self.db, session_id)
                self.db.flush()
                return self._generate_response_with_context(session_id, "System: User canceled. Acknowledge and ask how to help."), None

            try:
                intent = UserIntent(pending_tool)
                tool = self.tools[intent.value]
                extraction_prompt = tool.get_extraction_prompt(message, partial=collected_params)
                new_params = self.llm.extract_structured_data(extraction_prompt, tool.schema)
                merged_params = {**collected_params, **new_params}
                final_params = self._validate_and_clean_params(intent, merged_params)
                logger.info(f"Updated Params: {json.dumps(final_params, ensure_ascii=False)}")
                missing_fields = self._check_missing_fields(final_params, tool.schema)
                if not missing_fields:
                    logger.info(f"✅ All fields collected! Executing {intent.value}")
                    description, action_type = self._execute_tool(intent, final_params)
                    crud_chat.clear_session_state(self.db, session_id)
                    self.db.flush()
                    if action_type == "System Error":
                        return self._generate_response_with_context(session_id, f"System: Error: {description}"), action_type
                    system_context = f"System: Successfully created {intent.value}. Details: {description}. Confirm warmly."
                    return self._generate_response_with_context(session_id, system_context), action_type
                else:
                    crud_chat.update_session_state(
                        self.db,
                        session_id=session_id,
                        pending_tool=pending_tool,
                        collected_params=final_params,
                        missing_fields=missing_fields
                    )
                    self.db.flush()
                    return self._generate_follow_up_question(session_id, intent, final_params, missing_fields), None

            except ValueError:
                logger.error(f"Invalid pending_tool: {pending_tool}")
                crud_chat.clear_session_state(self.db, session_id)

        logger.info("🆕 NO FLOW - detecting new intent")
        intent = self._detect_intent(message)
        if intent in [UserIntent.EXPENSE, UserIntent.INCOME]:
            tool = self.tools[intent.value]
            extraction_prompt = tool.get_extraction_prompt(message)
            raw_params = self.llm.extract_structured_data(extraction_prompt, tool.schema)
            final_params = self._validate_and_clean_params(intent, raw_params)
            missing_fields = self._check_missing_fields(final_params, tool.schema)
            if not missing_fields:
                logger.info(f"✅ Complete in one message! Executing {intent.value}")
                description, action_type = self._execute_tool(intent, final_params)
                system_context = f"System: Successfully created {intent.value}. Details: {description}. Confirm warmly."
                return self._generate_response_with_context(session_id, system_context), action_type
            else:
                logger.info(f"🚀 STARTING {intent.value} flow - missing {missing_fields}")
                crud_chat.update_session_state(
                    self.db,
                    session_id=session_id,
                    pending_tool=intent.value,
                    collected_params=final_params,
                    missing_fields=missing_fields
                )
                self.db.flush()
                return self._generate_follow_up_question(session_id, intent, final_params, missing_fields), None

        elif intent == UserIntent.QUERY:
            logger.info("📊 Executing query")
            description, action_type = self._execute_tool(intent, {"query": message})
            return self._generate_response_with_context(session_id, f"System: Results: {description}. Present to user."), action_type

        else:
            logger.info("💬 General chat")
            return self._generate_response_with_context(session_id, "System: General conversation. Respond naturally."), None

    def _generate_follow_up_question(self, session_id: int, intent: UserIntent, current_params: dict, missing: list[str]) -> str:
        """Helper to generate the prompt asking for missing info."""
        first_missing = missing[0]
        if first_missing == 'category_name' and intent == UserIntent.EXPENSE:
            expense_tool = self.tools[UserIntent.EXPENSE.value]
            all_categories = expense_tool.schema["properties"]["category_name"]["enum"]
            category_list_str = "\n".join(f"- {cat}" for cat in all_categories)
            system_context = f"""System: You need to ask the user to pick a category for their expense.
            You MUST ask them to choose from this EXACT list:
            {category_list_str}
            If the user previously suggested a category that wasn't on this list, politely explain that you can only track these specific categories.
            """
        else:
            fields_have = list(current_params.keys())
            system_context = f"""System: User is creating a {intent.value}.
            Collected so far: {fields_have}
            Still need: {missing}
            Ask naturally for the FIRST missing field: '{first_missing}'."""
        return self._generate_response_with_context(session_id, system_context)

    def process_user_message(self, session_id: int, message: str, model_preference: str, model_name: str) -> str:
        self._setup_llm(model_preference, model_name)
        try:
            response_text, _ = self._handle_conversation_flow(session_id, message)
            self.db.commit()
            return response_text
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing message: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    def create_session_and_reply(self, message: str, model_preference: str, model_name: str) -> ChatResponse:
        self._setup_llm(model_preference, model_name)
        try:
            title = self._generate_title(message)
            session = crud_chat.create_session(self.db, user_id=APPLICATION_USER_ID, title=title)
            response_text, action_taken = self._handle_conversation_flow(session.id, message)
            self.db.commit()
            self.db.refresh(session)
            return ChatResponse(
                response=response_text,
                session_id=session.id,
                session_title=title,
                action_taken=action_taken,
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating session: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    def _generate_title(self, first_message: str) -> str:
        if not self.llm: return "New Chat"
        try:
            prompt = LLMMessage(role="user", content=f"Summarize in 3-5 words for title (Portuguese): '{first_message}'")
            return self.llm.get_chat_response([prompt]).strip().strip('"')
        except Exception:
            return "New Chat"