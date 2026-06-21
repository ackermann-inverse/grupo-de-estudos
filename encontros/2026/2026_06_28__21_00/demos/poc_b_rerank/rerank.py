"""POC B — Reranking e diversidade (MMR).

Recupera um top-k híbrido e reordena com um reranker escolhido, mostrando a ordem
ANTES e DEPOIS:

- none    : sem rerank (baseline)
- lexical : sobreposição de termos (stand-in barato)
- llm     : LLM local pontua relevância query×doc (cross-encoder na essência; padrão)
- cross   : cross-encoder real (sentence-transformers; OPCIONAL, pesado)
- mmr     : diversidade (Maximal Marginal Relevance), não relevância

Rode:
    python demos/poc_b_rerank/rerank.py --reranker llm   --query "prazo de reembolso"
    python demos/poc_b_rerank/rerank.py --reranker mmr   --query "reembolso pix estorno"
    python demos/poc_b_rerank/rerank.py --reranker cross --query "garantia SKU-4471"  # precisa requirements-extra
    USE_MOCK=1 python demos/poc_b_rerank/rerank.py       # llm cai para lexical (determinístico)
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.ollama_client import make_client  # noqa: E402
from common.rag_index import RagIndex  # noqa: E402
from common.rerankers import get_reranker  # noqa: E402

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "corpus")


def main() -> None:
    p = argparse.ArgumentParser(description="Reranking e diversidade")
    p.add_argument("--query", default="prazo de reembolso e estorno no cartão")
    p.add_argument("--reranker", choices=["none", "lexical", "llm", "cross", "mmr"],
                   default="llm")
    p.add_argument("--k", type=int, default=6, help="top-k recuperado (entrada do rerank)")
    p.add_argument("--top", type=int, default=3, help="top final após rerank")
    p.add_argument("--tenant", default="mercania")
    args = p.parse_args()

    client = make_client()
    index = RagIndex(client, CORPUS_DIR)
    print(f"== POC B · Rerank ({args.reranker}) ==  modelo={client.mode}\n")
    print(f"QUERY: {args.query}\n")

    cands = index.retrieve(args.query, method="hybrid", k=args.k, tenant=args.tenant)
    antes = [c.chunk_id for c in cands]

    rerank = get_reranker(args.reranker)
    try:
        reordered = rerank(args.query, list(cands), client=client)
    except RuntimeError as e:  # cross-encoder sem dependência instalada
        print(f"[erro] {e}")
        return
    depois = [c.chunk_id for c in reordered]

    print("ORDEM ANTES (híbrido):")
    for i, cid in enumerate(antes, 1):
        print(f"  {i}. {cid}")
    print(f"\nORDEM DEPOIS ({args.reranker}):")
    for i, c in enumerate(reordered, 1):
        marca = "  <- entra no contexto" if i <= args.top else ""
        print(f"  {i}. {c.chunk_id}  (rerank={c.rerank:.3f}){marca}")

    if antes[:args.top] != depois[:args.top]:
        print(f"\nO rerank MUDOU o top-{args.top}: {antes[:args.top]} -> {depois[:args.top]}")
    else:
        print(f"\nO top-{args.top} não mudou nesta query.")
    if args.reranker == "mmr":
        print("Obs.: MMR otimiza DIVERSIDADE, não relevância — pode rebaixar uma "
              "quase-duplicata mesmo sendo relevante.")
    if args.reranker == "llm" and client.mode == "mock":
        print("[MOCK] llm-reranker caiu para lexical (determinístico). Use Ollama para "
              "o reranker por LLM de verdade.")


if __name__ == "__main__":
    main()
