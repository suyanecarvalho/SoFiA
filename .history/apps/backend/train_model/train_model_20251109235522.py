import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

# ====== 1️⃣ Carregar dados do JSON ======
with open(r"../../../docs/classification.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extrair frases e rótulos
phrases = [item["message"] for item in data]
transaction = [item["transaction"] for item in data]
type_transaction = [item["type_transaction"] for item in data]

# ====== 2️⃣ Treinar modelo ======
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(phrases)

clf = LogisticRegression()
clf.fit(X, rotulos)

# ====== 3️⃣ Salvar modelo treinado ======
joblib.dump((vectorizer, clf), "intent_model.joblib")

print("✅ Modelo treinado e salvo como intent_model.joblib")
