# Orthodontic Wire Generator

**Version:** 2.1.0 (Professional Hybrid Edition)
**Branch:** feature/smoothwire

Automated orthodontic wire design system for generating custom archwires from 3D dental scans.

---

## Quick Start

### Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

### Run Application
```bash
# Launch the GUI
python run_app.py
```

---

## Features

- **Automatic Tooth Detection** - AI-powered detection of 14-16 teeth
- **3 Workflow Modes** - Automatic, Manual, and Hybrid design approaches
- **Ultra-Smooth Wire Paths** - Catmull-Rom splines with multi-stage Gaussian smoothing
- **Dual-Arch Support** - Upper and lower jaw processing with collision detection
- **Multiple Export Formats** - G-code (CNC), ESP32/Arduino, STL mesh
- **Interactive 3D Editing** - Real-time wire refinement with draggable control points

---

## Target Users

**Orthodontists** designing custom treatment wires for patients with unique dental anatomy

---

## Documentation

| Document | Description |
|----------|-------------|
| [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) | **START HERE** - Complete project overview, architecture, algorithms, and user guide |
| [ALGORITHM.md](ALGORITHM.md) | Detailed mathematical algorithms and technical specifications |
| [FILES_TO_DELETE.md](FILES_TO_DELETE.md) | Cleanup guide (historical reference) |
| [CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md) | Summary of repository cleanup performed |

---

## Project Structure

```
orthodontic_wire_generator/
├── core/                   # Core algorithms (tooth detection, bracket positioning)
├── wire/                   # Wire generation algorithms
├── gui/                    # PyQt5 user interface
├── visualization/          # PyVista 3D visualization
├── export/                 # G-code, ESP32, STL exporters
├── utils/                  # Utility functions
├── tests/                  # Unit tests
├── STLfiles/               # Sample STL files
├── run_app.py              # Main application launcher
├── requirements.txt        # Python dependencies
└── PROJECT_DOCUMENTATION.md # Complete documentation
```

---

## Technology Stack

- **Python 3.7+** with NumPy, SciPy, Open3D
- **GUI**: PyQt5 + PyVista (interactive 3D)
- **Algorithms**: Catmull-Rom splines, Gaussian filtering, angular segmentation
- **Export**: G-code (CNC), ESP32/Arduino code, STL meshes

---

## Workflows

### 1. Automatic Mode (Fast)
1. Load STL file → Auto-detect teeth → Generate wire → Export
2. **Time:** ~2 minutes

### 2. Manual Mode (Precise)
1. Load STL → Place 3+ control points → Generate wire → Export
2. **Time:** ~5 minutes

### 3. Hybrid Mode (Best)
1. Run automatic → Convert to editable points → Drag to refine → Export
2. **Time:** ~3 minutes

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **I** | Increase wire height (+0.1mm) |
| **K** | Decrease wire height (-0.1mm) |
| **J** | Move wire forward |
| **L** | Move wire backward |

---

## Export Formats

- **G-code** - For CNC wire-bending machines (Marlin/Grbl compatible)
- **ESP32 Code** - Arduino sketch for stepper motor wire benders
- **STL Mesh** - 3D visualization and printing

---

## Recent Improvements (feature/smoothwire)

- 3x higher wire resolution (300 points/segment)
- Enhanced smoothing (5 passes, σ=12.0)
- Removed sharp corners in wire paths
- Real-time point dragging in hybrid mode
- All 14 teeth now editable

---

## System Requirements

- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.7 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **GPU**: OpenGL 3.2+ capable

---

## Support

For detailed information, see [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)

For algorithm details, see [ALGORITHM.md](ALGORITHM.md)

---

## Status

- ✅ Core functionality: **Complete**
- ✅ GUI: **Professional PyQt5 interface**
- ✅ Export formats: **G-code, ESP32, STL**
- ⏳ Clinical validation: **In progress**
- ⏳ Testing: **Ongoing**

---

## License

To be specified

---

**Last Updated:** 2025-01-16
