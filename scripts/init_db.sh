#!/bin/sh
# Run DB migrations + seed data, then start the server.
# Extra args are forwarded to uvicorn (e.g. --reload for dev).
set -e

echo "[init] Running Alembic migrations..."
alembic upgrade head

echo "[init] Seeding products and demo user..."
python scripts/import_csv.py

echo "[init] Starting server..."
exec uvicorn src.main:app --host 0.0.0.0 --port "${PORT:-8000}" "$@"
