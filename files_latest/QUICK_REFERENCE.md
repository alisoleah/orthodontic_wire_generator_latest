# Quick Reference Card - Orthodontic Wire Generator

## Critical Algorithms (Copy-Paste Ready)

### 1. Arch Form Fitting (Core Algorithm)

```python
# Y = A·x^6 + B·x^2
def fit_arch_polynomial(points_2d):
    x, y = points_2d[:, 0], points_2d[:, 1]
    X_matrix = np.column_stack([x**6, x**2])
    coeffs, _, _, _ = np.linalg.lstsq(X_matrix, y, rcond=None)
    A, B = coeffs
    
    # Validate fit
    y_pred = A * x**6 + B * x**2
    r2 = 1 - np.sum((y - y_pred)**2) / np.sum((y - y.mean())**2)
    
    if r2 < 0.90:
        raise ValueError(f"Poor fit: R²={r2:.3f}")
    
    return A, B, r2
```

### 2. Arch Classification

```python
def classify_arch_form(A, B, width):
    x_canine = width / 4
    y_prime = 6 * A * x_canine**5 + 2 * B * x_canine
    y_double_prime = 30 * A * x_canine**4 + 2 * B
    kappa = abs(y_double_prime) / (1 + y_prime**2)**1.5
    
    if kappa > 0.15:
        return "SQUARE"
    elif kappa < 0.08:
        return "TAPERED"
    else:
        return "OVOID"
```

### 3. 3D Curve Construction

```python
from scipy.interpolate import CubicSpline

def construct_3d_curve(points_2d, z_coords, mode="anatomic"):
    # Arc length parameterization
    diff = np.diff(points_2d, axis=0)
    distances = np.sqrt(np.sum(diff**2, axis=1))
    arc_length = np.concatenate([[0], np.cumsum(distances)])
    
    # Z-processing
    if mode == "leveling":
        poly_coeffs = np.polyfit(arc_length, z_coords, deg=2)
        z_processed = np.polyval(poly_coeffs, arc_length)
    else:
        z_processed = z_coords
    
    # Cubic splines
    x_spline = CubicSpline(arc_length, points_2d[:, 0])
    y_spline = CubicSpline(arc_length, points_2d[:, 1])
    z_spline = CubicSpline(arc_length, z_processed)
    
    # Densify
    s_dense = np.linspace(0, arc_length[-1], num=len(points_2d) * 10)
    
    return np.column_stack([
        x_spline(s_dense),
        y_spline(s_dense),
        z_spline(s_dense)
    ])
```

### 4. Jaw Coordination (Maxilla from Mandible)

```python
def generate_maxillary_wire(mandibular_curve):
    maxillary_curve = []
    
    for i in range(len(mandibular_curve) - 1):
        P = mandibular_curve[i]
        P_next = mandibular_curve[i + 1]
        
        # Tangent vector
        tangent = (P_next - P) / np.linalg.norm(P_next - P)
        
        # Outward normal (in XY plane)
        normal_2d = np.array([-tangent[1], tangent[0], 0])
        
        # Variable offset: 3mm anterior → 1.5mm posterior
        s = i / len(mandibular_curve)
        offset = 3.0 - 1.5 * s
        
        # Offset point
        P_max = P + offset * normal_2d
        maxillary_curve.append(P_max)
    
    return np.array(maxillary_curve)
```

### 5. Frenet-Serret Frame (For XYZ→LRA)

```python
def compute_frenet_frame(points):
    n = len(points)
    T = np.zeros((n-1, 3))  # Tangent
    N = np.zeros((n-2, 3))  # Normal
    
    # Tangent
    for i in range(n-1):
        v = points[i+1] - points[i]
        T[i] = v / np.linalg.norm(v)
    
    # Normal (direction of turning)
    for i in range(n-2):
        dT = T[i+1] - T[i]
        dT_norm = np.linalg.norm(dT)
        
        if dT_norm < 1e-6:  # Straight section
            N[i] = N[i-1] if i > 0 else np.array([0, 0, 1])
        else:
            N[i] = dT / dT_norm
    
    return T, N
```

### 6. XYZ → LRA Conversion

