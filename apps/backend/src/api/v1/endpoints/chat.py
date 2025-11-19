from fastapi import APIRouter, status, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from src.db.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatSessionInit,
    ChatSessionUpdate,
    ChatSessionRead,
)
from src.services.chat_service import ChatService
from src.api.deps import get_chat_service
from src.db.database.connection import get_db
from src.db.crud import crud_chat

USER_ID = 1

router = APIRouter()


@router.post(
    "/sessions",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new chat session with an initial message",
)
def start_new_session(
    request: ChatSessionInit, service: ChatService = Depends(get_chat_service)
):
    """
    Creates a new conversation thread.

    1. Accepts an initial message and LLM settings.
    2. Generates a title for the session based on the message.
    3. Returns the initial AI response and the created session ID/Title.
    """
    return service.create_session_and_reply(
        message=request.message,
        model_preference=request.model_preference,
        model_name=request.model_name,
    )


@router.put(
    "/sessions/{session_id}",
    response_model=ChatSessionRead,
    status_code=status.HTTP_200_OK,
    summary="Update chat session details (e.g., Title)",
)
def update_session_details(
    update_data: ChatSessionUpdate,
    session_id: int = Path(..., description="The ID of the chat session"),
    db: Session = Depends(get_db),
):
    """
    Updates the title of an existing chat session.
    """
    session = crud_chat.update_session(
        db, session_id=session_id, user_id=USER_ID, title=update_data.title
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a chat session",
)
def delete_chat_session(
    session_id: int = Path(..., description="The ID of the chat session"),
    db: Session = Depends(get_db),
):
    """
    Deletes a chat session and all associated messages.
    """
    success = crud_chat.delete_session(db, session_id=session_id, user_id=USER_ID)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return None


@router.post(
    "/sessions/{session_id}/messages",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send message to a specific session",
)
def send_message(
    request: ChatRequest,
    session_id: int = Path(..., description="The ID of the chat session"),
    service: ChatService = Depends(get_chat_service),
    db: Session = Depends(get_db),
) -> ChatResponse:
    """
    Processes a message within an existing context.
    """
    session = crud_chat.get_session(db, session_id=session_id, user_id=USER_ID)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    response_text = service.process_user_message(
        session_id=session_id,
        message=request.message,
        model_preference=request.model_preference,
        model_name=request.model_name,
    )
    return ChatResponse(response=response_text, session_id=session_id)
