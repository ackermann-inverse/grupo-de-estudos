# ✅ Checklist de RAG Engineering

Lista prática para revisar um RAG antes de confiar nele. Não é "tudo ou nada" — é um
guia de maturidade. Marque o que se aplica ao seu sistema.

## Embeddings e índice

- [ ] O modelo de embedding está **declarado e versionado** (nome + dimensão).
- [ ] Reembedding usa **índice paralelo** + promoção + rollback (não in-place).
- [ ] O **threshold de similaridade** foi calibrado **neste** modelo de embedding.
- [ ] A dimensão foi escolhida com trade-off **custo × qualidade** (Matryoshka avaliado).
- [ ] **Indexing lag** (fonte → índice) é monitorado.

## Chunking e metadados

- [ ] Estratégia de chunking definida (fixo/semântico/hierárquico) e justificada.
- [ ] Chunks carregam metadados: **tenant, idioma, validade, versão, fonte, hash**.
- [ ] Tabelas/listas não são cortadas no meio (ou há mitigação).

## Recuperação

- [ ] Método escolhido (dense/lexical/híbrido) **bate com o tipo de query** do domínio.
- [ ] Há **reranking** ou um motivo documentado para não ter.
- [ ] Top-k inicial generoso; top final pequeno e ordenado.
- [ ] **Diversidade** considerada (evitar quase-duplicatas no contexto).

## Permissão e segurança

- [ ] Filtro por **tenant/permissão é no storage, fail-closed** (sem rótulo = negado).
- [ ] **Permission-aware**: retriever só devolve o que o usuário pode ver (RBAC/ABAC).
- [ ] Documentos recuperados são tratados como **dado, não instrução** (anti-injeção).
- [ ] Ingestão valida e registra **provenance**; fontes novas exigem aprovação.
- [ ] Pensou em **data/vector poisoning** e **source authentication**.
- [ ] OWASP **LLM08** (Vector & Embedding Weaknesses) revisado.

## Grounding e geração

- [ ] A resposta **cita as fontes** recuperadas (citation coverage medido).
- [ ] **No-answer** correto quando não há fonte (testado).
- [ ] Distinção plausível × correta × **suportada** está clara para o time.

## Avaliação

- [ ] Existe **golden set** (por tenant/idioma) e **adversarial set**.
- [ ] Métricas por camada: **recall@k**, context precision/recall, **faithfulness**.
- [ ] **Regressão** roda ao mudar chunking/embedding/top-k/reranker/prompt.
- [ ] Ninguém promove índice "por intuição".

## Observabilidade

- [ ] Cada consulta loga: query, chunks, **scores**, fontes, **versão do índice**,
      modelo de embedding, top-k, **latência**, custo.
- [ ] Há dashboards/alertas para queda de qualidade e indexing lag.

## Maturidade (POC × produção)

- [ ] Sei **onde** a POC didática para e o que muda em produção
      (vector DB, cross-encoder, CI de eval, trace estruturado, policy-as-code).
