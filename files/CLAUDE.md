# CLAUDE.md
## AI Context Document for Orthodontic Wire Generator

**Purpose:** This document provides comprehensive context for AI assistants (Claude, ChatGPT, etc.) to understand the project and assist with development, debugging, and enhancements.

**Last Updated:** January 9, 2026  
**Project:** Orthodontic Wire Generator - Professional Edition  
**Repository:** https://github.com/alisoleah/orthodontic_wire_generator_latest  
**Branch:** feature/smoothwire

---

## Quick Context Summary

### What Is This Project?

A professional orthodontic wire generator application that creates custom archwires from 3D dental scans (STL files). Think "FIXR alternative" - same workflow, open-source, AI-powered detection.

**Core Value:** Design clinically accurate custom orthodontic wires in 2-5 minutes instead of 30-45 minutes of manual work.

### Technology Stack

```
Frontend:    PyQt5 5.15+ (GUI)
3D Engine:   PyVista 0.46+ / VTK 9.5+ (visualization)
Algorithms:  NumPy, SciPy (Catmull-Rom splines, Gaussian smoothing)
Mesh:        Open3D 0.19+, trimesh 4.6+
Export:      Custom G-code, Arduino/ESP32 code, STL
Python:      3.7 - 3.11
Platform:    Windows, macOS (Intel + Apple Silicon), Linux
```

### Current Status (January 2026)

✅ **Working:**
- Core algorithms (tooth detection, wire generation)
- 3 workflow modes (Auto, Manual, Hybrid)
- Real-time 3D editing with draggable control points
- Export to G-code, Arduino, STL
- Ultra-smooth wires (Catmull-Rom + multi-stage Gaussian smoothing)

⏳ **In Progress:**
- Futuristic gradient UI redesign
- Clinical validation (testing on diverse anatomies)
- Cross-platform packaging (installers for Win/Mac/Linux)

🔮 **Planned:**
- Bracket prescription databases
- Cloud features (case storage, collaboration)
- Direct CNC machine control
- Advanced clinical features (torque calculations, treatment staging)

---

## Project Structure

```
orthodontic_wire_generator_latest/
├── run_app.py                          # Main entry point
├── core/
│   └── workflow_manager.py             # Central orchestrator
├── detection/
│   └── tooth_detector.py               # Angular segmentation algorithm
├── positioning/
│   └── bracket_positioner.py           # Bracket placement logic
├── wire/
│   └── wire_path_creator.py            # ⭐ CORE: Wire generation algorithm
├── gui/
│   └── enhanced_main_window.py         # PyQt5 main window
├── visualization/
│   └── pyvista_visualizer.py           # 3D interactive viewer
├── export/
│   ├── gcode_exporter.py               # G-code generation
│   ├── arduino_exporter.py             # Arduino/ESP32 code
│   └── stl_exporter.py                 # STL mesh export
├── tests/
│   ├── test_tooth_detection.py
│   ├── test_wire_generation.py
│   └── fixtures/                       # Test STL files
├── STLfiles/                           # Sample dental scans (38 files)
├── requirements.txt                    # Python dependencies
├── BRD_Orthodontic_Wire_Generator.md   # Business Requirements
├── PRD_Orthodontic_Wire_Generator.md   # Product Requirements
└── CLAUDE.md                           # This file
```

---

## Core Algorithms Explained

### 1. Tooth Detection (Angular Segmentation)

**Purpose:** Automatically detect individual tooth positions from a 3D dental scan.

**Algorithm:**
```python
# Pseudocode
def detect_teeth(crown_mesh, num_teeth=14):
    # 1. Find the center of the dental arch
    centroid = mean(crown_mesh.vertices)
    
    # 2. Convert vertices to polar coordinates (r, θ, z)
    for vertex in crown_mesh.vertices:
        r = distance(vertex, centroid)
        θ = atan2(vertex.y - centroid.y, vertex.x - centroid.x)
        z = vertex.z
        
    # 3. Divide 360° into N angular sectors (N = num_teeth)
    angle_step = 360 / num_teeth  # e.g., 25.7° for 14 teeth
    
    # 4. Group vertices by angular sector
    tooth_positions = []
    for i in range(num_teeth):
        start_angle = i * angle_step
        end_angle = (i + 1) * angle_step
        
        # Find vertices in this angular range
        sector_vertices = [v for v in vertices if start_angle <= θ(v) < end_angle]
        
        # Centroid of sector = tooth position
        tooth_center = mean(sector_vertices)
        tooth_positions.append(tooth_center)
        
    return tooth_positions
```

**Complexity:** O(V) where V = number of vertices (typically 200K)  
**Time:** ~5-10 seconds on modern hardware

**Strengths:**
- Fast (single-pass algorithm)
- Works well for normal spacing and mild crowding
- No machine learning required (deterministic)

**Weaknesses:**
- Struggles with severe crowding (>3mm overlap)
- Assumes roughly circular dental arch
- Doesn't detect missing teeth automatically

**Future Improvements:**
- Machine learning model (CNN or Point Transformer)
- Confidence scores per tooth
- Automatic missing tooth detection

### 2. Wire Path Generation (⭐ CORE ALGORITHM)

