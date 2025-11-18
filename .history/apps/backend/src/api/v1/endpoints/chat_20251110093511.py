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
    clf = joblib.load(os.path.join(models_path, "vetorizer.joblib"))
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

def detect_money_type(s: str) -> str:
    s_low = s.lower()
    ganho_kw = ["recebi", "recebido", "ganhei", "ganho", "entrada", "receita", "salário", "salario", "salario"]
    gasto_kw = ["gastei", "gasto", "paguei", "pago", "compra", "pagar", "despesa", "debito", "retirada", "cartao", "cartão"]
    for kw in ganho_kw:
        if kw in s_low:
            return "ganho"
    for kw in gasto_kw:
        if kw in s_low:
            return "gasto"
    # detectar sinais de valor negativo ou verbos de pagamento
    if re.search(r"-\s?\d+|pagou|pagarei|vou pagar|paguei", s_low):
        return "gasto"
    return "unknown"

def categorize_expense(s: str) -> str:
    s_low = s.lower()
    categories = {
        "alimentacao": ["supermercado", "mercado", "restaurante", "almoço", "almoço", "jantar", "café", "cafe", "padaria", "mercearia"],
        "lazer": ["cinema", "show", "teatro", "bar", "lazer", "festa", "viagem"],
        "transporte": ["uber", "taxi", "táxi", "onibus", "ônibus", "combustível", "gasolina", "passagem", "transporte"],
        "moradia": ["aluguel", "condomínio", "condominio", "luz", "água", "agua", "internet", "telefone"],
        "saude": ["remédio", "remedio", "farmacia", "farmácia", "consulta", "hospital", "médico", "medico"],
        "educacao": ["curso", "matrícula", "matricula", "faculdade", "escola", "livro", "curso"],
        "compras": ["roupa", "calçado", "calcado", "loja", "compra", "produto", "eletrônico", "eletronico"],
        "outros": []
    }
    for cat, kws in categories.items():
        for kw in kws:
            if kw in s_low:
                return cat
    # fallback simples
    return "outros"


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
        
        text = (request.input or "").strip()

        # --- 2️⃣ Predição da intenção ---
        input_user = vectorizer.transform([text])
        tipo = str(clf.predict(input_user)[0])  # pode ser "Busca", "Entrada", "Investimento", etc.

        # 2) detectar ganho/gasto
        money_type = detect_money_type(text)

        # 3) categorizar se for gasto
        category = None
        if money_type == "gasto":
            category = categorize_expense(text)

        resposta_llm = chain.invoke({"input": request.input})
        response_output = [f"intent: {tipo.lower()} ", f"Tipo: {money_type} "]
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