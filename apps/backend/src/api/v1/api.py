from fastapi import APIRouter
from .endpoints import transactions

api_router = APIRouter()
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])