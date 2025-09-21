#!/bin/bash

# Alternative start script for debugging Render deployment
PORT=${PORT:-8501}

echo "=== DEBUG: Traffic Management Deployment ==="
echo "PORT: $PORT"
echo "RENDER: ${RENDER:-not set}"
echo "Working Directory: $(pwd)"
echo "Python: $(python --version)"
echo "Streamlit: $(streamlit --version)"
echo "Environment Variables:"
env | grep -E "(PORT|RENDER|STREAMLIT)" || echo "No relevant env vars"
echo "Files in app directory:"
ls -la
echo "Frontend directory contents:"
ls -la frontend/ || echo "Frontend directory not found"
echo "============================================"

# Try to run the test app first
if [ "$1" = "test" ] || [ ! -f "frontend/app_unified_improved.py" ]; then
    echo "Running test app..."
    exec streamlit run test_app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
else
    echo "Running main app..."
    exec streamlit run frontend/app_unified_improved.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false
fi