**Purpose:** Create an ultra-smooth wire path through detected bracket positions.

**Multi-Stage Algorithm:**

```python
def create_smooth_path(bracket_positions):
    """
    Generate ultra-smooth wire path using 5-stage process
    
    Input: Nx3 array of bracket positions (e.g., 14 teeth × 3 coordinates)
    Output: Mx3 array of high-resolution wire path (e.g., 4200 × 3 points)
    """
    
    # STAGE 1: Dental Arch Curve Fitting
    # Fit parabolic curve to bracket positions using least-squares
    arch_curve = fit_parabola_least_squares(bracket_positions)
    
    # STAGE 2: Intermediate Point Generation
    # Insert 3 points between each pair of brackets
    dense_points = []
    for i in range(len(bracket_positions) - 1):
        p1, p2 = bracket_positions[i], bracket_positions[i+1]
        
        # Use arch curve to guide intermediate points
        for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
            interp_point = p1 + t * (p2 - p1)
            projected_point = project_onto_curve(interp_point, arch_curve)
            dense_points.append(projected_point)
    
    # STAGE 3: Catmull-Rom Spline Interpolation
    # Create super-high-resolution path (300 points per segment)
    spline_path = []
    for i in range(len(dense_points) - 1):
        # Get control points for Catmull-Rom (4 points: P0, P1, P2, P3)
        p0 = dense_points[max(0, i-1)]
        p1 = dense_points[i]
        p2 = dense_points[i+1]
        p3 = dense_points[min(len(dense_points)-1, i+2)]
        
        # Interpolate 300 points between P1 and P2
        for t in linspace(0, 1, 300):
            point = catmull_rom_point(p0, p1, p2, p3, t)
            spline_path.append(point)
    
    # STAGE 4: Multi-Pass Gaussian Smoothing
    # Apply Gaussian filter 5 times with large kernel (σ=12.0)
    smooth_path = np.array(spline_path)
    for pass_num in range(5):
        smooth_path = gaussian_filter1d(smooth_path, sigma=12.0, axis=0)
    
    # STAGE 5: Validation
    # Ensure path passes through brackets within tolerance
    for bracket in bracket_positions:
        distances = [distance(point, bracket) for point in smooth_path]
        min_distance = min(distances)
        if min_distance > 0.2:  # 0.2mm tolerance
            raise ValidationError(f"Path deviates {min_distance}mm from bracket")
    
    return smooth_path
```

**Key Parameters:**

| Parameter | Value | Impact |
|-----------|-------|--------|
| `points_per_segment` | 300 | Higher = smoother curves, larger file size |
| `sigma` | 12.0 | Higher = smoother, but may deviate from brackets |
| `smoothing_passes` | 5 | More passes = smoother, but slower |
| `intermediate_points` | 3 | More points = better arch following |

**Why This Works:**
1. **Catmull-Rom splines** ensure smooth curvature (C1 continuity)
2. **Gaussian smoothing** removes micro-jitter and ensures clinical smoothness
3. **Multi-stage approach** balances accuracy (passing through brackets) and smoothness

**Typical Output:**
- **Input:** 14 bracket positions (42 coordinates)
- **Output:** ~4,200 smooth path points (12,600 coordinates)
- **Time:** ~1-2 seconds

### 3. Real-Time Wire Updates (Hybrid Mode)

**Challenge:** Update wire path within 200ms when user drags a control point.

**Solution:**
```python
def on_sphere_drag(event, sphere_index):
    """Handle real-time wire update when user drags a sphere"""
    
    # Get new position from dragged sphere
    new_position = event.picked_point
    
    # Update bracket position
    self.bracket_positions[sphere_index] = new_position
    
    # Regenerate wire path (fast path: skip validation)
    new_wire_path = self.wire_creator.create_smooth_path(
        self.bracket_positions,
        fast_mode=True  # Skip some validation for speed
    )
    
    # Update 3D visualization (PyVista actor)
    self.wire_actor.GetMapper().SetInputData(new_wire_path)
    self.plotter.render()  # Force immediate redraw
```

**Optimization Tricks:**
- Skip some validation checks in fast mode
- Use smaller smoothing kernel (σ=8.0 instead of 12.0)
- Cache arch curve fit (reuse if only 1-2 points moved)
- Update only affected segments (not entire wire)

---

## Common Development Tasks

### How to Add a New Export Format

**Example: Adding CSV Point Cloud Export**

1. **Create exporter class:**

```python
# export/csv_exporter.py

import csv
from typing import List
import numpy as np

class CSVExporter:
    """Export wire path as CSV point cloud"""
    
    def export(self, wire_path: np.ndarray, file_path: str) -> None:
        """
        Export wire path to CSV file
        
        Format:
        X,Y,Z,Index
        12.345,5.678,2.500,0
        12.389,5.702,2.498,1
        ...
        """
        
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['X', 'Y', 'Z', 'Index'])
            
            # Data rows
            for i, point in enumerate(wire_path):
                x, y, z = point
                writer.writerow([f"{x:.3f}", f"{y:.3f}", f"{z:.3f}", i])
                
        print(f"Exported {len(wire_path)} points to {file_path}")
```

2. **Add to export manager:**

