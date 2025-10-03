# Modular Orthodontic Wire Generator

A professional-grade system for generating custom orthodontic wires with separated drawing algorithms and 3D rendering capabilities.

## Features

- **Modular Architecture**: Clean separation between drawing algorithm and 3D rendering
- **Interactive 3D Editor**: Real-time wire editing with height control
- **Multiple Export Formats**: G-code, ESP32 Arduino code, STL files
- **Professional Visualization**: Advanced 3D display with control point manipulation
- **Height Control System**: Precise vertical wire positioning
- **Extensible Design**: Easy to add new features and algorithms
- **User-Friendly GUI**: Comprehensive interface with modular panels

## Architecture Overview

```
orthodontic_wire_generator/
├── main.py                          # Entry point - defaults to GUI
├── core/                           # Fundamental processing
│   ├── mesh_processor.py          # STL loading and preprocessing
│   ├── tooth_detector.py          # Anatomical analysis and segmentation
│   ├── bracket_positioner.py      # Clinical bracket placement
│   └── constants.py               # Wire specifications
├── wire/                           # Wire generation (core algorithms)
│   ├── wire_generator.py          # Main coordinator class
│   ├── wire_path_creator.py       # 🎯 CORE DRAWING ALGORITHM
│   ├── wire_mesh_builder.py       # 🎯 3D WIRE RENDERING
│   └── height_controller.py       # Height adjustment management
├── visualization/                  # 3D display and interaction
│   ├── visualizer_3d.py          # Interactive 3D visualization
│   ├── control_point_manager.py  # Control point manipulation
│   └── mesh_factory.py           # 3D object creation utilities
├── export/                         # Output generation
│   ├── gcode_generator.py         # CNC manufacturing code
│   ├── esp32_generator.py         # Arduino microcontroller code
│   └── stl_exporter.py           # 3D model export
├── gui/                           # User interface
│   ├── main_window.py             # Main GUI application
│   ├── control_panel.py           # Parameter controls
│   ├── status_panel.py            # Status monitoring
│   └── gcode_panel.py             # Output generation
└── utils/                         # Utilities and helpers
    ├── math_utils.py              # Mathematical operations
    ├── file_utils.py              # File I/O operations
    └── design_serializer.py       # Save/load functionality
```

## Quick Start

### GUI Mode (Recommended)
```bash
# Launch GUI interface (default)
python main.py

# Browse and select STL files through the interface
# Adjust parameters using the control panels
# Launch 3D editor for interactive editing
```

### Command Line Usage
```bash
# Show all options
python main.py --help

# Launch GUI explicitly
python main.py --gui

# Process specific STL file
python main.py path/to/your/model.stl

# Run CLI demonstration
python main.py --cli

# Show architecture information
python main.py --architecture
```

