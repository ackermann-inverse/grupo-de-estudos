#!/usr/bin/env bash
set -euo pipefail

# Build de todas as imagens de benchmark

echo "== Buildando imagem Go =="
docker build -t bench-go -f go/Dockerfile.go go

echo "== Buildando imagem Node =="
docker build -t bench-node -f node/Dockerfile.node node

echo "== Buildando imagem Python =="
docker build -t bench-python -f python/Dockerfile.python python

echo "Imagens prontas:"
docker images | grep "bench-"
