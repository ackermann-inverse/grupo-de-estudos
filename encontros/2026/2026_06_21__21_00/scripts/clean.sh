#!/usr/bin/env bash
set -euo pipefail

# Limpeza: remove venv, caches e stores de runtime. NÃO remove .env nem o corpus.

cd "$(dirname "$0")/.."

echo "== Limpando =="
rm -rf .venv
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
find . -type d -name ".runtime" -prune -exec rm -rf {} +
find . -type f -name "memory_store.json" -delete 2>/dev/null || true
echo "OK. (.env e demos/corpus preservados)"
