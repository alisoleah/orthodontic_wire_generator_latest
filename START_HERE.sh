#!/bin/bash
# Orthodontic Wire Generator - Easy Launcher for Mac
# Just double-click this file or run: ./START_HERE.sh

clear

echo "════════════════════════════════════════════════════════════════"
echo "  ORTHODONTIC WIRE GENERATOR - Quick Start"
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
echo "  1. Test Open3D (verify 3D visualization works)"
echo "  2. Launch GUI (main application)"
echo "  3. Install/Update dependencies"
echo "  4. View Quick Start Guide"
echo "  5. Exit"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo "Testing Open3D visualization..."
        echo "A blue sphere should appear in a window"
        echo ""
        python3 test_open3d.py
        ;;
    2)
        echo ""
        echo "Launching Orthodontic Wire Generator GUI..."
        echo ""
        python3 run_app.py
        ;;
    3)
        echo ""
        echo "Installing/updating dependencies..."
        echo ""
        pip3 install -r requirements.txt
        echo ""
        echo "✅ Dependencies installed"
        ;;
    4)
        echo ""
        cat QUICK_START.md
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
