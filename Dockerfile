# ============================================================
# CCPA Compliance Analyzer — Unified Dockerfile
# Builds the React frontend + FastAPI backend into a single
# container, served via nginx (frontend) + uvicorn (backend).
# ============================================================

# ── Stage 1: Build the React frontend ────────────────────────
FROM node:22-slim AS frontend-build

WORKDIR /build

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build

# ── Stage 2: Python backend + nginx runtime ──────────────────
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install nginx, curl (for health checks), envsubst (from gettext-base)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    nginx \
    curl \
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

# Remove default nginx config
RUN rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf

# Copy nginx config template (uses $PORT substitution)
COPY nginx.conf /etc/nginx/templates/default.conf.template

WORKDIR /app

# ── Install Python dependencies ──────────────────────────────
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# ── Copy backend application code ────────────────────────────
COPY backend/app/ backend/app/
COPY backend/scripts/ backend/scripts/

# Pre-generate CCPA sections JSON
RUN cd backend && python scripts/preprocess_ccpa.py

# Pre-download the embedding model (~130MB, cached in image layer)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"

# ── Copy built frontend from Stage 1 ─────────────────────────
COPY --from=frontend-build /build/dist /usr/share/nginx/html

# ── Copy startup script ──────────────────────────────────────
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 10000

CMD ["/app/start.sh"]
