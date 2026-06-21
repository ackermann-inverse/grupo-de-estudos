# Demos — RAG Engineering (parte 2)

Quatro POCs **rodáveis** que aprofundam o retrieval. Sem framework: tudo à mão em
[`common/`](common/) (chunking, cosseno, BM25, RRF, MMR, métricas, observabilidade).
Reaproveitam o mesmo "vault" da parte 1 ([`corpus/`](corpus/)) + um **golden set**
([`golden/golden.jsonl`](golden/golden.jsonl)).

| POC | Pasta | Demonstra |
|---|---|---|
| **A. Retrieval** | [`poc_a_retrieval/`](poc_a_retrieval/) | dense × lexical × híbrido (RRF), lado a lado |
| **B. Rerank** | [`poc_b_rerank/`](poc_b_rerank/) | lexical / **llm** / **cross-encoder real** / **MMR** |
| **C. Eval** | [`poc_c_eval/`](poc_c_eval/) | recall@k/MRR/nDCG/context + faithfulness + Matryoshka sweep |
| **D. Observability** | [`poc_d_observability/`](poc_d_observability/) | trace JSONL (query/scores/fontes/versão/latência/custo) |

## Como rodar

```bash
make setup            # venv + deps
make demo             # POC C (avaliação) — demo principal
make retrieval rerank eval sweep observe   # cada POC
USE_MOCK=1 python demos/poc_a_retrieval/retrieval.py   # sem Ollama
```

## Módulos compartilhados ([`common/`](common/))

| Módulo | Papel |
|---|---|
| `ollama_client.py` | cliente Ollama (embed/chat) + **MOCK** determinístico + contadores de custo |
| `textutil.py` | tokenização, chunking, cosseno, **BM25**, **RRF**, **MMR** |
| `corpus.py` | carrega o vault Markdown + frontmatter |
| `rag_index.py` | índice (dense/lexical/hybrid), **tenant fail-closed**, **truncamento Matryoshka**, `index_version` |
| `rerankers.py` | lexical / llm / cross-encoder (opcional) / mmr |
| `metrics.py` | recall@k, precision@k, MRR, nDCG@k, context precision/recall |
| `observability.py` | `RagTrace`, `Timer`, `TraceLogger` (JSONL) |

## Os três modos do modelo

Igual à parte 1: **Ollama real** (demonstração), **fallback automático** para MOCK se o
Ollama cair, e **`USE_MOCK=1`** (determinístico, para testes/offline — não substitui a
execução real). O **cross-encoder real** (POC B `--reranker cross`) é opcional e exige
`make extra` (`requirements-extra.txt`, ~1–2 GB com torch).
