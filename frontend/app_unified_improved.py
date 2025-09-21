#!/usr/bin/env python3
"""
Redirect file for Render deployment
Render is looking for this file due to cached configuration
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import and run the correct app
try:
    from frontend.streamlit_app import main
    if __name__ == "__main__":
        main()
except ImportError:
    # Fallback to direct execution
    import subprocess
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "frontend/streamlit_app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0"
    ])