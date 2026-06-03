# Terra Natura — API + apps internas (/app, /video-pro)
FROM node:20-alpine AS frontend

WORKDIR /build

# App operativa (panel dueño)
COPY frontend/app/package.json frontend/app/package-lock.json frontend/app/
RUN cd frontend/app && npm ci
COPY frontend/app frontend/app
RUN cd frontend/app && npm run build

# Video Pro Creator
COPY frontend/video-pro-creator/package.json frontend/video-pro-creator/package-lock.json frontend/video-pro-creator/
RUN cd frontend/video-pro-creator && npm ci
COPY frontend/video-pro-creator frontend/video-pro-creator
RUN cd frontend/video-pro-creator && npm run build

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
COPY database /app/database
COPY video_pro /app/video_pro

COPY --from=frontend /build/frontend/app/dist /app/frontend/app/dist
COPY --from=frontend /build/frontend/video-pro-creator/dist /app/frontend/video-pro-creator/dist

RUN mkdir -p /app/data /app/video_pro/uploads /app/video_pro/output
ENV DATABASE_URL=sqlite:////app/data/terra_natura.db

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1

CMD ["sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
