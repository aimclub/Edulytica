#!/bin/sh

set -e

export POSTGRES_USER="edulytica"
export POSTGRES_PASSWORD="edulyticapassword"
export POSTGRES_DB="edulytica"
export PGPASSWORD="edulyticapassword"

until psql -h "edulytica_db" -U "edulytica" -d "edulytica" -c '\q'; do
  >&2 echo "Waiting Postgres..."
  sleep 2
done

echo "PostgreSQL is available. Starting migrations..."

alembic upgrade head

echo "Migrations are done."

exec uvicorn src.edulytica_api.app:app --host 0.0.0.0 --port 8000
