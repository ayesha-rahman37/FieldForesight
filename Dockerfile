# ==============================================================================
# FieldForesight Backend - Production Dockerfile
# Optimized for FastAPI, ML/AI Inference (CPU), Render, Railway, & Cloud Run
# ==============================================================================

FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000

WORKDIR /app

# Install system build dependencies required for C-extensions (psycopg2, numpy, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install lightweight CPU-only PyTorch first to avoid massive CUDA binaries (~5GB savings)
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application source code
COPY app/ ./app/
COPY main.py .

# Create a non-root security user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose backend service port
EXPOSE 8000

# Health check to ensure FastAPI is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/docs || exit 1

# Start Uvicorn server dynamically binding to Render/Cloud $PORT
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

