# Orthodontic Wire Generation Algorithm

## Overview
This document describes the mathematical algorithms and computational methods used to generate smooth, anatomically-accurate orthodontic wires that follow the natural curvature of dental arches.

---

## Table of Contents
1. [Mesh Processing](#1-mesh-processing)
2. [Tooth Detection](#2-tooth-detection)
3. [Bracket Positioning](#3-bracket-positioning)
4. [Wire Path Generation](#4-wire-path-generation)
5. [Wire Smoothing](#5-wire-smoothing)
6. [Offset Control](#6-offset-control)

---

## 1. Mesh Processing

### File: `core/mesh_processor.py`

#### Algorithm: Load and Clean STL Mesh
**Purpose**: Load dental arch STL files and prepare them for processing.

**Steps**:
1. **Load STL** using Open3D library
2. **Remove duplicates**: Eliminate duplicate vertices
3. **Remove degenerate triangles**: Clean up mesh topology
4. **Compute vertex normals**: Calculate surface normals for each vertex
5. **Unify normal orientation**: Ensure all normals point outward

**Mathematical Foundation**:
- Surface normal at vertex *v*: Average of adjacent face normals
- Face normal: Cross product of edge vectors

```
n_face = normalize((v2 - v1) × (v3 - v1))
n_vertex = normalize(Σ n_face_i / N)
```

---

## 2. Tooth Detection

### File: `core/tooth_detector.py`

#### Algorithm: Angular Segmentation Tooth Detection
**Purpose**: Automatically identify individual teeth from the dental arch mesh.

**Steps**:
1. **Identify anatomical axes**:
   - LR axis (Left-Right): Widest dimension
   - Height axis (Occlusal-Gingival): Smallest dimension
   - AP axis (Anterior-Posterior): Remaining dimension

2. **Extract crown region**:
   - Calculate crown level using height percentile
   - Filter vertices within tolerance of crown level

3. **Angular segmentation**:
   - Convert crown vertices to polar coordinates relative to arch center
   - Calculate angle: `θ = arctan2(y_AP, x_LR)`
   - Group vertices into 14-16 angular sectors
   - Each sector represents one tooth

4. **Tooth classification**:
   - **Incisors**: Teeth near front (|angle| < 30°)
   - **Canines**: Transition teeth (30° < |angle| < 60°)
   - **Premolars & Molars**: Posterior teeth (|angle| > 60°)

**Parameters**:
- Crown ratio: 0.3-0.4 (30-40% from gingival margin)
- Angular sectors: 14-16 (for full dentition)
- Height tolerance: 2-3mm

---

## 3. Bracket Positioning

### File: `core/bracket_positioner.py`

#### Algorithm: Anatomical Bracket Placement
**Purpose**: Position orthodontic brackets on the facial (front) surface of each tooth at the optimal height.

**Steps**:
1. **Determine target height**:
   - Upper arch: Minimum Z-coordinate + bracket_height offset
   - Lower arch: Maximum Z-coordinate - bracket_height offset

2. **Filter bracket-level vertices**:
   - Select vertices within height tolerance of target height
   - Typically ±1-2mm vertical range

3. **Find facial surface point**:
   - Calculate tooth-to-center direction vector
   - Project onto horizontal plane (ignore height)
   - Find vertex most aligned with this direction
   - This ensures bracket placement on front (facial) surface

4. **Calculate bracket normal**:
   - Use vertex normal as initial orientation
   - Ensure normal points outward from tooth surface

**Mathematical Foundation**:
```
direction_to_center = normalize(arch_center - tooth_center)
direction_to_center[z] = 0  # Project to horizontal plane

For each candidate vertex v:
  horizontal_pos = v[:2]  # X-Y coordinates only
  alignment = dot(normalize(horizontal_pos - tooth_center[:2]), direction_to_center[:2])

bracket_position = vertex with maximum alignment score
```

---

## 4. Wire Path Generation

### File: `wire/wire_path_creator.py`

#### Algorithm: Smooth Wire Path Through Brackets
**Purpose**: Generate a smooth, continuous wire path that passes through or near all bracket positions, following the natural dental arch curve.

### Phase 1: Dental Arch Curve Fitting

**Purpose**: Model the natural parabolic/circular shape of dental arches.

**Algorithm**: Parabolic Least-Squares Fitting

1. **Extract bracket positions** in horizontal plane (X-Y coordinates)
2. **Transform to arch-centered coordinates**:
   ```
   relative_pos = bracket_positions[:, :2] - arch_center[:2]
   ```

3. **Calculate average radius** for circular fallback:
   ```
   radius_avg = mean(||relative_pos||)
   ```

4. **Rotate coordinates** to arch-aligned frame:
   ```
   rotation_angle = -mean(arctan2(y, x))
   x_rot = x * cos(θ) - y * sin(θ)
   y_rot = x * sin(θ) + y * cos(θ)
   ```

5. **Fit parabola** using polynomial regression:
   ```
   y = ax² + bx + c
   coeffs = polyfit(x_rot, y_rot, degree=2)
   ```

**Output**: Arch parameters (parabola coefficients or circular radius)

### Phase 2: Intermediate Point Generation

**Purpose**: Create additional control points between brackets for smoother interpolation.

**Algorithm**: Arch-Projected Intermediate Points

**Steps**:
1. **For each bracket pair** (bracket_i, bracket_{i+1}):
   - Create **3 intermediate points** at t = 0.25, 0.5, 0.75

2. **Linear interpolation**:
   ```
   p_interp = bracket_i + t * (bracket_{i+1} - bracket_i)
   ```

3. **Project onto arch curve**:
   - Transform to rotated coordinates
   - Calculate y-coordinate from parabola equation
   - Transform back to original coordinates

4. **Apply adaptive offset** (move toward arch center):
   ```
   offset_distance = 1.5 + distance_from_center / 50.0  # 1.5-3mm range
   direction = normalize(arch_center - p_projected)
   direction[z] = 0  # Keep horizontal
   p_final = p_projected + direction * offset_distance
   ```

**Result**: Original N brackets → N + 3*(N-1) control points

### Phase 3: Spline Interpolation

**Purpose**: Create smooth curve through all control points.

**Algorithm**: Catmull-Rom Spline

**Properties**:
- Passes through all control points (interpolating, not approximating)
- C¹ continuous (smooth first derivative)
- Local control (changing one point affects only nearby curve)

**Formula** for segment between P₁ and P₂:
```
P(t) = 0.5 * [
  (2*P₁) +
  (-P₀ + P₂) * t +
  (2*P₀ - 5*P₁ + 4*P₂ - P₃) * t² +
  (-P₀ + 3*P₁ - 3*P₂ + P₃) * t³
]
where t ∈ [0, 1]
```

**Parameters**:
- Resolution: 10-500 points per segment (user-controllable via "Curve Smoothness" slider)

---

## 5. Wire Smoothing

### File: `wire/wire_path_creator.py`

#### Algorithm: Multi-Stage Smoothing

**Purpose**: Eliminate sharp angles and create ultra-smooth, natural-looking wire curves.

### Stage 1: Physical Tension Simulation

**Concept**: Simulate real orthodontic wire behavior under tension.

**Algorithm**:
```
For each interior point p_i:
  chord = p_{i+1} - p_{i-1}
  midpoint = p_{i-1} + chord / 2
  deviation = p_i - midpoint

  # Tension pulls wire toward straight line (chord)
  tension_adjustment = deviation * (1 - tension_factor)
  p_i_smoothed = p_i - tension_adjustment
```

**Effect**: Reduces sharp curvature while preserving overall path shape.

### Stage 2: Gaussian Smoothing

**Purpose**: Apply signal processing technique for ultra-smooth curves.

**Algorithm**: 1D Gaussian Filter

**Mathematical Foundation**:
- Gaussian kernel: `G(x) = (1/√(2πσ²)) * exp(-x²/(2σ²))`
- Convolution applied to each dimension (X, Y, Z) independently

**Implementation**:
```python
from scipy.ndimage import gaussian_filter1d

for dim in [X, Y, Z]:
    smoothed[:, dim] = gaussian_filter1d(
        path[:, dim],
        sigma=2.0,
        mode='nearest'  # Preserve endpoints
    )
```

**Parameters**:
- Sigma (σ) = 2.0: Controls smoothness
  - Higher σ → smoother but may deviate from brackets
  - Lower σ → closer to brackets but less smooth

**Effect**: Removes high-frequency variations, creating flowing curves.

---

## 6. Offset Control

### File: `core/workflow_manager.py`

#### Algorithm: User-Controlled Wire Adjustments

**Purpose**: Allow precise control of wire position relative to teeth.

### Height Offset (Vertical - Up/Down)

**Algorithm**: Pure Z-axis translation
```
For each bracket position:
  adjusted_position = original_position + [0, 0, height_offset]
```

**Range**: -10mm to +10mm (unlimited via keyboard)

**Keyboard Control**:
- **I key**: +0.1mm (move UP)
- **K key**: -0.1mm (move DOWN)

### Anterior-Posterior Offset (Forward/Backward)

**Algorithm**: Pure Y-axis translation
```
For each bracket position:
  adjusted_position = original_position + [0, ap_offset, 0]
```

**Range**: -10mm to +10mm (unlimited via keyboard)

**Keyboard Control**:
- **L key**: +0.1mm (move BACKWARD)
- **J key**: -0.1mm (move FORWARD)

**Note**: Offsets are applied BEFORE wire path generation, so the entire smooth curve shifts accordingly.

---

## Mathematical Summary

### Key Equations

1. **Arch Curve (Parabolic)**:
   ```
   y = ax² + bx + c
   ```

2. **Catmull-Rom Spline**:
   ```
   P(t) = 0.5 * [2P₁ + (-P₀+P₂)t + (2P₀-5P₁+4P₂-P₃)t² + (-P₀+3P₁-3P₂+P₃)t³]
   ```

3. **Gaussian Smoothing**:
   ```
   G(x) = (1/√(2πσ²)) * exp(-x²/(2σ²))
   ```

4. **Wire Tension**:
   ```
   p'ᵢ = pᵢ - (pᵢ - midpoint(pᵢ₋₁, pᵢ₊₁)) * (1 - tension_factor)
   ```

---

## Computational Complexity

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Mesh Loading | O(V + F) | O(V + F) |
| Tooth Detection | O(V) | O(V) |
| Bracket Positioning | O(V * T) | O(T) |
| Arch Curve Fitting | O(T²) | O(T) |
| Intermediate Points | O(T) | O(T) |
| Catmull-Rom Spline | O(T * R) | O(T * R) |
| Gaussian Smoothing | O(T * R * σ) | O(T * R) |

Where:
- V = number of vertices in mesh (~200,000)
- F = number of faces (~400,000)
- T = number of teeth (14-16)
- R = resolution (points per segment, 10-500)
- σ = Gaussian kernel size

**Total**: O(V + T*R*σ) ≈ O(200,000 + 16*100*5) ≈ **O(208,000)** operations

**Runtime**: ~0.5-2 seconds on modern hardware

---

## References

### Implemented Algorithms
1. **Catmull-Rom Splines** (1974) - Edwin Catmull, Raphael Rom
2. **Gaussian Filtering** - Signal Processing Theory
3. **Least-Squares Polynomial Fitting** - Carl Friedrich Gauss
4. **Angular Segmentation** - Computational Geometry

### Libraries Used
- **Open3D**: 3D mesh processing
- **NumPy**: Numerical computations
- **SciPy**: Scientific computing (interpolation, filtering)
- **PyVista**: 3D visualization

---

## Future Enhancements

### Planned Improvements
1. **Collision Detection**: Detect wire-tooth intersections
2. **Physics-Based Simulation**: Finite element analysis for wire stress
3. **Machine Learning**: Train neural network on expert-designed wires
4. **Multi-Wire Optimization**: Generate sequential treatment wires

---

*Last Updated: 2025-01-12*
*Version: 2.0.0*
