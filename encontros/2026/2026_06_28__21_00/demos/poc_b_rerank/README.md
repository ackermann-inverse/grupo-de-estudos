# POC B — Reranking e diversidade (MMR)

Recupera um top-k híbrido e reordena, mostrando a ordem **antes × depois**.

## Rodar

```bash
python demos/poc_b_rerank/rerank.py --reranker llm  --query "prazo de reembolso e estorno"
python demos/poc_b_rerank/rerank.py --reranker mmr  --query "reembolso pix estorno"
# cross-encoder REAL (opcional, pesado):
make extra
python demos/poc_b_rerank/rerank.py --reranker cross --query "garantia do SKU-4471"
USE_MOCK=1 python demos/poc_b_rerank/rerank.py     # llm cai para lexical (determinístico)
```

Flags: `--reranker {none,lexical,llm,cross,mmr}`, `--query`, `--k`, `--top`, `--tenant`.

## As estratégias

| Reranker | O que é | Custo |
|---|---|---|
| `lexical` | sobreposição de termos (stand-in da parte 1) | trivial |
| `llm` | LLM local pontua relevância query×doc (**cross-encoder na essência**) | sem download novo |
| `cross` | cross-encoder **real** (sentence-transformers) | ~1–2 GB (torch), via `make extra` |
| `mmr` | **diversidade** (não relevância): evita quase-duplicatas | trivial |

## O que observar

- `llm`/`cross` costumam **mudar o top-3** vs o baseline lexical.
- `mmr` **rebaixa** uma segunda quase-duplicata do mesmo documento, mesmo relevante.

## Limitação

Em **MOCK**, `llm` cai para `lexical` (o LLM canned não produz score) — determinístico
para teste. O `cross` exige a dependência opcional; sem ela, a POC avisa e sai.
