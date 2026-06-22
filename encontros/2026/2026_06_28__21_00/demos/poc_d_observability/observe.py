"""POC D — Observabilidade de RAG: sem logs, não dá para debugar.

Roda uma consulta ponta a ponta (retrieve → rerank → generate) e emite um TRACE
estruturado com tudo que importa para reproduzir e diagnosticar: query, método, top-k,
candidatos + scores, fontes, **versão do índice**, **modelo de embedding**, latência
por etapa e custo (nº de chamadas a embedding/geração). Grava JSONL inspecionável.

Rode:
    python demos/poc_d_observability/observe.py --query "qual o prazo de reembolso?"
    USE_MOCK=1 python demos/poc_d_observability/observe.py
    cat demos/poc_d_observability/.runtime/trace.jsonl | tail -1   # o trace cru
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.ollama_client import make_client  # noqa: E402
from common.observability import RagTrace, Timer, TraceLogger  # noqa: E402
from common.rag_index import RagIndex  # noqa: E402
from common.rerankers import get_reranker  # noqa: E402
from common.tracing import banner, traced  # noqa: E402

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "corpus")
RUNTIME = os.path.join(os.path.dirname(__file__), ".runtime")
SISTEMA = ("Você é um assistente de suporte. Responda em uma frase, só com base no "
           "CONTEXTO, citando a fonte. Se não houver base, diga 'não sei'.")


@traced("pocD.observability")
def main() -> None:
    p = argparse.ArgumentParser(description="Observabilidade de RAG")
    p.add_argument("--query", default="qual é o prazo de reembolso?")
    p.add_argument("--method", default="hybrid", choices=["dense", "lexical", "hybrid"])
    p.add_argument("--reranker", default="llm",
                   choices=["none", "lexical", "llm", "cross", "mmr"])
    p.add_argument("--k", type=int, default=6)
    p.add_argument("--top", type=int, default=3)
    p.add_argument("--tenant", default="mercania")
    args = p.parse_args()

    os.makedirs(RUNTIME, exist_ok=True)
    client = make_client()
    timer = Timer()

    with timer("build_index"):
        index = RagIndex(client, CORPUS_DIR)

    embed_before = client.embed_calls
    with timer("retrieve"):
        cands = index.retrieve(args.query, method=args.method, k=args.k, tenant=args.tenant)
    with timer("rerank"):
        cands = get_reranker(args.reranker)(args.query, list(cands), client=client)
    context = cands[:args.top]

    gen_before = client.gen_calls
    with timer("generate"):
        ctx = "\n".join(f"[fonte: {c.chunk_id}] {c.text}" for c in context)
        answer = client.generate(SISTEMA, f"CONTEXTO:\n{ctx}\n\nPERGUNTA: {args.query}\nRESPOSTA:")

    trace = RagTrace(
        query=args.query, method=args.method, tenant=args.tenant, top_k=args.k,
        index_version=index.index_version,
        embed_model=getattr(client, "embed_model", client.mode),
        gen_model=getattr(client, "gen_model", client.mode),
        candidates=[{"chunk_id": c.chunk_id, "doc_id": c.doc_id,
                     "dense": round(c.dense, 3), "lexical": round(c.lexical, 3),
                     "rerank": round(c.rerank, 3)} for c in cands],
        context_chunk_ids=[c.chunk_id for c in context],
        sources=sorted({c.doc_id for c in context}),
        answer=answer,
        latency_ms={**timer.spans, "total": timer.total()},
        cost={"embed_calls": client.embed_calls, "gen_calls": client.gen_calls,
              "embed_calls_query": client.embed_calls - embed_before,
              "gen_calls_query": client.gen_calls - gen_before},
    )

    logger = TraceLogger(os.path.join(RUNTIME, "trace.jsonl"))
    logger.log(trace)
    print(f"== POC D · Observabilidade ==  modelo={client.mode}")
    print("   Esta POC tem DUAS trilhas de observabilidade:")
    print("   (1) trace JSONL próprio, escrito em .runtime/trace.jsonl (sempre)")
    print(banner().replace("🔭 observabilidade:", "   (2) Phoenix —"))
    print()
    print(TraceLogger.summary(trace))
    print(f"\nTrace completo (JSONL): {os.path.relpath(os.path.join(RUNTIME, 'trace.jsonl'))}")
    print("Em produção: isto vira span OpenTelemetry (GenAI) + dashboards de qualidade, "
          "latência, custo e indexing lag.")


if __name__ == "__main__":
    main()