### Programmatic Usage
```python
from wire.wire_generator import WireGenerator

# Create generator
generator = WireGenerator(
    stl_path="dental_model.stl",
    arch_type="lower", 
    wire_size="0.018"
)

# Generate wire using modular pipeline
results = generator.generate_wire()

# Adjust height using modular controller
generator.adjust_wire_height(1.5)  # Move up 1.5mm

# Export using modular exporters
generator.generate_gcode("output.gcode")
generator.export_stl("wire.stl")

# Launch interactive 3D editor
generator.launch_interactive_mode()
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Dependencies
```bash
pip install numpy>=1.20.0
pip install open3d>=0.15.0
pip install scipy>=1.7.0
# tkinter is usually included with Python
```

### Setup
1. Clone or download the project
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

## Core Components

### Wire Drawing (Separated Algorithm & Rendering)

**🎯 WirePathCreator** - The Mathematical Drawing Algorithm
- **Location**: `wire/wire_path_creator.py`
- **Purpose**: Pure mathematical path generation using spline interpolation
- **Key Methods**:
  - `create_smooth_path()` - Main drawing algorithm
  - `_cubic_spline_interpolation()` - Smooth curve generation
  - `_apply_wire_tension()` - Physical behavior simulation
  - `calculate_bends()` - Manufacturing analysis

**🎯 WireMeshBuilder** - The 3D Renderer
- **Location**: `wire/wire_mesh_builder.py`
- **Purpose**: Converts mathematical path into 3D geometry
- **Key Methods**:
  - `build_wire_mesh()` - Main 3D mesh creation
  - `_create_wire_segments()` - Cylindrical segment generation
  - `_orient_cylinder()` - 3D rotation mathematics
  - `_apply_wire_material()` - Visual properties

### Processing Pipeline

1. **MeshProcessor**: STL loading and preprocessing
2. **ToothDetector**: Anatomical analysis and segmentation  
3. **BracketPositioner**: Clinical bracket placement
4. **WirePathCreator**: Mathematical wire path generation ⭐
5. **WireMeshBuilder**: 3D wire mesh creation ⭐
6. **HeightController**: Height adjustment management
7. **Export Systems**: G-code, ESP32, STL output

## GUI Interface

### Control Panel (Left)
- **STL Loading**: Browse and load dental models
- **Wire Parameters**: Size, arch type, bend radius, tension
- **Height Control**: Up/down adjustment with history
- **Advanced Settings**: Smoothing, resolution, mesh quality

### Status Panel (Center)
- **Real-time Status**: Teeth count, wire length, height offset
- **Progress Tracking**: Generation progress with detailed logging
- **Architecture Info**: Component status and system overview
- **Component Tree**: Status of all modular components

### Output Panel (Right)
- **Code Generation**: G-code and ESP32 Arduino code
- **Export Settings**: Configurable parameters for each format
- **Batch Export**: Export all formats to directory
- **Preview**: Statistics and summaries

## Interactive 3D Editor

Launch with the "3D Interactive Editor" button or:
```python
generator.launch_interactive_mode()
```

### Controls
- **Wire Height**: Up/Down arrows for global height adjustment
- **Control Points**: 1-9 keys to select, arrow keys to move
- **Navigation**: Mouse drag (rotate), scroll (zoom), right-click (pan)
- **Bending**: B + arrow keys for bend angle adjustment
- **Export**: Generate G-code and save designs in real-time

## Export Formats

### G-code for CNC Machines
```python
# Generate with height offset information
gcode_file = generator.generate_gcode("wire.gcode")
```
- Arduino-compatible commands
- Wire feeding control (M6)
- Precision bending (M5) with height-adjusted coordinates
- Safety positioning with configurable parameters

### ESP32 Arduino Code
```python
# Generate stepper motor control code
esp32_code = generator.generate_esp32_code()
```
- AccelStepper library integration
- 3-axis coordinated movement
- Configurable steps/mm and feed rates
- Serial communication and monitoring

### STL 3D Models
```python
# Export wire mesh with current height offset
generator.export_stl("wire_mesh.stl")
```
- High-quality 3D mesh export
- Includes height adjustments
- Compatible with 3D printing and CAD software

### Design Files
```python
# Save complete design with all parameters
generator.save_design("complete_design.json")
```
- Complete system state preservation
- Reloadable for further editing
- Version compatibility tracking

## Benefits of Modular Architecture

### Separation of Concerns
- **Drawing Algorithm**: Pure mathematical computation in `WirePathCreator`
- **3D Rendering**: Visual geometry creation in `WireMeshBuilder`
- **Height Control**: Centralized management in `HeightController`

### Modularity
- Components can be developed independently
- Easy to swap implementations (e.g., different interpolation methods)
- Minimal dependencies between modules

### Testability
```python
# Test drawing algorithm with known inputs
def test_wire_path_creator():
    creator = WirePathCreator()
    brackets = [...]  # Known test data
    path = creator.create_smooth_path(brackets, center)
    assert len(path) > 0
    
# Test 3D rendering separately  
def test_mesh_builder():
    builder = WireMeshBuilder()
    sample_path = np.array([[0,0,0], [1,1,1], [2,0,2]])
    mesh = builder.build_wire_mesh(sample_path)
    assert mesh is not None
