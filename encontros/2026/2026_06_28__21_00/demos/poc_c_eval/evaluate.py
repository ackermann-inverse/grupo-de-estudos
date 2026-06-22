"""POC C — RAG evaluation harness (avaliação em camadas, reprodutível).

Roda um golden set (demos/golden/golden.jsonl) e mede:
  - retriever: recall@k, precision@k, MRR, nDCG@k
  - contexto montado: context precision / context recall
  - resposta: answer_match (substring esperada — proxy determinístico de correção)
  - (opcional) faithfulness via LLM-as-judge (--faithfulness, exige Ollama)

Extra: --dims-sweep mostra recall@k vs dimensão do embedding (truncamento Matryoshka),
o trade-off custo × qualidade.

Rode:
    python demos/poc_c_eval/evaluate.py
    python demos/poc_c_eval/evaluate.py --rerank llm --k 5
    python demos/poc_c_eval/evaluate.py --dims-sweep
    python demos/poc_c_eval/evaluate.py --faithfulness        # precisa Ollama
    USE_MOCK=1 python demos/poc_c_eval/evaluate.py            # determinístico, sem modelo
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import metrics  # noqa: E402
from common.ollama_client import make_client  # noqa: E402
from common.rag_index import RagIndex  # noqa: E402
from common.rerankers import get_reranker  # noqa: E402
from common.tracing import banner, traced  # noqa: E402

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "corpus")
GOLDEN = os.path.join(os.path.dirname(__file__), "..", "golden", "golden.jsonl")
SISTEMA = (
    "Você é um assistente de suporte. Responda em uma frase, só com base no CONTEXTO, "
    "citando a fonte. Se não houver base, diga 'não sei'."
)


def load_golden(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _dedup(seq: list[str]) -> list[str]:
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x); out.append(x)
    return out


def eval_query(index, gold, *, k, top, reranker, client, do_answer) -> dict:
    cands = index.retrieve(gold["query"], method="hybrid", k=k,
                           tenant=gold.get("tenant"))
    if reranker != "none":
        cands = get_reranker(reranker)(gold["query"], list(cands), client=client)
    retrieved_docs = _dedup([c.doc_id for c in cands])
    context = cands[:top]
    context_docs = _dedup([c.doc_id for c in context])
    relevant = set(gold["relevant_doc_ids"])

    row = {
        "recall@k": metrics.recall_at_k(retrieved_docs, relevant, k),
        "precision@k": metrics.precision_at_k(retrieved_docs, relevant, k),
        "mrr": metrics.reciprocal_rank(retrieved_docs, relevant),
        "ndcg@k": metrics.ndcg_at_k(retrieved_docs, relevant, k),
        "ctx_precision": metrics.context_precision(context_docs, relevant),
        "ctx_recall": metrics.context_recall(context_docs, relevant),
    }
    if do_answer:
        ctx = "\n".join(f"[fonte: {c.chunk_id}] {c.text}" for c in context)
        ans = client.generate(SISTEMA, f"CONTEXTO:\n{ctx}\n\nPERGUNTA: {gold['query']}\nRESPOSTA:")
        row["answer_match"] = 1.0 if gold["answer_substr"].lower() in ans.lower() else 0.0
        row["_answer"] = ans
    return row


def run(index, golden, *, k, top, reranker, client, do_answer) -> tuple[list, dict]:
    rows = [eval_query(index, g, k=k, top=top, reranker=reranker, client=client,
                       do_answer=do_answer) for g in golden]
    return rows, metrics.aggregate([{kk: vv for kk, vv in r.items()
                                     if not kk.startswith("_")} for r in rows])


def _print_agg(title: str, agg: dict) -> None:
    print(f"\n== {title} ==")
    for kk, vv in agg.items():
        print(f"  {kk:<14} {vv:.3f}")


@traced("pocC.eval")
def main() -> None:
    p = argparse.ArgumentParser(description="RAG evaluation harness")
    p.add_argument("--k", type=int, default=5)
    p.add_argument("--top", type=int, default=3)
    p.add_argument("--rerank", choices=["none", "lexical", "llm", "cross", "mmr"],
                   default="none")
    p.add_argument("--dims-sweep", action="store_true",
                   help="recall@k vs dimensão do embedding (Matryoshka)")
    p.add_argument("--faithfulness", action="store_true",
                   help="mede faithfulness via LLM-as-judge (exige Ollama)")
    args = p.parse_args()

    client = make_client()
    golden = load_golden(GOLDEN)
    print(f"== POC C · RAG eval ==  modelo={client.mode} | {len(golden)} queries | "
          f"k={args.k} top={args.top} rerank={args.rerank}")
    print(banner())

    if args.dims_sweep:
        print("\nMatryoshka — recall@k e nDCG@k por dimensão de embedding:")
        print(f"  {'dims':<8}{'recall@k':<12}{'ndcg@k':<12}{'ctx_recall':<12}")
        for dims in (None, 256, 128, 64):
            idx = RagIndex(client, CORPUS_DIR, embed_dims=dims)
            _, agg = run(idx, golden, k=args.k, top=args.top, reranker=args.rerank,
                         client=client, do_answer=False)
            label = "full" if dims is None else str(dims)
            print(f"  {label:<8}{agg['recall@k']:<12.3f}{agg['ndcg@k']:<12.3f}{agg['ctx_recall']:<12.3f}")
        print("Leitura: truncar dimensão reduz custo de storage/memória; observe quanto "
              "a qualidade cai (e se compensa).")
        return

    index = RagIndex(client, CORPUS_DIR)
    rows, agg = run(index, golden, k=args.k, top=args.top, reranker=args.rerank,
                    client=client, do_answer=True)
    _print_agg(f"Agregado (retriever + contexto + resposta)", agg)

    falhas = [(g["query"], r) for g, r in zip(golden, rows) if r.get("answer_match") == 0.0]
    if falhas:
        print(f"\n{len(falhas)} query(s) sem answer_match (candidatas a regressão):")
        for q, r in falhas[:5]:
            print(f"  - {q}  -> {r.get('_answer','')[:70]!r}")

    if args.faithfulness:
        _faithfulness(client, index, golden, top=args.top)

    print("\nUse este harness como REGRESSÃO: rode antes de promover mudança em "
          "chunking, embedding, top-k, reranker ou prompt.")


def _faithfulness(client, index, golden, *, top) -> None:
    if client.mode == "mock":
        print("\n[faithfulness] indisponível em MOCK (precisa de um juiz LLM). Pulei.")
        return
    judge_sys = ("Você é um juiz. Dada uma RESPOSTA e o CONTEXTO, responda só JSON "
                 "{\"supported\": true|false}: a resposta é inteiramente suportada pelo contexto?")
    scores = []
    for g in golden:
        cands = index.retrieve(g["query"], method="hybrid", k=5, tenant=g.get("tenant"))[:top]
        ctx = "\n".join(c.text for c in cands)
        ans = client.generate(SISTEMA, f"CONTEXTO:\n{ctx}\n\nPERGUNTA: {g['query']}\nRESPOSTA:")
        verd = client.generate(judge_sys, f"CONTEXTO:\n{ctx}\n\nRESPOSTA:\n{ans}", json_format=True)
        scores.append(1.0 if '"supported": true' in verd.lower() or '"supported":true' in verd.lower() else 0.0)
    print(f"\n[faithfulness] (LLM-as-judge) suportadas: {sum(scores):.0f}/{len(scores)} "
          f"= {sum(scores)/len(scores):.2f}")


if __name__ == "__main__":
    main()
