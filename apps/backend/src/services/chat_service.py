from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Tuple

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
        logger.debug(f"Detecting intent for: '{message}'")
        schema = get_intent_schema()
        result = self.llm.extract_structured_data(message, schema)
        intent_str = result.get("intent", UserIntent.CHAT.value)

        try:
            return UserIntent(intent_str.lower())
        except ValueError:
            return UserIntent.CHAT

    def _extract_parameters(self, message: str, intent: UserIntent) -> dict[str, object]:
        if intent.value in self.tools:
            tool = self.tools[intent.value]
            logger.debug(f"Extracting params for tool: {tool.name}")
            return self.llm.extract_structured_data(message, tool.schema)
        return {}

    def _execute_tool(self, intent: UserIntent, params: dict[str, object]) -> Tuple[Optional[str], Optional[str]]:
        if intent.value in self.tools:
            try:
                return self.tools[intent.value].execute(params, APPLICATION_USER_ID)
            except Exception as e:
                logger.error(f"Tool Execution Error ({intent.value})", exc_info=True)
                return f"System: Error executing tool: {e}", "System Error"
        return None, None

    def _generate_title(self, first_message: str) -> str:
        if not self.llm:
            return "New Chat"
        try:
            prompt = LLMMessage(
                role="user",
                content=f"Summarize this in 3-5 words for a title (no quotes): '{first_message}'"
            )
            return self.llm.get_chat_response([prompt]).strip().strip('"')
        except:
            return "New Chat"

    def _handle_conversation_flow(self, session_id: int, message: str) -> tuple[str, Optional[str]]:
        intent = self._detect_intent(message)

        params = self._extract_parameters(message, intent) if intent.value in self.tools else {}

        crud_chat.add_message(self.db, session_id, ChatRole.USER, message, meta_data=params)

        tool_context, action_desc = self._execute_tool(intent, params)

        history = crud_chat.get_history(self.db, session_id, limit=10)

        messages: list[LLMMessage] = [
            LLMMessage(
                role="system",
                content=(
                    "You are SoFiA. Use the System info to answer. "
                    "If a transaction was created, confirm it. "
                    "If querying, summarize the results."
                ),
            )
        ]

        if tool_context:
            messages.append(LLMMessage(role="system", content=tool_context))

        messages.extend(
            [LLMMessage(role=m.role.value, content=m.content) for m in history]
        )

        response_text = self.llm.get_chat_response(messages)
        crud_chat.add_message(self.db, session_id, ChatRole.ASSISTANT, response_text)

        return response_text, action_desc

    def process_user_message(self, session_id: int, message: str, model_preference: str, model_name: str) -> str:
        self._setup_llm(model_preference, model_name)
        try:
            response_text, _ = self._handle_conversation_flow(session_id, message)
            self.db.commit()
            return response_text
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error: {e}")
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
            logger.error(f"Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
