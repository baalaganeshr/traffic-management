#!/bin/bash

# Render Build Script - Explicit deployment instructions
echo "🚀 VIN Traffic System - Render Build Script"
echo "============================================"

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "✅ Build completed successfully!"
echo "🎯 Use 'python main.py' as start command"