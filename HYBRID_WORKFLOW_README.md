# Hybrid Orthodontic Wire Generator - Professional Edition

## Overview

This enhanced version of the Orthodontic Wire Generator introduces a **hybrid workflow system** that combines the best of automatic detection and manual design approaches. Instead of completely replacing the existing automatic system, this implementation provides clinicians with maximum flexibility through three distinct workflow modes.

## 🚀 Key Features

### Workflow Modes

1. **Automatic Mode** - Quick wire generation using AI-powered tooth detection
2. **Manual Mode** - Full FixR-style control point placement for precision design
3. **Hybrid Mode** - Start with automatic detection, then manually refine for optimal results

### Advanced Capabilities

- **Dual-Arch Support** - Load and work with both upper and lower jaw models simultaneously
- **Collision Detection** - Check for interference with opposing arch
- **Professional UI** - Modern PyQt5-based interface with intuitive controls
- **Multiple Export Formats** - G-code, ESP32 Arduino code, and STL output
- **Real-time Visualization** - 3D OpenGL-based viewer with interactive controls

## 📋 System Requirements

### Required Dependencies

```bash
# Core GUI and visualization
PyQt5>=5.15.0
PyOpenGL>=3.1.0

# Scientific computing
numpy>=1.19.0
scipy>=1.5.0

# 3D mesh processing
trimesh>=3.9.0

# Additional dependencies (from existing project)
matplotlib>=3.3.0
```

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/alisoleah/orthodontic_wire_generator_latest.git
   cd orthodontic_wire_generator_latest
   ```

2. **Switch to the hybrid workflow branch**:
   ```bash
   git checkout feature/hybrid_workflow_implementation
   ```

3. **Install dependencies**:
   ```bash
   # Option 1: Automatic installation
   python run_hybrid_app.py --install-deps
   
   # Option 2: Manual installation
   pip install PyQt5 PyOpenGL numpy scipy trimesh matplotlib
   ```

4. **Run the application**:
   ```bash
   python run_hybrid_app.py
   ```

## 🎯 Usage Guide

### Quick Start

#### Automatic Mode (Fastest)
1. Load upper or lower arch STL file
2. Automatic detection runs immediately
3. Review detected teeth and generated wire
4. Adjust wire height if needed
5. Export your design

#### Manual Mode (Most Precise)
1. Load arch STL file
2. Switch to Manual mode
3. Define occlusal plane (click 3 tooth tips)
4. Place control points on tooth surfaces
5. Generate wire from control points
6. Export your design

#### Hybrid Mode (Best of Both)
1. Load arch STL file
2. Switch to Hybrid mode
3. Run automatic detection
4. Convert results to editable control points
5. Drag points to refine wire path
6. Export your design

### Advanced Features

#### Dual-Arch Workflow
1. Load both upper and lower arch STL files
2. Select active arch for design
3. Enable "Show Both Arches" for context
4. Load opposing arch for collision detection
5. Check for occlusal interference before export

#### Collision Detection
1. Load your primary arch and design wire
2. Load opposing arch using "Load Opposing Arch"
3. Click "Check for Collisions"
4. Review collision points (shown in red)
5. Adjust wire height or control points as needed

## 🏗️ Architecture

### Core Components

```
core/
├── workflow_manager.py      # Central workflow coordination
├── mesh_processor.py        # STL file processing
├── tooth_detector.py        # AI-powered tooth detection
└── bracket_positioner.py    # Bracket placement algorithms

gui/
├── enhanced_main_window.py     # Main application window
├── enhanced_control_panel.py   # Workflow control interface
└── status_panel.py            # Status and information display

visualization/
├── dual_arch_visualizer.py  # 3D OpenGL visualization
└── control_point_manager.py # Interactive point editing

wire/
├── wire_path_creator.py     # Wire path generation
└── wire_path_creator_enhanced.py  # Advanced path algorithms

export/
├── gcode_generator.py       # G-code export
├── esp32_generator.py       # ESP32 Arduino code export
└── stl_exporter.py         # STL file export
```

### Workflow Manager

The `WorkflowManager` class serves as the central coordinator:

```python
from core.workflow_manager import WorkflowManager, WorkflowMode

# Initialize workflow manager
manager = WorkflowManager()

# Load arches
manager.load_arch('upper_arch.stl', 'upper')
manager.load_arch('lower_arch.stl', 'lower')

# Switch modes
manager.set_mode(WorkflowMode.HYBRID)

# Run automatic detection
teeth, brackets, wire = manager.run_automatic_detection('upper')

# Convert to manual control points
control_points = manager.extract_control_points_from_auto('upper')

