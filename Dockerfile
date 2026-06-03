# Terra Natura — API en Render (Python only).
# Panel web: GitHub Pages · Marketing /app: PC local o build aparte.
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DEBUG=false

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend
COPY ama /app/ama
COPY agents /app/agents
COPY video_pro /app/video_pro

RUN mkdir -p /app/data /app/video_pro/uploads /app/video_pro/output

ENV DATABASE_URL=sqlite:////app/data/terra_natura.db

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1

CMD ["sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
