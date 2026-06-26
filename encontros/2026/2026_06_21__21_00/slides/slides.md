---
marp: true
title: Context Engineering, RAG & Memória
description: O problema não é prompt, é contexto. Context Engineering → Memória → RAG
author: Ruan Pato
paginate: true
theme: grupo-estudos
---

<!-- _class: lead -->

# Context Engineering, RAG & Memória

### O problema não é **prompt**. É **contexto**.

Context Engineering → Memória → RAG

Ruan Pato · 21/06/2026 · Grupo de Estudos

<!--
Speaker: encontro crítico de propósito. Ordem editorial: contexto e memória primeiro;
RAG é um caso específico (recuperar contexto externo). Cada claim forte tem fonte.
As demos mostram falhas, não só happy paths.
-->

---

## Por que esta ordem

- "Memória" virou **guarda-chuva** para coisas diferentes.
- RAG ≠ memória. Histórico ≠ estratégia de memória.
- "Tudo no prompt" ≠ context engineering.
- **RAG é recuperar contexto externo** — um caso da pergunta maior.

> Que informação entra no contexto, de onde vem, quanto dura, quem pode ver,
> como é validada e quando descartar?

<!-- Speaker: justifique a ordem Context → Memória → RAG. -->

---

## 1. Taxonomia (o alicerce)

| Conceito | Origem |
|---|---|
| Conhecimento paramétrico, janela de contexto, RAG | Categoria de IA |
| Semântica / episódica / procedural | Ciência cognitiva (Tulving) |
| Working / curto / longo prazo | Analogia (cognição) |
| Estado de sessão, cache, artefatos, workflow | Engenharia clássica |

**Não há taxonomia canônica única** — a indústria diverge. Adotamos esta.

<!-- Speaker: Checkpoint 1 — peça um exemplo de cada no sistema da plateia. -->

---

## 2. Context Engineering

**Prompt eng.:** como pedir melhor?
**Context eng.:** o que entra, em que ordem, com qual orçamento e proveniência?

Oito verbos: **seleção · transformação · ordenação · isolamento · autorização · atualização · observabilidade · avaliação**

- *Lost in the middle* (Liu et al., 2023): meio do contexto é mal usado.
- *Context rot* + **compactação** (Anthropic, 2025).
- **Selecionar > encher.**

---

## 🧪 POC1 — Context Assembly

Mesma pergunta, dois contextos, mesmas fontes:

```text
Ingênuo:       O prazo de reembolso é de 7 dias.     (OBSOLETO ❌)
Com critérios: ...30 dias corridos... [politica-reembolso v2] ✅
```

A diferença **não foi o modelo** — foi a montagem (conflito, recência, bookend, proveniência).

`make poc1`

---

## 3. Memória = sistema com operações

**Memória não é "guardar tudo".**

**escrever · recuperar · atualizar · consolidar · resumir · invalidar · expirar · esquecer · auditar · autorizar · corrigir**

- Escrita: memorize **fato confirmado**, não palpite do modelo.
- Recuperação: similaridade **não basta** — recência, importância, autorização, threshold.
- Sem invalidar/expirar/esquecer → **passivo**.

<!-- Speaker: MemGPT, LoCoMo, Mem0 — evidência parcial, não verdade universal. -->

---

## 🧪 POC3 — Lifecycle de memória

```text
CASO 1  preferência útil recuperada            ✅
CASO 2  pergunta irrelevante → nada recuperado ✅
CASO 3  endereço mudou → antigo INVALIDADO     ✅
CASO 4  dump_all → endereço ANTIGO (errado) ❌ | seletivo → vigente ✅
FORGET  direito ao esquecimento + auditoria
```

`make poc3`

---

## 4. RAG = recuperar contexto externo

Agora sim — **sob as mesmas regras** (proveniência, autorização, atualização):

```text
query → recuperação → filtro tenant → contexto (com fontes) → resposta citada
```