```python
# export/export_manager.py

from export.csv_exporter import CSVExporter

class ExportManager:
    def __init__(self):
        # ... existing exporters
        self.csv_exporter = CSVExporter()
        
    def export_csv(self, wire_path, file_path):
        """Export to CSV format"""
        self.csv_exporter.export(wire_path, file_path)
```

3. **Add UI button:**

```python
# gui/enhanced_main_window.py

def setup_export_buttons(self):
    # ... existing buttons
    
    csv_button = QPushButton("Export CSV")
    csv_button.clicked.connect(self.on_export_csv_clicked)
    self.export_layout.addWidget(csv_button)
    
def on_export_csv_clicked(self):
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Export CSV", "", "CSV Files (*.csv)"
    )
    if file_path:
        wire_path = self.workflow_manager.get_current_wire_path()
        self.export_manager.export_csv(wire_path, file_path)
        QMessageBox.information(self, "Success", f"Exported to {file_path}")
```

### How to Improve Tooth Detection

**Current Limitation:** Angular segmentation fails on severe crowding.

**Better Approach: Machine Learning**

```python
# detection/ml_tooth_detector.py

import torch
import torch.nn as nn
from pointnet import PointNet  # Hypothetical 3D point cloud network

class MLToothDetector:
    """Machine learning-based tooth detection using PointNet"""
    
    def __init__(self, model_path='models/tooth_detector.pth'):
        self.model = PointNet(num_classes=16, num_features=3)
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
        
    def detect_teeth(self, crown_mesh):
        """
        Detect teeth using neural network
        
        Returns:
        - tooth_positions: Nx3 array
        - confidence_scores: N array (0.0 to 1.0)
        """
        
        # Convert mesh to point cloud (sample 10K points)
        points = crown_mesh.sample_points_uniformly(n=10000)
        points_tensor = torch.tensor(points, dtype=torch.float32)
        
        # Run inference
        with torch.no_grad():
            predictions = self.model(points_tensor.unsqueeze(0))
            
        # Extract tooth centers from predictions
        tooth_positions = self.extract_centers(predictions)
        confidence_scores = self.extract_confidences(predictions)
        
        return tooth_positions, confidence_scores
```

**Training Data Requirements:**
- 500-1000 labeled dental scans
- Manual annotations of tooth boundaries
- Diverse anatomies (crowding, gaps, rotations)

**Next Steps:**
- Collect/generate training data
- Train PointNet or PointTransformer model
- Integrate into workflow manager as optional detector
- Fall back to angular segmentation if model not available

### How to Add Keyboard Shortcut

**Example: Add Ctrl+D for "Duplicate Wire"**

```python
# gui/enhanced_main_window.py

def setup_shortcuts(self):
    """Configure keyboard shortcuts"""
    
    # Existing shortcuts
    self.shortcut_increase_height = QShortcut(QKeySequence("I"), self)
    self.shortcut_increase_height.activated.connect(self.increase_wire_height)
    # ... other shortcuts
    
    # NEW: Duplicate wire shortcut
    self.shortcut_duplicate = QShortcut(QKeySequence("Ctrl+D"), self)
    self.shortcut_duplicate.activated.connect(self.duplicate_wire)
    
def duplicate_wire(self):
    """Create a copy of the current wire with offset"""
    
    if not self.workflow_manager.has_wire():
        QMessageBox.warning(self, "No Wire", "Generate a wire first")
        return
        
    # Get current wire
    current_wire = self.workflow_manager.get_current_wire_path()
    
    # Apply offset (e.g., 5mm upward for upper arch)
    offset = np.array([0, 0, 5.0])
    duplicated_wire = current_wire + offset
    
    # Add to visualization
    self.visualizer.add_wire(duplicated_wire, color='green', name='Wire Copy')
    
    # Notify user
    self.statusBar().showMessage("Wire duplicated with 5mm offset", 3000)
```

### How to Debug Performance Issues

**Tools:**

1. **Python Profiler:**

```python
# Add to run_app.py

import cProfile
import pstats

def run_with_profiling():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run app
    app = QApplication(sys.argv)
    window = EnhancedMainWindow()
    window.show()
    app.exec_()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 slowest functions

if __name__ == "__main__":
    run_with_profiling()
```

2. **Memory Profiler:**

```python
from memory_profiler import profile

@profile
def create_smooth_path(self, bracket_positions):
    # ... algorithm code
    pass
```

3. **PyVista Performance Tips:**

```python
# Slow: Create new actor every frame
def update_wire_slow(wire_path):
    self.plotter.remove_actor(self.wire_actor)
    self.wire_actor = self.plotter.add_lines(wire_path)
    
# Fast: Update existing actor's data
def update_wire_fast(wire_path):
    mesh = pv.PolyData(wire_path)
    self.wire_actor.GetMapper().SetInputData(mesh)
    self.plotter.render()
```

---

## UI/UX Design Guidelines

### Futuristic Gradient Theme

**Goal:** Create a modern, professional interface that feels like cutting-edge medical software.

