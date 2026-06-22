# 🔎 RAG Engineering (parte 2)

| Data | Apresentador |
|-:|:-|
| 28/06/2026 21:00 | [Ruan Pato](https://ruanpato.com) |

> **Continuação** do encontro [Context Engineering, RAG & Memória](../2026_06_21__21_00/README.md).
> Lá, RAG apareceu como **recuperar contexto externo** (o essencial: fluxo, fontes,
> filtro por tenant). Aqui aprofundamos o **retrieval engineering**: recuperar **bem**,
> **avaliar**, **observar** e **defender** — com POCs **rodáveis**.

> **Tese:** recuperar é fácil; recuperar bem, medir e observar é o trabalho. E RAG é
> **superfície de ataque**, não escudo.

## Sumário

- [🧭 0. Objetivo, público e como rodar](#-0-objetivo-público-e-como-rodar)
- [🧬 1. Embeddings (dimensionalidade, Matryoshka, thresholds)](#-1-embeddings-dimensionalidade-matryoshka-thresholds)
- [✂️ 2. Chunking e indexação](#️-2-chunking-e-indexação)
- [🔀 3. Retrieval: dense, lexical, híbrido — POC A](#-3-retrieval-dense-lexical-híbrido--poc-a)
- [🎯 4. Reranking e diversidade (MMR) — POC B](#-4-reranking-e-diversidade-mmr--poc-b)
- [🔐 5. Permission-aware retrieval](#-5-permission-aware-retrieval)
- [📐 6. RAG evaluation — POC C](#-6-rag-evaluation--poc-c)
- [🔭 7. Observabilidade — POC D](#-7-observabilidade--poc-d)
- [🛡️ 8. Segurança de RAG](#️-8-segurança-de-rag)
- [🏭 9. POC didática × produção](#-9-poc-didática--produção)
- [📚 10. Referências, roteiro e checklist](#-10-referências-roteiro-e-checklist)

---

## 🧭 0. Objetivo, público e como rodar

**Objetivo:** sair sabendo **recuperar bem, avaliar e observar** um RAG, e reconhecer
onde a POC didática difere de uma arquitetura de produção.

**Público / pré-requisito:** quem viu a parte 1 (contexto, memória, RAG-essencial).
Mesma filosofia: **sem framework** (chunking, cosseno, BM25, RRF, MMR à mão em
[`demos/common/`](./demos/common/)); roda em **CPU**, com **Ollama** ou em **MOCK**
determinístico (`USE_MOCK=1`).

```bash
make setup           # venv + deps; orienta o pull dos modelos
make demo            # POC C — harness de avaliação (demo principal)
make test            # 22 testes em MOCK (sem baixar modelo)

make retrieval       # POC A — dense × lexical × híbrido
make rerank          # POC B — reranking por LLM
make sweep           # POC C — recall@k vs dimensão (Matryoshka)
make observe         # POC D — trace estruturado de uma consulta
make extra && make cross   # cross-encoder REAL (opcional, ~1–2 GB)
```

**As 4 POCs (rodáveis):**

| POC | Pasta | Demonstra | `make` |
|---|---|---|---|
| **A** | [`poc_a_retrieval/`](./demos/poc_a_retrieval/) | dense × lexical × híbrido (RRF) | `retrieval` |
| **B** | [`poc_b_rerank/`](./demos/poc_b_rerank/) | reranking (lexical/llm/cross) + MMR | `rerank` / `cross` |
| **C** | [`poc_c_eval/`](./demos/poc_c_eval/) | golden set, recall@k/MRR/nDCG/context, faithfulness, Matryoshka sweep | `eval` / `sweep` |
| **D** | [`poc_d_observability/`](./demos/poc_d_observability/) | trace JSONL: query/chunks/scores/fontes/versão do índice/latência/custo | `observe` |

---

## 🧬 1. Embeddings (dimensionalidade, Matryoshka, thresholds)

- **Retrieval ≠ embedding interno do LLM.** O modelo de embedding é decisão **separada**
  do LLM gerador. Trocar o LLM **não** invalida o índice; trocar o **embedding invalida**
  e exige reembedding.
- **Dimensão custa.** Mais dims → mais storage, memória de índice e banda por consulta.
  768 (nomic) é um bom equilíbrio.
- **Matryoshka (MRL):** modelos treinam o vetor para que o **prefixo** já seja útil — dá
  para **truncar** (768→256→128→64) trocando qualidade por custo. Veja com `make sweep`.
  > **Nuance honesta observada:** no **nosso corpus pequeno e fácil**, truncar até 64
  > dims **não** derrubou o recall@5 (real); o efeito de queda aparece em corpus grande/
  > queries difíceis. No MOCK (hashing), a queda aparece já em 128/64 por colisão — é
  > artefato do mock. Não generalize de um corpus de brinquedo.
- **Thresholds dependem do modelo.** O baseline de cosseno do `nomic` é alto; um corte
  de "relevante" calibrado para um embedding **não** transfere para outro (vimos isso na
  memória da parte 1).

---

## ✂️ 2. Chunking e indexação

- **Chunking** fixo/semântico/hierárquico; **não há tamanho certo universal**. **Overlap**
  reduz perda na fronteira ao custo de redundância. (Em [`textutil.chunk_text`](./demos/common/textutil.py).)
- **Metadados** (tenant, idioma, validade, versão, fonte, hash) são o que permite
  **filtrar** e **invalidar** — não só recuperar por similaridade.
- **Index versioning:** o índice tem **versão** = modelo de embedding + chunking + dims +
  corpus. A POC expõe isso em `index_version` (visível na [POC D](./demos/poc_d_observability/)).
- **Stale index:** fonte muda e o índice não acompanha → resposta obsoleta com cara de
  atual. Monitore **indexing lag**.

---

## 🔀 3. Retrieval: dense, lexical, híbrido — POC A

| Método | Brilha | Falha |
|---|---|---|
| **Dense** (cosseno) | paráfrase, semântica | termo literal (SKU, código) |
| **Lexical/BM25** | termo exato, sigla | sinônimo, paráfrase |
| **Híbrido (RRF)** | mistura | custo/complexidade extra |

- **BM25** (Robertson & Zaragoza): tf saturado + idf + normalização por tamanho.
- **RRF** (Cormack et al.): funde **rankings**, não scores — insensível a escala.

```bash
python demos/poc_a_retrieval/retrieval.py --query "código da entrega econômica"   # lexical ganha
python demos/poc_a_retrieval/retrieval.py --query "como devolvo e recebo de volta" # dense ganha
```

> Em MOCK os embeddings por hashing colapsam dense≈lexical; rode com Ollama para o
> contraste semântico real.

---

## 🎯 4. Reranking e diversidade (MMR) — POC B

- **Reranking** reordena o top-k com um sinal mais caro/preciso. Estratégias:
  - **lexical** — sobreposição de termos (stand-in barato, o da parte 1);
  - **llm** — LLM local pontua relevância query×doc (**cross-encoder na essência**, sem
    download novo; **padrão** deste encontro);
  - **cross** — cross-encoder **real** (sentence-transformers, **opcional**, ~1–2 GB);
  - **mmr** — **diversidade**, não relevância: evita quase-duplicatas no contexto.

```bash
python demos/poc_b_rerank/rerank.py --reranker llm  --query "prazo de reembolso e estorno"
python demos/poc_b_rerank/rerank.py --reranker mmr  --query "reembolso pix estorno"   # diversifica
make extra && python demos/poc_b_rerank/rerank.py --reranker cross --query "garantia SKU-4471"
```

> **Didático × produção:** o reranker **lexical** é um stand-in; o **cross-encoder** lê
> query+doc juntos e é bem mais preciso (e pesado). O **llm-reranker** é um meio-termo
> que roda sem download novo.

---

## 🔐 5. Permission-aware retrieval

- **Filtro por tenant/permissão é no storage, fail-closed** — chunk sem rótulo de tenant
  **não passa** numa consulta tenant-scoped ([`rag_index.py`](./demos/common/rag_index.py);
  `RagIndex.retrieve`). Demonstre o vazamento desligando o filtro (`tenant=None`).
- **RBAC/ABAC por documento:** o retriever só devolve o que **aquele usuário** pode ver.
  Filtro no prompt **não** é segurança.

---

## 📐 6. RAG evaluation — POC C

Avalie em **camadas**, com **golden set** ([`demos/golden/golden.jsonl`](./demos/golden/golden.jsonl))
e **regressão**:

| Camada | Métricas (em [`metrics.py`](./demos/common/metrics.py)) |
|---|---|
| Retriever | recall@k, precision@k, MRR, nDCG@k |
| Contexto montado | context precision, context recall |
| Resposta | answer_match (substring esperada); faithfulness (LLM-as-judge) |

```bash
python demos/poc_c_eval/evaluate.py                  # métricas + queries que falham
python demos/poc_c_eval/evaluate.py --rerank llm     # mede o efeito do rerank
python demos/poc_c_eval/evaluate.py --dims-sweep     # Matryoshka: recall vs dims
python demos/poc_c_eval/evaluate.py --faithfulness   # LLM-as-judge (precisa Ollama)
```

- **Golden / adversarial / regression.** Rode **antes de promover** mudança em
  chunking, embedding, top-k, reranker ou prompt — mudança "por intuição" derruba recall
  sem ninguém ver até o incidente.
- A **"RAG triad"** (context relevance, groundedness, answer relevance) é um bom ponto de
  partida (Ragas formaliza). **Nenhuma métrica isolada resolve qualidade.**

> O harness imprime as queries **sem `answer_match`** — são candidatas a regressão. Os
> testes ([`tests/`](./tests/)) já são um esqueleto reprodutível (`make test`).

---

## 🔭 7. Observabilidade — POC D

Sem logs, não dá para debugar RAG. Para **cada consulta** registramos: query, método,
top-k, candidatos + scores, **fontes**, **versão do índice**, **modelo de embedding**,
**latência** por etapa e **custo** (nº de chamadas a embedding/geração).

```bash
python demos/poc_d_observability/observe.py --query "qual o prazo de reembolso?"
tail -1 demos/poc_d_observability/.runtime/trace.jsonl   # o trace cru (JSONL)
```

> Em produção isso vira span **OpenTelemetry (GenAI)** + dashboards de qualidade,
> latência, custo e indexing lag.

### Tracing visual opcional com Phoenix

Além do JSONL próprio, as PoCs emitem **spans OpenInference** para o
[Arize Phoenix](https://github.com/Arize-ai/phoenix) (UI local), o que deixa fácil ver
no navegador *o que é o quê*: `rag.retrieve` → `ollama.embed`, `ollama.generate`, etc.
É **opt-in** e 100% local (nada sai da máquina):

```bash
make phoenix-setup     # instala as deps de observabilidade (opcional)
make phoenix-start     # sobe a UI em http://127.0.0.1:6006
make trace-eval        # roda a POC C enviando spans ao Phoenix
make phoenix-stop
```

Sem `PHOENIX_TRACING=1`, nada é enviado e as PoCs rodam igual. Detalhes em
[`docs/observabilidade-phoenix.md`](./docs/observabilidade-phoenix.md).

---

## 🛡️ 8. Segurança de RAG

- **OWASP LLM08:2025 — Vector and Embedding Weaknesses:** RAG é **superfície de ataque**
  (poisoned embeddings, cross-tenant leakage, embedding inversion).
- **Indirect prompt injection** (demonstrado na parte 1, POC4): dado recuperado **não é
  instrução**. **Data/vector poisoning:** documento malicioso contamina recuperações.
- **Source authentication:** de onde veio o documento? Fonte não verificada é suspeita.
- **Limites reais:** mitigação é **parcial**. A defesa que mais vale é limitar o **blast
  radius** depois do modelo (autorização, HITL, egress).

---

## 🏭 9. POC didática × produção

| Aspecto | POC | Produção |
|---|---|---|
| Índice | em memória, sem ANN | vector DB (Qdrant/Chroma/pgvector) com HNSW/IVF |
| Reranker | lexical / llm | cross-encoder dedicado |
| Reembedding | a cada execução (didático) | índice paralelo + promoção + rollback |
| Eval | golden pequeno + mock | golden por tenant/idioma + regressão em CI |
| Observabilidade | JSONL local | trace OpenTelemetry + dashboards |
| Segurança | demarcação + guarda de saída | policy-as-code, RBAC/ABAC, egress, HITL |

> O ponto **não** é virar produto — é mostrar **onde** a POC para e o que muda quando o
> sistema vira software crítico.

---

## 📚 10. Referências, roteiro e checklist

- Roteiro do apresentador (60/90 min): [`ROTEIRO.md`](./ROTEIRO.md)
- Checklist de RAG Engineering: [`CHECKLIST.md`](./CHECKLIST.md)
- Bibliografia (papers/specs/docs, datas de acesso): [`referencias.md`](./referencias.md)
- Slides (Marp): [`slides/slides.md`](./slides/slides.md)
- Decisões técnicas e limitações: [`docs/decisoes-e-limitacoes.md`](./docs/decisoes-e-limitacoes.md)
- Matriz de compatibilidade: [`docs/matriz-compatibilidade.md`](./docs/matriz-compatibilidade.md)
