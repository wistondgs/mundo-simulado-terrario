#!/usr/bin/env bash
# Start the human-review workspace locally and open it in the default browser.
# This launcher never approves, locks, authorizes, or executes science.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$PROJECT_ROOT/.venv/bin/python"
PORT="${TERRARIO_LAB_PORT:-8765}"
# The review center is the human entry point. It exposes only explicit,
# auditable governance actions and links to the Lab work surfaces.
URL="http://127.0.0.1:${PORT}/review-center.html"
LOG_DIR="$PROJECT_ROOT/.terrario/logs"
LOG_FILE="$LOG_DIR/lab-server-${PORT}.log"

if [[ ! -x "$PYTHON" ]]; then
    printf 'Terrario Lab no puede iniciarse: falta %s\n' "$PYTHON" >&2
    exit 1
fi

is_terrario_lab_running() {
    "$PYTHON" - "$PORT" <<'PY'
from http.client import HTTPConnection
import sys

try:
    connection = HTTPConnection("127.0.0.1", int(sys.argv[1]), timeout=1)
    connection.request("GET", "/api/v1/session")
    response = connection.getresponse()
    response.read()
    raise SystemExit(0 if response.status == 200 else 1)
except OSError:
    raise SystemExit(1)
PY
}

if ! is_terrario_lab_running; then
    mkdir -p "$LOG_DIR"
    (
        cd "$PROJECT_ROOT"
        exec "$PYTHON" -m terrario.lab.api \
            --root "$PROJECT_ROOT" \
            --data-root "$PROJECT_ROOT/.terrario" \
            --host 127.0.0.1 \
            --port "$PORT"
    ) >>"$LOG_FILE" 2>&1 &

    for _ in $(seq 1 30); do
        if is_terrario_lab_running; then
            break
        fi
        sleep 0.2
    done

    if ! is_terrario_lab_running; then
        printf 'Terrario Lab no respondió. Revisa el registro: %s\n' "$LOG_FILE" >&2
        exit 1
    fi
fi

if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL" >/dev/null 2>&1 &
else
    printf '%s\n' "$URL"
fi
