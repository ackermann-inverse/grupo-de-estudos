# Go

Este diretório contém a implementação do benchmark em Go.

## Modos

- `benchmark_sequential.go` – modo **sequencial**.
- `benchmark_concurrent.go` – modo **concorrente** com goroutines, mas `GOMAXPROCS=1` (sem paralelismo real).
- `benchmark_parallel.go` – modo **paralelo** com goroutines e `GOMAXPROCS` ajustado para usar múltiplos núcleos.

## Uso com Docker

```bash
cd go
docker build -t go-bench -f Dockerfile.go .

# Sequencial
docker run --rm -e N=100000 go-bench go run ./src/benchmark_sequential.go

# Concorrente
docker run --rm -e N=100000 -e WORKERS=4 go-bench go run ./src/benchmark_concurrent.go

# Paralelo
docker run --rm -e N=100000 -e WORKERS=4 go-bench go run ./src/benchmark_parallel.go
```

Cada execução imprime um JSON com as métricas do benchmark.