**Design Principles:**
1. **Dark Theme Base** - Reduces eye strain, feels premium
2. **Gradient Accents** - Blue/purple/teal for modern aesthetic
3. **Glass Morphism** - Semi-transparent panels with blur
4. **Smooth Animations** - 200-300ms transitions, ease-out easing
5. **High Contrast Text** - White/light gray on dark backgrounds

**Implementation (PyQt5 Stylesheets):**

```python
# gui/styles.py

DARK_GRADIENT_THEME = """
QMainWindow {
    background-color: #1a1a2e;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #667eea, stop:1 #764ba2);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 14px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #7a8ef0, stop:1 #8a5bb8);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #5568d3, stop:1 #6a3f8f);
}

QSlider::groove:horizontal {
    background: rgba(255, 255, 255, 0.1);
    height: 4px;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #4facfe, stop:1 #00f2fe);
    width: 16px;
    height: 16px;
    border-radius: 8px;
    margin: -6px 0;
}

QLabel {
    color: #e0e0e0;
    font-size: 14px;
}

QGroupBox {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 16px;
    margin-top: 12px;
    color: #e0e0e0;
    font-weight: 600;
}

QStatusBar {
    background: #16213e;
    color: #a0a0a0;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}
"""

# Apply in main window
class EnhancedMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(DARK_GRADIENT_THEME)
```

**Visual Hierarchy:**

```
┌─────────────────────────────────────────┐
│ Title Bar (Gradient: #667eea → #764ba2) │ ← Primary accent
├─────────────────────────────────────────┤
│ Menu Bar (#16213e)                       │
├────────┬────────────────────────────────┤
│ Panel  │ 3D Viewport (#1a1a2e)          │
│ (#05)  │                                │ ← Surface: rgba(255,255,255,0.05)
│ ┌────┐ │  [Mesh rendering]              │
│ │Btn │ │                                │ ← Buttons: Gradient
│ └────┘ │                                │
└────────┴────────────────────────────────┘
│ Status Bar (#16213e)                    │
└─────────────────────────────────────────┘
```

### Animation Examples

**Wire Generation Animation:**

```python
def animate_wire_generation(self, wire_path, duration_ms=1000):
    """Animate wire path drawing"""
    
    # Create timer for progressive drawing
    self.animation_timer = QTimer()
    self.animation_step = 0
    self.total_steps = 50
    step_size = len(wire_path) // self.total_steps
    
    def update_frame():
        self.animation_step += 1
        
        # Draw partial wire
        end_index = self.animation_step * step_size
        partial_wire = wire_path[:end_index]
        
        self.visualizer.update_wire(partial_wire)
        
        if self.animation_step >= self.total_steps:
            self.animation_timer.stop()
            # Show completion effect (pulse)
            self.show_completion_pulse()
            
    self.animation_timer.timeout.connect(update_frame)
    self.animation_timer.start(duration_ms // self.total_steps)
```

**Completion Pulse Effect:**

```python
def show_completion_pulse(self):
    """Pulse effect when wire generation completes"""
    
    # Create opacity animation
    self.pulse_effect = QPropertyAnimation(self.wire_actor, b"opacity")
    self.pulse_effect.setDuration(500)
    self.pulse_effect.setStartValue(1.0)
    self.pulse_effect.setKeyValueAt(0.5, 0.5)
    self.pulse_effect.setEndValue(1.0)
    self.pulse_effect.setEasingCurve(QEasingCurve.InOutQuad)
    self.pulse_effect.start()
```

---

## Testing Strategies

### Unit Tests (pytest)

**Philosophy:** Test individual functions in isolation.

```python
# tests/test_wire_path_creator.py

import pytest
import numpy as np
from wire.wire_path_creator import WirePathCreator

@pytest.fixture
def wire_creator():
    return WirePathCreator()

class TestWirePathCreator:
    def test_straight_line_path(self, wire_creator):
        """Test with 3 points in a straight line"""
        brackets = np.array([
            [0.0, 0.0, 0.0],
            [5.0, 0.0, 0.0],
            [10.0, 0.0, 0.0]
        ])
        
        path = wire_creator.create_smooth_path(brackets)
        
        # All points should have Y ≈ 0 (straight line)
        assert np.allclose(path[:, 1], 0.0, atol=0.01)
        
    def test_parabolic_arch(self, wire_creator):
        """Test with parabolic arch shape"""
        brackets = np.array([
            [-10.0, 0.0, 0.0],
            [-5.0, 5.0, 0.0],
            [0.0, 6.0, 0.0],
            [5.0, 5.0, 0.0],
            [10.0, 0.0, 0.0]
        ])
        
        path = wire_creator.create_smooth_path(brackets)
        
        # Check path passes through each bracket
        for bracket in brackets:
            distances = np.linalg.norm(path - bracket, axis=1)
            min_dist = np.min(distances)
            assert min_dist < 0.15  # Within 0.15mm tolerance
            
    def test_smoothness(self, wire_creator):
        """Test that generated path is smooth (low curvature)"""
        brackets = np.array([
            [0.0, 0.0, 0.0],
            [5.0, 2.0, 0.0],
            [10.0, 0.0, 0.0]
        ])
        
        path = wire_creator.create_smooth_path(brackets)
        
        # Calculate maximum curvature
        curvatures = self._calculate_curvature(path)
        max_curvature = np.max(curvatures)
        
        # Should be smooth (no sharp bends)
        assert max_curvature < 0.5  # Max 0.5 / mm curvature
        
    @staticmethod
    def _calculate_curvature(path):
        """Calculate curvature at each point using finite differences"""
        # First derivatives
        dx = np.gradient(path[:, 0])
        dy = np.gradient(path[:, 1])
        
        # Second derivatives
        ddx = np.gradient(dx)
        ddy = np.gradient(dy)
        
        # Curvature formula: κ = |x'y'' - y'x''| / (x'^2 + y'^2)^(3/2)
        numerator = np.abs(dx * ddy - dy * ddx)
        denominator = (dx**2 + dy**2)**(3/2)
        denominator[denominator < 1e-10] = 1e-10  # Avoid division by zero
        
        return numerator / denominator
```

