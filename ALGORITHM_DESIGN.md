# FIXR-Inspired Upper Tooth Surface Adaptation: Algorithm Design

## 1. Overview

This document provides a detailed technical design for the new upper tooth surface adaptation algorithm. It expands on the concepts outlined in the `FIXR_ADAPTATION_PROPOSAL.md` and provides a concrete plan for implementation.

## 2. System Architecture Changes

The new workflow will be orchestrated primarily within the `WireGenerator` class, with significant modifications to the `ToothDetector`, `BracketPositioner`, `WirePathCreatorEnhanced`, and `Visualizer3D` classes.

### 2.1. Data Structures

We will introduce a new data class to represent the clinically significant Facial Axis (FA) points.

```python
from dataclasses import dataclass
import numpy as np

@dataclass
class FAPoint:
    """Represents a Facial Axis (FA) point on a tooth's clinical crown."""
    tooth_number: int
    position: np.ndarray
    normal: np.ndarray
    is_upper: bool
```

### 2.2. Core Class Modifications

| Class | Method(s) to be Added/Modified | Purpose |
| :--- | :--- | :--- |
| **`ToothDetector`** | `identify_fa_points(teeth: List[Dict]) -> List[FAPoint]` | Identifies the FA point for each tooth. |
| **`WireGenerator`** | `_identify_fa_points()` <br> `_project_point_to_mesh(point: np.ndarray) -> np.ndarray` <br> `_handle_interactive_update(control_point_index, new_screen_pos)` | New core workflow methods. |
| **`WirePathCreatorEnhanced`** | `generate_surface_projected_arch(fa_points: List[FAPoint], mesh: o3d.geometry.TriangleMesh) -> np.ndarray` | Creates the initial arch curve projected onto the tooth surfaces. |
| **`Visualizer3D`** | `register_mouse_drag_callback(callback_function)` <br> `_on_mouse_drag(event)` | Enables interactive, surface-constrained manipulation of the arch curve. |

## 3. Detailed Algorithm Breakdown

### 3.1. Step 1: Anatomical Landmark (FA Point) Identification

This step replaces the old `_position_brackets` method.

**Class:** `ToothDetector`
**New Method:** `identify_fa_points(self, teeth: List[Dict], mesh: o3d.geometry.TriangleMesh) -> List[FAPoint]`

**Logic:**

1.  For each detected tooth in the `teeth` list:
2.  Isolate the tooth's mesh geometry.
3.  Calculate the geometric center of the tooth's buccal (outer) surface. A simple approach is to take the average of the vertices on the buccal side.
4.  Define this center point as the **Facial Axis (FA) point**.
5.  Calculate the surface normal at the FA point.
6.  Store the result as a `FAPoint` object.

### 3.2. Step 2: Generate Initial Surface-Projected Ideal Arch

**Class:** `WirePathCreatorEnhanced`
**New Method:** `generate_surface_projected_arch(self, fa_points: List[FAPoint], mesh: o3d.geometry.TriangleMesh) -> np.ndarray`

**Logic:**

1.  Use the `fa_points` to generate a smooth, fourth-order polynomial curve as a starting point (similar to the previous implementation).
2.  For each point along this initial polynomial curve:
3.  Project the point onto the main dental `mesh` using raycasting. The ray should be cast from the point towards the arch center.
4.  The new point will be the intersection of the ray and the mesh.
5.  The collection of these projected points forms the initial, surface-adapted ideal arch.

### 3.3. Step 3: Interactive, Surface-Constrained Design

This is the core interactive component.

**Class:** `Visualizer3D`
**New/Modified Methods:** `register_mouse_drag_callback`, `_on_mouse_drag`

**Logic:**

1.  In `run()`, register a new mouse drag callback function.
2.  The `_on_mouse_drag` callback will be triggered when the user clicks and drags in the 3D view.
3.  Inside the callback:
    a.  Get the current mouse screen coordinates.
    b.  If a control point is selected, un-project the screen coordinates to a 3D ray in the scene.
    c.  Perform a raycast from this ray against the main dental `mesh`.
    d.  If there is an intersection, move the selected control point to the 3D intersection point on the tooth surface.
    e.  Trigger an update in the `WireGenerator` to recalculate the ideal arch curve with the new control point position.
    f.  Update the wire mesh in the visualizer in real-time.

**Class:** `WireGenerator`
**New Method:** `_handle_interactive_update(...)`

**Logic:**

1.  This method is called by the `Visualizer3D` callback.
2.  It takes the updated control point position.
3.  It calls `wire_path_creator.generate_surface_projected_arch()` to get the new, updated arch path.
4.  It calls `wire_mesh_builder.build_wire_mesh()` to create the new wire mesh.
5.  It calls `visualizer.update_wire_mesh()` to refresh the display.

### 3.4. Step 4: Finalize Wire and Generate Mesh

This step is triggered by a user action (e.g., pressing a key).

**Class:** `WireGenerator`
**Modified Method:** `generate_wire()`

**Logic:**

1.  The main loop in `run()` will wait for a "finalize" event.
2.  Once triggered, the current `self.wire_path` (which has been interactively modified) is considered final.
3.  The final `self.wire_mesh` is generated and can be exported.

## 4. Implementation Plan

1.  **Implement `FAPoint` data class.**
2.  **Implement `identify_fa_points` in `ToothDetector`.**
3.  **Implement `generate_surface_projected_arch` in `WirePathCreatorEnhanced`.**
4.  **Implement mouse drag callbacks in `Visualizer3D`.**
5.  **Overhaul `WireGenerator` to use the new workflow.**
6.  **Thoroughly test the interactive design process.**

This design provides a clear and robust path to implementing a professional-grade, FIXR-inspired workflow for upper tooth surface adaptation.

