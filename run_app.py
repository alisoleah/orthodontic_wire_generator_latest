#!/usr/bin/env python3
"""
Orthodontic Wire Generator - Main Launcher
===========================================
This script launches the modular orthodontic wire generator.

Usage:
    python3 run_app.py              # Launch GUI (default)
    python3 run_app.py --cli         # Command line mode
    python3 run_app.py <file.stl>   # Process specific STL file
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_requirements():
    """Check if all required packages are installed."""
    missing = []

    try:
        import numpy
    except ImportError:
        missing.append("numpy")

    try:
        import scipy
    except ImportError:
        missing.append("scipy")

    try:
        import open3d
    except ImportError:
        missing.append("open3d")

    try:
        import sklearn
    except ImportError:
        missing.append("scikit-learn")

    if missing:
        print("❌ Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nInstall with: pip3 install " + " ".join(missing))
        return False

    return True

def main():
    """Main entry point."""

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    print("="*70)
    print("MODULAR ORTHODONTIC WIRE GENERATOR")
    print("="*70)
    print()

    # Determine mode
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == '--gui'):
        # GUI mode (default)
        print("Launching GUI mode...")
        print()

        try:
            from gui.main_window import WireGeneratorGUI
            app = WireGeneratorGUI()
            app.run()
        except ImportError as e:
            print(f"❌ Error importing GUI: {e}")
            print("GUI components may not be available.")
            sys.exit(1)

    elif len(sys.argv) == 2 and sys.argv[1] == '--cli':
        # CLI mode
        print("Launching CLI mode...")
        print("This will run a command-line demonstration")
        print()

        from main import main_cli_demo
        main_cli_demo()

    elif len(sys.argv) == 2 and sys.argv[1].endswith('.stl'):
        # Process specific STL
        stl_path = sys.argv[1]
        if not os.path.exists(stl_path):
            print(f"❌ STL file not found: {stl_path}")
            sys.exit(1)

        print(f"Processing STL file: {stl_path}")
        print()

        from wire.wire_generator import WireGenerator

        generator = WireGenerator(stl_path=stl_path)
        results = generator.generate_wire()

        if results:
            generator.print_summary()
        else:
            print("❌ Wire generation failed")
            sys.exit(1)

    elif len(sys.argv) == 2 and sys.argv[1] in ['--help', '-h']:
        print(__doc__)

    else:
        print(f"❌ Unknown option: {sys.argv[1]}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
