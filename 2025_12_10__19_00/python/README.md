# Python

Este diretório contém a implementação do benchmark em Python.

## Modos

- `benchmark_sequential.py` – modo **sequencial**.
- `benchmark_threads.py` – modo **concorrente** com `ThreadPoolExecutor` (sem paralelismo real em CPU‑bound).
- `benchmark_processes.py` – modo **paralelo** com `ProcessPoolExecutor`.

## Uso com Docker

```bash
cd python
docker build -t python-bench -f Dockerfile.python .

# Sequencial
docker run --rm -e N=100000 python-bench python src/benchmark_sequential.py

# Concorrente (threads)
docker run --rm -e N=100000 -e WORKERS=4 python-bench python src/benchmark_threads.py

# Paralelo (processos)
docker run --rm -e N=100000 -e WORKERS=4 python-bench python src/benchmark_processes.py
```

Cada execução imprime um JSON com as métricas do benchmark.
