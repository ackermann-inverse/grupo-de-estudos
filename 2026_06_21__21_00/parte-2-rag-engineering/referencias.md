# 📚 Referências — Parte 2 (RAG Engineering)

Papers, specs e documentação oficial usados no texto desta extensão. Data de acesso
geral: **2026-06-16**. Sem bibliografia decorativa — cada item é citado no material.

## Retrieval e fusão

- Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* (NeurIPS 2020) — <https://arxiv.org/abs/2005.11401>
- Karpukhin et al., *Dense Passage Retrieval for Open-Domain QA* (EMNLP 2020) — <https://arxiv.org/abs/2004.04906>
- Robertson & Zaragoza, *The Probabilistic Relevance Framework: BM25 and Beyond* (2009) — DOI <https://doi.org/10.1561/1500000019>
- Cormack, Clarke & Büttcher, *Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods* (SIGIR 2009) — DOI <https://doi.org/10.1145/1571941.1572114>

## Embeddings, dimensionalidade e Matryoshka

- Nussbaum et al., *Nomic Embed: Training a Reproducible Long Context Text Embedder* (2024, Apache-2.0) — <https://arxiv.org/abs/2402.01613>
- Kusupati et al., *Matryoshka Representation Learning* (NeurIPS 2022) — <https://proceedings.neurips.cc/paper_files/paper/2022/hash/c32319f4868da7613d78af9993100e42-Abstract-Conference.html>

## GraphRAG

- Edge et al. (Microsoft Research), *From Local to Global: A Graph RAG Approach to Query-Focused Summarization* (2024) — <https://arxiv.org/abs/2404.16130>
- Microsoft GraphRAG (docs) — <https://microsoft.github.io/graphrag/>

## Avaliação de RAG

- Ragas, *Metrics* (docs) — <https://docs.ragas.io/en/stable/concepts/metrics/>
- TruLens, *RAG Triad of metrics* — <https://www.trulens.org/getting_started/core_concepts/rag_triad/>

## Observabilidade

- OpenTelemetry, *Semantic conventions for GenAI* — <https://opentelemetry.io/docs/specs/semconv/gen-ai/>

## Segurança

- OWASP, *Top 10 for LLM Applications 2025* (LLM01 Prompt Injection; **LLM08 Vector & Embedding Weaknesses**) — <https://owasp.org/www-project-top-10-for-large-language-model-applications/>
- Greshake et al., *Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection* (2023) — <https://arxiv.org/abs/2302.12173>

## Material complementar do autor

- Ruan Pato, *Engenharia de IA em Produção* — caps. 2.6–2.10 (RAG, hybrid/rerank,
  dimensionality/Matryoshka, GraphRAG, RAG×fine-tuning), 2.11 e 5.4 (avaliação),
  4.3/4.5 (injeção, poisoning). Repositório `production-ai-engineering`.
