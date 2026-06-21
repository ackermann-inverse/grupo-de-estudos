#!/usr/bin/env bash
set -euo pipefail

# Testes reprodutíveis. Por padrão rodam em MOCK (não baixam modelo).
# O teste de execução REAL (test_rag_real_*) só roda se o Ollama estiver no ar.

cd "$(dirname "$0")/.."
[ -d .venv ] && source .venv/bin/activate || true

export USE_MOCK="${USE_MOCK:-1}"

echo "== Testes (USE_MOCK=$USE_MOCK) =="
python -m pytest tests/ -q "$@"
