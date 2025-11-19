import json
from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, Tuple

from src.llm.factory import get_llm_instance
from src.llm.interface import LLMInterface, LLMMessage
from src.llm.schemas import get_intent_schema
from src.db.crud import crud_chat, crud_user, crud_category
from src.tools.base import BaseTool
from src.db.models.models import ChatRole
from src.db.schemas.chat import ChatResponse
from src.core.logger import logger
from src.utils.constants import APPLICATION_USER_ID
from src.utils.enums import UserIntent


class ExtractionResult(BaseModel):
    success: bool
    data: Optional[dict[str, object]] = None
    refusal_reason: Optional[str] = None


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
        """
        Detects user intent using classification.
        Only called when NO pending flow exists.
        """
        logger.debug(f"Detecting intent for: '{message}'")
        schema = get_intent_schema()

        prompt = f"""You are an intent classifier for SoFiA, a personal finance assistant.

USER MESSAGE: "{message}"

YOUR JOB:
Classify the user's intent into ONE category:
- "expense": User is talking about spending money (bought something, paid for something)
- "income": User received money (salary, payment, gift, etc)
- "query": User is asking about past transactions or financial data
- "chat": General conversation, greetings, or unclear intent

EXAMPLES:
"Comprei um vestido ontem" → {{"intent": "expense"}}
"Ele custou R$119.99" → {{"intent": "expense"}}
"Recebi meu salário" → {{"intent": "income"}}
"Quanto gastei esse mês?" → {{"intent": "query"}}
"Oi, tudo bem?" → {{"intent": "chat"}}

OUTPUT ONLY VALID JSON: {{"intent": "expense"}}"""

        result = self.llm.extract_structured_data(prompt, schema)
        intent_str = result.get("intent", UserIntent.CHAT.value)

        try:
            return UserIntent(intent_str.lower())
        except ValueError:
            return UserIntent.CHAT

    def _detect_cancellation(self, message: str) -> bool:
        """
        Use LLM to detect if user wants to cancel current flow.
        """
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
        Does the user want to CANCEL or STOP the current action they're in the middle of?
        Cancellation phrases (Portuguese): "não quero", "cancela", "cancelar", "deixa pra lá", "esquece", "desistir", "pare"
        EXAMPLES:
        "Não quero mais registrar isso" → {{"wants_to_cancel": true}}
        "120 reais" → {{"wants_to_cancel": false}}
        "Deixa pra lá, esquece" → {{"wants_to_cancel": true}}
        "Sim, quero continuar" → {{"wants_to_cancel": false}}
        OUTPUT ONLY JSON:"""
        result = self.llm.extract_structured_data(prompt, schema)
        return result.get("wants_to_cancel", False)

    def _check_missing_fields(self, params: dict[str, object], schema: dict) -> list[str]:
        """
        Checks which required fields are still missing from extracted parameters.

        Returns:
            List of missing field names (e.g., ["amount", "category_name"])
        """
        required = schema.get("required", [])
        missing = []

        for field in required:
            # Skip is_superfluous since it's optional and False is a valid value
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
        """
        Generate LLM response using conversation history and system context.
        NO hardcoded responses - LLM generates everything naturally.

        Args:
            session_id: Current chat session
            system_context: Instructions for the LLM about what to do/say

        Returns:
            Natural language response in Portuguese
        """
        history = crud_chat.get_history(self.db, session_id, limit=10)
        current_date = datetime.now().strftime("%Y-%m-%d (%A)")

        system_message = f"""Today is {current_date}. You are SoFiA, a warm and friendly personal finance assistant.
        You speak Brazilian Portuguese naturally and conversationally.
        {system_context}
        Guidelines:
        - Be brief and clear
        - Use a warm, supportive tone
        - Don't lecture or explain too much
        - Ask questions naturally
        - Confirm actions warmly
        Respond naturally in Portuguese:"""

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
        """
        State-based conversation flow.

        Logic:
        1. If pending_tool exists → Stay in that flow (no re-classification)
        2. If no pending_tool → Detect intent and start flow
        3. Keep collecting until all required fields are present
        4. Execute tool when complete OR user cancels
        """
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
                system_context = "System: The user canceled the current action. Acknowledge this naturally and ask if there's anything else you can help with."
                return self._generate_response_with_context(session_id, system_context), None
            try:
                intent = UserIntent(pending_tool)
            except ValueError:
                logger.error(f"Invalid pending_tool: {pending_tool}")
                crud_chat.clear_session_state(self.db, session_id)
                self.db.flush()
                intent = self._detect_intent(message)
                pending_tool = None
                collected_params = {}
            if pending_tool:
                tool = self.tools[intent.value]
                if intent == UserIntent.EXPENSE:
                    extraction_prompt = tool.get_extraction_prompt(message, partial=collected_params)
                elif intent == UserIntent.INCOME:
                    extraction_prompt = tool.get_extraction_prompt(message, partial=collected_params)
                else:
                    extraction_prompt = tool.get_extraction_prompt(message)
                raw_result = self.llm.extract_structured_data(extraction_prompt, tool.schema)
                if "refusal_reason" not in raw_result:
                    params = {**collected_params, **raw_result}
                    logger.info(f"Merged params: {json.dumps(params, ensure_ascii=False)}")
                else:
                    params = collected_params
                    logger.warning(f"Extraction refused: {raw_result.get('refusal_reason')}")
                missing_fields = self._check_missing_fields(params, tool.schema)
                if not missing_fields:
                    logger.info(f"✅ All fields collected! Executing {intent.value}")
                    description, action_type = self._execute_tool(intent, params)
                    if action_type == "System Error":
                        system_context = f"System: An internal error occurred while trying to create the {intent.value}. Apologize to the user and tell them to try again. The error was: {description}"
                        return self._generate_response_with_context(session_id, system_context), action_type
                    crud_chat.clear_session_state(self.db, session_id)
                    self.db.flush()
                    system_context = f"System: Successfully created {intent.value}. Details: {description}. Confirm this warmly to the user."
                    return self._generate_response_with_context(session_id, system_context), action_type
                else:
                    logger.info(f"❌ Still missing: {missing_fields}")
                    crud_chat.update_session_state(
                        self.db,
                        session_id=session_id,
                        pending_tool=pending_tool,
                        collected_params=params,
                        missing_fields=missing_fields
                    )
                    self.db.flush()
                    first_missing = missing_fields[0]
                    if first_missing == 'category_name' and intent == UserIntent.EXPENSE:
                        expense_tool = self.tools[UserIntent.EXPENSE.value]
                        all_categories = expense_tool.service.get_all_category_names()
                        category_list_str = "\n".join(f"- {cat}" for cat in all_categories)
                        system_context = f"""System: You are helping a user create an expense, but you are missing the category.
                        You MUST ask the user to choose from the following official list.
                        Do not invent or suggest any categories that are not on this list.
                        AVAILABLE CATEGORIES:
                        {category_list_str}
                        YOUR TASK:
                        In a warm and friendly tone, ask the user to choose one of the categories from the list that best fits their expense.
                        You can phrase it like "Could you tell me which of these categories fits best?"
                        """
                    else:
                        fields_have = list(params.keys())
                        system_context = f"""System: User is creating a {intent.value}.
                        Already collected: {fields_have}
                        Still need: {missing_fields}

                        Ask naturally for the FIRST missing field ({first_missing}) in a warm, conversational way."""

                    return self._generate_response_with_context(session_id, system_context), None
        logger.info("🆕 NO FLOW - detecting new intent")
        intent = self._detect_intent(message)
        if intent in [UserIntent.EXPENSE, UserIntent.INCOME]:
            tool = self.tools[intent.value]
            if intent == UserIntent.EXPENSE:
                extraction_prompt = tool.get_extraction_prompt(message)
            elif intent == UserIntent.INCOME:
                extraction_prompt = tool.get_extraction_prompt(message)
            else:
                extraction_prompt = tool.get_extraction_prompt(message)
            raw_result = self.llm.extract_structured_data(extraction_prompt, tool.schema)
            if "refusal_reason" not in raw_result:
                params = raw_result
                missing_fields = self._check_missing_fields(params, tool.schema)
                if not missing_fields:
                    logger.info(f"✅ Complete in one message! Executing {intent.value}")
                    description, action_type = self._execute_tool(intent, params)
                    system_context = f"System: Successfully created {intent.value} in one go. Details: {description}. Confirm warmly."
                    return self._generate_response_with_context(session_id, system_context), action_type
                else:
                    logger.info(f"🚀 STARTING {intent.value} flow - missing {missing_fields}")
                    crud_chat.update_session_state(
                        self.db,
                        session_id=session_id,
                        pending_tool=intent.value,
                        collected_params=params,
                        missing_fields=missing_fields
                    )
                    self.db.flush()
                    first_missing = missing_fields[0]
                    if first_missing == 'category_name' and intent == UserIntent.EXPENSE:
                        expense_tool = self.tools[UserIntent.EXPENSE.value]
                        all_categories = expense_tool.service.get_all_category_names()
                        category_list_str = "\n".join(f"- {cat}" for cat in all_categories)
                        system_context = f"""System: You are helping a user create an expense, but you are missing the category.
                        You MUST ask the user to choose from the following official list.
                        Do not invent or suggest any categories that are not on this list.
                        
                        AVAILABLE CATEGORIES:
                        {category_list_str}
                        
                        YOUR TASK:
                        In a warm and friendly tone, ask the user to choose one of the categories from the list that best fits their expense.
                        You can phrase it like "Could you tell me which of these categories fits best?"
                        """
                    else:
                        fields_have = list(params.keys())
                        system_context = f"""System: User is creating a {intent.value}.
                        Already collected: {fields_have}
                        Still need: {missing_fields}

                        Ask naturally for the FIRST missing field ({first_missing}) in a warm, conversational way."""

                    return self._generate_response_with_context(session_id, system_context), None
            else:
                logger.info(f"🚀 STARTING {intent.value} flow - no data extracted yet")
                all_required = tool.schema.get("required", [])
                crud_chat.update_session_state(
                    self.db,
                    session_id=session_id,
                    pending_tool=intent.value,
                    collected_params={},
                    missing_fields=all_required
                )
                self.db.flush()
                system_context = f"""System: User wants to create a {intent.value} but didn't provide enough details.
                Need to collect: {all_required}
                Ask naturally what information you need (in a warm, friendly way)."""
                return self._generate_response_with_context(session_id, system_context), None

        elif intent == UserIntent.QUERY:
            logger.info("📊 Executing query")
            description, action_type = self._execute_tool(intent, {"query": message})
            system_context = f"System: Query executed. Results: {description}. Present this to the user naturally."
            return self._generate_response_with_context(session_id, system_context), action_type

        else:
            logger.info("💬 General chat")
            system_context = "System: This is general conversation. Respond naturally and helpfully in Portuguese."
            return self._generate_response_with_context(session_id, system_context), None

    def process_user_message(self, session_id: int, message: str, model_preference: str, model_name: str) -> str:
        """Process a user message in an existing session."""
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
        """Create a new session and process the first message."""
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
        """Generate a title for the chat session."""
        if not self.llm:
            return "New Chat"
        try:
            prompt = LLMMessage(
                role="user",
                content=f"Summarize this in 3-5 words for a chat title (no quotes, Portuguese): '{first_message}'"
            )
            return self.llm.get_chat_response([prompt]).strip().strip('"').strip("'")
        except Exception as e:
            logger.warning(f"Title generation failed: {e}")
            return "New Chat"