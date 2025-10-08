#!/usr/bin/env python3
"""
Hybrid Orthodontic Wire Generator Application

This is the main entry point for the enhanced hybrid workflow application
that supports automatic, manual, and hybrid wire design modes.

Features:
- Automatic tooth detection and wire generation
- Manual control point placement (FixR style)
- Hybrid workflow combining both approaches
- Dual-arch support (upper/lower)
- Collision detection with opposing arch
- Professional UI with PyQt5
- Multiple export formats (G-code, ESP32, STL)

Usage:
    python run_hybrid_app.py

Requirements:
    - PyQt5 (for GUI)
    - PyOpenGL (for 3D visualization)
    - numpy, scipy (for calculations)
    - trimesh (for mesh processing)
    - All existing project dependencies
"""

import sys
import os
import traceback
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []

    # Check PyQt5
    try:
        import PyQt5
        print("[OK] PyQt5 available")
    except ImportError:
        missing_deps.append("PyQt5")
        print("[X] PyQt5 not available")

    # Check PyOpenGL
    try:
        import OpenGL
        print("[OK] PyOpenGL available")
    except ImportError:
        missing_deps.append("PyOpenGL")
        print("[X] PyOpenGL not available")

    # Check numpy
    try:
        import numpy
        print("[OK] NumPy available")
    except ImportError:
        missing_deps.append("numpy")
        print("[X] NumPy not available")

    # Check scipy
    try:
        import scipy
        print("[OK] SciPy available")
    except ImportError:
        missing_deps.append("scipy")
        print("[X] SciPy not available")

    # Check trimesh
    try:
        import trimesh
        print("[OK] Trimesh available")
    except ImportError:
        missing_deps.append("trimesh")
        print("[X] Trimesh not available")

    return missing_deps

def install_dependencies(missing_deps):
    """Attempt to install missing dependencies"""
    if not missing_deps:
        return True
    
    print(f"\nMissing dependencies: {', '.join(missing_deps)}")
    print("Attempting to install missing dependencies...")
    
    try:
        import subprocess
        
        # Install missing packages
        for dep in missing_deps:
            print(f"Installing {dep}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"[OK] {dep} installed successfully")
            else:
                print(f"[X] Failed to install {dep}: {result.stderr}")
                return False
        
        return True
        
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return False

def run_application():
    """Run the hybrid orthodontic wire generator application"""
    try:
        # Import the enhanced main window
        from gui.enhanced_main_window import main
        
        print("Starting Hybrid Orthodontic Wire Generator...")
        print("=" * 50)
        print("Features available:")
        print("• Automatic tooth detection and wire generation")
        print("• Manual control point placement (FixR style)")
        print("• Hybrid workflow (auto + manual refinement)")
        print("• Dual-arch support (upper/lower)")
        print("• Collision detection")
        print("• Multiple export formats")
        print("=" * 50)
        
        # Run the application
        main()
        
    except ImportError as e:
        print(f"❌ A critical component could not be imported: {e}")
        print("This is often due to an incomplete installation or a problem with a core module.")
        print("Please ensure all dependencies from 'requirements_hybrid.txt' are installed correctly.")
        print("If the problem persists, consider reinstalling the required packages.")
        traceback.print_exc()
        return False
    
    except Exception as e:
        print(f"Application error: {e}")
        print("Traceback:")
        traceback.print_exc()
        return False
    
    return True

def show_help():
    """Show help information"""
    help_text = """
Hybrid Orthodontic Wire Generator - Help

USAGE:
    python run_hybrid_app.py [options]

OPTIONS:
    --help, -h          Show this help message
    --check-deps        Check dependencies only
    --install-deps      Install missing dependencies
    --fallback          Run fallback application

WORKFLOW MODES:
    1. Automatic Mode:
       - Load STL file
       - Automatic tooth detection
       - Wire generated automatically
       - Adjust height if needed
       - Export

    2. Manual Mode:
       - Load STL file
       - Define occlusal plane (3 points)
       - Place control points on teeth
       - Generate wire from points
       - Export

    3. Hybrid Mode:
       - Load STL file
       - Run automatic detection
       - Convert to manual control points
       - Drag/adjust points as needed
       - Export

KEYBOARD SHORTCUTS:
    F3              Switch to Automatic Mode
    F4              Switch to Manual Mode
    F5              Switch to Hybrid Mode
    R               Reset camera view
    F1              Toggle control panel
    F2              Toggle status panel
    Ctrl+N          New project
    Ctrl+O          Open project
    Ctrl+S          Save project
    Ctrl+Q          Exit application

MOUSE CONTROLS:
    Left Click      Place points / Select objects
    Right Drag      Rotate camera
    Mouse Wheel     Zoom in/out
    Left Drag       Move control points (in edit mode)

SUPPORTED FILE FORMATS:
    Input:  STL files (dental arch models)
    Output: G-code, ESP32 Arduino code, STL

For more information, see the documentation or use the Help menu in the application.
"""
    print(help_text)

def main():
    """Main entry point"""
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--help', '-h']:
            show_help()
            return
        
        elif arg == '--check-deps':
            print("Checking dependencies...")
            missing_deps = check_dependencies()
            if missing_deps:
                print(f"\nMissing dependencies: {', '.join(missing_deps)}")
                print("Run with --install-deps to install them.")
            else:
                print("\n[OK] All dependencies are available!")
            return

        elif arg == '--install-deps':
            print("Checking and installing dependencies...")
            missing_deps = check_dependencies()
            if install_dependencies(missing_deps):
                print("\n[OK] All dependencies installed successfully!")
            else:
                print("\n[X] Failed to install some dependencies.")
            return
        
    
    # Check dependencies first
    print("Hybrid Orthodontic Wire Generator v2.0")
    print("Checking dependencies...")
    
    missing_deps = check_dependencies()
    
    if missing_deps:
        print(f"\nMissing dependencies: {', '.join(missing_deps)}")
        
        # Ask user if they want to install
        try:
            response = input("\nWould you like to install missing dependencies? (y/n): ").lower()
            if response in ['y', 'yes']:
                if install_dependencies(missing_deps):
                    print("\nDependencies installed. Starting application...")
                else:
                    print("\nFailed to install dependencies. Exiting.")
                    return
            else:
                print("Cannot run without required dependencies. Exiting.")
                return
        except KeyboardInterrupt:
            print("\nExiting.")
            return
    
    # Run the application
    success = run_application()
    
    if not success:
        print("\nApplication failed to start. Try running with --fallback option.")

if __name__ == "__main__":
    main()
