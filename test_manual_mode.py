"""
Test manual mode point selection and wire generation.
"""

import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.enhanced_main_window import EnhancedMainWindow

def main():
    app = QApplication(sys.argv)
    
    try:
        window = EnhancedMainWindow()
        window.show()
        
        print("\n" + "="*60)
        print("MANUAL MODE TEST - Detailed Error Reporting")
        print("="*60)
        print("\nSteps:")
        print("1. Click 'Load Upper Arch'")
        print("2. Select Manual Mode radio button")
        print("3. Click 'Define Wire Path (0/3)'")
        print("4. Right-click 3 times on the mesh")
        print("5. Click 'Generate Wire'")
        print("6. Check console for any errors")
        print("="*60 + "\n")
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print("\n" + "="*60)
        print("CRITICAL ERROR:")
        print("="*60)
        print(f"Error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        print("="*60)

if __name__ == '__main__':
    main()