### Integration Tests

**Philosophy:** Test component interactions.

```python
# tests/test_workflow_integration.py

from core.workflow_manager import WorkflowManager, WorkflowMode
from tests.utils import load_test_mesh

class TestWorkflowIntegration:
    def test_automatic_workflow_complete(self):
        """Test end-to-end automatic workflow"""
        
        # Setup
        manager = WorkflowManager()
        mesh = load_test_mesh("ideal_upper.stl")
        
        # Execute
        result = manager.process_automatic_mode(mesh)
        
        # Verify
        assert result.num_teeth_detected == 14
        assert result.wire_path is not None
        assert len(result.wire_path) > 1000
        assert result.success is True
        
    def test_mode_switching_preserves_data(self):
        """Test that switching modes doesn't lose work"""
        
        manager = WorkflowManager()
        mesh = load_test_mesh("ideal_upper.stl")
        
        # Start in automatic mode
        auto_result = manager.process_automatic_mode(mesh)
        original_brackets = auto_result.bracket_positions.copy()
        
        # Switch to hybrid mode
        manager.switch_mode(WorkflowMode.HYBRID)
        
        # Verify brackets preserved
        current_brackets = manager.get_current_bracket_positions()
        assert np.allclose(original_brackets, current_brackets)
```

### Manual Test Scripts

**Performance Benchmark:**

```python
# tests/benchmark_performance.py

import time
import numpy as np
from core.workflow_manager import WorkflowManager
from tests.utils import load_test_mesh

def benchmark_workflow():
    """Measure performance of key operations"""
    
    manager = WorkflowManager()
    mesh = load_test_mesh("large_scan_500k.stl")  # 500K vertices
    
    # Benchmark 1: Tooth detection
    start = time.time()
    teeth = manager.tooth_detector.detect_teeth(mesh)
    detection_time = time.time() - start
    print(f"Tooth Detection: {detection_time:.2f}s")
    assert detection_time < 10.0, "Detection too slow!"
    
    # Benchmark 2: Wire generation
    bracket_positions = np.array(teeth)
    start = time.time()
    wire_path = manager.wire_creator.create_smooth_path(bracket_positions)
    generation_time = time.time() - start
    print(f"Wire Generation: {generation_time:.2f}s")
    assert generation_time < 3.0, "Generation too slow!"
    
    # Benchmark 3: Real-time update (simulate drag)
    bracket_positions[5] += [0.5, 0.5, 0.0]  # Move one bracket
    start = time.time()
    wire_path = manager.wire_creator.create_smooth_path(
        bracket_positions, fast_mode=True
    )
    update_time = time.time() - start
    print(f"Real-Time Update: {update_time:.3f}s")
    assert update_time < 0.2, "Update too slow for real-time!"
    
    print("\n✅ All performance benchmarks passed!")

if __name__ == "__main__":
    benchmark_workflow()
```

---

## Common Issues & Solutions

### Issue 1: PyVista Rendering Fails on macOS

**Symptoms:**
- Black screen in 3D viewport
- Error: "Failed to initialize OpenGL context"

**Solution:**
```python
# Set PyVista to use OSMesa (software rendering) on macOS
import os
os.environ['PYVISTA_USE_PANEL'] = '0'
os.environ['PYVISTA_OFF_SCREEN'] = 'false'

# Or explicitly set renderer
import pyvista as pv
pv.set_plot_theme("document")
pv.global_theme.notebook = False
```

**Alternative:** Install XQuartz (X11 for macOS)

### Issue 2: Memory Leak During Extended Use

**Symptoms:**
- RAM usage grows over time
- Application slows down after 30+ minutes

**Diagnosis:**
```python
# Add memory tracking
import tracemalloc

tracemalloc.start()

# ... run application

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

for stat in top_stats[:10]:
    print(stat)
```

**Common Causes:**
1. Not clearing old PyVista actors
2. NumPy arrays not garbage collected
3. Circular references in PyQt objects

**Solution:**
```python
def cleanup_visualization(self):
    """Properly dispose of 3D objects"""
    
    # Remove all actors
    self.plotter.clear()
    
    # Force garbage collection
    import gc
    gc.collect()
    
    # Clear cached data
    self.wire_path_cache = None
    self.mesh_cache = None
```

### Issue 3: Wire Doesn't Pass Through Bracket

