#!/usr/bin/env sh
set -eu

APP_PORT="${PORT:-8000}"

echo "Running database migrations..."
alembic upgrade head

echo "Starting backend on port ${APP_PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${APP_PORT}"
