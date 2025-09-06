"""
Entry point to launch the improved Professional dashboard directly.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from frontend.app_unified_improved import main

if __name__ == "__main__":
    main()

