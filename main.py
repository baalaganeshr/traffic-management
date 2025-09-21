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
    
    print("🚀 VIN Traffic Management System - MAIN.PY ENTRY")
    print("🎉 SUCCESS: Render is using our production system!")
    print(f"📂 Working Directory: {os.getcwd()}")
    print(f"📁 Files in directory: {os.listdir('.')}")
    
    # 🔥 NUCLEAR: Restore hidden app files to prevent auto-detection
    print("⚡ Restoring application files from hidden directory...")
    import shutil
    
    try:
        if os.path.exists('_app_hidden/frontend') and not os.path.exists('frontend'):
            shutil.move('_app_hidden/frontend', 'frontend')
            print("✅ Restored frontend directory")
            
        if os.path.exists('_app_hidden/demo') and not os.path.exists('demo'):
            shutil.move('_app_hidden/demo', 'demo') 
            print("✅ Restored demo directory")
            
        # Cleanup hidden directory
        if os.path.exists('_app_hidden'):
            os.rmdir('_app_hidden')
            print("✅ Cleaned up hidden directory")
            
    except Exception as e:
        print(f"⚠️ Warning: Could not restore files: {e}")
    
    print(f"📁 Files after restoration: {os.listdir('.')}")
    
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
        
        # Ensure files are restored before running
        if not os.path.exists('frontend/streamlit_app.py'):
            print("🆘 App files not found - cannot run fallback")
            sys.exit(1)
            
        cmd = [
            sys.executable, '-m', 'streamlit', 'run',
            'frontend/streamlit_app.py',
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