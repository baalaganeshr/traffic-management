#!/bin/bash
# UrbanFlow360 PRIT Enhanced Deployment Script

echo "🚦 UrbanFlow360 - PRIT Enhanced Deployment"
echo "============================================="

# Stop any existing containers
echo "Stopping existing containers..."
docker stop urbanflow360-prit-enhanced 2>/dev/null || true
docker stop urbanflow360-gamified-live 2>/dev/null || true

# Remove old containers
echo "Cleaning up old containers..."
docker rm urbanflow360-prit-enhanced 2>/dev/null || true

# Build new image
echo "Building PRIT-Enhanced image..."
docker build -t urbanflow360-prit-enhanced .

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    # Run the container
    echo "Starting PRIT-Enhanced container..."
    docker run -d -p 8512:8501 --name urbanflow360-prit-enhanced urbanflow360-prit-enhanced
    
    if [ $? -eq 0 ]; then
        echo "✅ Deployment successful!"
        echo ""
        echo "🎉 Your enhanced system is ready!"
        echo "🌐 Access at: http://localhost:8512"
        echo ""
        echo "Available interfaces:"
        echo "  🏢 Professional Dashboard"
        echo "  🎮 Gamified Interface" 
        echo "  🤖 PRIT Enhanced (NEW!)"
        echo ""
        echo "Features:"
        echo "  ⚡ Automatic Input/Output Generation"
        echo "  🧠 NEAT Neural Networks"
        echo "  🚗 Realistic Vehicle Physics"
        echo "  🏆 Gamification with XP/Badges"
        echo "  📊 Real-time Performance Analytics"
        echo ""
        
        # Wait a moment then check status
        sleep 3
        echo "Container status:"
        docker ps | grep urbanflow360-prit-enhanced
        
        echo ""
        echo "📋 Quick commands:"
        echo "  View logs: docker logs urbanflow360-prit-enhanced -f"
        echo "  Stop: docker stop urbanflow360-prit-enhanced"
        echo "  Restart: docker restart urbanflow360-prit-enhanced"
        
    else
        echo "❌ Failed to start container"
        exit 1
    fi
else
    echo "❌ Build failed"
    exit 1
fi