```

### Maintainability
- **Better spline interpolation?** Only modify `WirePathCreator`
- **Improved 3D rendering?** Only touch `WireMeshBuilder`
- **New export formats?** Add classes to `export/`
- Changes are localized and don't ripple through the system

### Extensibility
- **New interpolation methods**: Extend `WirePathCreator`
- **Different wire materials**: Extend `WireMeshBuilder`
- **Additional machine types**: Add export classes
- **Custom visualization**: Extend `Visualizer3D`

## Wire Drawing Algorithm Details

The wire drawing is cleanly separated into two phases:

### Phase 1: Mathematical Computation (`WirePathCreator`)
```python
def create_smooth_path(self, bracket_positions, arch_center, height_offset):
    # 1. Sort brackets by angle around arch
    sorted_brackets = self._sort_brackets_by_angle(bracket_positions, arch_center)
    
    # 2. Generate control points (brackets + intermediates)
    self.control_points = self._generate_control_points(sorted_brackets, arch_center)
    
    # 3. Apply height offset
    self._apply_height_offset(height_offset)
    
    # 4. Mathematical interpolation
    self.wire_path = self._interpolate_spline_path()
    
    # 5. Apply physical effects
    self.wire_path = self._apply_wire_tension()
    
    # 6. Validate and clean
    return self._validate_and_clean_path()
```

### Phase 2: 3D Rendering (`WireMeshBuilder`)
```python
def build_wire_mesh(self, wire_path):
    # 1. Create cylindrical segments
    combined_mesh = self._create_wire_segments(wire_path)
    
    # 2. Apply materials
    self._apply_wire_material()
    
    # 3. Optimize for performance
    self._optimize_mesh()
    
    return combined_mesh
```

## Requirements

- **Python**: 3.8+
- **numpy**: >=1.20.0 (numerical computations)
- **open3d**: >=0.15.0 (3D visualization and mesh processing)
- **scipy**: >=1.7.0 (spline interpolation and mathematical functions)
- **tkinter**: Usually included with Python (GUI interface)

## Performance and Compatibility

### Optimizations
- Efficient spline interpolation algorithms
- Optimized 3D mesh generation with configurable resolution
- Smart memory management for large dental models
- Cached calculations for real-time height adjustments

### Tested Platforms
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 18.04+)

## Development and Contributing

### Code Organization
- Each module has a single, well-defined responsibility
- Clear interfaces between components
- Comprehensive documentation and examples
- Type hints for better code clarity

### Testing
```bash
# Test individual components
python main.py --test-components

# Test with specific STL file
python main.py test_model.stl
```

### Adding New Features
1. **New interpolation methods**: Extend `WirePathCreator`
2. **Additional export formats**: Create new classes in `export/`
3. **Enhanced visualizations**: Extend `Visualizer3D`
4. **New wire materials**: Extend `WireMeshBuilder`

## Troubleshooting

### Common Issues

**GUI won't launch**
```bash
# Check if tkinter is installed
python -c "import tkinter"

# If missing, install tkinter (Ubuntu/Debian)
sudo apt-get install python3-tk
```

**STL file won't load**
- Ensure file is valid STL format
- Check file permissions
- Try with a smaller test file first

**3D visualization issues**
- Update graphics drivers
- Check Open3D installation: `python -c "import open3d"`
- Try reducing mesh resolution in advanced settings

**Memory issues with large models**
- Reduce mesh quality in advanced settings
- Close other applications
- Consider using smaller STL files for testing

### Getting Help
- Check the console output for detailed error messages
- Use `python main.py --help` for command options
- Try the CLI demo mode for debugging: `python main.py --cli`

## License

MIT License - see LICENSE file for details.

## Acknowledgments

This modular architecture transforms a complex monolithic system into a maintainable, extensible, and testable professional application suitable for both research and production use in orthodontic wire manufacturing.

The separation between mathematical algorithms and 3D rendering provides a clear foundation for future development and customization.