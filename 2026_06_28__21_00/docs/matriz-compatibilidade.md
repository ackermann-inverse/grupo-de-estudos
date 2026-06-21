# Matriz de compatibilidade e requisitos — parte 2

Mesma base da parte 1 (CPU-only, Ollama nativo ou Docker, fallback MOCK). A única adição
é o **cross-encoder real opcional**, que é pesado.

## Ambientes

| Ambiente | Caminho | Status |
|---|---|---|
| macOS Apple Silicon | Ollama nativo | ✅ testado |
| Linux x86_64 | Ollama nativo ou Docker | ✅ esperado |
| Windows 10/11 | WSL2 ou Docker Desktop | ⚠️ não testado nativamente |
| CPU-only | qualquer um acima | ✅ caminho principal |
| Sem baixar modelo | `USE_MOCK=1` | ✅ testado (não é a demo real) |

## Downloads

| Item | Download | Quando |
|---|---:|---|
| `nomic-embed-text` (embeddings) | ~274 MB | sempre (caminho real) |
| `llama3.2:3b` (geração + llm-reranker + judge) | ~2.0 GB | caminho real (`1b` ~1.3 GB p/ ≤8 GB RAM) |
| **cross-encoder real** (`requirements-extra.txt`) | **~1–2 GB** (torch + modelo) | **opcional**, só `--reranker cross` |

Caminho padrão ≈ **2,3 GB** (nomic + 3b). O cross-encoder **não** é necessário — o
reranker padrão é o `llm` (via Ollama, sem download novo).

## Validação rápida

```bash
make setup
make test                 # 22 (MOCK), sem Ollama
ollama pull nomic-embed-text && ollama pull llama3.2:3b
make demo                 # eval real
make test-real            # 22 contra Ollama
# opcional (pesado):
make extra && make cross
```

Tempos observados (Apple Silicon, 8 GB, CPU): `make test` (MOCK) ~1 s; eval real (12
queries, com geração) poucos segundos; dims-sweep (4 índices) ~segundos.
