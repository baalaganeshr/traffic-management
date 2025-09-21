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
    # Import and run the enhanced Kerala demo directly
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    
    if __name__ == "__main__":
        # Direct execution of Kerala demo
        import subprocess
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "demo/kerala_demo.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=true"
        ])
except Exception as e:
    # Fallback to direct execution
    import subprocess
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "demo/kerala_demo.py",
        "--server.port=8501",
        "--server.address=0.0.0.0"
    ])