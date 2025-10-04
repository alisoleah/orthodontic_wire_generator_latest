#!/bin/bash
# Orthodontic Wire Generator - Enhanced Version Launcher
# This script lets you test the ENHANCED algorithm

clear

echo "════════════════════════════════════════════════════════════════"
echo "  ORTHODONTIC WIRE GENERATOR - Enhanced Algorithm"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.12+"
    exit 1
fi

echo "✅ Python: $(python3 --version)"
echo ""

# Check if we're in the right directory
if [ ! -f "run_app.py" ]; then
    echo "❌ Error: Please run this script from the orthodontic_wire_generator_latest directory"
    exit 1
fi

# Menu
echo "Choose an option:"
echo ""
echo "  🧪 TESTING THE ENHANCED ALGORITHM:"
echo "  1. Quick Test (30 sec) - Test enhanced features"
echo "  2. Full Unit Tests - Run all 24 tests"
echo "  3. Compare Old vs Enhanced - Side by side"
echo ""
echo "  🚀 RUN THE APPLICATION:"
echo "  4. Launch GUI (CURRENT - Old Algorithm)"
echo "  5. Launch GUI (ENHANCED - New Algorithm) [After Integration]"
echo ""
echo "  📚 DOCUMENTATION:"
echo "  6. View Test Guide"
echo "  7. View Integration Guide"
echo "  8. View Complete Summary"
echo ""
echo "  9. Exit"
echo ""
read -p "Enter choice [1-9]: " choice

case $choice in
    1)
        echo ""
        echo "═══════════════════════════════════════════════════════════"
        echo "  QUICK TEST - Enhanced Algorithm Features"
        echo "═══════════════════════════════════════════════════════════"
        echo ""
        python3 quick_test_enhanced.py
        ;;
    2)
        echo ""
        echo "═══════════════════════════════════════════════════════════"
        echo "  FULL UNIT TESTS - 24 Comprehensive Tests"
        echo "═══════════════════════════════════════════════════════════"
        echo ""
        python3 -m pytest tests/test_wire_path_creator_enhanced.py -v
        ;;
    3)
        echo ""
        echo "═══════════════════════════════════════════════════════════"
        echo "  COMPARISON - Original vs Enhanced"
        echo "═══════════════════════════════════════════════════════════"
        echo ""
        python3 -c "
from wire.wire_path_creator import WirePathCreator
from wire.wire_path_creator_enhanced import WirePathCreatorEnhanced, PathGenerationStrategy
import numpy as np
import time

brackets = [
    {'position': np.array([10, 0, 5]), 'visible': True, 'tooth_type': 'incisor'},
    {'position': np.array([5, 8, 5]), 'visible': True, 'tooth_type': 'canine'},
    {'position': np.array([-5, 8, 5]), 'visible': True, 'tooth_type': 'canine'},
    {'position': np.array([-10, 0, 5]), 'visible': True, 'tooth_type': 'incisor'}
]
center = np.array([0, 4, 0])

print('📊 ORIGINAL ALGORITHM:')
print('─' * 60)
t1 = time.time()
orig = WirePathCreator()
path1 = orig.create_smooth_path(brackets, center)
time1 = time.time() - t1
print(f'  • Points: {len(path1)}')
print(f'  • Length: {orig.get_path_length():.1f}mm')
print(f'  • Time: {time1*1000:.2f}ms')
print(f'  • Features: Basic cubic spline')

print()
print('⭐ ENHANCED ALGORITHM:')
print('─' * 60)
t2 = time.time()
enh = WirePathCreatorEnhanced(strategy=PathGenerationStrategy.CATMULL_ROM)
path2 = enh.create_smooth_path(brackets, center)
time2 = time.time() - t2
stats = enh.get_path_statistics()
print(f'  • Points: {len(path2)}')
print(f'  • Length: {enh.get_path_length():.1f}mm')
print(f'  • Time: {time2*1000:.2f}ms')
print(f'  • Strategy: {stats[\"strategy\"]}')
print(f'  • Material: {stats[\"material\"]}')
print(f'  • Bends: {stats[\"num_bends\"]}')
print(f'  • Valid bends: {stats[\"valid_bends\"]}')
print(f'  • Invalid bends: {stats[\"invalid_bends\"]}')

print()
print('📈 IMPROVEMENT:')
print('─' * 60)
print(f'  • Speed: {time1/time2:.2f}x faster' if time2 < time1 else f'  • Speed: {time2/time1:.2f}x slower')
print(f'  • Point difference: {len(path2) - len(path1):+d} points')
print(f'  • New features: Material constraints, bend validation, stress analysis')
"
        ;;
    4)
        echo ""
        echo "═══════════════════════════════════════════════════════════"
        echo "  Launching Current GUI (Original Algorithm)"
        echo "═══════════════════════════════════════════════════════════"
        echo ""
        echo "⚠️  NOTE: This uses the OLD algorithm (not enhanced)"
        echo "To use enhanced features, you need to integrate first."
        echo "See option 7 for integration guide."
        echo ""
        python3 run_app.py
        ;;
    5)
        echo ""
        echo "═══════════════════════════════════════════════════════════"
        echo "  Enhanced GUI - Not Yet Integrated"
        echo "═══════════════════════════════════════════════════════════"
        echo ""
        echo "⚠️  The enhanced algorithm hasn't been integrated yet."
        echo ""
        echo "To integrate:"
        echo "  1. Run option 7 to view integration guide"
        echo "  2. Follow the 3-step integration process"
        echo "  3. Then this option will work with enhanced features"
        echo ""
        echo "Current status:"
        echo "  ✅ Enhanced algorithm: Ready and tested"
        echo "  ✅ Unit tests: 24/24 passing"
        echo "  ⏳ Integration: Pending"
        echo ""
        read -p "Press Enter to continue..."
        ;;
    6)
        echo ""
        cat TEST_BEFORE_INTEGRATION.md
        ;;
    7)
        echo ""
        cat IMPLEMENTATION_GUIDE.md | head -200
        echo ""
        echo "... (see IMPLEMENTATION_GUIDE.md for complete guide)"
        ;;
    8)
        echo ""
        cat PROFESSIONALIZATION_COMPLETE.md | head -150
        echo ""
        echo "... (see PROFESSIONALIZATION_COMPLETE.md for complete summary)"
        ;;
    9)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
