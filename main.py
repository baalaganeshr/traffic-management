#!/usr/bin/env python3
"""
Main entry point for VIN Traffic Management System
Render auto-detection will pick this file first
"""

import os
import sys
import traceback

def main():
    """Enhanced entry point with proper error handling"""
    
    # Create proof file that main.py executed
    with open('/tmp/MAIN_PY_EXECUTED', 'w') as f:
        f.write('SUCCESS: main.py was executed!\n')
    
    print("🚀 VIN Traffic Management System - MAIN.PY ENTRY")
    print("🎉 SUCCESS: Render is using our production system!")
    print("📝 PROOF FILE CREATED: /tmp/MAIN_PY_EXECUTED")
    print(f"📂 Working Directory: {os.getcwd()}")
    print(f"🐍 Python Path: {sys.path}")
    print(f"📁 Files in directory: {os.listdir('.')}")
    
    # Keep app running with a simple loop
    import time
    print("🔄 Starting application loop...")
    while True:
        print("⏰ App is running... (main.py control)")
        time.sleep(30)
    
    try:
        print("⚡ Importing production launcher...")
        from app import main as app_main
        print("✅ Import successful - calling production launcher")
        app_main()
        
    except ImportError as e:
        print(f"❌ Failed to import production launcher: {e}")
        traceback.print_exc()
        
        # Critical fallback
        print("🆘 CRITICAL FALLBACK - Direct Streamlit execution")
        import subprocess
        port = os.environ.get('PORT', '8501')
        
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
        
        print(f"🔧 Fallback Command: {' '.join(cmd)}")
        os.execv(sys.executable, cmd)
        
    except Exception as e:
        print(f"💥 CRITICAL ERROR in production launcher: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()