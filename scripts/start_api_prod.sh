#!/bin/sh
set -e

if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL is empty."
  echo "Env keys: $(env | cut -d= -f1 | sort | tr '\n' ' ')"
  exit 1
fi
if [ -z "$REDIS_URL" ]; then
  echo "ERROR: REDIS_URL is empty."
  exit 1
fi

echo "Starting: DATABASE_URL set, REDIS_URL set"

alembic upgrade head
exec uvicorn bgclub_api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
