from typing import Any
from pydantic import BaseModel
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain.messages import SystemMessage, HumanMessage
import os
import joblib

# Desabilita GPU no Ollama
os.environ["OLLAMA_NO_GPU"] = "1"


# ==========================
# 1) CARREGAR MODELOS
# ==========================
def load_or_none(path):
    try:
        model = joblib.load(path)
        print(f"✅ Modelo carregado: {path}")
        return model
    except Exception as e:
        print(f"⚠️ Erro ao carregar modelo ({path}): {e}")
        return None


transaction_model = load_or_none(
    r"C:\Users\beand\Documents\SoFIA\SoFiA\apps\backend\train_model\modelo_transaction.pkl"
)

type_transaction_model = load_or_none(
    r"C:\Users\beand\Documents\SoFIA\SoFiA\apps\backend\train_model\modelo_type_transaction.pkl"
)

category_model = load_or_none(
    r"C:\Users\beand\Documents\SoFIA\SoFiA\apps\backend\train_model\modelo_category.pkl"
)


# ==========================
# 2) CONFIGURAR LLM
# ==========================
llm = OllamaLLM(model="mistral", temperature=0)

system_mes = SystemMessage(
    content=(
        "Você é um assistente financeiro. "
        "Responda APENAS ao que o usuário disser. "
        "Não crie introduções. "
        "Não ofereça ajuda extra. "
        "Não pergunte nada. "
        "Não gere listas ou explicações a menos que o usuário peça. "
        "Seja direto e objetivo."
    )
)

messages = [
    system_mes,
    HumanMessage(content="{input}"),
]

prompt = ChatPromptTemplate.from_messages(messages)
chain = prompt | llm


# ==========================
# 3) FUNÇÃO DE PROCESSAMENTO
# ==========================
def processar_texto(texto_usuario: str) -> str:
    # ---------------- Etapa 1 ----------------
    if transaction_model is None:
        raise ValueError("Modelo transaction não carregado.")

    vec_t, clf_t = transaction_model
    X_transformed = vec_t.transform([texto_usuario])
    transaction_pred = clf_t.predict(X_transformed)[0]

    # ---------------- Etapa 2 ----------------
    if type_transaction_model is None:
        raise ValueError("Modelo type_transaction não carregado.")

    vec_tt, clf_tt = type_transaction_model
    features_tt = texto_usuario + " " + transaction_pred
    X_transformed = vec_tt.transform([features_tt])
    type_transaction_pred = clf_tt.predict(X_transformed)[0]

    # ---------------- Etapa 3 ----------------
    if category_model is None:
        raise ValueError("Modelo category não carregado.")

    vec_c, clf_c = category_model
    features_cat = texto_usuario + " " + transaction_pred + " " + type_transaction_pred
    X_transformed = vec_c.transform([features_cat])
    category_pred = clf_c.predict(X_transformed)[0]

    # ---------------- Resultado base ----------------
    resposta_modelos = (
        f"\n*Classificações automáticas*\n"
        f"- Transaction: {transaction_pred}\n"
        f"- Type Transaction: {type_transaction_pred}\n"
        f"- Category: {category_pred}\n"
    )

    # ---------------- Chamada ao LLM ----------------
    resposta_llm = chain.invoke({"input": texto_usuario})

    return resposta_modelos 


# ==========================
# 4) LOOP NO TERMINAL
# ==========================
if __name__ == "__main__":
    print("Chatbot Financeiro – rodando no terminal")
    print("Digite uma frase ou 'sair' para encerrar.\n")

    while True:
        texto = input("Você: ")

        if texto.lower() in ["sair", "exit", "quit"]:
            print("Até mais!")
            break

        try:
            resposta = processar_texto(texto)
            print("\nResposta:")
            print(resposta)
            print("\n" + "=" * 70 + "\n")
        except Exception as e:
            print(f"Erro: {e}")