```python
def xyz_to_lra(points, pin_radius=1.0):
    lra_commands = []
    
    for i in range(1, len(points) - 1):
        V_prev = points[i] - points[i-1]
        V_curr = points[i+1] - points[i]
        
        # Angle
        cos_angle = np.dot(V_prev, V_curr) / (
            np.linalg.norm(V_prev) * np.linalg.norm(V_curr)
        )
        angle = np.arccos(np.clip(cos_angle, -1, 1))
        
        # Rotation (dihedral angle)
        n_prev = np.cross(V_prev, points[i-1] - points[i-2])
        n_curr = np.cross(V_prev, V_curr)
        
        if np.linalg.norm(n_prev) < 1e-6 or np.linalg.norm(n_curr) < 1e-6:
            rotation = 0
        else:
            n_prev /= np.linalg.norm(n_prev)
            n_curr /= np.linalg.norm(n_curr)
            rotation = np.arctan2(
                np.linalg.norm(V_prev) * np.dot(n_prev, n_curr),
                np.dot(np.cross(n_prev, n_curr), V_prev)
            )
        
        # Length (with tangent compensation)
        tangent_dist = pin_radius * np.tan(angle / 2)
        length = np.linalg.norm(V_prev) - 2 * tangent_dist
        
        lra_commands.append((
            length,
            np.degrees(rotation),
            np.degrees(angle)
        ))
    
    return lra_commands
```

### 7. Material Springback Compensation

```python
from scipy.interpolate import CubicSpline

# Material database structure
material_db = {
    "SS_016": {
        "calibration": [[10, 11], [45, 50], [90, 98], [180, 190]]
    },
    "NiTi_016": {
        "calibration": [[10, 14], [45, 65], [90, 125], [180, 220]]
    }
}

def compensate_springback(material, target_angle):
    calib = np.array(material_db[material]["calibration"])
    target_vals = calib[:, 0]
    machine_vals = calib[:, 1]
    
    spline = CubicSpline(target_vals, machine_vals)
    return float(spline(target_angle))
```

### 8. Collision Detection (OBB-Tree)

```python
import trimesh

def check_collision(wire_curve, gingiva_mesh, wire_diameter=0.4):
    manager = trimesh.collision.CollisionManager()
    manager.add_object('gingiva', gingiva_mesh)
    
    collision_points = []
    
    for i in range(len(wire_curve) - 1):
        P1, P2 = wire_curve[i], wire_curve[i+1]
        
        # Create cylinder segment
        height = np.linalg.norm(P2 - P1)
        cylinder = trimesh.creation.cylinder(
            radius=wire_diameter/2,
            height=height
        )
        
        # Transform to position
        # ... transformation matrix ...
        
        if manager.in_collision_single(cylinder):
            collision_points.append(i)
    
    return len(collision_points) == 0, collision_points
```

### 9. G-Code Generation

```python
def generate_gcode(lra_commands, material="SS_016"):
    gcode = [
        "G21 ; Millimeters",
        "G90 ; Absolute positioning",
        ""
    ]
    
    for i, (length, rotation, angle) in enumerate(lra_commands):
        # Apply material compensation
        angle_compensated = compensate_springback(material, angle)
        
        gcode.extend([
            f"; Bend {i+1}",
            f"G1 Y{length:.3f} F500",
            f"G1 A{rotation:.3f} F100",
            f"G1 C{angle_compensated:.3f} F50",
            ""
        ])
    
    return "\n".join(gcode)
```

---

## Decision Trees

### Which Mathematical Model?

```
Need to fit arch form?
├─ For research/publication → Beta Function
│   └─ More accurate but slower
└─ For production/clinical → 6th Order Polynomial
    └─ 97%+ accuracy, much faster
```

### Which Interpolation Mode?

```
Generating 3D curve?
├─ Initial alignment wire → "anatomic"
│   └─ Wire follows teeth exactly
└─ Treatment progression → "leveling"
    └─ Wire smooths irregularities
```

### Which Jaw First?

```
Always generate mandible FIRST
├─ Mandible = single bone (fixed)
├─ Maxilla = derived from mandible
└─ Offset: 3mm at canines → 1.5mm at molars
```

---

## Common Pitfalls & Solutions

### Problem: R² < 0.90 (Poor Fit)

**Causes:**
- Bracket positions contain errors
- Severe malocclusion
- Wrong coordinate system

**Solution:**
```python
# 1. Check for duplicate points
unique_points = np.unique(points_2d, axis=0)

# 2. Check coordinate range (should be ±30mm max)
assert np.max(np.abs(points_2d)) < 50, "Coordinates out of range"

# 3. Plot raw data
plt.scatter(points_2d[:, 0], points_2d[:, 1])
plt.show()  # Visual inspection
```

