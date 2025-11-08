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
    vectorizer, clf = joblib.load(r"C:\Users\beand\Documents\SoFIA\SoFiA\apps\backend\train_model\intent_model.joblib")
    print("✅ Modelo de intenção carregado com sucesso.")
except Exception as e:
    print("⚠️ Erro ao carregar modelo de intenção:", e)
    vectorizer = None
    clf = None

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
        if vectorizer is None or clf is None:
            raise ValueError("Modelo de intenção não carregado.")

        # --- 2️⃣ Predição da intenção ---
        X_input = vectorizer.transform([request.input])
        tipo = clf.predict(X_input)[0]  # pode ser "Busca", "Entrada", "Investimento", etc.

        # --- 3️⃣ Mensagem base dependendo da classe ---
        mensagens_base = {
            "busca": "🔎 Entendido, vou buscar as informações solicitadas.",
            "entrada": "✏️ Entendido, vou registrar a nova transação.",
            "resumo": "📊 Entendido, vou gerar um resumo financeiro.",
        }

        resposta_base = mensagens_base.get(tipo.lower(), f"🤖 Entendido, sua intenção foi classificada como: {tipo}.")

        # --- 4️⃣ Chamada opcional ao LLM ---
        resposta_llm = chain.invoke({"input": request.input})
        resposta_final = f"{resposta_base}\n\n💬 {resposta_llm}"

        return ChatResponse(
            resposta=str(resposta_final),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar a requisição: {str(e)}",
        )