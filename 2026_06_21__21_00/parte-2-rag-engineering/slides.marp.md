---
marp: true
title: Parte 2 — RAG Engineering
description: Recuperar bem, avaliar e observar. RAG é superfície de ataque, não escudo.
author: Ruan Pato
paginate: true
theme: default
---

<!-- _class: lead -->

# 🔎 Parte 2 — RAG Engineering

### Recuperar é fácil. Recuperar **bem**, **avaliar** e **observar** é o trabalho.

Continuação de *Context Engineering, RAG & Memória* · Ruan Pato

---

## Onde paramos

Na parte 1: RAG = **recuperar contexto externo** (fluxo, fontes, filtro por tenant).

Aqui: embeddings, retrieval, reranking, **avaliação**, **observabilidade**, **segurança**.

> RAG é **superfície de ataque**, não escudo (OWASP LLM08).

---

## Embeddings

- Embedding de **retrieval ≠ interno** do LLM. Trocar embedding **invalida o índice**.
- **Dimensão tem custo** (storage/memória/banda). **Matryoshka** permite truncar.
- **Threshold depende do modelo** — não transfere entre embeddings.

---

## Recuperação: dense × lexical × híbrido

| Método | Brilha | Falha |
|---|---|---|
| Dense | paráfrase, semântica | termo literal (SKU) |
| BM25 | termo exato | sinônimo |
| Híbrido (RRF) | mistura | custo extra |

```bash
python ../demos/poc2_rag/rag.py --method lexical --query "garantia do SKU-4471"
```

---

## Reranking e MMR

- **Reranker didático** (sobreposição) × **cross-encoder** de produção (lê query+doc).
- **MMR**: relevante **E** diverso — evita 5 quase-duplicatas no contexto.

> Trade-off latência/qualidade. Cross-encoder costuma valer a pena.

---

## RAG evaluation (em camadas)

| Camada | Métrica |
|---|---|
| Retriever | recall@k, nDCG@k |
| Contexto | context precision/recall |
| Resposta | faithfulness, citation coverage |

**Golden set + regressão** ao mudar chunking/embedding/top-k/prompt.
Nenhuma métrica isolada resolve qualidade.

---

## Observabilidade

Logar por consulta: **query · chunks · scores · fontes · versão do índice · modelo de
embedding · top-k · latência · custo**.

> Sem logs, não dá para debugar RAG. A POC2 já imprime tudo isso.

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
| Reranker | didático | cross-encoder |
| Eval | mock + golden pequeno | golden + regressão em CI |
| Segurança | demarcação | policy-as-code, RBAC/ABAC, HITL |

---

<!-- _class: lead -->

## Obrigado

`parte-2-rag-engineering/` — README · ROTEIRO · CHECKLIST · referencias

Próximo tema do grupo: 🛡️ **Segurança, Guardrails & Autorização**
