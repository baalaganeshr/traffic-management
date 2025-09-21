#!/bin/bash

# Render Start Script - Forces our production launcher
echo "🚦 Starting VIN Traffic Management System..."
echo "🌍 Environment: ${RENDER:-unknown}"
echo "🔌 Port: ${PORT:-8501}"

# Run our production launcher
exec python main.py