- **A maioria dos problemas está FORA do LLM** (ingestão, parsing, índice).
- RAG **não** elimina alucinação; pode trazer doc errado/obsoleto/**de outro tenant**.

---

## 🧪 POC2 — RAG visível (compacta)

`query → candidatos → escolhidos → contexto → resposta → fontes`

```text
fontes citadas + grounding
--no-tenant-filter → vaza doc do atacado-norte ⚠️
```

> Filtro de tenant é **fail-closed**, no **storage**, não no prompt.

`make poc2` · `make leak`

---

## ⏸️ Como saber se o RAG está funcionando?

Três camadas — não basta "a resposta pareceu boa":

1. **Retriever** achou os documentos certos?
2. **Contexto montado** colocou evidência suficiente e pouco ruído?
3. **Resposta final** ficou **fiel** (grounded) ao contexto?

> Plausível ≠ correta ≠ **suportada por fontes**.

---

## 🧭 RAG Engineering fica para a **parte 2**

`parte-2-rag-engineering/` (possível 2º encontro de até 1h):

- embeddings, dimensionalidade, Matryoshka, thresholds
- chunking, *index versioning*, dense/lexical/BM25, híbrido/RRF, MMR, reranking
- RAG evaluation (recall@k, context precision/recall, faithfulness, golden set)
- observabilidade e segurança (OWASP **LLM08**, poisoning, source auth)

---

## 5. Contexto × Estado × Memória

| | Dono | Ciclo | Fronteira |
|---|---|---|---|
| Contexto | App | 1 chamada | instrução×dado |
| Estado WF | Orquestrador | 1 execução | por execução |
| Histórico | App | 1 sessão+ | por sessão |
| Conhecimento (RAG) | KB | versão do índice | por tenant (storage) |
| Memória | Sistema mem. | longo, TTL | por usuário/tenant |
| Dados de negócio | Domínio | permanente | **fonte de verdade** |

---

## 6. Segurança (ponte → tema 2)

- **Indirect prompt injection** via documento recuperado = vetor de produção.
- **Não existe defesa completa** (Greshake 2023; OWASP **LLM01:2025**).
- OWASP **LLM08:2025** — Vector & Embedding Weaknesses: RAG é **superfície de ataque**.
- Vazamento cross-tenant, poisoning, memória falsa.

> Dado recuperado **não é instrução confiável**. Limite o **blast radius**.

---

## 🧪 POC4 — Injeção indireta + mitigação parcial

```text
INGÊNUO   → "PWNED-7Q2"  (obedeceu) ❌ ; guarda de saída bloqueia
MITIGADO  → demarcação evita obediência ✅
PORÉM     → o doc envenenado CONTINUA sendo recuperado ⚠️
```

Mitigar injeção **não** conserta o retrieval. `make poc4`

---

## 7. Avaliação (em 1 minuto)

Avalie o **pipeline por etapas**, não só a resposta:
**retriever → contexto montado → resposta fiel**. E memória: certa? falso positivo?

`make test` = exemplo reprodutível (fail-closed tenant, invalidação, injeção).

> Métricas formais (recall@k, faithfulness, golden set) → **parte 2**.
> Nenhuma métrica isolada "resolve" qualidade.

---

## Conclusões

1. O problema não é prompt — é **contexto**.
2. **Memória exige esquecimento** (invalidar/expirar/auditar).
3. **RAG é recuperação de contexto externo** — falha **fora** do LLM.
4. **Seleção > acúmulo.**
5. **Não há bala de prata** (nem GraphRAG, nem long-context, nem framework).

---

<!-- _class: lead -->

## Obrigado

Material: `README.md` · Roteiro: `ROTEIRO.md` · Demos: `make demo`

Continuação: 🔎 **`parte-2-rag-engineering/`** (RAG Engineering)
Próximo tema sugerido: 🛡️ **Segurança, Guardrails & Autorização**
