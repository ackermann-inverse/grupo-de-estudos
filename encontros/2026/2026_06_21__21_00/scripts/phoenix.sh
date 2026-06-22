#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

ACTION="${1:-status}"
PHOENIX_DIR="$PWD/.phoenix"
PID_FILE="$PHOENIX_DIR/server.pid"
LOG_FILE="$PHOENIX_DIR/server.log"
URL="${PHOENIX_URL:-http://127.0.0.1:6006}"

mkdir -p "$PHOENIX_DIR"

case "$ACTION" in
  setup)
    .venv/bin/python -m pip install -r requirements-observability.txt
    ;;
  start)
    if curl -sf "$URL/healthz" >/dev/null 2>&1 || curl -sf "$URL" >/dev/null 2>&1; then
      echo "Phoenix já está rodando em $URL"
      exit 0
    fi
    PHOENIX_WORKING_DIR="$PHOENIX_DIR" \
      nohup .venv/bin/phoenix serve --host 127.0.0.1 --port 6006 --no-internet \
      >"$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    for _ in $(seq 1 60); do
      if curl -sf "$URL" >/dev/null 2>&1; then
        echo "Phoenix pronto: $URL"
        exit 0
      fi
      sleep 1
    done
    echo "Phoenix não iniciou. Veja $LOG_FILE" >&2
    exit 1
    ;;
  stop)
    if [[ -f "$PID_FILE" ]]; then
      kill "$(cat "$PID_FILE")" 2>/dev/null || true
      rm -f "$PID_FILE"
    fi
    echo "Phoenix parado."
    ;;
  status)
    if curl -sf "$URL" >/dev/null 2>&1; then
      echo "Phoenix online: $URL"
    else
      echo "Phoenix offline"
      exit 1
    fi
    ;;
  *)
    echo "Uso: $0 {setup|start|stop|status}" >&2
    exit 2
    ;;
esac
