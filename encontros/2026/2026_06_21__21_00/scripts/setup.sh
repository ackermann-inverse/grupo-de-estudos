#!/usr/bin/env bash
set -euo pipefail

# Setup do encontro 5: cria venv, instala deps e (opcionalmente) baixa os modelos.
# Idempotente: pode rodar de novo sem quebrar.

cd "$(dirname "$0")/.."
ROOT="$(pwd)"

echo "== Setup: Context Engineering, RAG & Memória =="
echo

# --- 1) Python (>= 3.10). Prefere o mais novo disponível. ---
PYTHON_BIN=""
for cand in python3.12 python3.11 python3.10 python3; do
  if command -v "$cand" >/dev/null 2>&1; then
    ver="$("$cand" -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
    major="${ver%.*}"; minor="${ver#*.}"
    if [ "$major" -eq 3 ] && [ "$minor" -ge 10 ]; then
      PYTHON_BIN="$cand"; break
    fi
  fi
done
if [ -z "$PYTHON_BIN" ]; then
  echo "ERRO: Python 3.10+ não encontrado. Instale antes de continuar." >&2
  exit 1
fi
echo "[python] usando $PYTHON_BIN ($("$PYTHON_BIN" --version 2>&1))"

# --- 2) venv + dependências ---
if [ ! -d .venv ]; then
  "$PYTHON_BIN" -m venv .venv
  echo "[venv] criado em $ROOT/.venv"
else
  echo "[venv] já existe, reutilizando"
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt
echo "[deps] instaladas"
echo

# --- 3) .env ---
if [ ! -f .env ]; then
  cp .env.example .env
  echo "[env] .env criado a partir de .env.example"
fi

# --- 4) Ollama (opcional, mas é o caminho da demo real) ---
GEN_MODEL="${GEN_MODEL:-llama3.2:3b}"
EMBED_MODEL="${EMBED_MODEL:-nomic-embed-text}"

if command -v ollama >/dev/null 2>&1; then
  echo "[ollama] encontrado: $(ollama --version 2>&1 | head -1)"
  if [ "${PULL_MODELS:-ask}" = "ask" ]; then
    echo
    echo "Para a demo REAL é preciso baixar:"
    echo "  - $EMBED_MODEL  (~274 MB)"
    echo "  - $GEN_MODEL    (~2 GB; use llama3.2:1b se a RAM for <= 8 GB)"
    echo "Baixe com:"
    echo "  ollama pull $EMBED_MODEL && ollama pull $GEN_MODEL"
    echo "Ou rode 'PULL_MODELS=1 ./scripts/setup.sh' para baixar agora."
  elif [ "${PULL_MODELS:-ask}" = "1" ]; then
    echo "[ollama] baixando modelos..."
    ollama pull "$EMBED_MODEL"
    ollama pull "$GEN_MODEL"
    echo "[ollama] modelos prontos"
  fi
else
  echo "[ollama] NÃO encontrado."
  echo "  - macOS/Linux: https://ollama.com/download  (ou 'brew install ollama')"
  echo "  - Sem Ollama você ainda pode rodar tudo em MOCK: USE_MOCK=1 (e 'make test')."
fi

echo
echo "== Setup concluído =="
echo "Próximos passos:"
echo "  source .venv/bin/activate"
echo "  make test     # valida o pipeline (MOCK, sem baixar modelo)"
echo "  make demo     # RAG com modelo local (precisa do Ollama rodando)"