**Symptoms:**
- Generated wire visibly misses some bracket positions
- Validation error: "Path deviates X mm from bracket"

**Diagnosis:**
```python
# Check deviation at each bracket
def diagnose_wire_accuracy(wire_path, bracket_positions):
    for i, bracket in enumerate(bracket_positions):
        distances = np.linalg.norm(wire_path - bracket, axis=1)
        min_dist = np.min(distances)
        min_idx = np.argmin(distances)
        
        print(f"Bracket {i}: {min_dist:.3f}mm deviation at point {min_idx}")
        
        if min_dist > 0.15:
            print(f"  ⚠️ WARNING: Exceeds 0.15mm tolerance")
```

**Possible Causes:**
1. Smoothing too aggressive (σ too large)
2. Not enough intermediate points
3. Bracket position outlier (detection error)

**Solutions:**
- Reduce smoothing sigma: `σ = 12.0 → 10.0`
- Increase intermediate points: `3 → 5 per segment`
- Add constraint: Force path through exact bracket position

### Issue 4: App Crashes on Corrupted STL

**Symptoms:**
- App crashes when loading certain STL files
- Error: "Segmentation fault" or "Access violation"

**Solution:**
```python
def safe_stl_import(file_path):
    """Import STL with error handling"""
    
    try:
        # Try Open3D first
        mesh = o3d.io.read_triangle_mesh(file_path)
        
        # Validate mesh
        if not mesh.has_vertices():
            raise ValueError("Mesh has no vertices")
            
        if not mesh.has_triangles():
            raise ValueError("Mesh has no triangles")
            
        # Check for NaN/Inf values
        vertices = np.asarray(mesh.vertices)
        if np.any(np.isnan(vertices)) or np.any(np.isinf(vertices)):
            raise ValueError("Mesh contains invalid coordinates")
            
        return mesh
        
    except Exception as e:
        # Try trimesh as fallback
        try:
            mesh = trimesh.load(file_path)
            return mesh
        except Exception as e2:
            raise RuntimeError(
                f"Failed to load STL file: {str(e)}\n"
                f"Fallback also failed: {str(e2)}"
            )
```

---

## Future Enhancement Ideas

### Phase 2 Enhancements (Next 6 Months)

#### 1. Bracket Prescription Databases

**Goal:** Support different orthodontic bracket systems (Roth, MBT, Andrews).

**Implementation:**
```python
# data/bracket_prescriptions.py

PRESCRIPTIONS = {
    "roth": {
        "upper_central_incisor": {
            "torque": 12,  # degrees
            "tip": 5,      # degrees
            "in_out": 0.0  # mm
        },
        # ... other teeth
    },
    "mbt": {
        "upper_central_incisor": {
            "torque": 17,
            "tip": 5,
            "in_out": 0.0
        },
        # ... other teeth
    }
}

class BracketPrescriptionManager:
    def apply_prescription(self, tooth_positions, prescription_name):
        """Adjust bracket positions based on prescription"""
        
        prescription = PRESCRIPTIONS[prescription_name]
        
        for tooth_id, position in tooth_positions.items():
            params = prescription[tooth_id]
            
            # Apply torque (rotation around X-axis)
            position = self.apply_torque(position, params["torque"])
            
            # Apply tip (rotation around Y-axis)
            position = self.apply_tip(position, params["tip"])
            
            # Apply in-out (translation along Z-axis)
            position[2] += params["in_out"]
            
        return tooth_positions
```

#### 2. Treatment Staging (Multi-Arch Progression)

**Goal:** Design a sequence of wires for gradual tooth movement.

**Concept:**
```
Initial Wire (Stage 1): Minimal force, fits current anatomy
  ↓ (2 weeks)
Intermediate Wire (Stage 2): Moderate force, 50% to target
  ↓ (2 weeks)
Final Wire (Stage 3): Full force, ideal arch form
```

**Implementation:**
```python
def generate_treatment_stages(
    current_anatomy, 
    target_anatomy, 
    num_stages=3
):
    """Generate progressive wire sequence"""
    
    stages = []
    
    for i in range(num_stages):
        # Interpolate between current and target
        t = (i + 1) / num_stages
        intermediate_anatomy = current_anatomy + t * (target_anatomy - current_anatomy)
        
        # Generate wire for this stage
        wire = create_smooth_path(intermediate_anatomy)
        
        stages.append({
            "stage": i + 1,
            "anatomy": intermediate_anatomy,
            "wire": wire,
            "expected_duration_weeks": 2
        })
        
    return stages
```

#### 3. Force/Moment Calculations

**Goal:** Predict orthodontic forces applied by the wire.

**Physics:**
```
F = k * δ  (Hooke's Law for elastic deformation)

Where:
- F: Force applied to tooth (Newtons)
- k: Wire stiffness (depends on material and cross-section)
- δ: Deflection distance (mm)
```

