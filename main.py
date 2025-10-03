#!/usr/bin/env python3
"""
main.py - Main Entry Point with GUI as Default
===============================================
This is the main entry point that defaults to GUI mode when no arguments are provided.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the main coordinator
from wire.wire_generator import WireGenerator

# Import GUI if available
try:
    from gui.main_window import WireGeneratorGUI
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("GUI components not available. Running in CLI mode.")


def main_gui_demo():
    """Launch the GUI version if available."""
    if not GUI_AVAILABLE:
        print("GUI not available. Please install required GUI dependencies.")
        print("Falling back to CLI demo...")
        return main_cli_demo()
    
    print("\n" + "="*80)
    print("MODULAR ORTHODONTIC WIRE GENERATOR - GUI MODE")
    print("Enhanced Interface with Modular Architecture")
    print("="*80)
    
    try:
        # Create and run GUI application
        app = WireGeneratorGUI()
        app.run()
    except Exception as e:
        print(f"GUI Error: {e}")
        print("Falling back to CLI demo...")
        return main_cli_demo()


def main_cli_demo():
    """
    Command-line demonstration of the modular wire generator.
    
    This shows how the refactored architecture works with clean separation
    of concerns and modular components.
    """
    print("\n" + "="*80)
    print("MODULAR ORTHODONTIC WIRE GENERATOR - COMMAND LINE DEMO")
    print("Refactored Architecture with Separated Drawing Components")
    print("="*80)
    
    # Check if STL file was provided as argument
    stl_path = None
    if len(sys.argv) > 1:
        provided_path = sys.argv[1]
        if provided_path.endswith('.stl') and os.path.exists(provided_path):
            stl_path = provided_path
        elif provided_path not in ['--gui', '--architecture', '--help', '-h']:
            print(f"STL file not found: {provided_path}")
    
    # Use default demo file if no valid STL provided
    if not stl_path:
        # Look for demo files in common locations
        demo_files = [
            "demo.stl",
            "sample.stl", 
            "test.stl",
            "example.stl",
            "lower_arch.stl",
            "upper_arch.stl"
        ]
        
        for demo_file in demo_files:
            if os.path.exists(demo_file):
                stl_path = demo_file
                break
        
        if not stl_path:
            print("No STL file found for CLI demo.")
            print("\nTo run CLI demo with your STL file:")
            print("  python main.py /path/to/your/model.stl")
            print("\nTo launch GUI (recommended):")
            print("  python main.py --gui")
            print("  or just: python main.py")
            return None
    
    print(f"\nProcessing: {stl_path}")
    
    # Create the main wire generator coordinator
    print("\n--- INITIALIZING MODULAR COMPONENTS ---")
    generator = WireGenerator(
        stl_path=stl_path,
        arch_type='auto',  # Will auto-detect from filename
        wire_size='0.018'  # Standard wire size
    )
    
    print("✓ Core components initialized:")
    print("  • MeshProcessor - STL loading and cleaning")
    print("  • ToothDetector - Tooth identification algorithms") 
    print("  • BracketPositioner - Clinical bracket placement")
    print("  • WirePathCreator - ⭐ CORE DRAWING ALGORITHM")
    print("  • WireMeshBuilder - ⭐ 3D WIRE RENDERING")
    print("  • HeightController - Wire height management")
    print("  • Visualization & Export components")
    
    # Generate the complete wire
    print("\n--- RUNNING WIRE GENERATION PIPELINE ---")
    results = generator.generate_wire()
    
    if not results:
        print("❌ Wire generation failed!")
        return None
    
    print("✅ Wire generation completed successfully!")
    
    # Demonstrate modular capabilities
    print("\n--- DEMONSTRATING MODULAR CAPABILITIES ---")
    
    # 1. Height Control (using HeightController)
    print("\n1. Height Control Demonstration:")
    print(f"   Initial height offset: {generator.get_wire_height_offset():.2f}mm")
    
    generator.adjust_wire_height(1.5)  # Move up 1.5mm
    print(f"   After adjustment: {generator.get_wire_height_offset():.2f}mm")
    
    generator.adjust_wire_height(-0.5)  # Move down 0.5mm
    print(f"   After fine-tuning: {generator.get_wire_height_offset():.2f}mm")
    
    # 2. Control Point Manipulation (using ControlPointManager)
    print("\n2. Control Point Manipulation:")
    control_points = generator.wire_path_creator.control_points
    print(f"   Total control points: {len(control_points)}")
    
    if control_points:
        generator.select_control_point(0)
        print("   Selected first control point for editing")
        
        # Move control point slightly
        import numpy as np
        generator.move_control_point(np.array([0.5, 0, 0]), step=0.3)
        print("   Moved control point 0.3mm in X direction")
    
    # 3. Wire Path Analysis (using WirePathCreator)
    print("\n3. Wire Path Analysis:")
    wire_length = generator.wire_path_creator.get_path_length()
    bends = generator.wire_path_creator.calculate_bends()
    print(f"   Wire length: {wire_length:.1f}mm")
    print(f"   Calculated bends: {len(bends)}")
    
    if bends:
        print("   Major bends detected:")
        for i, bend in enumerate(bends[:3]):  # Show first 3 bends
            print(f"     • Bend {i+1}: {bend['angle']:.1f}° {bend['direction']} at {bend['wire_length']:.1f}mm")
    
    # 4. Export Capabilities
    print("\n4. Export Demonstrations:")
    
    # Generate G-code with height information
    gcode_file = generator.generate_gcode("demo_wire.gcode")
    if gcode_file:
        print(f"   ✓ G-code generated: {gcode_file}")
        print("     • Includes height offset data")
        print("     • Arduino-compatible commands")
        print("     • Wire bending instructions")
    
    # Generate ESP32 code
    esp32_code = generator.generate_esp32_code()
    if esp32_code:
        print("   ✓ ESP32 Arduino code generated")
        print("     • 3-axis stepper control")
        print("     • Path following algorithms")
        
        # Save ESP32 code to file
        with open("demo_esp32_code.ino", "w") as f:
            f.write(esp32_code)
        print("     • Saved to: demo_esp32_code.ino")
    
    # Export STL with height offset
    stl_exported = generator.export_stl("demo_wire_mesh.stl")
    if stl_exported:
        print("   ✓ Wire mesh STL exported: demo_wire_mesh.stl")
        print(f"     • Includes {generator.get_wire_height_offset():.2f}mm height offset")
    
    # Save complete design
    design_file = generator.save_design("demo_complete_design.json")
    if design_file:
        print(f"   ✓ Complete design saved: {design_file}")
        print("     • All component data included")
        print("     • Height control settings preserved")
        print("     • Can be reloaded for further editing")
    
    # 5. Show Architecture Summary
    print("\n--- MODULAR ARCHITECTURE SUMMARY ---")
    print("\n🎯 WIRE DRAWING COMPONENTS:")
    print("   • WirePathCreator.create_smooth_path() - Core drawing algorithm")
    print("     └─ Spline interpolation, control points, path smoothing")
    print("   • WireMeshBuilder.build_wire_mesh() - 3D mesh creation")  
    print("     └─ Cylindrical segments, material properties, optimization")
    
    print("\n🏗️ SUPPORTING COMPONENTS:")
    print("   • MeshProcessor - STL loading and preprocessing")
    print("   • ToothDetector - Anatomical analysis and segmentation")
    print("   • BracketPositioner - Clinical positioning algorithms")
    print("   • HeightController - Height adjustment management")
    print("   • ControlPointManager - Interactive editing interface")
    
    print("\n📤 EXPORT COMPONENTS:")
    print("   • GCodeGenerator - Manufacturing instructions")
    print("   • ESP32Generator - Microcontroller code")
    print("   • STLExporter - 3D model export")
    
    print("\n🔄 DATA FLOW:")
    print("   STL Input → MeshProcessor → ToothDetector → BracketPositioner")
    print("   → WirePathCreator (DRAWING) → WireMeshBuilder (RENDERING)")
    print("   → HeightController → Visualization → Export")
    
    # 6. Interactive Mode Option
    print("\n--- INTERACTIVE MODE ---")
    if GUI_AVAILABLE:
        response = input("\nLaunch GUI for interactive editing? (y/n): ").lower().strip()
        
        if response == 'y':
            print("Launching GUI...")
            main_gui_demo()
            return generator
    else:
        print("GUI not available for interactive mode")
    
    # Final summary
    generator.print_summary()
    
    print("\n" + "="*80)
    print("MODULAR WIRE GENERATOR DEMO COMPLETE")
    print("="*80)
    print("\nKey Benefits of This Refactored Architecture:")
    print("✓ Separation of Concerns - Each class has a single responsibility")
    print("✓ Modularity - Components can be developed independently")
    print("✓ Maintainability - Easy to modify specific algorithms")
    print("✓ Testability - Each component can be unit tested")
    print("✓ Extensibility - New features can be added with minimal impact")
    print("✓ Wire Drawing Clarity - Algorithm and rendering are separate")
    
    return generator


def show_architecture_info():
    """Display detailed architecture information."""
    print("\n" + "="*80)
    print("MODULAR ARCHITECTURE DETAILED BREAKDOWN")
    print("="*80)
    
    print("""
