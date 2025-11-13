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
category= [item.get("category") for item in data]

# ====== 2️⃣ Treinar modelos ======
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(phrases)

clf_transaction = LogisticRegression()
clf_transaction.fit(X, transaction)

clf_type = LogisticRegression()
clf_type.fit(X, type_transaction)

# treinar modelo para categoria e Filtrar apenas as entradas com categoria não nula
data_category = [(phrases[i], category[i]) for i in range(len(phrases)) if category[i] is not None]

if data_category > 5:
    phrases_cat= [d[0] for d in data_category] 
    category_cat = [d[1] for d in data_category]
    
    X_cat = vectorizer.transform(phrases_cat)
    clf_category = LogisticRegression()
    clf_category.fit(X_cat, category_cat)
    print(f"✅ Modelo de categoria treinado com {len(data_category)} exemplos.")
else:
    clf_category = None
    print("⚠️ Dados insuficientes para treinar o modelo de categoria.")
    
# ====== 3️⃣ Salvar modelo treinado ======
joblib.dump((vectorizer), "vetorizer.joblib")
joblib.dump((clf), "vetorizer.joblib")

print("✅ Modelo treinado e salvo como intent_model.joblib")
