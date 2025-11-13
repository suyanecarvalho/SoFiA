from fastapi import APIRouter, HTTPException, status
from typing import Any
from pydantic import BaseModel
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain.messages import SystemMessage, HumanMessage
import os
import joblib
import json
from datetime import datetime

# ========== CONFIGURAÇÕES ==========
os.environ["OLLAMA_NO_GPU"] = "1"

router = APIRouter()

MODELS_PATH = r"C:\Users\suyane\SoFiA\apps\backend\train_model"

# ====== CARREGAR MODELOS EM CASCATA ======
try:
    vectorizer = joblib.load(os.path.join(MODELS_PATH, "vectorizer.joblib"))
    clf_operacao = joblib.load(os.path.join(MODELS_PATH, "model_operacao.joblib"))
    clf_tipo_transacao = joblib.load(os.path.join(MODELS_PATH, "model_tipo_transacao.joblib"))

    categoria_path = os.path.join(MODELS_PATH, "model_categoria.joblib")
    clf_categoria = joblib.load(categoria_path) if os.path.exists(categoria_path) else None

    print("✅ Modelos carregados com sucesso!")
except Exception as e:
    print("⚠️ Erro ao carregar modelos:", e)
    vectorizer = clf_operacao = clf_tipo_transacao = clf_categoria = None

# ====== CONFIGURAÇÃO DO LLM ======
llm = OllamaLLM(model="mistral", temperature=0)

system_message = SystemMessage(
    content=(
        "Você é um chatbot de assistência financeira. "
        "Seu objetivo é ajudar o usuário a gerenciar suas finanças pessoais, "
        "explicando de forma clara e simples os gastos, ganhos e categorias financeiras. "
        "Sempre responda de maneira amigável e profissional, e incentive boas práticas de economia."
    )
)

messages = [system_message, HumanMessage(content="{input}")]
prompt = ChatPromptTemplate.from_messages(messages)
chain = prompt | llm


# ====== MODELOS DE REQUISIÇÃO E RESPOSTA ======
class ChatRequest(BaseModel):
    input: str


class ChatResponse(BaseModel):
    transaction: str
    type_transaction: str | None = None
    category: str | None = None
    resposta: str


# ====== ENDPOINT PRINCIPAL ======
@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Enviar mensagem ao chatbot",
    response_description="Resposta gerada pelo modelo Ollama",
)
def chat_with_model(request: ChatRequest) -> Any:
    try:
        # 1️⃣ Verifica se os modelos estão carregados
        if vectorizer is None or clf_operacao is None or clf_tipo_transacao is None:
            raise ValueError("Modelos não carregados. Execute o treinamento primeiro.")

        X_input = vectorizer.transform([request.input])

        # 2️⃣ Etapa 1 - Classificação da operação (busca ou modificação)
        transaction = clf_operacao.predict(X_input)[0]
        transaction_proba = float(max(clf_operacao.predict_proba(X_input)[0]))

        type_transaction = None
        category = None
        tipo_proba = categoria_proba = None

        # 3️⃣ Etapa 2 - Se for MODIFICAÇÃO, detectar tipo (ganho, gasto, investimento)
        if transaction.lower() in ["modificacao", "entrada"]:
            type_transaction = clf_tipo_transacao.predict(X_input)[0]
            tipo_proba = float(max(clf_tipo_transacao.predict_proba(X_input)[0]))

            # 4️⃣ Etapa 3 - Se for GASTO, detectar categoria
            if type_transaction.lower() == "gasto" and clf_categoria:
                category = clf_categoria.predict(X_input)[0]
                categoria_proba = float(max(clf_categoria.predict_proba(X_input)[0]))

        # 5️⃣ Validação e fallback de classes
        if transaction not in ["busca", "modificacao", "entrada"]:
            transaction = "indefinido"
        if type_transaction not in ["gasto", "ganho", "investimento", None]:
            type_transaction = None
        if category == "None":
            category = None

        # 6️⃣ Construção da resposta base
        if transaction.lower() == "busca":
            resposta_base = "🔎 Entendi! Vou buscar informações sobre seus gastos."
        elif transaction.lower() in ["modificacao", "entrada"]:
            resposta_base = f"✏️ Entendi! Vou registrar: {type_transaction or 'transação'}"
            if category:
                resposta_base += f" na categoria {category}"
            if transaction_proba:
                resposta_base += f". (Confiança: {transaction_proba:.0%})"
        else:
            resposta_base = "🤔 Não entendi muito bem sua intenção. Pode reformular?"

        # 7️⃣ Logs para depuração
        print({
            "input": request.input,
            "transaction": transaction,
            "type_transaction": type_transaction,
            "category": category,
            "confidences": {
                "transaction": transaction_proba,
                "tipo": tipo_proba,
                "categoria": categoria_proba
            }
        })

        # 8️⃣ Integração com LLM (geração de resposta natural)
        llm_input = (
            f"O usuário disse: '{request.input}'. "
            f"O sistema entendeu que é uma '{transaction}'. "
            f"Tipo: '{type_transaction}', categoria: '{category}'. "
            "Explique ao usuário o que será feito e dê uma dica financeira útil."
        )

        resposta_llm = chain.invoke({"input": llm_input})
        resposta_final = f"{resposta_base}\n\n💬 {resposta_llm}"

        # 9️⃣ Retorno estruturado
        return ChatResponse(
            transaction=transaction,
            type_transaction=type_transaction,
            category=category,
            resposta=str(resposta_final),
        )

    except Exception as e:
        print("❌ Erro durante o processamento:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar a requisição: {str(e)}",
        )
