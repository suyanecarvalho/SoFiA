from fastapi import Depends
from sqlalchemy.orm import Session
from src.db.database.connection import get_db
from src.services.chat_service import ChatService


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    """
    Dependency provider that instantiates the ChatService
    with a valid database session.
    """
    return ChatService(db=db)
