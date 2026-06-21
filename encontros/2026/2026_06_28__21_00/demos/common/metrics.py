"""Métricas de retrieval, puras e testáveis (sem modelo).

Relevância é binária e em nível de DOCUMENTO: um item recuperado é relevante se o seu
`doc_id` está no conjunto esperado (golden). Mantemos as definições explícitas — não
dependa cegamente de uma lib; entenda o que cada número quer dizer.

- recall@k          : dos relevantes, quantos apareceram no top-k.
- precision@k       : do top-k, quantos eram relevantes.
- MRR               : 1/posição do primeiro relevante (média entre queries).
- nDCG@k            : ganho descontado por posição, normalizado pelo ideal.
- context precision : fração do contexto montado que é relevante (precisão no top usado).
- context recall    : fração dos relevantes que entraram no contexto montado.
"""

from __future__ import annotations

import math


def recall_at_k(retrieved_doc_ids: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    top = set(retrieved_doc_ids[:k])
    return len(top & relevant) / len(relevant)


def precision_at_k(retrieved_doc_ids: list[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        return 0.0
    top = retrieved_doc_ids[:k]
    hits = sum(1 for d in top if d in relevant)
    return hits / k


def reciprocal_rank(retrieved_doc_ids: list[str], relevant: set[str]) -> float:
    for i, d in enumerate(retrieved_doc_ids, start=1):
        if d in relevant:
            return 1.0 / i
    return 0.0


def ndcg_at_k(retrieved_doc_ids: list[str], relevant: set[str], k: int) -> float:
    def dcg(ids: list[str]) -> float:
        return sum((1.0 if d in relevant else 0.0) / math.log2(i + 1)
                   for i, d in enumerate(ids[:k], start=1))
    actual = dcg(retrieved_doc_ids)
    # ideal: todos os relevantes primeiro
    ideal_ids = list(relevant) + [d for d in retrieved_doc_ids if d not in relevant]
    ideal = dcg(ideal_ids)
    return actual / ideal if ideal > 0 else 0.0


def context_precision(context_doc_ids: list[str], relevant: set[str]) -> float:
    """Dos trechos efetivamente colocados no contexto, quantos são relevantes."""
    if not context_doc_ids:
        return 0.0
    hits = sum(1 for d in context_doc_ids if d in relevant)
    return hits / len(context_doc_ids)


def context_recall(context_doc_ids: list[str], relevant: set[str]) -> float:
    """Dos relevantes esperados, quantos entraram no contexto montado."""
    if not relevant:
        return 0.0
    present = set(context_doc_ids) & relevant
    return len(present) / len(relevant)


def aggregate(per_query: list[dict]) -> dict:
    """Média de cada métrica sobre as queries (ignora chaves não numéricas)."""
    if not per_query:
        return {}
    keys = [k for k, v in per_query[0].items() if isinstance(v, (int, float))]
    return {k: sum(q[k] for q in per_query) / len(per_query) for k in keys}
