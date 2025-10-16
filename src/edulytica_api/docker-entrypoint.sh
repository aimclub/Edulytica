#!/bin/sh
set -eu

: "${API_PORT:=8002}"
: "${POSTGRES_PORT:=5432}"

export PGPASSWORD="${POSTGRES_PASSWORD:-}"

echo "Waiting for database at ${POSTGRES_IP}:${POSTGRES_PORT}..."
until psql -h "${POSTGRES_IP}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -p "${POSTGRES_PORT}" -c '\q' >/dev/null 2>&1; do
  >&2 echo "PostgreSQL is not ready, still waiting..."
  sleep 2
done

echo "PostgreSQL is ready, running migrations..."
alembic upgrade head

echo "Starting API on port ${API_PORT}..."
exec uvicorn src.edulytica_api.app:app --host 0.0.0.0 --port "${API_PORT}"
