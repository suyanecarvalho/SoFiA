#!/usr/bin/env python3
"""
Script de treinamento para modelos de classificação financeira.
Treina três modelos: operação (busca/entrada), tipo (ganho/gasto/investimento) e categoria.
"""
import json
import os
import sys
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import warnings

warnings.filterwarnings("ignore")

# ========== CONFIGURAÇÕES ==========
DATASET_PATH = Path(__file__).parent.parent / "docs" / "classification.json"
OUTPUT_DIR = Path(__file__).parent / "train_model"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"📁 Dataset: {DATASET_PATH}")
print(f"📁 Output: {OUTPUT_DIR}")

# ========== CARREGAMENTO DO DATASET ==========
print("\n📂 Carregando dataset...")
try:
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ {len(data)} exemplos carregados")
except FileNotFoundError:
    print(f"❌ Dataset não encontrado em {DATASET_PATH}")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"❌ Erro ao decodificar JSON: {e}")
    sys.exit(1)

# ========== PRÉ-PROCESSAMENTO ==========
print("\n🔧 Pré-processamento...")

messages = [d.get("message", "").lower() for d in data]
transactions = [str(d.get("transaction", "")).lower() for d in data]
types = [str(d.get("type_transaction", "")).lower() for d in data]
categories = [str(d.get("category", "")).lower() if d.get("category") else "none" for d in data]

# Remover exemplos com dados ausentes críticos
valid_indices = [i for i, (msg, trans, typ) in enumerate(zip(messages, transactions, types))
                 if msg and trans and typ]

messages = [messages[i] for i in valid_indices]
transactions = [transactions[i] for i in valid_indices]
types = [types[i] for i in valid_indices]
categories = [categories[i] for i in valid_indices]

print(f"✅ {len(messages)} exemplos após limpeza")

# Estatísticas
from collections import Counter
print(f"\nDistribuição de classes:")
print(f"  Operações: {dict(Counter(transactions))}")
print(f"  Tipos: {dict(Counter(types))}")

# ========== TREINAMENTO DO VETORIZADOR ==========
print("\n🎯 Treinando vetorizador TF-IDF...")
vectorizer = TfidfVectorizer(
    max_features=500,
    min_df=1,
    max_df=0.95,
    ngram_range=(1, 2),
    lowercase=True,
    stop_words=['o', 'a', 'de', 'do', 'da', 'e', 'é', 'em', 'por'],
)
X = vectorizer.fit_transform(messages)
print(f"✅ Vetorizador treinado. Features: {X.shape[1]}")

# ========== MODELO 1: OPERAÇÃO (busca/entrada) ==========
print("\n🎯 Treinando modelo de operação...")
clf_transaction = LogisticRegression(
    max_iter=200,
    random_state=42,
    class_weight='balanced'
)
clf_transaction.fit(X, transactions)
print(f"✅ Classes: {clf_transaction.classes_}")

# ========== MODELO 2: TIPO (ganho/gasto/investimento) ==========
print("\n🎯 Treinando modelo de tipo...")
clf_type = LogisticRegression(
    max_iter=200,
    random_state=42,
    class_weight='balanced'
)
clf_type.fit(X, types)
print(f"✅ Classes: {clf_type.classes_}")

# ========== MODELO 3: CATEGORIA (apenas para gastos) ==========
print("\n🎯 Treinando modelo de categoria...")
# Filtrar exemplos onde type == 'gasto'
gasto_indices = [i for i, t in enumerate(types) if t == 'gasto']
if gasto_indices:
    X_gasto = X[gasto_indices]
    categories_gasto = [categories[i] for i in gasto_indices]
    
    clf_category = LogisticRegression(
        max_iter=200,
        random_state=42,
        class_weight='balanced'
    )
    clf_category.fit(X_gasto, categories_gasto)
    print(f"✅ Classes (primeiras 10): {list(clf_category.classes_[:10])}")
else:
    clf_category = None
    print("⚠️ Nenhum exemplo de 'gasto' encontrado, pulando treinamento de categoria")

# ========== SALVAMENTO DOS MODELOS ==========
print("\n💾 Salvando modelos...")

files_saved = []
try:
    # Salvar vetorizador com ambos os nomes (compatibilidade)
    vec_paths = [
        OUTPUT_DIR / "vectorizer.joblib",
        OUTPUT_DIR / "vetorizer.joblib",
    ]
    for path in vec_paths:
        joblib.dump(vectorizer, str(path))
        files_saved.append(path.name)
        print(f"  ✅ {path.name}")

    # Modelo de operação/transação
    model_trans_paths = [
        OUTPUT_DIR / "model_operacao.joblib",
        OUTPUT_DIR / "model_transaction.joblib",
    ]
    for path in model_trans_paths:
        joblib.dump(clf_transaction, str(path))
        files_saved.append(path.name)
        print(f"  ✅ {path.name}")

    # Modelo de tipo
    model_type_paths = [
        OUTPUT_DIR / "model_tipo_transacao.joblib",
        OUTPUT_DIR / "model_type_transaction.joblib",
    ]
    for path in model_type_paths:
        joblib.dump(clf_type, str(path))
        files_saved.append(path.name)
        print(f"  ✅ {path.name}")

    # Modelo de categoria (se treinado)
    if clf_category:
        model_cat_paths = [
            OUTPUT_DIR / "model_categoria.joblib",
            OUTPUT_DIR / "model_category.joblib",
        ]
        for path in model_cat_paths:
            joblib.dump(clf_category, str(path))
            files_saved.append(path.name)
            print(f"  ✅ {path.name}")

except Exception as e:
    print(f"❌ Erro ao salvar modelos: {e}")
    sys.exit(1)

print(f"\n✅ Treinamento concluído! {len(files_saved)} arquivos salvos em {OUTPUT_DIR}")

# ========== TESTE RÁPIDO ==========
print("\n🧪 Teste rápido de inferência...")
test_messages = [
    "Quanto eu ganhei este mês",
    "Paguei 50 reais no mercado",
    "Mostre meus ganhos",
]

X_test = vectorizer.transform(test_messages)
for msg in test_messages:
    X_msg = vectorizer.transform([msg])
    trans = clf_transaction.predict(X_msg)[0]
    trans_proba = clf_transaction.predict_proba(X_msg)[0].max()
    typ = clf_type.predict(X_msg)[0]
    typ_proba = clf_type.predict_proba(X_msg)[0].max()
    cat = "N/A"
    if clf_category and typ == 'gasto':
        cat = clf_category.predict(X_msg)[0]
    print(f"\n  Entrada: '{msg}'")
    print(f"    Operação: {trans} ({trans_proba:.1%})")
    print(f"    Tipo: {typ} ({typ_proba:.1%})")
    print(f"    Categoria: {cat}")