# Generate refined wire
refined_wire = manager.generate_wire_from_control_points('upper')
```

## 🎮 User Interface

### Control Panel Sections

1. **File Loading** - Load upper, lower, and opposing arch STL files
2. **Workflow Mode** - Select between Automatic, Manual, and Hybrid modes
3. **Active Arch** - Choose which arch to design and display options
4. **Design Workflow** - Dynamic steps that change based on selected mode
5. **Wire Parameters** - Height offset, diameter, and smoothness controls
6. **Collision Check** - Interference detection with opposing arch
7. **Export Options** - Multiple output format choices

### 3D Visualizer

- **Camera Controls**: Right-click drag to rotate, mouse wheel to zoom
- **Interactive Modes**: 
  - View mode for navigation
  - Point placement for manual design
  - Point dragging for refinement
- **Visual Elements**:
  - Dental arch meshes (upper/lower)
  - Detected teeth outlines
  - Bracket positions
  - Control points
  - Wire path
  - Collision points
  - Occlusal plane

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `F3` | Switch to Automatic Mode |
| `F4` | Switch to Manual Mode |
| `F5` | Switch to Hybrid Mode |
| `R` | Reset camera view |
| `F1` | Toggle control panel |
| `F2` | Toggle status panel |
| `Ctrl+N` | New project |
| `Ctrl+O` | Open project |
| `Ctrl+S` | Save project |
| `Ctrl+Q` | Exit application |

## 🔧 Configuration

### Wire Parameters

- **Height Offset**: -5.0mm to +5.0mm adjustment range
- **Wire Diameter**: 0.3mm to 2.0mm (default: 0.9mm)
- **Curve Smoothness**: 10-200 interpolation points (default: 100)

### Display Options

- **Show Both Arches**: Toggle simultaneous upper/lower display
- **Show Detected Teeth**: Toggle tooth outline visibility
- **Show Bracket Positions**: Toggle bracket marker visibility

## 📤 Export Formats

### G-Code Export
- Compatible with CNC wire bending machines
- Includes setup and safety commands
- Optimized tool paths

### ESP32 Arduino Code
- Ready-to-upload microcontroller code
- Servo motor control sequences
- Wire bending automation

### STL Export
- 3D printable wire models
- Visualization and verification
- Integration with CAD workflows

## 🔍 Troubleshooting

### Common Issues

#### "PyQt5 not available"
```bash
pip install PyQt5
```

#### "OpenGL not available"
```bash
pip install PyOpenGL PyOpenGL_accelerate
```

#### "Mesh loading failed"
- Ensure STL files are valid and not corrupted
- Check file permissions
- Try with different STL files

#### "Automatic detection failed"
- Verify STL file contains dental arch geometry
- Check mesh quality and resolution
- Ensure proper arch orientation

### Performance Optimization

- **Large STL Files**: Consider mesh decimation for faster processing
- **Slow Visualization**: Reduce curve smoothness setting
- **Memory Issues**: Process one arch at a time for very large models

## 🧪 Testing

### Test Files
Use the provided test STL files in `STLfiles/assets/`:
- `AyaKhairy_UpperJaw.stl`
- `AyaKhairy_LowerJaw.stl`
- `HanaElfouly_UpperJaw.stl`
- `HanaElfouly_LowerJaw.stl`

### Validation Workflow
1. Load test upper arch
2. Run automatic detection
3. Verify teeth detection accuracy
4. Switch to hybrid mode
5. Convert to manual points
6. Adjust control points
7. Generate refined wire
8. Export and validate output

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch from `feature/hybrid_workflow_implementation`
3. Make changes following existing code style
4. Test with multiple STL files
5. Submit pull request

### Code Style
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Document all public methods
- Include error handling

## 📄 License

This project maintains the same license as the original Orthodontic Wire Generator project.

## 🆘 Support

For issues, questions, or feature requests:

1. Check existing issues in the GitHub repository
2. Create new issue with detailed description
3. Include STL files and error messages if applicable
4. Specify your operating system and Python version

## 🔮 Future Enhancements

### Planned Features
- **Project Save/Load** - Persistent workflow state
- **Batch Processing** - Multiple arch processing
- **Advanced Collision Resolution** - Automatic wire adjustment
- **Machine Learning Integration** - Improved tooth detection
- **Cloud Processing** - Remote computation for complex cases
- **Mobile App Integration** - Companion mobile application

### Research Areas
- **AI-Powered Wire Optimization** - Machine learning for optimal wire paths
- **Biomechanical Simulation** - Force analysis and prediction
- **Patient-Specific Customization** - Individual treatment planning
- **Real-time Collaboration** - Multi-user design sessions

---

**Version**: 2.0  
**Last Updated**: 2024  
**Compatibility**: Python 3.7+, Windows/macOS/Linux