**Implementation:**
```python
class BiomechanicalAnalyzer:
    def __init__(self, wire_material="stainless_steel", wire_diameter=0.016):
        self.E = self.get_elastic_modulus(wire_material)  # Young's modulus
        self.I = (np.pi * wire_diameter**4) / 64  # Moment of inertia
        
    def calculate_force_at_bracket(self, wire_path, bracket_position):
        """Calculate force applied to bracket"""
        
        # Find closest point on wire to bracket
        distances = np.linalg.norm(wire_path - bracket_position, axis=1)
        closest_idx = np.argmin(distances)
        deflection = distances[closest_idx]
        
        # Calculate curvature at that point
        curvature = self._calculate_curvature(wire_path, closest_idx)
        
        # Force = (E * I * curvature) * deflection
        force = (self.E * self.I * curvature) * deflection
        
        return force
```

### Phase 3 Enhancements (6-12 Months)

#### 1. Cloud-Based Case Storage

**Features:**
- Save/load projects from cloud (AWS S3, Google Cloud Storage)
- Share cases with colleagues (view-only or collaborative)
- Version history (track changes over time)

**Architecture:**
```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Desktop    │ HTTPS   │   Backend    │         │  Cloud DB    │
│     App      │ ←----→  │   (Flask/    │ ←----→  │ (PostgreSQL) │
│              │         │   FastAPI)   │         │              │
└──────────────┘         └──────────────┘         └──────────────┘
                                 │
                                 ↓
                         ┌──────────────┐
                         │ Object Store │
                         │ (S3/GCS)     │
                         │  - STL files │
                         │  - Projects  │
                         └──────────────┘
```

#### 2. Collaborative Editing

**Real-Time Collaboration:**
- Multiple users edit same wire simultaneously
- See live cursors of other users
- Chat/comments within application

**Tech Stack:**
- WebRTC for peer-to-peer communication
- WebSockets for server-coordinated updates
- Operational Transform (OT) for conflict resolution

#### 3. Direct CNC Machine Control

**Serial Communication:**
```python
import serial

class CNCController:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        self.serial = serial.Serial(port, baudrate, timeout=1)
        
    def send_gcode(self, gcode_line):
        """Send single G-code command"""
        self.serial.write(f"{gcode_line}\n".encode())
        
        # Wait for acknowledgment
        response = self.serial.readline().decode().strip()
        return response == "ok"
        
    def stream_wire_path(self, wire_path):
        """Stream wire path to machine in real-time"""
        
        for i, point in enumerate(wire_path):
            x, y, z = point
            gcode = f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f} F1500"
            
            if not self.send_gcode(gcode):
                raise RuntimeError(f"Machine rejected command at point {i}")
                
            # Update progress in UI
            self.progress_callback(i / len(wire_path) * 100)
```

---

## API Documentation (For Developers)

### Core Classes

#### WorkflowManager

**Purpose:** Central orchestrator for all operations.

```python
class WorkflowManager:
    """
    Manages the entire wire generation workflow.
    
    Attributes:
        mode (WorkflowMode): Current workflow mode (AUTO, MANUAL, HYBRID)
        tooth_detector (ToothDetector): Tooth detection engine
        bracket_positioner (BracketPositioner): Bracket placement logic
        wire_creator (WirePathCreator): Wire generation algorithm
        
    Example:
        >>> manager = WorkflowManager()
        >>> manager.set_mode(WorkflowMode.AUTOMATIC)
        >>> result = manager.process_automatic_mode(mesh)
        >>> wire_path = result.wire_path
    """
    
    def process_automatic_mode(self, mesh: o3d.geometry.TriangleMesh) -> WorkflowResult:
        """
        Execute automatic workflow: detect → position → generate wire.
        
        Args:
            mesh: Open3D triangle mesh of dental arch
            
        Returns:
            WorkflowResult with detected teeth, bracket positions, and wire path
            
        Raises:
            DetectionError: If tooth detection fails
            ValidationError: If wire validation fails
        """
        
    def process_manual_mode(self, mesh, control_points: List[np.ndarray]) -> WorkflowResult:
        """
        Execute manual workflow: use user-defined control points.
        
        Args:
            mesh: Open3D triangle mesh (for visualization)
            control_points: List of XYZ coordinates where user clicked
            
        Returns:
            WorkflowResult with wire path through control points
        """
        
    def switch_mode(self, new_mode: WorkflowMode):
        """
        Change workflow mode and preserve relevant state.
        
        Args:
            new_mode: Target mode (AUTO, MANUAL, or HYBRID)
        """
```

#### WirePathCreator

**Purpose:** Core algorithm for generating smooth wire paths.

```python
class WirePathCreator:
    """
    Generates ultra-smooth wire paths through bracket positions.
    
    Uses multi-stage algorithm:
    1. Arch curve fitting
    2. Intermediate point generation
    3. Catmull-Rom spline interpolation
    4. Multi-pass Gaussian smoothing
    5. Validation
    
    Example:
        >>> creator = WirePathCreator()
        >>> brackets = np.array([[0,0,0], [5,0,0], [10,0,0]])
        >>> wire = creator.create_smooth_path(brackets)
        >>> print(wire.shape)  # (1200, 3) - 1200 points
    """
    
    def create_smooth_path(
        self, 
        bracket_positions: np.ndarray,
        sigma: float = 12.0,
        smoothing_passes: int = 5,
        points_per_segment: int = 300,
        fast_mode: bool = False
    ) -> np.ndarray:
        """
        Generate smooth wire path.
        
        Args:
            bracket_positions: Nx3 array of bracket XYZ coordinates
            sigma: Gaussian smoothing kernel size (larger = smoother)
            smoothing_passes: Number of smoothing iterations
            points_per_segment: Interpolation resolution
            fast_mode: Skip some validation for real-time updates
            
        Returns:
            Mx3 array of high-resolution wire path
            
        Raises:
            ValidationError: If path doesn't pass through brackets
        """
```

