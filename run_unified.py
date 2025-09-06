"""
UrbanFlow360 - Main Entry Point
Unified traffic management system combining Professional, Gamified, and PRIT Enhanced interfaces
"""

import sys
import os

# Add the current directory to Python path for proper imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the unified dashboard
from frontend.app_unified import main

if __name__ == "__main__":
    main()
