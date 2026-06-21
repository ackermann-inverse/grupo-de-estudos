---
marp: true
title: RAG Engineering (parte 2)
description: Recuperar bem, avaliar e observar. RAG é superfície de ataque, não escudo.
author: Ruan Pato
paginate: true
theme: default
---

<!-- _class: lead -->

# 🔎 RAG Engineering (parte 2)

### Recuperar é fácil. Recuperar **bem**, **avaliar** e **observar** é o trabalho.

Continuação de *Context Engineering, RAG & Memória* · Ruan Pato · 28/06/2026

<!--
Speaker: parte 1 deixou RAG como "recuperar contexto externo". Aqui é o retrieval
engineering, com POCs rodáveis. RAG é superfície de ataque (OWASP LLM08), não escudo.
-->

---

## Onde paramos

Parte 1: RAG = **recuperar contexto externo** (fluxo, fontes, filtro por tenant).

Aqui: **embeddings, retrieval, reranking, avaliação, observabilidade, segurança** — tudo rodável.

```bash
make demo   # POC C: harness de avaliação
make test   # 22 testes em MOCK
```

---

## Embeddings

- Embedding de **retrieval ≠ interno** do LLM. Trocar embedding **invalida o índice**.
- **Dimensão custa** (storage/memória/banda). **Matryoshka** permite truncar.
- **Threshold depende do modelo** — não transfere entre embeddings.

> Honesto: no nosso corpus pequeno, truncar até 64 dims **não** doeu (real). Em corpus
> grande, dói. Não generalize de um toy corpus. `make sweep`

---

## POC A — Retrieval: dense × lexical × híbrido

| Método | Brilha | Falha |
|---|---|---|
| Dense | paráfrase, semântica | termo literal (SKU) |
| BM25 | termo exato | sinônimo |
| Híbrido (RRF) | mistura | custo extra |

```bash
make retrieval   # python demos/poc_a_retrieval/retrieval.py
```

---

## POC B — Reranking e MMR

- **lexical** — sobreposição (stand-in) · **llm** — query+doc juntos (sem download) ·
  **cross** — cross-encoder real (opcional, pesado) · **mmr** — diversidade.

```bash
make rerank                 # reranker llm
make extra && make cross    # cross-encoder real (~1–2 GB)
```

> MMR otimiza **diversidade**, não relevância — rebaixa quase-duplicatas.

---

## POC C — RAG evaluation (em camadas)

| Camada | Métrica |
|---|---|
| Retriever | recall@k, MRR, nDCG@k |
| Contexto | context precision/recall |
| Resposta | answer_match, faithfulness (LLM-judge) |

```bash
make eval     # golden set + métricas + queries que falham
make sweep    # recall vs dimensão (Matryoshka)
```

**Golden set + regressão** ao mudar chunking/embedding/top-k/prompt. Nenhuma métrica isolada resolve qualidade.

---

## POC D — Observabilidade

Por consulta: **query · chunks · scores · fontes · versão do índice · embedding · top-k · latência · custo**.

```bash
make observe
tail -1 demos/poc_d_observability/.runtime/trace.jsonl
```

> Sem logs, não dá para debugar RAG. Em produção: span OpenTelemetry (GenAI) + dashboards.

---

## Segurança de RAG

- **OWASP LLM08** — Vector & Embedding Weaknesses.
- Indirect prompt injection, **data/vector poisoning**, source authentication.
- **Permission-aware retrieval** (fail-closed, no storage).

> Dado recuperado **não é instrução**. Mitigação é parcial — limite o blast radius.

---

## POC × Produção

| | POC | Produção |
|---|---|---|
| Índice | em memória | vector DB + ANN |
| Reranker | lexical/llm | cross-encoder |
| Eval | golden pequeno | golden + regressão em CI |
| Obs. | JSONL | OpenTelemetry + dashboards |
| Segurança | demarcação | policy-as-code, RBAC/ABAC, HITL |

---

<!-- _class: lead -->

## Obrigado

`README.md` · `ROTEIRO.md` · `CHECKLIST.md` · `referencias.md` · `make demo`

Próximo tema do grupo: 🛡️ **Segurança, Guardrails & Autorização**
