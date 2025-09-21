#!/bin/bash

# Render-compatible start script
# Uses $PORT if available (Render), otherwise defaults to 8501 (local)

PORT=${PORT:-8501}

echo "Starting Streamlit on port $PORT..."

streamlit run frontend/app_unified_improved.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false