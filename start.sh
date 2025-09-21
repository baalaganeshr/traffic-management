#!/bin/bash
echo "🚀 Simple startup script for Render"
echo "📂 Directory: $(pwd)"
echo "📁 Files: $(ls -la)"
echo "🐍 Python version: $(python --version)"
echo "🌍 Port: $PORT"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Start the application
echo "🎯 Starting Kerala Traffic Demo..."
python run.py