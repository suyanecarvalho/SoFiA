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
import json
from datetime import datetime

# ========== CONFIGURAÇÕES ==========
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
    transaction: str
    type_transaction: str | None = None
    category: str | None = None
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

        # 2️⃣ Etapa 1 - Classificação da operação (busca ou entrada)
        transaction = clf_transaction.predict(X_input)[0]
        transaction_proba = None
        try:
            transaction_proba = float(max(clf_transaction.predict_proba(X_input)[0]))
        except Exception:
            transaction_proba = None

        type_transaction = None
        category = None
        tipo_proba = categoria_proba = None

        # 3️⃣ Etapa 2 - Se for MODIFICAÇÃO/ENTRADA, detectar tipo (ganho, gasto, investimento)
        if str(transaction).lower() == "entrada":
            type_transaction = clf_type_transaction.predict(X_input)[0]
            try:
                tipo_proba = float(max(clf_type_transaction.predict_proba(X_input)[0]))
            except Exception:
                tipo_proba = None

            # 4️⃣ Etapa 3 - Se for GASTO, detectar categoria
            if str(type_transaction).lower() == "gasto" and clf_category is not None:
                category = clf_category.predict(X_input)[0]
                try:
                    categoria_proba = float(max(clf_category.predict_proba(X_input)[0]))
                except Exception:
                    categoria_proba = None

        # 5️⃣ Normalizações e validações simples
        if transaction not in ["busca", "modificacao", "entrada", "indefinido"]:
            # permitir que o modelo retorne outros rótulos, mas normalizar
            transaction = str(transaction)
        if type_transaction not in ["gasto", "ganho", "investimento", None]:
            type_transaction = type_transaction if type_transaction else None
        if category == "None":
            category = None

        # 6️⃣ Construção da resposta base (mensagem curta)
        if str(transaction).lower() == "busca":
            resposta_base = "🔎 Entendi! Vou buscar informações sobre seus gastos."
        elif str(transaction).lower() in ["modificacao", "entrada"]:
            resposta_base = f"✏️ Entendi! Vou registrar: {type_transaction or 'transação'}"
            if category:
                resposta_base += f" na categoria {category}"
            if transaction_proba:
                resposta_base += f" .(Confiança: {transaction_proba:.0%})"
        else:
            resposta_base = "🤔 Não entendi muito bem sua intenção. Pode reformular?"

        # 7️⃣ Logs para depuração
        print({
            "timestamp": datetime.utcnow().isoformat(),
            "input": request.input,
            "transaction": transaction,
            "type_transaction": type_transaction,
            "category": category,
            "confidences": {
                "transaction": transaction_proba,
                "tipo": tipo_proba,
                "categoria": categoria_proba,
            },
        })

        # 8️⃣ Integração com LLM (se disponível) — monta um prompt resumido
        llm_input = (
            f"O usuário disse: '{request.input}'. "
            f"O sistema entendeu que é uma '{transaction}'. "
            f"Tipo: '{type_transaction}', categoria: '{category}'. "
            "Explique ao usuário o que será feito e dê uma dica financeira útil."
        )

        resposta_llm = None
        if chain is not None:
            try:
                resposta_llm = chain.invoke({"input": llm_input})
            except Exception as e:
                print("⚠️ Erro ao chamar LLM (usando fallback):", e)
                resposta_llm = None

        if not resposta_llm:
            # fallback textual simples quando LLM não puder ser usado
            resposta_llm = (
                resposta_base + "\n\n" +
                "Sugestão: mantenha um registro dos seus lançamentos e verifique categorias regularmente."
            )

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