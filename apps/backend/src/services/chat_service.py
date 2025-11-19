from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from pydantic import TypeAdapter, ValidationError
from src.llm.factory import get_llm_instance
from src.llm.interface import LLMInterface
from src.db.crud import crud_chat, crud_user, crud_category
from src.services.transaction_service import TransactionService
from src.db.models.models import ChatRole
from src.db.schemas import transaction as transaction_schema
from src.db.schemas.chat import ChatResponse
from typing import Dict, Any, Optional, Tuple
from src.core.logger import logger
from src.utils.constants import APPLICATION_USER_ID
from src.utils.enums import UserIntent


class ChatService:
    def __init__(self, db: Session):
        self.llm: Optional[LLMInterface] = None
        self.db = db
        self.transaction_service = TransactionService(db)

    def _setup_llm(self, model_preference: str, model_name: str):
        logger.info(f"Initializing LLM: {model_preference} ({model_name})")
        match model_preference:
            case "remote":
                user = crud_user.get_user(self.db, user_id=APPLICATION_USER_ID)
                if not user or not user.api_key:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Gemini API key is not configured for the user.",
                    )
                self.llm = get_llm_instance(
                    "remote", model_name=model_name, apiKey=user.api_key
                )
            case "local":
                self.llm = get_llm_instance("local", model_name=model_name)
            case _:
                self.llm = get_llm_instance("dummy")

    def _detect_intent(self, message: str) -> str:
        valid_intents = [e.value for e in UserIntent]
        schema = {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": valid_intents,
                    "description": "Classify the user text. 'expense' for spending money, 'income' for receiving money, 'query' for asking about past data, 'chat' for everything else.",
                }
            },
            "required": ["intent"],
        }
        logger.debug(f"Step 1: Detecting intent for: '{message}'")
        result = self.llm.extract_structured_data(message, schema)
        intent_str = result.get("intent", UserIntent.CHAT.value)
        try:
            return UserIntent(intent_str.lower())
        except ValueError:
            return UserIntent.CHAT

    def _extract_parameters(self, message: str, intent: str) -> Dict[str, Any]:
        logger.debug(f"Step 2: Extracting parameters for intent: {intent}")
        if intent == UserIntent.EXPENSE:
            db_categories = crud_category.get_categories(self.db, limit=100)
            category_names = [c.name for c in db_categories] if db_categories else []
            schema = {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "integer",
                        "description": "The expense amount in CENTS (integer). E.g., R$ 10,50 -> 1050. R$ 50 -> 5000.",
                    },
                    "description": {
                        "type": "string",
                        "description": "What was bought?",
                    },
                    "category_name": {
                        "type": "string",
                        "enum": category_names,
                        "description": "Select the closest existing category.",
                    },
                    "is_superfluous": {
                        "type": "boolean",
                        "description": "Is this a need (False) or a want (True)?",
                    },
                },
                "required": ["amount", "description", "category_name"],
            }
            return self.llm.extract_structured_data(message, schema)

        elif intent == UserIntent.INCOME:
            schema = {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "integer",
                        "description": "The income amount in CENTS (integer). E.g., R$ 100,00 -> 10000.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Source of income.",
                    },
                },
                "required": ["amount", "description"],
            }
            return self.llm.extract_structured_data(message, schema)

        elif intent == UserIntent.QUERY:
            schema = {
                "type": "object",
                "properties": {
                    "date_from": {
                        "type": "string",
                        "format": "date",
                        "description": "YYYY-MM-DD",
                    },
                    "date_to": {
                        "type": "string",
                        "format": "date",
                        "description": "YYYY-MM-DD",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of items to retrieve",
                    },
                },
            }
            return self.llm.extract_structured_data(message, schema)

        return {}

    def _resolve_category_id(self, category_name: str) -> Optional[int]:
        if not category_name:
            return None
        categories = crud_category.get_categories(self.db, name_contains=category_name)
        for cat in categories:
            if cat.name.lower() == category_name.lower():
                return cat.id
        return categories[0].id if categories else None

    def _execute_tool(
            self, intent: str, params: Dict[str, Any]
    ) -> Tuple[Optional[str], Optional[str]]:
        if intent == UserIntent.CHAT:
            return None, None

        if intent in [UserIntent.EXPENSE, UserIntent.INCOME]:
            try:
                normalized_intent = intent.lower()
                params["transaction_type"] = normalized_intent
                if normalized_intent == "expense":
                    cat_name = params.pop("category_name", None)
                    if cat_name:
                        cat_id = self._resolve_category_id(cat_name)
                        if cat_id:
                            params["category_id"] = cat_id

                elif normalized_intent == "income":
                    params["category_id"] = None
                    params["is_superfluous"] = None

                logger.info(
                    f"Creating Transaction ({normalized_intent})",
                    extra={"payload": params},
                )
                adapter = TypeAdapter(transaction_schema.TransactionCreate)
                validated_data = adapter.validate_python(params)
                db_transaction = self.transaction_service.create_transaction(
                    user_id=APPLICATION_USER_ID, transaction_data=validated_data
                )
                human_amount = f"{db_transaction.amount / 100:.2f}"
                context = f"System: Successfully created {normalized_intent} ID {db_transaction.id}."
                action_desc = f"Created {normalized_intent.title()}: {db_transaction.description} (R$ {human_amount})"
                return context, action_desc
            except ValidationError as ve:
                logger.error(f"Validation Error: {ve}")
                return (
                    f"System: I couldn't process that transaction. Missing info: {ve}",
                    "Validation Error",
                )
            except Exception as e:
                logger.error("Transaction Creation Error", exc_info=True)
                return f"System: Error creating transaction: {e}", "System Error"

        elif intent == UserIntent.QUERY:
            try:
                logger.info("Querying Transactions", extra={"payload": params})
                results = self.transaction_service.get_transactions(
                    filters=params
                )
                if not results:
                    return "System: No transactions found matching those criteria.", "Query executed (0 results)"
                summary_lines = []
                for tx in results:
                    date_str = tx.created_at.strftime("%Y-%m-%d")
                    amount = f"R$ {tx.amount / 100:.2f}"
                    t_type = getattr(tx, "transaction_type", "transaction")
                    summary_lines.append(f"- {date_str}: {tx.description} ({amount}) [{t_type}]")
                context = "System: Found the following transactions:\n" + "\n".join(summary_lines)
                action_desc = f"Retrieved {len(results)} transactions"
                return context, action_desc
            except Exception as e:
                logger.error("Query Error", exc_info=True)
                return f"System: Error running query: {e}", "Query Error"
        return None, None

    def _generate_title(self, first_message: str) -> str:
        if not self.llm:
            return "New Chat"
        try:
            prompt = [
                {
                    "role": "user",
                    "content": f"Summarize this in 3-5 words for a title (no quotes): '{first_message}'",
                }
            ]
            return self.llm.get_chat_response(prompt).strip().strip('"')
        except:
            return "New Chat"

    def _handle_conversation_flow(
            self, session_id: int, message: str
    ) -> Tuple[str, Optional[str]]:
        intent = self._detect_intent(message)
        params = {}
        if intent != UserIntent.CHAT:
            params = self._extract_parameters(message, intent)
        crud_chat.add_message(self.db, session_id, ChatRole.USER, message, meta_data=params)
        tool_context, action_desc = self._execute_tool(intent, params)
        history = crud_chat.get_history(self.db, session_id, limit=10)
        messages = [
            {
                "role": "system",
                "content": "You are SoFiA. Use the System info to answer. If a transaction was created, confirm it. If querying, summarize the results.",
            }
        ]
        if tool_context:
            messages.append({"role": "system", "content": tool_context})
        messages.extend([{"role": m.role.value, "content": m.content} for m in history])
        response_text = self.llm.get_chat_response(messages)
        crud_chat.add_message(self.db, session_id, ChatRole.ASSISTANT, response_text)
        return response_text, action_desc

    def create_session_and_reply(
            self, message: str, model_preference: str, model_name: str
    ) -> ChatResponse:
        self._setup_llm(model_preference, model_name)
        title = self._generate_title(message)
        session = crud_chat.create_session(
            self.db, user_id=APPLICATION_USER_ID, title=title
        )
        response_text, action_taken = self._handle_conversation_flow(
            session.id, message
        )
        return ChatResponse(
            response=response_text,
            session_id=session.id,
            session_title=title,
            action_taken=action_taken,
        )

    def process_user_message(
            self, session_id: int, message: str, model_preference: str, model_name: str
    ) -> str:
        self._setup_llm(model_preference, model_name)
        response_text, _ = self._handle_conversation_flow(session_id, message)
        return response_text