### Helper Functions

```python
def catmull_rom_point(p0, p1, p2, p3, t):
    """
    Calculate point on Catmull-Rom spline.
    
    Args:
        p0, p1, p2, p3: Control points (np.ndarray of shape (3,))
        t: Parameter in [0, 1] (position along curve)
        
    Returns:
        np.ndarray of shape (3,): Point on spline
    """
    
def gaussian_smooth_1d(data, sigma, passes=1):
    """
    Apply 1D Gaussian smoothing to 3D curve.
    
    Args:
        data: Nx3 array of points
        sigma: Kernel size
        passes: Number of iterations
        
    Returns:
        Nx3 array of smoothed points
    """
    
def validate_stl_mesh(mesh):
    """
    Check if STL mesh is valid for processing.
    
    Args:
        mesh: Open3D or trimesh object
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: With specific reason if invalid
    """
```

---

## Deployment Checklist

### Pre-Release

- [ ] All P0 features complete and tested
- [ ] No critical bugs (crash, data loss)
- [ ] Documentation complete (README, tutorials)
- [ ] Cross-platform testing (Win/Mac/Linux)
- [ ] Performance benchmarks pass
- [ ] Legal review (license, disclaimers)

### Packaging

**Windows:**
```bash
# Using PyInstaller
pyinstaller --name="OrthoWireGen" \
            --windowed \
            --icon=assets/icon.ico \
            --add-data="assets:assets" \
            run_app.py

# Create installer with Inno Setup
iscc ortho_wire_gen_installer.iss
```

**macOS:**
```bash
# Create .app bundle
python setup.py py2app

# Sign and notarize (requires Apple Developer account)
codesign --deep --force --verify --verbose --sign "Developer ID" dist/OrthoWireGen.app
xcrun notarytool submit OrthoWireGen.dmg --wait

# Create DMG
hdiutil create -volname "OrthoWireGen" -srcfolder dist/OrthoWireGen.app -ov -format UDZO OrthoWireGen.dmg
```

**Linux:**
```bash
# Create AppImage
appimagetool ortho_wire_gen.AppDir

# Or Flatpak
flatpak-builder build-dir com.orthodontics.WireGenerator.yaml
```

### Post-Release

- [ ] GitHub release with binaries
- [ ] Announce on Reddit (r/Dentistry, r/Python)
- [ ] Post on LinkedIn
- [ ] Email potential beta testers
- [ ] Monitor issue tracker for bugs
- [ ] Collect user feedback

---

## Frequently Asked Questions (for AI Assistants)

**Q: How do I add support for a new tooth count (e.g., 12 teeth instead of 14)?**

A: The tooth count is configurable in the `ToothDetector`:
```python
# In tooth_detector.py
detector = ToothDetector()
teeth = detector.detect_teeth(mesh, num_teeth=12)  # Pass desired count
```

**Q: Can this work for lower arches?**

A: Yes! The algorithm is arch-agnostic. Just set `arch_type` parameter:
```python
result = workflow_manager.process_automatic_mode(mesh, arch_type="lower")
```

**Q: How do I change the wire material (e.g., NiTi instead of stainless steel)?**

A: Currently, wire material only affects G-code comments. For biomechanical calculations (future feature), add material database:
```python
MATERIALS = {
    "stainless_steel": {"E": 200e9, "density": 8000},  # Pascals, kg/m³
    "niti": {"E": 83e9, "density": 6450}
}
```

**Q: Can I contribute to this project?**

A: Yes! See CONTRIBUTING.md for guidelines. Focus areas:
- Clinical validation (testing on diverse anatomies)
- Platform-specific fixes (especially macOS/Linux)
- UI/UX improvements
- Documentation and tutorials

**Q: Is this FDA-approved medical software?**

A: No. This is a design tool for professionals. Clinical application is the user's responsibility. Not intended to replace professional judgment.

---

## Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| 0.1.0 | Dec 2025 | Initial prototype (basic tooth detection) |
| 0.2.0 | Dec 2025 | Added manual mode (FIXR-like workflow) |
| 0.3.0 | Jan 2026 | Hybrid mode with draggable spheres |
| 0.4.0 | Jan 2026 | Ultra-smooth wires (multi-stage smoothing) |
| 0.5.0 | Jan 2026 | Export to G-code, Arduino, STL |
| **1.0.0** | **TBD** | **Public release (feature/smoothwire → main)** |

---

## Contact & Support

**Project Maintainer:** Aly Soleah  
**GitHub:** https://github.com/alisoleah/orthodontic_wire_generator_latest  
**Email:** [Contact via GitHub issues]

**For AI Assistants:**
- Report bugs via GitHub issues
- Suggest features via GitHub discussions
- Contribute code via pull requests

---

**Document End - CLAUDE.md v1.0**
