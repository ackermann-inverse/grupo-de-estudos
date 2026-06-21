# 🎤 Roteiro — Parte 2: RAG Engineering (≈ 1 hora)

Continuação do encontro principal. Pressupõe que a plateia já viu contexto, memória e
RAG-essencial. Reutiliza o código de [`../demos/poc2_rag/`](../demos/poc2_rag/).

> **Tese:** recuperar é fácil; recuperar **bem**, **avaliar** e **observar** é o
> trabalho. E RAG é **superfície de ataque**, não escudo.

## Agenda (60 min)

| Tempo | Bloco | Prática |
|---:|---|---|
| 00–05 | Recap: RAG = recuperar contexto externo; onde paramos na parte 1 | — |
| 05–15 | **Embeddings**: retrieval ≠ interno; dimensão/custo; Matryoshka; thresholds por modelo | `rag.py --show-scores` (real × mock) |
| 15–28 | **Recuperação**: dense × lexical/BM25 × híbrido/RRF; chunking/overlap/metadados | `--method dense/lexical/hybrid` lado a lado |
| 28–38 | **Reranking** (didático × cross-encoder) e **MMR/diversidade** | discutir trade-off latência/qualidade |
| 38–50 | **RAG evaluation** em camadas: golden set, recall@k, context precision/recall, faithfulness; regressão | mostrar `make test` como esqueleto |
| 50–57 | **Observabilidade** + **segurança** (OWASP LLM08, poisoning, permission-aware) | `make leak`; POC4 recap |
| 57–60 | Fechamento: POC didática × produção; próximos passos | Perguntas |

## Falas-chave

- **Embeddings:** "Trocar o LLM não invalida o índice; trocar o **embedding** invalida.
  E o threshold de 'relevante' **não** transfere entre modelos — vimos na POC3."
- **Recuperação:** "Denso acha paráfrase; BM25 acha `SKU-4471`. Híbrido (RRF) funde os
  dois. Não existe método universal."
- **Reranking:** "O reranker da POC é um stand-in. Um cross-encoder real lê query+doc
  juntos, é mais caro e costuma valer a pena."
- **Eval:** "Avalie em camadas: retriever, contexto, resposta. Golden set + regressão.
  Nenhuma métrica isolada resolve qualidade."
- **Segurança:** "OWASP LLM08: RAG é superfície de ataque. Dado recuperado não é
  instrução confiável. Mitigação é parcial — limite o blast radius."

## Demonstrações reutilizando a POC2

```bash
# embeddings reais × mock (mostra o papel do modelo de embedding)
python ../demos/poc2_rag/rag.py --show-scores --query "garantia do SKU-4471"
USE_MOCK=1 python ../demos/poc2_rag/rag.py --show-scores --query "garantia do SKU-4471"

# dense × lexical × híbrido
for m in dense lexical hybrid; do
  python ../demos/poc2_rag/rag.py --method $m --query "qual o prazo de reembolso?"
done

# obsolescência (índice com versão antiga conflitante)
python ../demos/poc2_rag/rag.py --include-adversarial --query "prazo de reembolso"

# permission-aware: vazamento só com filtro desligado
python ../demos/poc2_rag/rag.py --no-tenant-filter
```

## Checkpoints

1. (embeddings) "Qual modelo de embedding seu RAG usa? Qual a dimensão e o custo?"
2. (recuperação) "Suas queries dependem de termo literal? Então BM25/híbrido importa."
3. (eval) "Você tem golden set? Roda regressão ao mudar chunking/embedding/top-k?"
4. (segurança) "Como você autentica a origem de um documento que entra no índice?"

## Exercícios sugeridos

- Trocar o `rerank` didático por um cross-encoder via Ollama-compatible reranker e medir
  Precision@k no golden set.
- Implementar `mmr` (esboço no [README](./README.md)) e medir redundância no top-k.
- Montar um golden set de 10 queries por tenant e um adversarial set de injeções.
