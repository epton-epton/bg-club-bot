FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ ./shared/
COPY api/ ./api/
COPY bot/ ./bot/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY scripts/ ./scripts/
RUN chmod +x scripts/start_api_prod.sh

ENV PYTHONPATH=/app/shared:/app/api:/app/bot

CMD ["sh", "scripts/start_api_prod.sh"]