📁 PROJECT STRUCTURE:
orthodontic_wire_generator/
├── main.py                          # Entry point (this file)
├── core/
│   ├── mesh_processor.py           # STL loading and preprocessing  
│   ├── tooth_detector.py           # Tooth detection algorithms
│   ├── bracket_positioner.py      # Bracket positioning logic
│   └── constants.py                # Wire sizes and clinical parameters
├── wire/
│   ├── wire_generator.py          # Main coordinator class
│   ├── wire_path_creator.py       # ⭐ CORE DRAWING ALGORITHM
│   ├── wire_mesh_builder.py       # ⭐ 3D WIRE RENDERING
│   └── height_controller.py       # Height adjustment management
├── visualization/
│   ├── visualizer_3d.py          # 3D visualization
│   └── control_point_manager.py  # Interactive editing
├── export/
│   ├── gcode_generator.py         # G-code generation
│   ├── esp32_generator.py         # ESP32 Arduino code
│   └── stl_exporter.py           # STL export
├── gui/
│   └── main_window.py             # GUI application
└── utils/
    ├── math_utils.py              # Mathematical utilities
    └── file_utils.py              # File operations

🎯 WHERE THE WIRE IS DRAWN:

1. ALGORITHM LEVEL (wire/wire_path_creator.py):
   • WirePathCreator.create_smooth_path() - Mathematical path generation
   • Uses spline interpolation, Bezier curves, control points
   • Handles height offsets, wire tension, path smoothing
   • Pure mathematical computation - no graphics

