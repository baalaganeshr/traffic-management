# Production Dockerfile for Traffic Management System
# Multi-stage build for optimized production deployment

FROM python:3.11-slim as builder

# Set build arguments
ARG APP_VERSION=2.0.0
ARG BUILD_DATE
ARG VCS_REF

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set labels for better image management
LABEL maintainer="VIN Traffic System" \
      version="${APP_VERSION}" \
      description="Production Traffic Management System" \
      build-date="${BUILD_DATE}" \
      vcs-ref="${VCS_REF}"

# Create app user for security
RUN groupadd -r app && useradd -r -g app app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set up application directory
WORKDIR /app
RUN chown -R app:app /app

# Copy application files
COPY --chown=app:app . .

# Copy virtual environment path
ENV PATH="/opt/venv/bin:$PATH"

# Set production environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Expose port (Docker build requirement)
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8501}/_stcore/health || exit 1

# Switch to non-root user
USER app

# Use the production app launcher
CMD ["python", "start.py"]
