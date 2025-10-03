#!/usr/bin/env python3
"""
GUI Launcher for Orthodontic Wire Generator
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.main_window import WireGeneratorGUI

if __name__ == "__main__":
    print("Launching Orthodontic Wire Generator GUI...")
    app = WireGeneratorGUI()
    app.run()