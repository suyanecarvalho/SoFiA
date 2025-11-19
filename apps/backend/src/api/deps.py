from typing import Generator, List
from fastapi import Depends
from sqlalchemy.orm import Session
from src.db.database.connection import SessionLocal
from src.services.chat_service import ChatService
from src.services.transaction_service import TransactionService
from src.tools.base import BaseTool
from src.tools.finance import ExpenseTool, IncomeTool, QueryTool

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    return TransactionService(db)

def get_tools(
    db: Session = Depends(get_db),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> List[BaseTool]:
    """
    Registry of all available tools.
    If you add a 'DeleteTool' later, you just add it to this list.
    """
    return [
        ExpenseTool(transaction_service),
        IncomeTool(transaction_service),
        QueryTool(transaction_service)
    ]

def get_chat_service(
    db: Session = Depends(get_db),
    tools: List[BaseTool] = Depends(get_tools)
) -> ChatService:
    return ChatService(db=db, tools=tools)