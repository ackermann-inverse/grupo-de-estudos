#!/usr/bin/env bash
set -euo pipefail

echo "== Setup do ambiente local (Go, Node, Python) =="

# --- Checagens básicas ---
need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERRO: comando '$1' não encontrado. Instale antes de continuar."
    exit 1
  fi
}

need_cmd go
need_cmd node
# tenta python3 primeiro, se não tiver cai pra python
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "ERRO: python3/python não encontrado."
  exit 1
fi

echo "Usando python: $PYTHON_BIN"
echo

# --- Go ---
echo "[Go] Baixando dependências (go mod download)..."
(
  cd go
  go mod download
)
echo "[Go] OK."
echo

# --- Node ---
echo "[Node] Instalando dependências (npm install)..."
(
  cd node
  if [ -d node_modules ]; then
    echo "node_modules já existe, pulando npm install."
  else
    npm install
  fi
)
echo "[Node] OK."
echo

# --- Python (venv) ---
echo "[Python] Preparando virtualenv em ./python/.venv ..."
(
  cd python
  if [ -d .venv ]; then
    echo "Virtualenv .venv já existe, instalando requirements só pra garantir..."
  else
    "$PYTHON_BIN" -m venv .venv
  fi

  # Ativa venv de forma portável (Linux/Mac/WSL)
  # shellcheck disable=SC1091
  source .venv/bin/activate

  pip install --upgrade pip
  pip install -r requirements.txt
)
echo "[Python] OK."
echo

echo "== Setup concluído =="
echo "Agora você pode rodar: N=100000 WORKERS=4 ./scripts/run_benchmarks.sh"
