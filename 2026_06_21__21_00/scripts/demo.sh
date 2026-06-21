#!/usr/bin/env bash
set -euo pipefail

# Demo principal: RAG local com pipeline visível (POC2).
# Variáveis úteis: QUERY, METHOD (dense|lexical|hybrid), USE_MOCK=1.

cd "$(dirname "$0")/.."
[ -d .venv ] && source .venv/bin/activate || true
[ -f .env ] && set -a && . ./.env && set +a || true

QUERY="${QUERY:-qual é o prazo de reembolso?}"
METHOD="${METHOD:-hybrid}"

echo "== Demo principal: POC2 RAG =="
echo "QUERY=\"$QUERY\" | METHOD=$METHOD | USE_MOCK=${USE_MOCK:-0}"
echo

python demos/poc2_rag/rag.py --query "$QUERY" --method "$METHOD" --show-scores

echo
echo "Outras demos:"
echo "  python demos/poc1_context_assembly/assemble.py"
echo "  python demos/poc3_memory/memory.py"
echo "  python demos/poc4_failure/attack.py"
echo "  python demos/poc2_rag/rag.py --no-tenant-filter   # vazamento cross-tenant"
