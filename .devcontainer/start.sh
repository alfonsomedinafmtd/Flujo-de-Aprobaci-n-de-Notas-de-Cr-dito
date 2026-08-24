#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$ROOT/.venv/bin/python"
STATE="$ROOT/.devcontainer/.state"
DATABASE_FILE="$STATE/finance_portal_codespace.db"
CREDENTIALS_FILE="$STATE/demo-credentials.txt"

umask 077
mkdir -p "$STATE"
chmod 700 "$STATE"

portal_url="http://localhost:5173"
api_url="http://localhost:8000/docs"
vite_allowed_host=""
allowed_hosts="localhost,127.0.0.1,testserver"
session_cookie_secure="false"

if [[ "${CODESPACES:-}" == "true" ]] &&
   [[ -n "${CODESPACE_NAME:-}" ]] &&
   [[ -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]]; then
  frontend_host="${CODESPACE_NAME}-5173.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
  backend_host="${CODESPACE_NAME}-8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"

  portal_url="https://${frontend_host}"
  api_url="https://${backend_host}/docs"
  vite_allowed_host="$frontend_host"
  allowed_hosts="${allowed_hosts},${backend_host}"
  session_cookie_secure="true"
fi

export DATABASE_URL="sqlite:///$DATABASE_FILE"
export CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"
export ALLOWED_HOSTS="$allowed_hosts"
export SESSION_COOKIE_SECURE="$session_cookie_secure"

(
  cd "$ROOT/backend"
  "$PYTHON" -m alembic upgrade head
)

if ! curl -fsS "http://127.0.0.1:8000/api/health" >/dev/null 2>&1; then
  (
    cd "$ROOT/backend"
    nohup "$PYTHON" -m uvicorn app.main:app \
      --reload \
      --host 0.0.0.0 \
      --port 8000 \
      >"$STATE/backend.log" 2>&1 </dev/null &
    printf '%s\n' "$!" >"$STATE/backend.pid"
  )
fi

if ! curl -fsS "http://127.0.0.1:5173" >/dev/null 2>&1; then
  vite_environment=("VITE_API_URL=/api")
  if [[ -n "$vite_allowed_host" ]]; then
    vite_environment+=(
      "__VITE_ADDITIONAL_SERVER_ALLOWED_HOSTS=$vite_allowed_host"
    )
  fi

  (
    cd "$ROOT/frontend"
    nohup env "${vite_environment[@]}" \
      npm run dev -- --host 0.0.0.0 --port 5173 --strictPort \
      >"$STATE/frontend.log" 2>&1 </dev/null &
    printf '%s\n' "$!" >"$STATE/frontend.pid"
  )
fi

wait_for_service() {
  local name="$1"
  local url="$2"
  local log="$3"

  for _ in $(seq 1 45); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done

  printf 'No inicio %s. Ultimas lineas:\n' "$name" >&2
  tail -n 80 "$log" 2>/dev/null || true
  return 1
}

wait_for_service \
  "FastAPI" \
  "http://127.0.0.1:8000/api/health" \
  "$STATE/backend.log"

wait_for_service \
  "Vite" \
  "http://127.0.0.1:5173" \
  "$STATE/frontend.log"

printf '\nPortal: %s\nAPI: %s\n' "$portal_url" "$api_url"

if [[ -f "$CREDENTIALS_FILE" ]]; then
  printf '\nCredenciales aleatorias de esta base:\n'
  cat "$CREDENTIALS_FILE"
fi
