# Orthodontic Wire Generator - Project Documentation

**Version:** 2.1.0 (Professional Hybrid Edition)
**Last Updated:** 2025-01-16
**Current Branch:** `feature/smoothwire`

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Target Users & Use Cases](#target-users--use-cases)
3. [Technology Stack](#technology-stack)
4. [Architecture & Components](#architecture--components)
5. [Workflows](#workflows)
6. [Key Algorithms](#key-algorithms)
7. [Export Capabilities](#export-capabilities)
8. [Installation & Setup](#installation--setup)
9. [File Structure](#file-structure)
10. [Clinical Validation Status](#clinical-validation-status)
11. [Future Enhancements](#future-enhancements)
12. [Machine Integration Recommendations](#machine-integration-recommendations)

---

## 1. Project Overview

The **Orthodontic Wire Generator** is a sophisticated Python application designed to automatically generate custom orthodontic wires for dental treatment. The system processes 3D dental arch models (STL files), detects individual teeth, positions brackets, and creates smooth wire paths that follow the natural curvature of the dental arch.

### Key Features
- ✅ **Automatic tooth detection** from 3D STL scans (14-16 teeth)
- ✅ **Three workflow modes**: Automatic, Manual, and Hybrid
- ✅ **Ultra-smooth wire paths** using Catmull-Rom splines + multi-stage Gaussian smoothing
- ✅ **Dual-arch support** with collision detection between upper and lower jaws
- ✅ **Interactive 3D visualization** with PyVista
- ✅ **Real-time wire editing** with draggable control points
- ✅ **Multiple export formats**: G-code (CNC), ESP32/Arduino code, STL meshes

### What Problem Does It Solve?
Traditional orthodontic wire design is manual, time-consuming, and requires expert knowledge. This tool:
1. **Automates** the detection and measurement process
2. **Generates** clinically accurate wire paths in seconds
3. **Exports** manufacturing-ready instructions for wire-bending machines
4. **Enables** orthodontists to customize designs with intuitive visual tools

---

## 2. Target Users & Use Cases

### Primary Target Users
**Orthodontists Designing Treatment Plans**
- Design custom archwires for patients with unique dental anatomy
- Visualize wire paths in 3D before manufacturing
- Iterate on designs with real-time feedback
- Export designs for manufacturing or 3D printing

### Use Cases

#### Use Case 1: Standard Archwire Design
**Scenario:** Orthodontist has a patient STL scan and needs a standard archwire.

**Workflow:**
1. Load upper arch STL file
2. Run automatic detection (detects 14 teeth, positions brackets)
3. Adjust height/AP offset using sliders or keyboard (I/K/J/L keys)
4. Export G-code for CNC wire bender
5. **Time:** ~2 minutes

#### Use Case 2: Complex Anatomy (Crowded Teeth)
**Scenario:** Patient has crowded teeth where automatic detection may fail.

**Workflow:**
1. Load STL file
2. Switch to Manual Mode
3. Click 3+ control points on tooth surfaces
4. System generates smooth wire through selected points
5. Fine-tune with offset controls
6. Export to manufacturing
7. **Time:** ~5 minutes

#### Use Case 3: Refinement of Automatic Design
**Scenario:** Automatic design is 90% correct but needs bracket adjustment.

**Workflow:**
1. Run automatic detection
2. Switch to Hybrid Mode ("Convert to Manual Points")
3. Drag any of the 14 bracket sphere widgets to adjust position
4. Wire regenerates in real-time
5. Export when satisfied
6. **Time:** ~3 minutes

#### Use Case 4: Dual-Arch Collision Check
**Scenario:** Check if upper and lower wires will collide during jaw movement.

**Workflow:**
1. Load both upper and lower arch STL files
2. Generate wires for both arches
3. Use "Rotate Lower Jaw" slider to simulate jaw closing
4. Visual collision detection highlights interference zones
5. Adjust offsets to eliminate collisions
6. **Time:** ~4 minutes

---

## 3. Technology Stack

### Core Python Libraries
- **Python 3.7+** - Programming language
- **NumPy 1.24+** - Numerical computing and array operations
- **SciPy 1.10+** - Scientific algorithms (interpolation, Gaussian filtering)
- **Open3D 0.17+** - 3D mesh processing and geometry operations

### GUI & Visualization
- **PyQt5 5.15+** - Cross-platform GUI framework
- **PyVista 0.43+** - Interactive 3D visualization (VTK-based)
- **PyVistaQt** - PyVista integration with Qt

### Mesh Processing
- **trimesh 3.21+** - Mesh manipulation and analysis
- **numpy-stl 3.0+** - STL file I/O

### Optional Dependencies
- **scikit-learn** - Machine learning utilities (future enhancement)
- **pytest** - Unit testing framework
- **black** - Code formatting
- **pylint** - Code quality analysis

### Export Targets
- **G-code** - CNC wire-bending machines (generic Marlin/Grbl compatible)
- **Arduino/ESP32** - Stepper motor control code (AccelStepper library)
- **STL** - 3D mesh export for visualization or 3D printing

---

## 4. Architecture & Components

### 4.1 System Architecture

```
┌─────────────────────────────────────────────┐
│      PyQt5 GUI (Main Window)                │
│  ┌─────────────────────────────────────┐   │
│  │ Enhanced Control Panel │ 3D View    │   │
│  │  (buttons/sliders)     │ PyVista    │   │
│  │                        │ Visualizer │   │
│  └─────────────────────────────────────┘   │
└──────────────┬──────────────────────────────┘
               │ Qt Signals/Slots
┌──────────────▼──────────────────────────────┐
│    WorkflowManager (Core Orchestrator)      │
├──────────────────────────────────────────────┤
│ ┌─────────────┐ ┌──────────────────┐        │
│ │ Tooth       │ │ Bracket          │        │
│ │ Detector    │ │ Positioner       │        │
│ └─────────────┘ └──────────────────┘        │
│ ┌─────────────────────────────────┐         │
│ │ Wire Path Creator               │         │
│ │ (Catmull-Rom + Gaussian)        │         │
│ └─────────────────────────────────┘         │
└──────────────┬──────────────────────────────┘
               │
        ┌──────┴──────────┬──────────┐
        │                 │          │
    ┌───▼──┐         ┌────▼──┐  ┌──▼──┐
    │G-Code│         │ESP32  │  │STL  │
    │Export│         │Export │  │Exp. │
    └──────┘         └───────┘  └─────┘
```

### 4.2 Core Modules

#### **WorkflowManager** ([core/workflow_manager.py](core/workflow_manager.py))
**Role:** Central orchestrator managing all processing stages.

**Key Responsibilities:**
- Coordinates tooth detection, bracket positioning, wire generation
- Manages dual-arch data (upper/lower)
- Handles workflow state transitions (AUTO → MANUAL → HYBRID)
- Applies global offsets (height, anterior-posterior)
- Triggers collision detection

**Data Structure:**
```python
arch_data = {
    'upper': {
        'mesh': Open3D TriangleMesh object,
        'teeth_detected': List of tooth dictionaries,
        'bracket_positions': List of bracket position dicts,
        'control_points': List of 3D numpy arrays,
        'wire_path': Nx3 numpy array of wire coordinates,
        'arch_center': 3D center point of dental arch
    },
    'lower': { ... }  # Same structure
}
```

#### **Tooth Detector** ([core/tooth_detector.py](core/tooth_detector.py))
**Algorithm:** Angular Segmentation

**Process:**
1. Identify anatomical axes (LR, AP, Height)
2. Extract crown-level vertices
3. Convert to polar coordinates around arch center
4. Divide into 14-16 angular sectors (one per tooth)
5. Classify tooth types (incisors, canines, premolars, molars)

**Output:** List of tooth dictionaries with center, vertices, angle, type

**Detection Parameters:**
- Crown ratio: 0.25 (upper), 0.75 (lower)
- Height tolerance: ±2mm
- Expected teeth: 14

**Known Limitations:**
- Crowded teeth may merge into single detection
- Large gaps may create false teeth
- Unusual anatomy (rotated teeth) may fail
- **Accuracy:** Not yet tested on diverse clinical cases

#### **Bracket Positioner** ([core/bracket_positioner.py](core/bracket_positioner.py))
**Algorithm:** Lingual Surface Detection

**Process:**
1. Determine bracket height based on tooth type
2. Filter vertices at target height
3. Find lingual (inner) surface
4. Apply clinical offset toward arch center

**Output:** Bracket position with 3D coordinates, normal, tooth type

**Key Feature:** Only frontal teeth (6-8) are marked "visible" and included in wire

#### **Wire Path Creator** ([wire/wire_path_creator.py](wire/wire_path_creator.py))
**Algorithm:** Multi-Stage Smooth Path Generation

**Stages:**
1. **Control Point Generation** - Adds intermediate points between brackets
2. **Catmull-Rom Spline** - Interpolates smooth curve (300 pts/segment)
3. **Tension Simulation** - Physical wire behavior under tension
4. **Gaussian Smoothing** - 5 passes with σ=12.0 for ultra-smooth curves

**Parameters:**
- `path_resolution`: 300 points per segment (adjustable 10-1000)
- `wire_tension`: 1.0 (tension factor)
- `smoothing_sigma`: 12.0 (Gaussian kernel width)

**Recent Improvements (feature/smoothwire branch):**
- 3x higher resolution (100 → 300 pts/segment)
- Removed inward offset causing sharp corners
- Enhanced smoothing (σ: 6.0 → 12.0, passes: 3 → 5)

#### **PyVista Visualizer** ([visualization/pyvista_visualizer.py](visualization/pyvista_visualizer.py))
**Role:** Interactive 3D mesh and wire visualization

**Key Features:**
- Point picking (right-click to add control points)
- Sphere widget dragging (Hybrid mode)
- Dual-arch visualization with opacity blending
- Lower jaw rotation simulation
- Real-time wire updates

**Interaction Modes:**
- `VIEW` - Orbit, zoom, pan
- `DEFINE_PLANE` - Select 3 points for occlusal plane
- `PLACE_POINTS` - Manual control point placement
- `DRAG_POINTS` - Edit control points with sphere widgets

---

## 5. Workflows

### 5.1 Automatic Workflow
**Best For:** Standard anatomy, quick designs

**Steps:**
1. Click "Load Upper Arch (.stl)" or "Load Lower Arch (.stl)"
2. Select STL file from `STLfiles/assets/`
3. Click "Run Auto Detection"
4. System automatically:
   - Detects 14 teeth via angular segmentation
   - Positions 6-8 brackets on frontal teeth
   - Generates ultra-smooth wire path (~4200 points)
5. Adjust offsets if needed (Height: I/K keys, AP: J/L keys)
6. Click "Export G-code" or "Export ESP32 Code"

**Time:** ~2 minutes
**User Control:** Low (automated) → High (via offsets)

### 5.2 Manual Workflow
**Best For:** Complex anatomy, crowded teeth, unusual cases

**Steps:**
1. Load STL file
2. Click "Define Wire Path (0/3)"
3. Right-click on mesh 3 times to select control points
4. System automatically adds 9 intermediate points between each pair
5. Click "Generate Wire" - creates smooth wire through all points
6. Adjust offsets for fine-tuning
7. Export when satisfied

**Time:** ~5 minutes
**User Control:** Very High (manual point selection)

**Note:** Minimum 3 control points required. System supports unlimited control points.

### 5.3 Hybrid Workflow
**Best For:** Refinement of automatic designs

**Steps:**
1. Run automatic detection
2. Click "Convert to Manual Points"
   - Extracts all 14 bracket positions as draggable control points
3. Click "Enable Point Dragging"
   - Yellow sphere widgets appear at each bracket
4. Drag any sphere to adjust bracket position
   - Wire regenerates in real-time on each drag
5. Continue refining until satisfied
6. Export design

**Time:** ~3 minutes
**User Control:** Medium to High (refine automatic results)

**Technical Detail:** Each drag emits `point_moved` signal → updates both control points AND bracket positions → regenerates wire using `generate_wire_from_control_points()`

---

## 6. Key Algorithms

### 6.1 Angular Segmentation (Tooth Detection)
**Reference:** [ALGORITHM.md](ALGORITHM.md) Section 2

**Mathematical Foundation:**
```
1. Convert vertices to polar coordinates:
   θ = arctan2(y_AP, x_LR)
   r = sqrt(x² + y²)

2. Divide into N angular sectors:
   sector_i = floor(θ / (2π / N))

3. Group vertices by sector:
   tooth_i = {v | v.sector == i}
```

**Time Complexity:** O(V) where V = vertex count (~200,000)

### 6.2 Catmull-Rom Spline Interpolation
**Reference:** [ALGORITHM.md](ALGORITHM.md) Section 4, [utils/catmull_rom.py](utils/catmull_rom.py)

**Formula:**
```
P(t) = 0.5 × [
  (2*P₁) +
  (-P₀ + P₂) * t +
  (2*P₀ - 5*P₁ + 4*P₂ - P₃) * t² +
  (-P₀ + 3*P₁ - 3*P₂ + P₃) * t³
]
where t ∈ [0, 1]
```

**Properties:**
- Interpolating (passes through all control points)
- C¹ continuous (smooth first derivative)
- Local control (changing one point affects only nearby curve)

**Parameters:**
- Resolution: 300 points per segment (default)
- Adjustable via "Curve Smoothness" slider (10-1000)

### 6.3 Multi-Stage Wire Smoothing
**Reference:** [ALGORITHM.md](ALGORITHM.md) Section 5

**Stage 1: Tension Simulation**
```python
For each interior point p_i:
  chord = p_{i+1} - p_{i-1}
  midpoint = p_{i-1} + chord / 2
  deviation = p_i - midpoint
  p_i_smoothed = p_i - deviation * (1 - tension_factor)
```

**Stage 2: Gaussian Smoothing**
```python
from scipy.ndimage import gaussian_filter1d

for dim in [X, Y, Z]:
    smoothed[:, dim] = gaussian_filter1d(
        path[:, dim],
        sigma=12.0,
        mode='nearest'
    )
# Applied 5 times for ultra-smoothness
```

**Time Complexity:** O(T × R × σ) where T=teeth, R=resolution, σ=Gaussian passes

### 6.4 Collision Detection (Upper/Lower Jaw)
**Reference:** [core/collision_detector2.py](core/collision_detector2.py), [utils/collision_detector.py](utils/collision_detector.py)

**Purpose:** Detect interference between upper and lower arch wires during jaw movement

**Algorithm:**
1. Rotate lower jaw by angle θ (simulating jaw closing)
2. For each point on upper wire:
   - Find nearest point on lower wire
   - Calculate distance d
   - If d < threshold (e.g., 1.0mm): collision detected
3. Highlight collision zones in visualization

**Status:** Basic implementation exists. Not yet fully tested for clinical accuracy.

---

## 7. Export Capabilities

### 7.1 G-Code Export ([export/gcode_generator.py](export/gcode_generator.py))
**Target:** CNC wire-bending machines (generic Marlin/Grbl compatible)

**Output Format:**
```gcode
; Orthodontic Wire G-code
; Generated: 2025-01-16
G21 ; Units in millimeters
G90 ; Absolute positioning
G28 ; Home all axes

; Wire path
G1 X10.50 Y5.23 Z2.10 F1000
G1 X10.52 Y5.25 Z2.11 F1000
...
M2 ; Program end
```

**Features:**
- Configurable feed rates
- Safety height moves
- Time estimation
- Header/footer customization

**Usage:** Click "Export G-code" → Select filename → Load into CNC controller

### 7.2 ESP32/Arduino Code Export ([export/esp32_generator.py](export/esp32_generator.py))
**Target:** ESP32/Arduino-based stepper motor wire benders

**Output Format:**
```cpp
#include <AccelStepper.h>

// Stepper motor definitions
AccelStepper stepperX(1, 2, 5); // X-axis
AccelStepper stepperY(1, 3, 6); // Y-axis
AccelStepper stepperZ(1, 4, 7); // Z-axis

const int NUM_POINTS = 4200;
float wire_path[NUM_POINTS][3] = {
  {10.50, 5.23, 2.10},
  {10.52, 5.25, 2.11},
  ...
};

void setup() {
  // Stepper configuration
  stepperX.setMaxSpeed(1000);
  stepperY.setMaxSpeed(1000);
  stepperZ.setMaxSpeed(1000);
}

void loop() {
  // Coordinated XYZ movement
  for (int i = 0; i < NUM_POINTS; i++) {
    moveToPoint(wire_path[i]);
  }
}
```

**Features:**
- AccelStepper library integration
- Coordinated multi-axis movement
- Serial command interface
- Homing sequence

**Usage:** Click "Export ESP32 Code" → Upload to Arduino IDE → Flash to ESP32

### 7.3 STL Mesh Export ([export/stl_exporter.py](export/stl_exporter.py))
**Target:** 3D visualization, 3D printing

**Output:** Wire geometry as 3D mesh (cylindrical wire with specified diameter)

**Features:**
- Mesh cleaning and validation
- Metadata in filename
- Compatible with CAD software

**Usage:** Click "Export STL" → Import into Blender/Fusion 360/PrusaSlicer

---

## 8. Installation & Setup

### 8.1 Prerequisites
- **Python 3.7 or higher** (tested on 3.11 and 3.12)
- **Windows 10/11, macOS 10.15+, or Linux** (Ubuntu 20.04+)
- **4GB RAM minimum** (8GB recommended for large STL files)
- **OpenGL-capable GPU** (for PyVista 3D rendering)

### 8.2 Installation Steps

**1. Clone or Download Repository**
```bash
cd C:\Users\galala\Downloads\orthodontic_wire_generator_project\orthodontic_wire_generator
```

**2. Create Virtual Environment (Recommended)**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # macOS/Linux
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Verify Installation**
```bash
python -c "import open3d; import pyvista; import PyQt5; print('All dependencies installed!')"
```

### 8.3 Running the Application

**Main Application (Enhanced GUI):**
```bash
python run_app.py
```

**Hybrid Mode Application:**
```bash
python run_hybrid_app.py
```

**Test PyVista GUI:**
```bash
python test_pyvista_gui.py
```

### 8.4 Troubleshooting

**Issue:** PyVista window is black/not rendering
**Solution:** Update graphics drivers, ensure OpenGL 3.2+ support

**Issue:** "No module named 'vtkmodules'"
**Solution:** `pip install --upgrade vtk pyvista`

**Issue:** STL file won't load
**Solution:** Verify STL is binary format, not ASCII. Check file isn't corrupted.

---

## 9. File Structure

```
orthodontic_wire_generator/
├── core/                          # Core algorithms
│   ├── workflow_manager.py         # Central orchestrator (CRITICAL)
│   ├── mesh_processor.py           # STL loading and mesh cleaning
│   ├── tooth_detector.py           # Tooth detection (angular segmentation)
│   ├── bracket_positioner.py       # Bracket placement
│   ├── collision_detector2.py      # Wire-tooth collision detection
│   └── constants.py                # Clinical parameters
│
├── wire/                           # Wire generation algorithms
│   ├── wire_path_creator.py        # MAIN: Smooth path generation
│   ├── wire_mesh_builder.py        # Convert path to 3D mesh
│   ├── height_controller.py        # Z-axis adjustments
│   └── wire_generator.py           # Legacy (kept for reference)
│
├── gui/                            # User interface
│   ├── enhanced_main_window.py     # Main PyQt5 window
│   ├── enhanced_control_panel.py   # Control panel (buttons/sliders)
│   ├── enhanced_status_panel.py    # Status display
│   └── main_window.py              # Legacy tkinter version
│
├── visualization/                  # 3D visualization
│   ├── pyvista_visualizer.py       # MAIN: PyVista 3D viewer
│   ├── dual_arch_visualizer.py     # Dual-arch support
│   ├── control_point_manager.py    # Control point handling
│   └── mesh_factory.py             # Mesh creation utilities
│
├── export/                         # Export formats
│   ├── gcode_generator.py          # G-code for CNC machines
│   ├── esp32_generator.py          # Arduino/ESP32 code
│   └── stl_exporter.py             # STL mesh export
│
├── utils/                          # Utility functions
│   ├── catmull_rom.py              # Catmull-Rom splines
│   ├── math_utils.py               # Mathematical helpers
│   ├── collision_detector.py       # Collision detection
│   ├── file_utils.py               # File I/O utilities
│   └── design_serializer.py        # Project save/load (future)
│
├── tests/                          # Unit tests
│   ├── test_environment.py
│   ├── test_wire_path_creator_enhanced.py
│   └── test_manual_workflow.py
│
├── STLfiles/                       # Sample STL files
│   └── assets/                     # STL assets directory
│
├── run_app.py                      # MAIN ENTRY POINT
├── run_hybrid_app.py               # Hybrid workflow launcher
├── run_optimized_app.py            # Performance-optimized version
├── test_pyvista_gui.py             # GUI test script
├── test_manual_mode.py             # Manual mode test
├── requirements.txt                # Python dependencies
├── ALGORITHM.md                    # Detailed algorithm docs
└── PROJECT_DOCUMENTATION.md        # This file
```

---

## 10. Clinical Validation Status

### Current Status: **Pre-Clinical Development**

#### ✅ Completed
- [x] Core algorithms implemented (tooth detection, bracket positioning, wire generation)
- [x] Multi-stage smoothing for ultra-smooth wires
- [x] Export to manufacturing formats (G-code, ESP32)
- [x] Interactive GUI with real-time visualization
- [x] Dual-arch support with collision detection

#### 🔄 In Progress (feature/smoothwire branch)
- [ ] Wire smoothness optimization (recent improvements made)
- [ ] GUI refinements (lower jaw movement fixes)
- [ ] Testing on diverse dental anatomies

#### ⚠️ Not Yet Tested
- [ ] **Accuracy validation** with clinically approved wires
- [ ] **Success rate** of automatic tooth detection on varied anatomies
- [ ] **Failure cases** for crowded teeth, large gaps, rotated teeth
- [ ] **Clinical outcomes** (no patient testing yet)
- [ ] **Manufacturing accuracy** (G-code/ESP32 code not yet tested on physical machines)

### Validation Resources Available
- **STL files with existing wires:** You mentioned having STLs with wires for comparison
- **Recommendation:** Compare auto-generated wires against these reference wires
- **Metrics to validate:**
  1. Bracket position deviation (mm)
  2. Wire path deviation from reference (RMS error)
  3. Smoothness (curvature analysis)
  4. Manufacturing feasibility (min bend radius)

### Next Steps for Validation
1. **Create validation dataset:** Organize STLs with reference wires
2. **Implement comparison tool:** Measure deviation between generated and reference wires
3. **Define acceptance criteria:** Max deviation thresholds (e.g., ±0.5mm)
4. **Document failure cases:** Identify anatomies where detection fails
5. **Iterate on algorithms:** Improve based on validation results

---

## 11. Future Enhancements

### High Priority (Recommended Next Steps)

#### 1. Project Save/Load System
**Status:** Currently missing
**Benefit:** Users can save their work and resume later

**Implementation:**
- Use `utils/design_serializer.py` (already exists but not integrated)
- Save format: JSON with base64-encoded STL data
- Include: mesh, control points, brackets, wire path, parameters

#### 2. Wire Quality Metrics Dashboard
**Status:** Not implemented
**Benefit:** Give users confidence in design quality

**Metrics to Display:**
- Maximum curvature (detect kinks)
- Smoothness score (derivative analysis)
- Total wire length
- Deviation from ideal parabolic arch
- Manufacturing feasibility score

#### 3. Undo/Redo System
**Status:** Not implemented
**Benefit:** Essential for interactive editing (Hybrid mode)

**Implementation:**
- Command pattern for action history
- Store: control point positions, bracket positions, offsets
- Keyboard shortcuts: Ctrl+Z (undo), Ctrl+Y (redo)

#### 4. Automated Testing Suite
**Status:** Basic tests exist, need expansion
**Benefit:** Prevent regressions, ensure algorithm stability

**Test Coverage Needed:**
- Unit tests for each algorithm (tooth detection, bracket positioning, wire generation)
- Integration tests for full workflows
- Regression tests with sample STL files
- Performance benchmarks

### Medium Priority

#### 5. Clinical Presets
**Status:** Not implemented
**Benefit:** Support different orthodontic philosophies

**Presets to Add:**
- Roth prescription (bracket angles, torque values)
- MBT prescription
- Alexander prescription
- Custom preset editor

#### 6. Measurement Tools
**Status:** Not implemented
**Benefit:** Professional analysis features

**Tools:**
- Distance measurement between brackets
- Angle measurement
- Arc length calculation
- Curvature visualization (heatmap)

#### 7. Improved Error Handling
**Status:** Basic error handling
**Benefit:** Better user experience with malformed files

**Improvements:**
- Validate STL files before processing
- Graceful failure with informative error messages
- Auto-recovery from crashes (autosave)

### Low Priority (Future Vision)

#### 8. Machine Learning Enhancement
**Status:** Concept phase
**Benefit:** Improve detection accuracy

**Approach:**
- Train neural network on expert-designed wires
- Learn optimal bracket positions from clinical data
- Predict ideal wire shape for given anatomy

#### 9. Multi-Stage Wire Sequence
**Status:** Not implemented
**Benefit:** Full treatment planning

**Feature:**
- Generate sequence of wires (light → heavy gauge)
- Progressive alignment simulation
- Estimate treatment time

#### 10. Web-Based Version
**Status:** Not implemented
**Benefit:** No installation required

**Technology:**
- Frontend: React + Three.js for 3D visualization
- Backend: FastAPI or Flask
- Deploy: Cloud hosting (AWS, Azure, GCP)

---

## 12. Machine Integration Recommendations

### Current Export Formats
You're currently using:
- **G-code** (generic CNC format)
- **ESP32/Arduino code** (custom stepper motor control)

These are good starting points for prototyping.

### Recommendations for Production Integration

#### Option 1: CNC Wire Bender (Professional)
**Recommendation:** Standardize on G-code with machine-specific post-processing

**Advantages:**
- Industry standard format
- Most CNC machines support it
- Mature ecosystem (simulators, validators)

**Next Steps:**
1. Test generated G-code with simulation software (CAMotics, CNCSimulator)
2. Identify your target CNC machine model
3. Customize G-code generator for that machine:
   - Feed rates optimized for wire material (SS, NiTi)
   - Machine-specific commands (M-codes)
   - Safety features (limit checks, collision avoidance)

**Suggested Machines:**
- **BendTec-300** (if available in your region)
- **Wafios FMU** series
- Custom 3-axis CNC with wire bending head

#### Option 2: Custom ESP32 Wire Bender (DIY/Prototyping)
**Recommendation:** Expand ESP32 code with closed-loop control

**Current Implementation:** Open-loop stepper control
**Improvement Needed:** Add feedback (encoders, limit switches)

**Enhanced Features:**
1. **Homing sequence** with limit switches
2. **Position feedback** via rotary encoders
3. **Real-time monitoring** via WiFi (ESP32 → computer)
4. **Emergency stop** functionality
5. **Calibration routine** for accuracy

**Code Structure:**
```cpp
// Enhanced ESP32 code structure
class WireBender {
  public:
    void homeAllAxes();
    void moveToPoint(float x, float y, float z);
    void calibrate();
    bool checkLimits();
    void emergencyStop();
    void reportStatus();  // Send to computer via Serial/WiFi
};
```

#### Option 3: Hybrid Approach (Recommended for Orthodontic Clinics)
**Scenario:** Clinic has no CNC machine yet

**Solution:**
1. **Generate G-code** from software
2. **Send to external wire bending service** (many dental labs offer this)
3. **Alternative:** Partner with local makerspace/fab lab with CNC capabilities

**Benefit:**
- No hardware investment required
- Focus on software refinement
- Validate designs before investing in machinery

### Additional Export Formats to Consider

#### 1. STEP/IGES (CAD Exchange)
**Purpose:** Import wire design into professional CAD software (SolidWorks, Fusion 360)

**Use Case:**
- Further refinement in CAD
- Integration with other dental appliances
- Engineering analysis (FEA for stress/strain)

**Implementation:** Use Open CASCADE library or trimesh export

#### 2. DICOM/STL with Metadata
**Purpose:** Integration with dental CAD/CAM systems

**Use Case:**
- Send design to dental lab
- Archive in patient management system
- Share with other orthodontists

**Implementation:** Embed wire data in STL metadata or separate XML file

#### 3. 3D Printing (SLA/FDM)
**Purpose:** Create physical wire models for visualization

**Use Case:**
- Show patient their treatment plan
- Training/education
- Design verification before bending actual wire

**Current Support:** STL export already implemented ✅

---

## Appendix A: Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **I** | Increase height offset (+0.1mm) |
| **K** | Decrease height offset (-0.1mm) |
| **J** | Move wire forward (-0.1mm AP) |
| **L** | Move wire backward (+0.1mm AP) |
| **Ctrl+O** | Open STL file |
| **Ctrl+S** | Save project (future) |
| **Ctrl+E** | Export G-code (future) |
| **Ctrl+Z** | Undo (future) |
| **Ctrl+Y** | Redo (future) |

---

## Appendix B: File Formats

### Input: STL Files
- **Format:** Binary or ASCII STL
- **Units:** Millimeters (assumed)
- **Orientation:** No specific requirement (auto-detected)
- **Quality:** Higher mesh density = better detection accuracy
- **Recommended:** 50,000-500,000 vertices

### Output: G-Code
- **Dialect:** Generic Marlin/Grbl compatible
- **Units:** G21 (millimeters)
- **Coordinate System:** G90 (absolute)
- **Feed Rates:** F1000 (1000 mm/min default, configurable)

### Output: ESP32 Code
- **Language:** C++ (Arduino framework)
- **Libraries:** AccelStepper
- **Data Format:** Embedded float array
- **Size Limit:** ~4200 points × 12 bytes = 50KB (fits in ESP32 flash)

### Output: STL Mesh
- **Format:** Binary STL
- **Content:** Wire geometry as cylindrical mesh
- **Diameter:** 0.5mm default (configurable)
- **Segments:** 20 faces per wire segment (smooth appearance)

---

## Appendix C: Contact & Support

### Project Information
- **Repository:** Local development (not yet public)
- **Version:** 2.1.0 (Professional Hybrid Edition)
- **License:** Not yet specified (recommend MIT or Apache 2.0 for open source)

### For Orthodontists
If you're an orthodontist interested in using this tool:
1. Contact project maintainer for collaboration
2. Provide sample STL files for testing
3. Review generated wires for clinical accuracy
4. Suggest improvements based on clinical needs

### For Developers
Contributions welcome:
- Bug fixes
- Algorithm improvements
- New export formats
- UI/UX enhancements
- Documentation

---

## Version History

### v2.1.0 (2025-01-16) - Current
- **Feature:** Ultra-smooth wires (3x resolution, enhanced smoothing)
- **Feature:** Hybrid mode with draggable sphere widgets
- **Fix:** Lower jaw movement GUI issues
- **Fix:** Wire not updating during point dragging
- **Improvement:** All 14 teeth now editable in hybrid mode

### v2.0.0 (2025-01-13)
- **Feature:** PyQt5 enhanced GUI
- **Feature:** PyVista 3D visualization
- **Feature:** Dual-arch support
- **Feature:** ESP32 code generation

### v1.x (Earlier)
- Basic tooth detection
- Bracket positioning
- Wire generation with Catmull-Rom splines
- Tkinter GUI

---

**Document Maintained By:** Project Development Team
**Last Review:** 2025-01-16
**Next Review:** 2025-02-16 (monthly)

---

*For detailed algorithm documentation, see [ALGORITHM.md](ALGORITHM.md)*
*For technical specifications, see inline code documentation*
