# POC C — RAG evaluation harness

Roda o **golden set** ([`../golden/golden.jsonl`](../golden/golden.jsonl)) e mede o
pipeline **em camadas**. É o coração do "RAG Engineering": sem avaliação, qualquer
mudança entra no escuro.

## Rodar

```bash
python demos/poc_c_eval/evaluate.py                 # métricas + queries que falham
python demos/poc_c_eval/evaluate.py --rerank llm    # efeito do rerank
python demos/poc_c_eval/evaluate.py --dims-sweep    # Matryoshka: recall vs dims
python demos/poc_c_eval/evaluate.py --faithfulness  # LLM-as-judge (precisa Ollama)
USE_MOCK=1 python demos/poc_c_eval/evaluate.py      # determinístico
```

Flags: `--k`, `--top`, `--rerank {none,lexical,llm,cross,mmr}`, `--dims-sweep`, `--faithfulness`.

## Métricas (em [`../common/metrics.py`](../common/metrics.py))

- **Retriever:** recall@k, precision@k, MRR, nDCG@k.
- **Contexto montado:** context precision, context recall.
- **Resposta:** `answer_match` (substring esperada — proxy determinístico de correção);
  `faithfulness` via LLM-as-judge (opcional).

## O que observar

- As queries **sem `answer_match`** são impressas — candidatas a **regressão**.
- `--dims-sweep` mostra o trade-off custo×qualidade do truncamento Matryoshka.

> **Nuance honesta:** no nosso corpus pequeno/fácil, o sweep real fica **estável** (até
> 64 dims mantém recall@5); no MOCK (hashing) ele **degrada** já em 128/64 por colisão.
> O efeito real de queda aparece em corpus grande e queries difíceis — não generalize
> de um toy corpus.

## Uso recomendado

Como **regressão**: rode antes de promover mudança em chunking, embedding, top-k,
reranker ou prompt. Os [testes](../../tests/) já são um esqueleto reprodutível.
