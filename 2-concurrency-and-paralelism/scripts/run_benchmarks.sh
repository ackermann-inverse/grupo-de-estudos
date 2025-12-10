#!/usr/bin/env bash
set -euo pipefail

# Mesmo caso de teste para todas as linguagens (podem ser sobrescritos via env)
N="${N:-100000}"
WORKERS="${WORKERS:-4}"

# Limites "seguros"
# Maior inteiro seguro comum entre Go (int64) e Node (Number.MAX_SAFE_INTEGER).
# Node limita a 2^53 - 1 = 9007199254740991 para aritmética inteira precisa.
MAX_N=9007199254740991

# Descobre número de CPUs para limitar WORKERS
cpu_count=4
if command -v nproc >/dev/null 2>&1; then
  cpu_count="$(nproc)"
elif [ "$(uname)" = "Darwin" ]; then
  cpu_count="$(sysctl -n hw.ncpu)"
fi

# Workers máximos: até 4x o número de CPUs, com clamp em [1, 64]
MAX_WORKERS=$((cpu_count * 4))
if [ "$MAX_WORKERS" -lt 1 ]; then
  MAX_WORKERS=1
elif [ "$MAX_WORKERS" -gt 64 ]; then
  MAX_WORKERS=64
fi

# --- Sanitização de N ---
if ! [[ "$N" =~ ^[0-9]+$ ]]; then
  echo "[WARN] N inválido ($N). Usando valor padrão 100000." >&2
  N=100000
fi

# Aplica limite em N
if [ "$N" -gt "$MAX_N" ]; then
  echo "[WARN] N=$N > MAX_N=$MAX_N. Ajustando para $MAX_N." >&2
  N="$MAX_N"
fi

# --- Sanitização de WORKERS ---
if ! [[ "$WORKERS" =~ ^[0-9]+$ ]]; then
  echo "[WARN] WORKERS inválido ($WORKERS). Usando valor padrão 4." >&2
  WORKERS=4
fi

if [ "$WORKERS" -lt 1 ]; then
  echo "[WARN] WORKERS=$WORKERS não faz sentido (<1). Ajustando para 1." >&2
  WORKERS=1
elif [ "$WORKERS" -gt "$MAX_WORKERS" ]; then
  echo "[WARN] WORKERS=$WORKERS > MAX_WORKERS=$MAX_WORKERS (cpu_count=$cpu_count). Ajustando para $MAX_WORKERS." >&2
  WORKERS="$MAX_WORKERS"
fi

echo "========================================"
echo "== Benchmarks (local, sem Docker)     =="
echo "== N=$N | WORKERS=$WORKERS           =="
echo "== MAX_N=$MAX_N | MAX_WORKERS=$MAX_WORKERS =="
echo "========================================"
echo

time_cmd() {
  # Se quiser /usr/bin/time -v, troca aqui
  command time -p "$@"
}

# Decide qual python usar (venv > python3 > python)
PYTHON_BIN="python"
if [ -x "python/.venv/bin/python" ]; then
  # vamos chamar de dentro de python/, então usamos caminho relativo
  PYTHON_BIN=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

print_section() {
  local title="$1"
  echo
  echo "========================================"
  echo "== [$title]"
  echo "========================================"
  echo
}

run_go() {
  print_section "Go"

  echo ">> sequential"
  (cd go && N="$N" time_cmd go run ./src/benchmark_sequential.go)
  echo

  echo ">> concurrent (goroutines, GOMAXPROCS=1)"
  (cd go && N="$N" WORKERS="$WORKERS" time_cmd go run ./src/benchmark_concurrent.go)
  echo

  echo ">> parallel (goroutines, GOMAXPROCS=WORKERS)"
  (cd go && N="$N" WORKERS="$WORKERS" time_cmd go run ./src/benchmark_parallel.go)
  echo
}

run_node() {
  print_section "Node.js"

  echo ">> sequential"
  (cd node && N="$N" time_cmd node ./src/benchmark.sequential.js)
  echo

  echo ">> concurrent (workers/logical concurrency)"
  (cd node && N="$N" WORKERS="$WORKERS" time_cmd node ./src/benchmark.concurrent.js)
  echo

  echo ">> parallel (worker threads / processos)"
  (cd node && N="$N" WORKERS="$WORKERS" time_cmd node ./src/benchmark.parallel.js)
  echo
}

run_python() {
  print_section "Python"

  if [ "$PYTHON_BIN" = ".venv/bin/python" ]; then
    echo "Usando Python: python/.venv/bin/python (venv)"
  else
    echo "Usando Python: $PYTHON_BIN"
  fi
  echo

  echo ">> sequential"
  (cd python && N="$N" time_cmd "$PYTHON_BIN" ./src/benchmark_sequential.py)
  echo

  echo ">> concurrent (ThreadPoolExecutor)"
  (cd python && N="$N" WORKERS="$WORKERS" time_cmd "$PYTHON_BIN" ./src/benchmark_threads.py)
  echo

  echo ">> parallel (ProcessPoolExecutor)"
  (cd python && N="$N" WORKERS="$WORKERS" time_cmd "$PYTHON_BIN" ./src/benchmark_processes.py)
  echo
}

run_go
run_node
run_python
