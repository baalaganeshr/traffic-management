#!/usr/bin/env python3
"""
UrbanFlow360 - Official Render Entry Point
==========================================
This is the definitive startup script for Render deployment.
Render Blueprint (render.yaml) specifies this as the startCommand.
"""

import os
import sys

def main():
    """Official entry point for Render deployment"""
    
    print("🚀 VIN Traffic Management System v2.0.0")
    print("🏷️  OFFICIAL RENDER DEPLOYMENT")
    print("=" * 60)
    
    # Set production environment flags
    os.environ['VIN_PRODUCTION_MODE'] = 'true'
    os.environ['RENDER_DEPLOYMENT'] = 'true'
    
    # Log environment details
    print(f"🌍 Platform: Render Web Service")  
    print(f"🔌 Port: {os.environ.get('PORT', '10000')}")
    print(f"📁 Working Directory: {os.getcwd()}")
    print(f"🐍 Python Version: {sys.version}")
    
    # Use our production application launcher
    try:
        print("✅ Loading production application launcher...")
        from app import main as app_main
        print("🚀 Starting VIN Traffic Management System...")
        app_main()
        
    except ImportError as e:
        print(f"⚠️  Production launcher not available: {e}")
        print("� Using direct Streamlit startup...")
        
        # Direct Streamlit execution as fallback
        import subprocess
        port = os.environ.get('PORT', '10000')
        
        cmd = [
            sys.executable, '-m', 'streamlit', 'run',
            'frontend/app_unified_improved.py',
            f'--server.port={port}',
            '--server.address=0.0.0.0',
            '--server.headless=true',
            '--server.enableCORS=false', 
            '--server.enableXsrfProtection=false',
            '--browser.gatherUsageStats=false'
        ]
        
        print(f"🔧 Command: {' '.join(cmd)}")
        subprocess.exec(cmd)
        
    except Exception as e:
        print(f"❌ Critical startup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()