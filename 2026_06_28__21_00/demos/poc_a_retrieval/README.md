# POC A — Retrieval: dense × lexical × híbrido

Mostra, lado a lado, os três métodos para a **mesma query**. Não existe método universal.

## Rodar

```bash
python demos/poc_a_retrieval/retrieval.py --query "código da entrega econômica"   # lexical ganha (termo literal)
python demos/poc_a_retrieval/retrieval.py --query "como devolvo e recebo de volta" # dense ganha (paráfrase)
USE_MOCK=1 python demos/poc_a_retrieval/retrieval.py
```

Flags: `--query`, `--k`, `--tenant`.

## O que observar

- A coluna **só no DENSE** vs **só no LEXICAL** mostra onde cada método acerta sozinho.
- Score exibido: `(dense/lexical)` normalizados em [0,1].

## Limitação

Em **MOCK**, embeddings por hashing colapsam dense≈lexical (o contraste some). Rode com
**Ollama** (`nomic-embed-text`) para ver o contraste semântico real.
