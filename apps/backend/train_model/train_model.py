import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib


# ============================================================
# Utilidades
# ============================================================

def load_data(file_path: str):
    """Carrega o arquivo JSON e retorna a lista de itens."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_model(vectorizer, clf, file_name: str):
    """Salva o modelo (vetorizador + classificador)."""
    joblib.dump((vectorizer, clf), file_name)
    print(f"✅ Modelo salvo como: {file_name}")


# ============================================================
# Feature Builders (um por tipo de dataset)
# ============================================================

def build_features_transaction(data):
    """
    Dataset 1:
    message → transaction
    """
    X = [item["message"] for item in data]
    y = [item["transaction"] for item in data]
    return X, y


def build_features_type_transaction(data):
    """
    Dataset 2:
    message → type_transaction
    """
    X = [item["message"] for item in data]
    y = [item["type_transaction"] for item in data]
    return X, y


def build_features_category(data):
    """
    Dataset 3:
    message → category
    """
    X = [item["message"] for item in data]
    y = [item["category"] for item in data]
    return X, y


# ============================================================
# Treinar modelo genérico
# ============================================================

def train_model(X, y):
    """
    Treina um modelo TF-IDF + Logistic Regression.
    """
    vectorizer = TfidfVectorizer()
    X_transformed = vectorizer.fit_transform(X)

    clf = LogisticRegression(max_iter=500)
    clf.fit(X_transformed, y)

    return vectorizer, clf


# ============================================================
# Pipeline genérico para cada dataset
# ============================================================

def train_pipeline(json_path: str, feature_builder, output_model: str):
    """
    Carrega dados, monta features, treina e salva modelo.
    """
    print(f"\n📌 Treinando modelo para {output_model}...")

    data = load_data(json_path)
    X, y = feature_builder(data)
    vec, clf = train_model(X, y)
    save_model(vec, clf, output_model)

    print(f"🎉 Modelo '{output_model}' treinado com sucesso!\n")


# ============================================================
# Execução Principal
# ============================================================

if __name__ == "__main__":

    base = r"C:\Users\beand\Documents\SoFIA\SoFiA\docs"

    train_pipeline(
        json_path=f"{base}\classification1.json",
        feature_builder=build_features_transaction,
        output_model="modelo_transaction.pkl"
    )

    train_pipeline(
        json_path=f"{base}\classification2.json",
        feature_builder=build_features_type_transaction,
        output_model="modelo_type_transaction.pkl"
    )

    train_pipeline(
        json_path=f"{base}\classification3.json",
        feature_builder=build_features_category,
        output_model="modelo_category.pkl"
    )
