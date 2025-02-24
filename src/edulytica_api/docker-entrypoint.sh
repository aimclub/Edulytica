#!/bin/bash

echo "Ожидаем, пока база данных будет готова к подключению..."
until pg_isready -h edulytica_db -p 5432; do
  sleep 2
done

echo "Запуск миграций Alembic..."
alembic upgrade head

echo "Запуск API..."
exec "$@"
