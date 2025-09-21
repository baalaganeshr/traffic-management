#!/bin/bash

# Render-compatible start script with enhanced logging
# Uses $PORT if available (Render), otherwise defaults to 8501 (local)

PORT=${PORT:-8501}

echo "=== Traffic Management App Starting ==="
echo "Environment: ${RENDER:-local}"
echo "Port: $PORT"
echo "Working Directory: $(pwd)"
echo "Python Version: $(python --version)"
echo "Streamlit Version: $(streamlit --version)"
echo "Files in current directory:"
ls -la
echo "======================================"

# Verify the main app file exists
if [ ! -f "frontend/app_unified_improved.py" ]; then
    echo "ERROR: Main app file not found at frontend/app_unified_improved.py"
    echo "Available files:"
    find . -name "*.py" -type f
    exit 1
fi

echo "Starting Streamlit on port $PORT..."

# Run Streamlit with comprehensive configuration
exec streamlit run frontend/app_unified_improved.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --browser.gatherUsageStats=false \
    --global.developmentMode=false \
    --logger.level=info