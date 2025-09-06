# UrbanFlow360 PRIT Enhanced Deployment Script (Windows)

Write-Host "🚦 UrbanFlow360 - PRIT Enhanced Deployment" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Stop any existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker stop urbanflow360-prit-enhanced 2>$null
docker stop urbanflow360-gamified-live 2>$null

# Remove old containers  
Write-Host "Cleaning up old containers..." -ForegroundColor Yellow
docker rm urbanflow360-prit-enhanced 2>$null

# Build new image
Write-Host "Building PRIT-Enhanced image..." -ForegroundColor Yellow
docker build -t urbanflow360-prit-enhanced .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build successful!" -ForegroundColor Green
    
    # Run the container
    Write-Host "Starting PRIT-Enhanced container..." -ForegroundColor Yellow
    docker run -d -p 8512:8501 --name urbanflow360-prit-enhanced urbanflow360-prit-enhanced
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Deployment successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎉 Your enhanced system is ready!" -ForegroundColor Cyan
        Write-Host "🌐 Access at: http://localhost:8512" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Available interfaces:" -ForegroundColor White
        Write-Host "  🏢 Professional Dashboard" -ForegroundColor Gray
        Write-Host "  🎮 Gamified Interface" -ForegroundColor Gray
        Write-Host "  🤖 PRIT Enhanced (NEW!)" -ForegroundColor Green
        Write-Host ""
        Write-Host "Features:" -ForegroundColor White
        Write-Host "  ⚡ Automatic Input/Output Generation" -ForegroundColor Gray
        Write-Host "  🧠 NEAT Neural Networks" -ForegroundColor Gray
        Write-Host "  🚗 Realistic Vehicle Physics" -ForegroundColor Gray
        Write-Host "  🏆 Gamification with XP/Badges" -ForegroundColor Gray
        Write-Host "  📊 Real-time Performance Analytics" -ForegroundColor Gray
        Write-Host ""
        
        # Wait a moment then check status
        Start-Sleep 3
        Write-Host "Container status:" -ForegroundColor White
        docker ps | Select-String "urbanflow360-prit-enhanced"
        
        Write-Host ""
        Write-Host "📋 Quick commands:" -ForegroundColor White
        Write-Host "  View logs: docker logs urbanflow360-prit-enhanced -f" -ForegroundColor Gray
        Write-Host "  Stop: docker stop urbanflow360-prit-enhanced" -ForegroundColor Gray
        Write-Host "  Restart: docker restart urbanflow360-prit-enhanced" -ForegroundColor Gray
        
    } else {
        Write-Host "❌ Failed to start container" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}
