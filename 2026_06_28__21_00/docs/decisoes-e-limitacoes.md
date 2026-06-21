# Decisões técnicas e limitações conhecidas — RAG Engineering (parte 2)

Documento de honestidade. Sem esconder o que não foi validado.

## Decisões

- **Reranker: dois caminhos.** Padrão = **LLM-as-reranker** via Ollama (lê query+doc
  juntos, "cross-encoder na essência", **sem download novo**). O **cross-encoder real**
  (sentence-transformers) é **opcional** (`requirements-extra.txt`, ~1–2 GB com torch),
  atrás da flag `--reranker cross`. Motivo: manter o caminho principal leve e CPU-only,
  sem abrir mão de mostrar um cross-encoder de verdade para quem quiser. Em **MOCK**, o
  LLM-reranker cai para lexical (determinístico).
- **Avaliação com golden set pequeno** (12 queries) + métricas à mão em `metrics.py`
  (recall@k, precision@k, MRR, nDCG@k, context precision/recall). Faithfulness via
  **LLM-as-judge** (opcional, exige Ollama). Proxy de correção determinístico:
  `answer_match` por substring esperada.
- **Truncamento Matryoshka** implementado por corte simples do vetor (`rag_index._truncate`).
- **Observabilidade** como JSONL local (`observability.py`), não OpenTelemetry — para ser
  autocontido e inspecionável em sala.
- **Self-contained:** este encontro tem a própria cópia de `demos/common` e do corpus
  (não importa da parte 1), seguindo o padrão de cada encontro ser independente.

## Limitações e o que NÃO foi validado

- **Cross-encoder real não foi executado nesta máquina.** O código está implementado e o
  caminho documentado, mas não rodei `make extra` (evitar baixar torch ~1–2 GB). O
  reranker `cross` está marcado como caminho opcional/`pragma: no cover`; **validado só
  por inspeção**, não por execução. Os testes cobrem lexical/llm/mmr.
- **Matryoshka sweep não degradou no real.** No corpus pequeno/fácil, recall@5 ficou em
  1.0 de `full` até `64` dims (real, nomic). No **MOCK** (hashing) ele degrada em 128/64
  por colisão de hash — isso é artefato do mock. **O efeito real de queda existe em
  corpus grande e queries difíceis**; não generalize do nosso toy corpus. Está dito no
  README e na POC C.
- **Faithfulness depende do juiz.** LLM-as-judge é ruidoso; trate como sinal, não verdade.
  Em MOCK é pulado (não há juiz).
- **`answer()`/eval reembeda o corpus por índice construído** (didático). Em produção,
  índice persistente + reembedding governado (tema do README, seção 9).
- **Corpus e golden são pequenos de propósito.** Métricas têm variância alta com 12
  queries; servem para ensinar o **método**, não para benchmark.

## O que está validado

- `make test` (MOCK): **22 testes** (21 + 1 *skip* se não houver Ollama).
- `make test-real` (Ollama): **22 testes**, incluindo eval real com recall@k ≥ 0.8.
- POCs A–D rodam em MOCK **e** com `llama3.2:3b` + `nomic-embed-text` reais.
  Eval real observado: recall@k=1.00, MRR=0.96, nDCG=0.97, answer_match=0.92 (1 miss
  honesto: "2FA" → "não sei").
- Corpus original/redistribuível; nenhum segredo.
