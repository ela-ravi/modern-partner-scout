# =============================================================================
# PartnerScout AI — Backend Dockerfile
# Base: Python 3.13 slim (Debian Bookworm)
# Runs FastAPI via Uvicorn on port 8000
# =============================================================================

# -- Base image ---------------------------------------------------------------
# Using slim variant to keep the image small (~150MB vs ~1GB for full)
FROM python:3.13-slim-bookworm AS base

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
# so logs appear immediately in `docker logs`
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# -- System dependencies ------------------------------------------------------
# Install only the OS packages needed by Python libs (lxml, cryptography, etc.)
# Then clean up apt cache to keep the layer small
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libxml2-dev \
        libxslt1-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# -- Application directory -----------------------------------------------------
WORKDIR /app

# -- Install Python dependencies -----------------------------------------------
# Copy requirements first so Docker can cache this layer when code changes
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -- Copy application code -----------------------------------------------------
# This layer is rebuilt whenever source code changes
COPY . .

# -- Create non-root user ------------------------------------------------------
# Running as root inside a container is a security risk; create a dedicated user
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app

# Switch to the non-root user for all subsequent commands and runtime
USER appuser

# -- Expose port ---------------------------------------------------------------
# Uvicorn will listen on this port; Docker Compose maps it internally
EXPOSE 8000

# -- Health check ---------------------------------------------------------------
# Docker will ping this endpoint every 30s; container is marked unhealthy after 3 failures
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# -- Start the app --------------------------------------------------------------
# 0.0.0.0 binds to all interfaces so the container is reachable from Docker network
# --workers 2 is a safe default for a KVM2 VPS (2-4 vCPUs typically)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
