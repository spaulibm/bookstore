#!/usr/bin/env bash
# Runs the bookstore API on http://localhost:${PORT:-8000} (docs at /docs)
set -e
cd "$(dirname "$0")"

[ -d .venv ] || python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate

pip install -q -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example - change SECRET_KEY before deploying."
fi

exec uvicorn app.main:app --reload --port "${PORT:-8000}"
