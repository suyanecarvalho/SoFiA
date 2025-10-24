from fastapi import FastAPI
from .api.v1.api import api_router

app = FastAPI(title="SofIA Backend")

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

app.include_router(api_router, prefix="/api/v1")