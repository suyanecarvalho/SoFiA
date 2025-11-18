from fastapi import APIRouter
from src.api.v1.endpoints import transactions, health, categories, chat

api_router = APIRouter()
api_router.include_router(
    transactions.router, prefix="/transactions", tags=["transactions"]
)
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
