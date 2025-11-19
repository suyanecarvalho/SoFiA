from sqlalchemy.orm import Session
from src.db.models import models


def create_session(
    db: Session, user_id: int, title: str = "New Chat"
) -> models.ChatSession:
    db_session = models.ChatSession(user_id=user_id, title=title)
    db.add(db_session)
    db.flush()
    db.refresh(db_session)
    return db_session


def get_session(
    db: Session, session_id: int, user_id: int
) -> models.ChatSession | None:
    return (
        db.query(models.ChatSession)
        .filter(
            models.ChatSession.id == session_id, models.ChatSession.user_id == user_id
        )
        .first()
    )


def update_session(
    db: Session, session_id: int, user_id: int, title: str
) -> models.ChatSession | None:
    """Updates the title of a chat session."""
    db_session = get_session(db, session_id, user_id)
    if db_session:
        db_session.title = title
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
    return db_session


def delete_session(db: Session, session_id: int, user_id: int) -> bool:
    """Deletes a session and its messages (via cascade). Returns True if deleted."""
    db_session = get_session(db, session_id, user_id)
    if db_session:
        db.delete(db_session)
        db.commit()
        return True
    return False


def add_message(
    db: Session,
    session_id: int,
    role: models.ChatRole,
    content: str,
    meta_data: dict = None,
) -> models.ChatMessage:
    db_message = models.ChatMessage(
        session_id=session_id, role=role, content=content, meta_data=meta_data
    )
    db.add(db_message)
    db.flush()
    db.refresh(db_message)
    return db_message


def get_history(db: Session, session_id: int, limit: int = 20):
    """Retrieves the last N messages for context window."""
    return (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.session_id == session_id)
        .order_by(models.ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )