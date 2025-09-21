#!/usr/bin/env python3
"""
Simple Render deployment entry point
"""

import os
import sys
import subprocess
import time

# Get port from environment (Render sets this)
port = os.environ.get('PORT', '10000')

print(f"🚀 Starting Kerala Traffic Demo on port {port}")
print(f"📂 Working directory: {os.getcwd()}")
print(f"📁 Available files: {os.listdir('.')}")
print(f"🌍 Environment PORT: {os.environ.get('PORT', 'Not Set')}")

# Ensure the demo file exists
if os.path.exists('demo/kerala_demo.py'):
    print("✅ Kerala demo file found")
else:
    print("❌ Kerala demo file NOT found")
    sys.exit(1)

# Run the Kerala demo directly with explicit process replacement
print(f"🔧 Executing Streamlit on port {port}")

# Use os.execv to replace the current process completely
cmd = [
    sys.executable, '-m', 'streamlit', 'run',
    'demo/kerala_demo.py',
    f'--server.port={port}',
    '--server.address=0.0.0.0',
    '--server.headless=true',
    '--server.enableCORS=false',
    '--server.enableXsrfProtection=false',
    '--browser.gatherUsageStats=false'
]

print(f"🎯 Final command: {' '.join(cmd)}")

# Replace current process with streamlit
os.execv(sys.executable, cmd)