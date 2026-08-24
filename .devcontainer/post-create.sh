#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv"
PYTHON="$VENV/bin/python"
STATE="$ROOT/.devcontainer/.state"
DATABASE_FILE="$STATE/finance_portal_codespace.db"
CREDENTIALS_FILE="$STATE/demo-credentials.txt"

umask 077
mkdir -p "$STATE"
chmod 700 "$STATE"

python -m venv "$VENV"
"$PYTHON" -m pip install \
  --disable-pip-version-check \
  -r "$ROOT/backend/requirements-dev.txt"

npm --prefix "$ROOT/frontend" ci --no-audit --no-fund

export DATABASE_URL="sqlite:///$DATABASE_FILE"

cd "$ROOT/backend"
"$PYTHON" -m alembic upgrade head

seed_output="$("$PYTHON" -m app.seed)"
printf '%s\n' "$seed_output"

if grep -q "Credenciales demo generadas" <<<"$seed_output"; then
  printf '%s\n' "$seed_output" > "$CREDENTIALS_FILE"
elif [[ ! -f "$CREDENTIALS_FILE" ]]; then
  printf '%s\n' \
    "La base ya existe, pero falta el archivo local de credenciales." >&2
  printf '%s\n' \
    "Crea un Codespace nuevo para generar otra base de demostracion." >&2
  exit 1
fi

chmod 600 "$DATABASE_FILE" "$CREDENTIALS_FILE"
