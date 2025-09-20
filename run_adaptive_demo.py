"""Entry point for the adaptive signal demo."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from demo.app_adaptive_demo import main


if __name__ == "__main__":
    # Streamlit expects working directory to include project root packages
    os.environ.setdefault("STREAMLIT_SERVER_PORT", "8502")
    main()
