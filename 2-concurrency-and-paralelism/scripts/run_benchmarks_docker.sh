#!/usr/bin/env bash
set -euo pipefail

N="${N:-100000}"
WORKERS="${WORKERS:-4}"

mkdir -p results

echo "== Benchmarks via Docker =="
echo "N=$N WORKERS=$WORKERS"
echo

### Node.js
echo "[Node] Rodando modos seq / concurrent / parallel..."

docker run --rm \
  -e N="$N" \
  bench-node \
  npm run start:seq \
  > results/node-seq.json

docker run --rm \
  -e N="$N" \
  -e WORKERS="$WORKERS" \
  bench-node \
  npm run start:concurrent \
  > results/node-concurrent.json

docker run --rm \
  -e N="$N" \
  -e WORKERS="$WORKERS" \
  bench-node \
  npm run start:parallel \
  > results/node-parallel.json


### Python
echo "[Python] Rodando modos seq / threads / processes..."

docker run --rm \
  -e N="$N" \
  bench-python \
  python src/benchmark_sequential.py \
  > results/python-seq.json

docker run --rm \
  -e N="$N" \
  -e WORKERS="$WORKERS" \
  bench-python \
  python src/benchmark_threads.py \
  > results/python-threads.json

docker run --rm \
  -e N="$N" \
  -e WORKERS="$WORKERS" \
  bench-python \
  python src/benchmark_processes.py \
  > results/python-processes.json


### Go
echo "[Go] Rodando modos seq / concurrent / parallel..."

docker run --rm \
  -e N="$N" \
  bench-go \
  go run ./src/benchmark_sequential.go \
  > results/go-seq.json

docker run --rm \
  -e N="$N" \
  -e WORKERS="$WORKERS" \
  bench-go \
  go run ./src/benchmark_concurrent.go \
  > results/go-concurrent.json

docker run --rm \
  -e N="$N" \
  -e WORKERS="$WORKERS" \
  bench-go \
  go run ./src/benchmark_parallel.go \
  > results/go-parallel.json

echo "Benchmarks concluídos. Resultados em ./results:"
ls -1 results
