#!/usr/bin/env bash
set -euo pipefail

# Demo principal da parte 2: o harness de avaliação de RAG (POC C).
# Variáveis úteis: USE_MOCK=1.

cd "$(dirname "$0")/.."
[ -d .venv ] && source .venv/bin/activate || true
[ -f .env ] && set -a && . ./.env && set +a || true

echo "== Demo principal: POC C · RAG evaluation harness =="
echo "USE_MOCK=${USE_MOCK:-0}"
echo

python demos/poc_c_eval/evaluate.py

echo
echo "Outras POCs:"
echo "  python demos/poc_a_retrieval/retrieval.py --query 'código da entrega econômica'"
echo "  python demos/poc_b_rerank/rerank.py --reranker llm --query 'prazo de reembolso'"
echo "  python demos/poc_c_eval/evaluate.py --dims-sweep      # Matryoshka"
echo "  python demos/poc_d_observability/observe.py           # trace estruturado"
