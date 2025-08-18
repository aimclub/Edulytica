#!/bin/sh
set -e

export PGPASSWORD="$POSTGRES_PASSWORD"

echo "Waiting for database..."
until psql -h "$POSTGRES_IP" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -p "$POSTGRES_PORT" -c '\q'; do
  >&2 echo "PostgreSQL is not ready, still waiting..."
  sleep 2
done

echo "PostgreSQL is ready, migration starting..."
alembic upgrade head
exec uvicorn edulytica.edulytica_api.app:app --host 0.0.0.0 --port 8002
