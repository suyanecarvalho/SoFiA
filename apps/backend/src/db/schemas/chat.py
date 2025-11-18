from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The user's natural language input.")
    model_preference: Optional[str] = Field(
        default="dummy",
        description="Optional preference for which LLM model to use (e.g., 'local', 'remote')."
    )

class ChatResponse(BaseModel):
    response: str = Field(..., description="The natural language response from the system.")