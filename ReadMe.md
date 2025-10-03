# Orthodontic Wire Generator - Refactored Architecture

## Project Structure
```
orthodontic_wire_generator/
├── __init__.py
├── main.py                          # Entry point
├── core/
│   ├── __init__.py
│   ├── mesh_processor.py           # STL loading and preprocessing
│   ├── tooth_detector.py           # Tooth detection algorithms
│   ├── bracket_positioner.py      # Bracket positioning logic
│   └── constants.py                # Wire sizes and constants
├── wire/
│   ├── __init__.py
│   ├── wire_generator.py          # Main wire generation logic
│   ├── wire_path_creator.py       # Wire path algorithms ⭐ DRAWING ALGORITHM
│   ├── wire_mesh_builder.py       # 3D wire mesh creation ⭐ WIRE DRAWING
│   └── height_controller.py       # Height adjustment logic
├── visualization/
│   ├── __init__.py
│   ├── visualizer_3d.py          # 3D visualization and interaction
│   ├── control_point_manager.py  # Control point manipulation
│   └── mesh_factory.py           # Mesh creation utilities
├── export/
│   ├── __init__.py
│   ├── gcode_generator.py         # G-code generation
│   ├── esp32_generator.py         # ESP32 Arduino code generation
│   └── stl_exporter.py           # STL export functionality
├── gui/
│   ├── __init__.py
│   ├── main_window.py             # Main GUI application
│   ├── control_panel.py           # Left control panel
│   ├── status_panel.py            # Center status panel
│   └── gcode_panel.py             # Right G-code panel
└── utils/
    ├── __init__.py
    ├── math_utils.py              # Mathematical utilities
    ├── file_utils.py              # File I/O operations
    └── design_serializer.py       # Save/load designs
```

## Key Classes and Responsibilities

### 🎯 **Wire Drawing Components** (Most Important)

#### 1. `WirePathCreator` - **The Drawing Algorithm**
- **Location**: `wire/wire_path_creator.py`
- **Purpose**: Contains the core algorithm for creating the wire path
- **Key Methods**:
  - `create_smooth_path()` - Main path generation algorithm
  - `interpolate_spline()` - Spline interpolation for smooth curves
  - `calculate_control_points()` - Generate intermediate control points
  - `apply_height_offset()` - Apply vertical adjustments

#### 2. `WireMeshBuilder` - **The Wire Renderer**
- **Location**: `wire/wire_mesh_builder.py`
- **Purpose**: Converts wire path into 3D mesh geometry
- **Key Methods**:
  - `build_wire_mesh()` - Create 3D cylindrical wire mesh
  - `create_wire_segments()` - Generate individual wire segments
  - `apply_wire_material()` - Set wire appearance and color

### 🏗️ **Core Architecture Classes**

#### 3. `WireGenerator` - **Main Coordinator**
- **Location**: `wire/wire_generator.py`
- **Purpose**: Orchestrates the entire wire generation process
- **Dependencies**: Uses WirePathCreator and WireMeshBuilder

#### 4. `MeshProcessor` - **STL Handler**
- **Location**: `core/mesh_processor.py`
- **Purpose**: Load and preprocess dental STL files

#### 5. `ToothDetector` - **Anatomy Analysis**
- **Location**: `core/tooth_detector.py`
- **Purpose**: Detect and classify teeth from dental models

#### 6. `BracketPositioner` - **Clinical Positioning**
- **Location**: `core/bracket_positioner.py`
- **Purpose**: Calculate optimal bracket positions

#### 7. `HeightController` - **Height Management**
- **Location**: `wire/height_controller.py`
- **Purpose**: Handle wire height adjustments and offsets

### 🖼️ **Visualization Classes**

#### 8. `Visualizer3D` - **3D Scene Manager**
- **Location**: `visualization/visualizer_3d.py`
- **Purpose**: Manage 3D visualization and user interaction

#### 9. `ControlPointManager` - **Interactive Editing**
- **Location**: `visualization/control_point_manager.py`
- **Purpose**: Handle control point selection and manipulation

### 🖥️ **GUI Classes**

#### 10. `MainWindow` - **GUI Coordinator**
- **Location**: `gui/main_window.py`
- **Purpose**: Main GUI application controller

#### 11. `ControlPanel` - **Parameter Controls**
- **Location**: `gui/control_panel.py`
- **Purpose**: Wire parameters and height controls

### 📤 **Export Classes**

#### 12. `GCodeGenerator` - **Manufacturing Output**
- **Location**: `export/gcode_generator.py`
- **Purpose**: Generate G-code for wire bending machines

## Data Flow Architecture

```
STL File Input
    ↓
MeshProcessor (load, clean mesh)
    ↓
ToothDetector (find teeth, classify)
    ↓
BracketPositioner (calculate bracket positions)
    ↓
WirePathCreator ⭐ (generate wire path - DRAWING ALGORITHM)
    ↓
HeightController (apply height adjustments)
    ↓
WireMeshBuilder ⭐ (create 3D wire mesh - WIRE DRAWING)
    ↓
Visualizer3D (display and interact)
    ↓
Export Classes (G-code, STL, etc.)
```

## Class Interaction Diagram

```
WireGenerator
├── uses → MeshProcessor
├── uses → ToothDetector
├── uses → BracketPositioner
├── uses → WirePathCreator ⭐ (DRAWING ALGORITHM)
├── uses → WireMeshBuilder ⭐ (WIRE RENDERER)
├── uses → HeightController
└── provides data to → Visualizer3D

MainWindow (GUI)
├── creates → WireGenerator
├── displays → Visualizer3D
└── uses → Export Classes
```

## Key Algorithms Located In:

### 🔴 **Wire Drawing Algorithm**: `WirePathCreator.create_smooth_path()`
- Spline interpolation between control points
- Bezier curve generation
- Path smoothing and optimization
- Height offset application

### 🔵 **Wire Mesh Creation**: `WireMeshBuilder.build_wire_mesh()`
- Cylindrical mesh generation along path
- Segment connection and joining
- Material application and texturing
- Mesh optimization

### 🟢 **Height Control Algorithm**: `HeightController.adjust_height()`
- Global height offset calculation
- Individual control point adjustment
- Real-time mesh updates

## Benefits of This Architecture

1. **Separation of Concerns**: Each class has a single, well-defined responsibility
2. **Modularity**: Components can be developed and tested independently
3. **Maintainability**: Easy to modify specific algorithms without affecting others
4. **Extensibility**: New features can be added with minimal impact
5. **Testability**: Each class can be unit tested in isolation
6. **Reusability**: Core algorithms can be reused in different contexts

## Wire Drawing Specifically

The **wire drawing** happens in two main stages:

1. **Algorithm Stage** (`WirePathCreator`): 
   - Calculates the mathematical path the wire should follow
   - Uses spline interpolation and control points
   - Applies height adjustments and clinical constraints

2. **Rendering Stage** (`WireMeshBuilder`):
   - Takes the mathematical path and creates actual 3D geometry
   - Generates cylindrical mesh segments
   - Handles wire radius, material properties, and visual appearance

This separation allows the drawing algorithm to be purely mathematical while the mesh builder handles the 3D graphics aspects.