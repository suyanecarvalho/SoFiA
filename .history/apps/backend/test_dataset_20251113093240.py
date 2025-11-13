#!/usr/bin/env python3
"""
Script de teste para verificar o dataset de classification.json
e diagnosticar a distribuição de classes.
"""
import json
import os
from collections import Counter

# Caminho do dataset
dataset_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "classification.json")

print(f"Carregando dataset de: {dataset_path}")

try:
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ Dataset carregado com sucesso! Total de exemplos: {len(data)}")
except Exception as e:
    print(f"❌ Erro ao carregar dataset: {e}")
    exit(1)

# Análise de distribuição
transactions = [d.get("transaction") for d in data]
types = [d.get("type_transaction") for d in data]
categories = [d.get("category") for d in data]

print("\n=== DISTRIBUIÇÃO DE TRANSACTIONS ===")
trans_counter = Counter(transactions)
for trans, count in trans_counter.most_common():
    print(f"  {trans}: {count}")

print("\n=== DISTRIBUIÇÃO DE TIPOS ===")
type_counter = Counter(types)
for typ, count in type_counter.most_common():
    print(f"  {typ}: {count}")

print("\n=== DISTRIBUIÇÃO DE CATEGORIAS ===")
cat_counter = Counter(categories)
for cat, count in sorted(cat_counter.items(), key=lambda x: x[1], reverse=True)[:20]:
    print(f"  {cat}: {count}")

# Análise de combinações
print("\n=== ANÁLISE: BUSCA + GANHO ===")
busca_ganho = [d for d in data if d.get("transaction") == "busca" and d.get("type_transaction") == "ganho"]
print(f"Exemplos de 'busca' com tipo 'ganho': {len(busca_ganho)}")
for i, example in enumerate(busca_ganho[:5], 1):
    print(f"  {i}. '{example['message']}'")
if len(busca_ganho) > 5:
    print(f"  ... e mais {len(busca_ganho) - 5}")

print("\n=== ANÁLISE: ENTRADA + GANHO ===")
entrada_ganho = [d for d in data if d.get("transaction") == "entrada" and d.get("type_transaction") == "ganho"]
print(f"Exemplos de 'entrada' com tipo 'ganho': {len(entrada_ganho)}")

print("\n=== RESUMO ===")
print(f"Total de 'ganho' (qualquer tipo de transação): {sum(1 for d in data if d.get('type_transaction') == 'ganho')}")
print(f"Total de 'gasto' (qualquer tipo de transação): {sum(1 for d in data if d.get('type_transaction') == 'gasto')}")
print(f"Razão gasto/ganho: {sum(1 for d in data if d.get('type_transaction') == 'gasto') / max(1, sum(1 for d in data if d.get('type_transaction') == 'ganho')):.1f}x")