2. RENDERING LEVEL (wire/wire_mesh_builder.py):
   • WireMeshBuilder.build_wire_mesh() - 3D geometry creation
   • Converts math path to cylindrical mesh segments
   • Handles materials, colors, optimization
   • Creates actual 3D graphics objects

🔄 SEPARATION BENEFITS:
   • Drawing algorithm is pure math - easier to test and modify
   • Rendering is separate - can change visualization without affecting algorithm
   • Height control works at algorithm level - automatically affects rendering
   • Multiple export formats possible from same algorithm
""")


def show_help():
    """Show help information."""
    print("\nModular Orthodontic Wire Generator")
    print("Usage:")
    print("  python main.py                    # Launch GUI (default)")
    print("  python main.py --gui              # Launch GUI explicitly")
    print("  python main.py --cli              # Run CLI demo")
    print("  python main.py --architecture     # Show architecture info")
    print("  python main.py <stl_file>         # Process specific STL file")
    print("  python main.py --help             # Show this help")
    print("\nRecommended: Just run 'python main.py' to launch the GUI")


def process_specific_stl(stl_path: str):
    """Process a specific STL file."""
    if not os.path.exists(stl_path):
        print(f"Error: STL file not found: {stl_path}")
        return False
    
    print(f"Processing STL file: {stl_path}")
    
    try:
        generator = WireGenerator(stl_path=stl_path)
        results = generator.generate_wire()
        
        if results:
            print("Wire generation completed successfully!")
            
            # Offer to launch GUI for interactive editing
            if GUI_AVAILABLE:
                response = input("Launch GUI for interactive editing? (y/n): ").lower().strip()
                if response == 'y':
                    # This would ideally load the generated results into the GUI
                    main_gui_demo()
            
            return True
        else:
            print("Wire generation failed")
            return False
            
    except Exception as e:
        print(f"Error processing STL: {e}")
        return False


def main():
    """Main entry point with command line argument handling."""
    
    # No arguments - default to GUI
    if len(sys.argv) == 1:
        print("No arguments provided - launching GUI...")
        main_gui_demo()
        return
    
    # Handle command line arguments
    command = sys.argv[1].lower()
    
    if command in ["--help", "-h"]:
        show_help()
        
    elif command == "--gui":
        main_gui_demo()
        
    elif command == "--cli":
        main_cli_demo()
        
    elif command == "--architecture":
        show_architecture_info()
        
    elif command.endswith(".stl"):
        # Process specific STL file
        process_specific_stl(sys.argv[1])
        
    else:
        print(f"Unknown command: {command}")
        show_help()


# Example of how to use individual components programmatically
def example_component_usage():
    """
    Example showing how to use individual components directly.
    
    This demonstrates the modularity - you can use components independently
    without running the full pipeline.
    """
    
    # Example 1: Use just the drawing algorithm
    from wire.wire_path_creator import WirePathCreator
    import numpy as np
    
    path_creator = WirePathCreator(bend_radius=2.0, wire_tension=1.0)
    
    # Create some sample bracket positions
    sample_brackets = [
        {'position': np.array([10, 0, 5]), 'visible': True},
        {'position': np.array([5, 8, 5]), 'visible': True},
        {'position': np.array([-5, 8, 5]), 'visible': True},
        {'position': np.array([-10, 0, 5]), 'visible': True}
    ]
    
    arch_center = np.array([0, 0, 0])
    
    # Generate wire path using just the path creator
    wire_path = path_creator.create_smooth_path(sample_brackets, arch_center, height_offset=1.0)
    
    if wire_path is not None:
        print(f"Generated wire path with {len(wire_path)} points")
        print(f"Wire length: {path_creator.get_path_length():.2f}mm")
    
    # Example 2: Use just the mesh builder
    from wire.wire_mesh_builder import WireMeshBuilder
    
    mesh_builder = WireMeshBuilder(wire_radius=0.25)
    wire_mesh = mesh_builder.build_wire_mesh(wire_path)
    
    if wire_mesh:
        stats = mesh_builder.get_mesh_statistics()
        print(f"Wire mesh: {stats['vertex_count']} vertices, {stats['triangle_count']} triangles")
    
    # Example 3: Use height controller independently
    from wire.height_controller import HeightController
    
    height_ctrl = HeightController()
    height_ctrl.adjust_height(2.0)
    print(f"Height offset: {height_ctrl.get_height_offset()}mm")
    
    return wire_path, wire_mesh


if __name__ == "__main__":
    """Main entry point - defaults to GUI mode."""
    main()


# For development and testing
if __name__ == "__main__" and "--test-components" in sys.argv:
    print("\nTesting individual components...")
    example_component_usage()