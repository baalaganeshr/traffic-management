#!/usr/bin/env python3
"""
Simple Render deployment entry point
"""

import os
import sys
import subprocess

# Get port from environment
port = os.environ.get('PORT', '10000')

print(f"🚀 Starting Kerala Traffic Demo on port {port}")
print(f"📂 Working directory: {os.getcwd()}")
print(f"📁 Available files: {os.listdir('.')}")

# Run the Kerala demo directly
subprocess.run([
    sys.executable, '-m', 'streamlit', 'run',
    'demo/kerala_demo.py',
    f'--server.port={port}',
    '--server.address=0.0.0.0',
    '--server.headless=true',
    '--server.enableCORS=false',
    '--server.enableXsrfProtection=false',
    '--browser.gatherUsageStats=false'
])