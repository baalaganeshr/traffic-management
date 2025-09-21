#!/usr/bin/env python3
"""
UrbanFlow360 Production Starter
================================
This script ensures the application starts correctly in any environment.
It's designed to be the definitive entry point for all deployment platforms.
"""

import os
import sys
import subprocess

def start_application():
    """Start the UrbanFlow360 application with proper configuration"""
    
    print("🚀 UrbanFlow360 Production Starter")
    print("=" * 50)
    
    # Set production mode flag
    os.environ['VIN_PRODUCTION_MODE'] = 'true'
    
    # Detect environment
    environment = "Unknown"
    if os.environ.get('RENDER'):
        environment = "Render"
    elif os.environ.get('RAILWAY_ENVIRONMENT'):
        environment = "Railway"  
    elif os.environ.get('DYNO'):
        environment = "Heroku"
    elif os.environ.get('PORT'):
        environment = "Cloud Platform"
    else:
        environment = "Local/Docker"
    
    print(f"🌍 Environment: {environment}")
    
    # Get port
    port = os.environ.get('PORT', '8501')
    print(f"🔌 Port: {port}")
    
    # Try to use our production launcher first
    try:
        print("✅ Starting production launcher...")
        from app import main
        main()
    except ImportError as e:
        print(f"⚠️  Production launcher not available: {e}")
        print("🔄 Falling back to direct Streamlit execution")
        
        # Fallback to direct Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            "frontend/app_unified_improved.py",
            "--server.port", port,
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ]
        
        print(f"🔧 Command: {' '.join(cmd)}")
        subprocess.run(cmd)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("🆘 Critical startup failure")
        sys.exit(1)

if __name__ == "__main__":
    start_application()