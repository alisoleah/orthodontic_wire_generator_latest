"""
Test script for PyVista + PyQt5 integration.
Verifies that 3-point selection works correctly.
"""

import sys
from PyQt5.QtWidgets import QApplication
from gui.enhanced_main_window import EnhancedMainWindow

def main():
    app = QApplication(sys.argv)
    
    # Create main window
    window = EnhancedMainWindow()
    window.show()
    
    # Test instructions
    print("\n" + "="*60)
    print("PyVista + PyQt5 Integration Test")
    print("="*60)
    print("\nTest Steps:")
    print("1. Click 'Load Upper Arch (.stl)' or 'Load Lower Arch (.stl)'")
    print("2. Select an STL file from STLfiles/assets/")
    print("3. Click 'Define Wire Path (0/3)'")
    print("4. Right-click on the mesh 3 times to select points")
    print("5. Verify that:")
    print("   - Red, green, blue spheres appear")
    print("   - Point labels show P1, P2, P3")
    print("   - Plane visualization appears (semi-transparent blue)")
    print("   - 'Generate Wire' button becomes enabled")
    print("\n" + "="*60 + "\n")
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()