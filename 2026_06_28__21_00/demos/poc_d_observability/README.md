# POC D — Observabilidade de RAG

Roda uma consulta ponta a ponta (retrieve → rerank → generate) e emite um **trace
estruturado** com tudo que importa para reproduzir e diagnosticar.

## Rodar

```bash
python demos/poc_d_observability/observe.py --query "qual o prazo de reembolso?"
tail -1 demos/poc_d_observability/.runtime/trace.jsonl   # o trace cru (JSONL)
USE_MOCK=1 python demos/poc_d_observability/observe.py
```

Flags: `--query`, `--method`, `--reranker`, `--k`, `--top`, `--tenant`.

## O que vai no trace (em [`../common/observability.py`](../common/observability.py))

`query · method · top_k · tenant · index_version · embed_model · gen_model ·
candidatos (chunk_id/doc_id/dense/lexical/rerank) · context_chunk_ids · sources ·
answer · latency_ms (por etapa) · cost (embed_calls/gen_calls)`.

O trace vai para `.runtime/trace.jsonl` (uma linha por consulta; **gitignored**).

## Por que importa

Sem isto, "o RAG respondeu errado" é indebugável. Com o trace você responde: qual a
**versão do índice**? qual **embedding**? quais **scores**? quanto **custou** e
**demorou**? Em produção, isto vira span **OpenTelemetry (GenAI)** + dashboards de
qualidade, latência, custo e indexing lag.
