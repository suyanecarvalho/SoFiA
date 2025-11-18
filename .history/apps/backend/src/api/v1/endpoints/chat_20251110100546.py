from pathlib import Path
import re
from fastapi import APIRouter, HTTPException, status
from typing import Any
from pydantic import BaseModel
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain.messages import SystemMessage, HumanMessage
import os
import joblib

os.environ["OLLAMA_NO_GPU"] = "1"

router = APIRouter()

# ====== CARREGAR MODELO DE INTENÇÃO ======
try:
    models_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "train_model")
    
    vectorizer = joblib.load(os.path.join(models_path, "vetorizer.joblib"))
    clf_transaction = joblib.load(os.path.join(models_path, "model_transaction.joblib"))
    clf_type_transaction = joblib.load(os.path.join(models_path, "model_type_transaction.joblib"))
    clf_category = joblib.load(os.path.join(models_path, "model_category.joblib"))
    
    print("✅ Modelos de intenção carregado com sucesso.")
except Exception as e:
    print("⚠️ Erro ao carregar modelos de intenção:", e)
    vectorizer =clf_transaction = clf_type_transaction = clf_category = None

llm = OllamaLLM(model="mistral", temperature=0)

system_mes = SystemMessage(content="Você e um chatbot de assistência financeira para os usuários. " \
            "Seu principal obetivo é ajudar os usuários a gerenciar suas finanças pessoais, " \
            "fornecendo conselhos sobre orçamento, economia, organização finaceira e relatórios detalhados. " \
            "Seja amigável, prestativo e profissional em suas respostas." \
            "Sempre explique conceitos financeiros de maneira clara e simples." \
            "Incentive os usuários a adotarem boas práticas financeiras e ofereça dicas personalizadas " \
            "com base nas informações fornecidas por eles."
            "Sempre deixe claro quais foram os gastos do usuário em cada resposta")

messages = [
    system_mes,
    HumanMessage(content="{input}"),
]

prompt = ChatPromptTemplate.from_messages(messages)
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
        # --- 1️⃣ Verifica se o modelo está carregado ---
        if not all ([vectorizer, clf_transaction, clf_type_transaction, clf_category]):
            raise ValueError("Modelos de intenção não carregado.")
       
        #vetorizar o input do usuário
        X_input = vectorizer.transform([request.input])
        
        # --- 2️⃣ Predição ---
        transaction = clf_transaction.predict(X_input)[0]
        type_transaction = clf_type_transaction.predict(X_input)[0]
        category = None
        if type_transaction == "gasto":
            category = clf_category.predict(X_input)[0]
            
        resposta_llm = chain.invoke({"input": request.input})
        response_output = [f"Transação: {tipo.lower()} ", f"Tipo: {money_type} "]
        if category:
            response_output.append(f"Categoria: {category}")
        
        response_output.append("Resposta do assistente:")
        response_output.append(str(resposta_llm))
        # --- 4️⃣ Chamada opcional ao LLM ---

        return ChatResponse(resposta=str(response_output))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar a requisição: {str(e)}",
        )