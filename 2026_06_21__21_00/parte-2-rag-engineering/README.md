# 🔎 Parte 2 — RAG Engineering (extensão)

> **Continuação possível** do encontro [Context Engineering, RAG & Memória](../README.md),
> não obrigação dele. Este material está preparado para virar um **segundo encontro de
> até 1 hora**: copie/mova esta pasta e ajuste o que quiser.

No encontro principal, RAG aparece como **recuperação de contexto externo** — o
essencial: fluxo, fontes/grounding e filtro por tenant. Aqui aprofundamos o
**retrieval engineering**: como recuperar bem, como avaliar, como observar e como
defender. Partimos da POC já existente em [`../demos/poc2_rag/`](../demos/poc2_rag/).

## Sumário

- [Objetivo e pré-requisitos](#objetivo-e-pré-requisitos)
- [1. Embeddings](#1-embeddings)
- [2. Chunking e indexação](#2-chunking-e-indexação)
- [3. Recuperação: dense, lexical, híbrido](#3-recuperação-dense-lexical-híbrido)
- [4. Reranking e diversidade (MMR)](#4-reranking-e-diversidade-mmr)
- [5. Permission-aware retrieval](#5-permission-aware-retrieval)
- [6. Grounding](#6-grounding)
- [7. RAG evaluation](#7-rag-evaluation)
- [8. Observabilidade de RAG](#8-observabilidade-de-rag)
- [9. Segurança de RAG](#9-segurança-de-rag)
- [10. POC didática × arquitetura de produção](#10-poc-didática--arquitetura-de-produção)
- [Referências](#referências)

---

## Objetivo e pré-requisitos

**Objetivo:** sair sabendo recuperar bem, **avaliar** e **observar** um RAG, e
reconhecer onde a POC didática difere de uma arquitetura de produção.

**Pré-requisito:** ter visto a parte 1 (contexto, memória, RAG-essencial) e a
[POC2](../demos/poc2_rag/). Os exemplos de comando abaixo reutilizam aquele código.

---

## 1. Embeddings

- **Embedding de retrieval ≠ embedding interno do LLM.** O modelo de embedding é uma
  **decisão separada** do LLM gerador. Trocar o LLM **não** invalida o índice; trocar
  o **modelo de embedding invalida** o índice e exige reembedding.
- **Dimensionalidade tem custo.** Mais dimensões → mais **storage**, mais **memória**
  no índice ANN, mais **banda** por consulta. 768 dims (nomic) é um bom equilíbrio;
  1536+ pesa em corpus grande.
- **Matryoshka / truncamento de embeddings.** Modelos Matryoshka (MRL) treinam o vetor
  para que os **primeiros** k componentes já sejam úteis — dá para **truncar** (ex.: de
  768 para 256) trocando um pouco de qualidade por muito menos custo. Conceito, não
  aula: avalie o trade-off no seu golden set.
- **Thresholds dependem do modelo.** O baseline de cosseno varia por modelo: `nomic`
  deixa textos curtos sem relação em ~0.4–0.6; um corte de "relevante" que funciona
  para um modelo **não** transfere para outro. (Vimos isso na [POC3](../demos/poc3_memory/),
  onde `sim_min` é específico do embedding.)
- **Open weights × open source × API.** `nomic-embed-text` é Apache-2.0 com **dados
  abertos**; muitos "abertos" são só pesos com restrição; APIs (OpenAI, Cohere) tiram o
  custo de operar mas adicionam dependência e questões de privacidade.

> Demo: `python ../demos/poc2_rag/rag.py --show-scores` mostra os scores densos reais
> com `nomic-embed-text`. Compare com `USE_MOCK=1` (hashing) para ver como o modelo
> muda tudo.

---

## 2. Chunking e indexação

- **Chunking:** fixo (por tokens), semântico (por seção/heading), hierárquico
  (parent/child). **Não há tamanho certo universal** — grande dilui similaridade,
  pequeno perde contexto. Tabelas e listas cortadas no meio são uma fonte clássica de
  erro.
- **Overlap:** sobreposição entre chunks reduz perda de contexto na fronteira, ao custo
  de redundância/armazenamento. (Implementado em [`textutil.chunk_text`](../demos/common/textutil.py).)
- **Metadados:** tenant, idioma, jurisdição, confidencialidade, **validade**, versão,
  fonte, hash. É o que permite **filtrar** e **invalidar** — não só recuperar por
  similaridade.
- **Index versioning:** o índice tem **versão** (modelo de embedding + parâmetros de
  chunking + corpus). Reembedding gera índice novo; promova com **índice paralelo** e
  rollback.
- **Stale index:** documento-fonte muda e o índice não acompanha → resposta obsoleta
  com cara de atual. Monitore **indexing lag** (tempo entre alteração e disponibilidade).

---

## 3. Recuperação: dense, lexical, híbrido

| Método | Brilha | Falha | No código |
|---|---|---|---|
| **Dense** (cosseno de embeddings) | paráfrase, sinônimo, semântica | termo literal (SKU, código), idioma cruzado | [`RagIndex._dense_scores`](../demos/poc2_rag/rag.py) |
| **Lexical / BM25** | termo exato, código, sigla | sinônimo, paráfrase | [`textutil.BM25`](../demos/common/textutil.py) |
| **Híbrido (RRF)** | mistura natural + literal | custo/complexidade; desperdício em corpus homogêneo | [`textutil.rrf`](../demos/common/textutil.py) |

- **BM25** (Robertson & Zaragoza, 2009): tf saturado + idf + normalização por tamanho
  do documento. Implementação mínima e comentada em `textutil.BM25`.
- **RRF** (Cormack et al., 2009): funde **rankings**, não scores — insensível a escala,
  default sensato. `score(d) = Σ 1/(k + rank_r(d))`.

> Demo: compare lado a lado
> `python ../demos/poc2_rag/rag.py --method dense --query "garantia do SKU-4471"` vs
> `--method lexical` (o lexical acerta o código onde o denso erra).

---

## 4. Reranking e diversidade (MMR)

- **Reranking** reordena os top-k com um modelo **mais caro e mais preciso**. O padrão
  é o **cross-encoder**: lê **query + documento juntos** (ex.: `bge-reranker`,
  `mxbai-rerank`), em vez de comparar embeddings independentes.
- **Reranker didático × de produção.** Na [POC2](../demos/poc2_rag/rag.py), `rerank()`
  é um **stand-in** por sobreposição de termos — serve para mostrar a **etapa**, não
  para entregar qualidade. Um cross-encoder real é mais pesado (latência/custo) e
  costuma valer a pena.
- **MMR (Maximal Marginal Relevance):** seleciona itens **relevantes E diversos**, para
  não encher o contexto com 5 quase-duplicatas do mesmo trecho. Trade-off relevância ×
  diversidade por um `λ`. (Foi mantido **fora** do código da parte 1 de propósito — é
  assunto daqui.)

```text
# esboço de MMR (pseudocódigo)
selecionados = []
enquanto faltam e |selecionados| < N:
    para cada candidato i:
        score_i = λ·sim(query, i) − (1−λ)·max_j∈selecionados sim(i, j)
    escolhe o de maior score_i
```

---

## 5. Permission-aware retrieval

- **Filtro por tenant/permissão é no storage, fail-closed** — chunk sem rótulo de
  tenant **não passa** numa consulta tenant-scoped (corrigido na
  [POC2](../demos/poc2_rag/rag.py); `make leak` mostra o vazamento quando desligado).
- **Permission-aware retrieval:** além de tenant, RBAC/ABAC por documento — o retriever
  só devolve o que **aquele usuário** pode ver. Filtro no prompt **não** é segurança.
- **Confused deputy:** cuidado quando o agente recupera com privilégios próprios coisas
  que o usuário não poderia pedir.

---

## 6. Grounding

- **Plausível ≠ correta ≠ suportada.** RAG mira a terceira: cada afirmação ancorada em
  **fonte recuperada e citável**.
- Peça **citação por trecho** e **valide** que a resposta cita as fontes esperadas.
- **No-answer correto:** sem fonte recuperada, a resposta certa é "não sei" — e isso
  deve ser **testado**.

---

## 7. RAG evaluation

Avalie em **camadas**, com **golden set** e **regressão**:

| Camada | Métricas |
|---|---|
| **Retriever** | Recall@k, Precision@k, MRR, nDCG@k |
| **Contexto montado** | context precision / context recall; taxa de truncamento |
| **Resposta final** | faithfulness / groundedness; answer correctness; citation coverage; no-answer correto |
| **Operação** | p95 latência, custo por consulta, freshness/indexing lag |

- **Golden set / eval set:** query + trecho esperado (+ resposta esperada). Por tenant
  e idioma. **Adversarial set:** injeção, OOD, idioma trocado, no-answer.
- **Regressão de qualidade:** ao mudar **chunking, embedding, top-k, reranker ou
  prompt**, rode o golden set antes de promover. Mudança "por intuição" derruba recall
  sem ninguém perceber até o incidente.
- A **"RAG triad"** (context relevance, groundedness, answer relevance) é um bom ponto
  de partida; ferramentas como **Ragas** formalizam — use as **definições**, não
  dependa cegamente da pontuação. **Nenhuma métrica isolada resolve qualidade.**

> Os [testes da parte 1](../tests/) já são um esqueleto de regressão reprodutível
> (`make test`): filtro por tenant fail-closed, invalidação de memória, injeção.

---

## 8. Observabilidade de RAG

Sem logs não dá para debugar RAG. Para **cada consulta**, registre:

- **query** (e query reescrita, se houver);
- **chunks recuperados** + **scores** (denso, lexical, fused, rerank);
- **fontes** (doc id, versão);
- **versão do índice / corpus** e **modelo de embedding**;
- **top-k** e parâmetros;
- **latência** (retrieval, rerank, geração) e **custo** (se fizer sentido).

> A [POC2](../demos/poc2_rag/rag.py) já **imprime** query → candidatos → scores →
> escolhidos → contexto → fontes. Em produção isso vira trace estruturado
> (OpenTelemetry GenAI) e dashboards.

---

## 9. Segurança de RAG

- **OWASP LLM08:2025 — Vector and Embedding Weaknesses:** RAG é **superfície de
  ataque**, não escudo (poisoned embeddings, cross-tenant leakage, embedding inversion).
- **Indirect prompt injection:** documento recuperado com instruções maliciosas
  (demonstrado na [POC4](../demos/poc4_failure/)). Dado recuperado **não é instrução**.
- **Data / vector poisoning:** documento malicioso/ruidoso entra no índice e contamina
  recuperações futuras. Mitigue com validação de ingestão, **provenance**, aprovação de
  fontes novas, isolamento por tenant.
- **Source authentication:** de onde veio o documento? Fonte não verificada é suspeita.
- **Limites reais:** mitigação é **parcial**, não garantia. A defesa que mais vale é
  limitar o **blast radius** depois do modelo (autorização, HITL, egress).

---

## 10. POC didática × arquitetura de produção

| Aspecto | POC desta extensão | Produção |
|---|---|---|
| Índice | em memória, sem ANN | vector DB (Qdrant/Chroma/pgvector) com HNSW/IVF |
| Reranker | sobreposição de termos | cross-encoder dedicado |
| Reembedding | a cada execução (ineficiente, didático) | índice paralelo + promoção + rollback |
| Eval | testes mock + golden pequeno | golden por tenant/idioma + regressão em CI |
| Observabilidade | `print` do pipeline | trace estruturado + dashboards |
| Segurança | demarcação + guarda de saída | policy-as-code, RBAC/ABAC, egress, HITL |

> O ponto da extensão **não** é virar um produto — é mostrar **onde** a POC didática
> para e o que muda quando o sistema vira software crítico.

---

## Referências

Ver [`referencias.md`](./referencias.md) (papers, specs e docs oficiais, com datas de
acesso). Roteiro de 1h em [`ROTEIRO.md`](./ROTEIRO.md) e checklist em
[`CHECKLIST.md`](./CHECKLIST.md).
