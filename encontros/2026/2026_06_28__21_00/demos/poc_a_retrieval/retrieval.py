"""POC A — Retrieval: dense × lexical × híbrido (RRF), lado a lado.

Mostra que NÃO existe método universal: o denso acerta paráfrase/semântica; o lexical
(BM25) acerta termo literal (códigos, SKUs); o híbrido (RRF) funde os dois.

Rode:
    python demos/poc_a_retrieval/retrieval.py --query "qual o prazo de reembolso?"
    python demos/poc_a_retrieval/retrieval.py --query "código da entrega econômica"
    USE_MOCK=1 python demos/poc_a_retrieval/retrieval.py   # sem baixar modelo
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.ollama_client import make_client  # noqa: E402
from common.rag_index import RagIndex  # noqa: E402
from common.tracing import banner, explain_card, traced  # noqa: E402

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "corpus")


@traced("pocA.retrieval")
def main() -> None:
    p = argparse.ArgumentParser(description="Comparação de retrieval")
    p.add_argument("--query", default="qual é o prazo de reembolso?")
    p.add_argument("--k", type=int, default=5)
    p.add_argument("--tenant", default="mercania")
    args = p.parse_args()

    client = make_client()
    print(f"== POC A · Retrieval ==  modelo={client.mode}")
    print(banner())
    print(f"\nENTRADA (query): {args.query}\n")
    index = RagIndex(client, CORPUS_DIR)
    print(f"ÍNDICE: {index.index_version}\n")

    cols = {}
    for method in ("dense", "lexical", "hybrid"):
        cands = index.retrieve(args.query, method=method, k=args.k, tenant=args.tenant)
        cols[method] = cands

    explain_card("RETRIEVAL — COMPARAÇÃO", {
        "query": args.query,
        "tenant": args.tenant,
        "métodos": "dense, lexical, hybrid/RRF",
        "top-k": args.k,
        "index": index.index_version,
        "salvo onde": "nada novo; candidatos ficam em RAM e podem virar trace no Phoenix",
    })

    width = 34
    print(f"{'#':<2} {'dense':<{width}} {'lexical':<{width}} {'hybrid (RRF)':<{width}}")
    print("-" * (width * 3 + 6))
    for i in range(args.k):
        row = []
        for method in ("dense", "lexical", "hybrid"):
            cands = cols[method]
            if i < len(cands):
                c = cands[i]
                row.append(f"{c.chunk_id} ({c.dense:.2f}/{c.lexical:.2f})"[:width].ljust(width))
            else:
                row.append(" " * width)
        print(f"{i+1:<2} {row[0]} {row[1]} {row[2]}")

    dense_top = {c.chunk_id for c in cols["dense"][:args.k]}
    lex_top = {c.chunk_id for c in cols["lexical"][:args.k]}
    so_dense = dense_top - lex_top
    so_lex = lex_top - dense_top
    print("\nLeitura:")
    print(f"  só no DENSE (semântico):  {sorted(so_dense) or '—'}")
    print(f"  só no LEXICAL (literal):  {sorted(so_lex) or '—'}")
    print("  (formato: chunk_id (score_dense/score_lexical), normalizados em [0,1])")
    if client.mode == "mock":
        print("\n[MOCK] embeddings por hashing colapsam dense≈lexical. Rode com Ollama "
              "para ver o contraste semântico real.")


if __name__ == "__main__":
    main()
