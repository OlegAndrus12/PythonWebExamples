#!/bin/sh

echo "DB user is $DB_USER"
echo "DB host is $DB_DOMAIN"

# Example: wait for Postgres
until pg_isready -h "$DB_DOMAIN" -p "$DB_PORT" -U "$DB_USER"; do
  echo "Waiting for Postgres..."
  sleep 1
done


echo "Running Alembic migrations..."
poetry run alembic upgrade head

echo "Starting FastAPI server..."
export UVICORN_APP=main:app
export UVICORN_HOST=0.0.0.0
export UVICORN_PORT=8000
export UVICORN_RELOAD=true

poetry run uvicorn $UVICORN_APP --host $UVICORN_HOST --port $UVICORN_PORT --reload
