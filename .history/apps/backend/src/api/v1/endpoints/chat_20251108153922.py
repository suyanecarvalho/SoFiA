from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from typing import Any
from pydantic import BaseModel
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
try:
    # tentativa de importar o conector Ollama; se não houver, seguimos com fallback
    from langchain_ollama.llms import OllamaLLM
    from langchain.messages import SystemMessage, HumanMessage
    _HAS_LANGCHAIN_OLLAMA = True
except Exception:
    # pacote ausente ou erro de import
    from langchain.messages import SystemMessage, HumanMessage
    _HAS_LANGCHAIN_OLLAMA = False
import os
import joblib

os.environ["OLLAMA_NO_GPU"] = "1"

router = APIRouter()

# ====== CARREGAR MODELO DE INTENÇÃO ======
try:
    base_dir = os.path.dirname(__file__)
    model_path = os.path.abspath(os.path.join(base_dir, "..", "..", "..", "..", "train_model", "intent_model.joblib"))
    vectorizer, clf = joblib.load(model_path)
    print("✅ Modelo de intenção carregado com sucesso.")
except Exception as e:
    print("⚠️ Erro ao carregar modelo de intenção:", e)
    vectorizer = None
    clf = None

# ====== Inicializa LLM / fallback ======
chain = None
if _HAS_LANGCHAIN_OLLAMA and shutil.which("ollama") is not None:
    model_name = os.environ.get("OLLAMA_MODEL", "mistral")
    try:
        llm = OllamaLLM(model=model_name, temperature=0)
        system_mes = SystemMessage(content=(
            "Você é um chatbot de assistência financeira. Seja claro e profissional."
        ))
        messages = [system_mes, HumanMessage(content="{input}")]
        prompt = ChatPromptTemplate.from_messages(messages)
        chain = prompt | llm
        print(f"✅ Ollama LLM pronto (modelo: {model_name})")
    except Exception as e:
        print(f"⚠️ Não foi possível iniciar Ollama LLM (modelo {model_name}):", e)
        chain = None
else:
    if not _HAS_LANGCHAIN_OLLAMA:
        print("⚠️ pacote 'langchain_ollama' não disponível — usando fallback.")
    else:
        print("⚠️ binário 'ollama' não encontrado no PATH — usando fallback.")
    chain = None

def _fallback_llm(input_text: str) -> str:
    return "LLM indisponível. Intenção detectada e processada localmente: " + (input_text[:200] + ("..." if len(input_text) > 200 else ""))


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
    """Rota principal: classifica intenção, detecta ganho/gasto e categoriza gastos."""
    try:
        if vectorizer is None or clf is None:
            raise HTTPException(status_code=500, detail="Modelo de intenção não carregado.")

        text = request.input or ""

        # --- 1) predizer intenção ---
        X_input = vectorizer.transform([text])
        intent = str(clf.predict(X_input)[0]).lower()

        # --- 2) detectar se é ganho ou gasto ---
        def detect_money_type(s: str) -> str:
            s_low = s.lower()
            ganho_kw = ["recebi", "recebido", "ganhei", "ganho", "entrada", "receita", "rendeu"]
            gasto_kw = ["gastei", "gasto", "paguei", "pago", "compra", "pagar", "despesa", "gasto"]
            for kw in ganho_kw:
                if kw in s_low:
                    return "ganho"
            for kw in gasto_kw:
                if kw in s_low:
                    return "gasto"
            # regra simples: se houver símbolos de moeda com sinal negativo/verbos, assume gasto
            if re.search(r"-\s?\d+|\bpagou\b|\bpagarei\b", s_low):
                return "gasto"
            # default: unknown
            return "unknown"

        money_type = detect_money_type(text)

        # --- 3) categorizar gasto por palavras-chave ---
        def categorize_expense(s: str) -> str:
            s_low = s.lower()
            categories = {
                "alimentacao": ["supermercado", "mercado", "restaurante", "almoço", "jantar", "café", "padaria"],
                "lazer": ["cinema", "show", "teatro", "bar", "lazer", "festa"],
                "transporte": ["uber", "taxi", "ônibus", "onibus", "combustível", "gasolina", "transporte"],
                "moradia": ["aluguel", "condomínio", "luz", "água", "agua", "internet", "telefone"],
                "saude": ["remédio", "farmácia", "consulta", "hospital", "medico", "médico"],
                "educacao": ["curso", "matrícula", "faculdade", "escola", "livro"],
                "compras": ["roupa", "calçado", "loja", "compra", "produto"],
                "outros": []
            }
            for cat, kws in categories.items():
                for kw in kws:
                    if kw in s_low:
                        return cat
            # fallback: tentar extrair palavras significativas
            return "outros"

        category = None
        if money_type == "gasto":
            category = categorize_expense(text)

        # --- 4) gerar resposta via LLM ou fallback ---
        if chain is not None:
            try:
                resposta_llm = chain.invoke({"input": text})
            except Exception as e:
                print("⚠️ erro ao chamar LLM:", e)
                resposta_llm = _fallback_llm(text)
        else:
            resposta_llm = _fallback_llm(text)

        # --- 5) montar resposta final ---
        parts = [f"Intenção: {intent}"]
        parts.append(f"Tipo financeiro: {money_type}")
        if category:
            parts.append(f"Categoria (gasto): {category}")
        parts.append("Resposta do assistente:")
        parts.append(str(resposta_llm))

        return ChatResponse(resposta="\n\n".join(parts))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar a requisição: {e}")

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