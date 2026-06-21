# 🎤 Roteiro do apresentador — RAG Engineering (parte 2)

Continuação do encontro 5. Pressupõe contexto/memória/RAG-essencial já vistos. Material
canônico: [`README.md`](./README.md). Slides: [`slides/slides.md`](./slides/slides.md).

> **Tese:** recuperar é fácil; recuperar **bem**, **avaliar** e **observar** é o
> trabalho. RAG é **superfície de ataque**, não escudo.

> **Regra de ouro:** cada bloco tem uma POC **rodável**. Baixe os modelos antes
> (`ollama pull nomic-embed-text && ollama pull llama3.2:3b`).

---

## Versão principal: 60 minutos

| Tempo | Bloco | Prática |
|---:|---|---|
| 00–05 | Recap: onde a parte 1 parou; RAG = recuperar contexto externo | — |
| 05–15 | **Embeddings**: retrieval ≠ interno; dimensão/custo; Matryoshka; thresholds | `make sweep` |
| 15–28 | **Retrieval**: dense × lexical/BM25 × híbrido/RRF; chunking/metadados | **POC A** (`make retrieval`) |
| 28–40 | **Reranking** (lexical/llm/cross) + **MMR/diversidade** | **POC B** (`make rerank`) |
| 40–52 | **RAG evaluation** em camadas: golden, recall@k, context, faithfulness; regressão | **POC C** (`make eval`) |
| 52–58 | **Observabilidade** + **segurança** (OWASP LLM08, permission-aware, poisoning) | **POC D** (`make observe`) |
| 58–60 | Fechamento: POC × produção; próximos passos | Perguntas |

**Buffer:** se atrasar, mostre saídas pré-capturadas (READMEs das POCs) e encurte a
discussão. Não corte a **POC C** (avaliação) — é o coração de "RAG Engineering".

---

## Alternativa: 90 minutos

Versão de 60 + (a) `make cross` com cross-encoder real (se `make extra` já rodou); (b)
`--faithfulness` ao vivo; (c) inspeção do `trace.jsonl` da POC D; (d) discussão de
arquitetura de produção (vector DB, índice paralelo, reindex/rollback).

---

## Preparação

1. `make setup` e `ollama pull nomic-embed-text llama3.2:3b` **antes**.
2. (opcional) `make extra` se for demonstrar o cross-encoder real — avise que baixa ~1–2 GB.
3. `make test` (22, ou 21 + 1 skip sem Ollama) e `make demo` "a frio".
4. Plano B: `USE_MOCK=1` em tudo (determinístico).

---

## Falas-chave

- **Embeddings:** "Trocar o LLM não invalida o índice; trocar o **embedding** invalida.
  Matryoshka deixa truncar dimensão. **Mas** — no nosso corpus de brinquedo, truncar até
  64 dims não doeu; em corpus grande, dói. Não generalize de um toy corpus."
- **Retrieval:** "Denso acha paráfrase; BM25 acha `SKU-4471`. Híbrido (RRF) funde. Não
  existe método universal." Rodar POC A com a query de código.
- **Reranking:** "O reranker da parte 1 é um stand-in. LLM-reranker lê query+doc juntos
  sem baixar nada; cross-encoder real é mais preciso e mais pesado." Rodar POC B; mostrar
  MMR diversificando (rebaixa a 2ª quase-duplicata).
- **Eval:** "Avalie em camadas: retriever → contexto → resposta. Golden set + regressão.
  Olhem as queries que **falham** — são a regressão. Nenhuma métrica isolada resolve."
- **Observabilidade:** "Sem isto não dá para debugar. Olhem o `trace.jsonl`: versão do
  índice, modelo de embedding, scores, latência, custo."
- **Segurança:** "OWASP LLM08. Dado recuperado não é instrução. Mitigação é parcial —
  limite o blast radius."

---

## Checkpoints

1. (embeddings) "Qual embedding seu RAG usa? Dimensão e custo? Threshold calibrado nele?"
2. (retrieval) "Suas queries dependem de termo literal? Então BM25/híbrido importa."
3. (eval) "Você tem golden set? Roda regressão ao mudar chunking/embedding/top-k?"
4. (segurança) "Como você autentica a origem de um documento que entra no índice?"

---

## Planos de recuperação de falha

| Falha | Recuperação |
|---|---|
| Ollama caiu | segue em MOCK (`USE_MOCK=1`); saídas batem com os READMEs |
| `cross` sem dependência | a POC avisa para rodar `make extra` ou usar `--reranker llm` |
| dims-sweep "não degrada" no real | é o ponto: corpus pequeno é robusto; explique o limite do toy corpus |
| eval lento no real | rode `--dims-sweep`/sem `do_answer` (só retrieval) para ser rápido |