### Problem: NaN in LRA Conversion

**Cause:** Division by zero when wire is straight

**Solution:**
```python
# Add epsilon threshold
if bend_angle < 1e-6:  # Essentially straight
    rotation = 0
    continue  # Skip this bend
```

### Problem: Negative Feed Length

**Cause:** Bends too close together

**Solution:**
```python
if length < 0:
    # Merge with previous bend
    # Or flag error to user
    raise ValueError(f"Bends at position {i} too close. Min spacing: 3mm")
```

### Problem: Wire Collides with Gums

**Cause:** Loop too low or arch too narrow

**Solution:**
```python
# Automatically lift loops
if collision_detected:
    curve_3d[:, 2] += 2.0  # Raise Z by 2mm
    # Re-check collision
```

---

## Performance Benchmarks

| Operation | Target Time | Typical Time | Status |
|-----------|-------------|--------------|--------|
| Polynomial Fit | <0.1s | 0.02s | ✓ |
| 3D Curve Generation | <1s | 0.3s | ✓ |
| XYZ→LRA (500 pts) | <5s | TBD | - |
| Collision Check | <10s | TBD | - |
| Complete Pipeline | <30s | TBD | - |

---

## File Organization Quick Ref

```
Key Files (Edit These):
├─ src/ortho_wire/core/arch_modeling.py       → Polynomial fitting
├─ src/ortho_wire/core/curve_construction.py  → 3D curves
├─ src/ortho_wire/core/jaw_coordination.py    → Maxilla generation
├─ src/ortho_wire/kinematics/xyz_to_lra.py    → Machine commands
└─ src/ortho_wire/materials/springback.py     → Compensation

Key Tests (Run These):
├─ tests/unit/test_arch_modeling.py
├─ tests/unit/test_curve_construction.py
└─ tests/integration/test_end_to_end.py

Key Data (Configure These):
└─ data/calibration/material_database.json
```

---

## Git Workflow

```bash
# Daily workflow
git checkout -b feature/day-X-module-name
# ... make changes ...
pytest tests/ -v  # All tests must pass
git add .
git commit -m "feat: implement module X with tests"
git push origin feature/day-X-module-name

# Weekly
git checkout main
git merge feature/day-X-module-name
git tag v0.1.X  # Version increment
```

---

## When to Ask for Help

**Red Flags (Stop and Ask):**
- Test failures you can't debug after 30 min
- Math producing NaN/Inf values
- Don't understand a concept from the research paper
- Code works but you're not sure why
- Performance >10x slower than target

**Show Me:**
1. The error message (full traceback)
2. The input data that causes it
3. What you've tried so far

**Don't Waste Time:**
- Guessing at random fixes
- Copying code without understanding
- Skipping tests "to save time"

---

## Success Metrics (Phase 1)

Before claiming "Phase 1 Complete":

```bash
# Run full test suite
pytest tests/ -v --cov=ortho_wire --cov-report=html

# Check coverage
open htmlcov/index.html
# Should see >95% coverage for arch_modeling and curve_construction

# Check all arch types
pytest tests/integration/ -v -s
# Should see PASSED for square, ovoid, tapered

# Run self-tests
python -m ortho_wire.core.arch_modeling
python -m ortho_wire.core.curve_construction
# Should see "✓ All self-tests passed"
```

**Only move to Phase 2 when ALL these pass.**

---

## Emergency Debugging Commands

```bash
# Find function definition
grep -r "def function_name" src/

# See what's imported
python -c "from ortho_wire.core import arch_modeling; print(dir(arch_modeling))"

# Interactive testing
python
>>> from ortho_wire.core.arch_modeling import *
>>> points = np.load('tests/fixtures/square_points_2d.npy')
>>> arch = create_arch_form(points)
>>> print(arch)

# Profile slow code
python -m cProfile -s cumtime script.py

# Check dependencies
pip list | grep -E "numpy|scipy|trimesh"
```

---

## Contact Info

**Questions? Stuck?**
- Show me the code + error
- I'll debug it with you
- No question is too basic

**Remember:**
- Professional code = tested code
- One module at a time
- Tests pass before moving on
- Commit often

---

**Print this card. Keep it next to your keyboard.**
