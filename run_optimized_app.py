#!/usr/bin/env python3
"""
run_optimized_app.py

Optimized Wire Generator with Smooth Real-Time Interaction
===========================================================
This script runs the wire generator with automatic performance optimizations
for smooth, responsive wire position adjustments.

Usage:
    python3 run_optimized_app.py <file.stl>

Example:
    python3 run_optimized_app.py STLfiles/assets/ayalower.stl
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import optimizations FIRST - this automatically patches the WireGenerator
import apply_optimizations

from wire.wire_generator import WireGenerator


def main():
    """Main entry point with optimizations."""
    print("="*70)
    print("OPTIMIZED ORTHODONTIC WIRE GENERATOR")
    print("Real-Time Smooth Wire Adjustment")
    print("="*70)
    print()

    if len(sys.argv) < 2:
        print("Usage: python3 run_optimized_app.py <stl_file>")
        print("\nExample:")
        print("  python3 run_optimized_app.py STLfiles/assets/ayalower.stl")
        sys.exit(1)

    stl_path = sys.argv[1]

    if not os.path.exists(stl_path):
        print(f"❌ STL file not found: {stl_path}")
        sys.exit(1)

    print(f"Processing: {stl_path}\n")

    # Create wire generator
    generator = WireGenerator(
        stl_path=stl_path,
        arch_type='auto',
        wire_size='0.018'
    )

    # Generate wire
    print("Generating wire...")
    results = generator.generate_wire()

    if not results:
        print("❌ Wire generation failed")
        sys.exit(1)

    # Print summary
    generator.print_summary()

    # Save outputs
    design_file = generator.save_design()
    gcode_file = generator.generate_gcode()

    print(f"\n✅ Files saved:")
    print(f"   • Design: {design_file}")
    print(f"   • G-code: {gcode_file}")

    # Launch interactive mode
    # Optimizations are automatically applied via apply_optimizations module
    print("\n" + "="*70)
    print("LAUNCHING OPTIMIZED INTERACTIVE MODE")
    print("="*70)
    print("\nControls:")
    print("  ↑↓ arrows   - Move wire up/down (smooth!)")
    print("  W/S keys    - Move wire forward/backward (smooth!)")
    print("  R key       - Reset position")
    print("  H key       - Help")
    print("  Q key       - Quit")
    print("\n✨ Wire movement is now optimized for smooth real-time interaction!")
    print()

    generator.launch_interactive_mode()


if __name__ == "__main__":
    main()
