#!/usr/bin/env python3
"""
Orthodontic Wire Generator - Main Launcher
===========================================
This script now serves as a compatibility launcher for the main hybrid application.
It will execute `run_hybrid_app.py`, which is the correct entry point.

Usage:
    python3 run_app.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """
    Main entry point. Defers to the hybrid application launcher.
    """
    print("="*70)
    print("MODULAR ORTHODONTIC WIRE GENERATOR - LAUNCHER")
    print("="*70)
    print("\nThis script is a compatibility launcher.")
    print("Redirecting to the main application: run_hybrid_app.py\n")

    try:
        # Import and run the main function from the hybrid app
        from run_hybrid_app import main as hybrid_main
        hybrid_main()
    except ImportError as e:
        print(f"❌ Failed to launch the main application: {e}")
        print("Please ensure 'run_hybrid_app.py' exists and all dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()