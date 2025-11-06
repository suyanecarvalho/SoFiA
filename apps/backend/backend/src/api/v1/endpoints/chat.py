from fastapi import APIRouter, HTTPException, status
from typing import Any
from pydantic import BaseModel
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import PromptTemplate

router = APIRouter()

llm = OllamaLLM(model="mistral")
prompt = PromptTemplate.from_template("Usuário: {input}\nIA:")
chain = prompt | llm

class ChatRequest(BaseModel):
    input: str


class ChatResponse(BaseModel):
    resposta: str

@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Enviar mensagem ao chatbot",
    response_description="Resposta gerada pelo modelo Ollama",
)
def chat_with_model(request: ChatRequest) -> Any:
   
    try:
        resposta = chain.invoke({"input": request.input})
        return ChatResponse(
            resposta=str(resposta),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar a requisição: {str(e)}",
        )