#!/usr/bin/env python3
"""
Orthodontic Wire Generator - Main Launcher
===========================================
This script launches the modern, PyQt5-based GUI for the orthodontic wire generator.

Usage:
    python3 run_app.py
"""

import sys
from pathlib import Path

# Add project root to path to ensure correct module imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """
    Main entry point for the application.
    This function imports and runs the enhanced PyQt5 main window.
    """
    print("="*70)
    print("Launching the Orthodontic Wire Generator (PyQt5 Edition)")
    print("="*70)
    print()

    try:
        # Import the main function from the enhanced GUI module
        from gui.enhanced_main_window import main as launch_gui

        # Launch the application
        launch_gui()

    except ImportError as e:
        print(f"❌ A critical error occurred while trying to launch the application: {e}")
        print("\nPlease ensure all required dependencies are installed.")
        print("You can install them by running:")
        print("pip install -r requirements_hybrid.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()