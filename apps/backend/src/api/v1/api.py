from fastapi import APIRouter
from .endpoints import transactions, health, categories

api_router = APIRouter()
api_router.include_router(
    transactions.router, prefix="/transactions", tags=["transactions"]
)
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
