#!/bin/sh
set -e

case "${RAILWAY_SERVICE_NAME:-}" in
  bot)
    echo "Starting bot (RAILWAY_SERVICE_NAME=bot)"
    exec python -m bgclub_bot.main
    ;;
  *)
    echo "Starting API (RAILWAY_SERVICE_NAME=${RAILWAY_SERVICE_NAME:-api})"
    exec sh scripts/start_api_prod.sh
    ;;
esac
