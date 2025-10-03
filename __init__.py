
# ================================================================
# Main package __init__.py (orthodontic_wire_generator/__init__.py)
"""
Modular Orthodontic Wire Generator

A comprehensive system for generating custom orthodontic wires with:
- Advanced tooth detection and bracket positioning
- Interactive 3D wire editing with height control
- Real-time G-code generation for Arduino-controlled machines
- Professional-grade visualization and export capabilities

Architecture:
- Separated drawing algorithm and 3D rendering
- Modular components for easy testing and maintenance
- Clear separation of concerns
"""

from wire.wire_generator import WireGenerator
from core.constants import WIRE_SIZES
from gui.main_window import WireGeneratorGUI

# Main classes for easy import
__all__ = [
    'WireGenerator',
    'WireGeneratorGUI', 
    'WIRE_SIZES'
]

__version__ = "3.0.0"
__author__ = "Orthodontic Wire Generator Project"
__description__ = "Modular system for generating custom orthodontic wires"

# Quick start example
def quick_start_example():
    """
    Quick start example showing basic usage.
    
    Returns:
        WireGenerator instance ready for use
    """
    # This would be used like:
    # generator = quick_start_example()
    # results = generator.generate_wire()
    
    print("Quick Start Example:")
    print("1. generator = WireGenerator('model.stl', 'lower', '0.018')")
    print("2. results = generator.generate_wire()")
    print("3. generator.adjust_wire_height(1.0)")
    print("4. generator.launch_interactive_mode()")
    
    return None  # Would return actual generator with valid STL path

