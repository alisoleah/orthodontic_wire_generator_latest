"""
PyVista-based 3D visualizer with interactive point picking.
Replaces the DualArchVisualizer with PyVista's QtInteractor.
"""

import numpy as np
import pyvista as pv
import pyvistaqt as pvqt
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from typing import Optional, List
import open3d as o3d


class PyVistaVisualizer(QWidget):
    """
    PyVista-based 3D visualizer with built-in point picking.
    This is a QWidget so it can be added directly to layouts.
    """
    
    # Signals for communication with main window
    point_added = pyqtSignal(np.ndarray, str)  # (point, type) - for compatibility
    point_moved = pyqtSignal(int, np.ndarray)  # (index, new_position)
    interaction_mode_changed = pyqtSignal(str)  # mode name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create layout for this widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create PyVista plotter that embeds in PyQt5
        self.plotter = pvqt.QtInteractor(self)
        layout.addWidget(self.plotter.interactor)
        
        # State management
        self.selected_points = []
        self.point_spheres = []
        self.mesh_actor = None
        self.wire_actor = None
        self.picking_enabled = False
        self.current_arch = 'upper'
        self.show_both_arches = False
        
        # Store meshes for both arches
        self.upper_mesh = None
        self.lower_mesh = None
        
        # Control points and wire path (per-arch)
        self.control_points = []
        self.wire_path = None
        self.detected_teeth = []
        self.bracket_positions = []

        # Store wire paths for both arches
        self.upper_wire = None
        self.lower_wire = None
        
        # Visualization settings
        self.plotter.set_background('white')
        self.plotter.add_axes()
        
        # Add initial instructions
        self.plotter.add_text(
            "Load a dental arch STL to begin",
            position='upper_left',
            font_size=12,
            color='gray',
            name='instructions'
        )
    
    def load_arch(self, o3d_mesh: o3d.geometry.TriangleMesh, arch_type: str = 'upper'):
        """Load and display an Open3D mesh."""
        # Convert Open3D mesh to PyVista format
        pv_mesh = self._open3d_to_pyvista(o3d_mesh)
        
        # Store mesh
        if arch_type == 'upper':
            self.upper_mesh = pv_mesh
        else:
            self.lower_mesh = pv_mesh
        
        # Remove previous mesh if exists
        try:
            self.plotter.remove_actor(f'{arch_type}_arch')
        except:
            pass
        
        # Add mesh to scene
        color = 'tan' if arch_type == 'upper' else 'lightblue'
        self.mesh_actor = self.plotter.add_mesh(
            pv_mesh,
            color=color,
            show_edges=True,
            pickable=True,
            name=f'{arch_type}_arch',
            opacity=1.0 if arch_type == self.current_arch else 0.3
        )
        
        self.plotter.reset_camera()
        
        # Update instructions
        self.plotter.add_text(
            "Mesh loaded! Ready for 3-point selection",
            position='upper_left',
            font_size=12,
            color='green',
            name='instructions'
        )
    
    def set_active_arch(self, arch_type: str):
        """Set which arch is active for editing."""
        self.current_arch = arch_type
        
        # Update visibility/opacity
        if self.upper_mesh:
            try:
                self.plotter.remove_actor('upper_arch')
                self.plotter.add_mesh(
                    self.upper_mesh,
                    color='tan',
                    show_edges=True,
                    pickable=(arch_type == 'upper'),
                    name='upper_arch',
                    opacity=1.0 if arch_type == 'upper' else 0.3
                )
            except:
                pass
        
        if self.lower_mesh:
            try:
                self.plotter.remove_actor('lower_arch')
                self.plotter.add_mesh(
                    self.lower_mesh,
                    color='lightblue',
                    show_edges=True,
                    pickable=(arch_type == 'lower'),
                    name='lower_arch',
                    opacity=1.0 if arch_type == 'lower' else 0.3
                )
            except:
                pass
    
    def set_show_both_arches(self, show_both: bool):
        """Toggle showing both arches simultaneously."""
        self.show_both_arches = show_both
        
        if show_both:
            # Make both visible
            if self.upper_mesh:
                try:
                    self.plotter.remove_actor('upper_arch')
                    self.plotter.add_mesh(
                        self.upper_mesh,
                        color='tan',
                        show_edges=True,
                        pickable=(self.current_arch == 'upper'),
                        name='upper_arch',
                        opacity=0.7
                    )
                except:
                    pass
            
            if self.lower_mesh:
                try:
                    self.plotter.remove_actor('lower_arch')
                    self.plotter.add_mesh(
                        self.lower_mesh,
                        color='lightblue',
                        show_edges=True,
                        pickable=(self.current_arch == 'lower'),
                        name='lower_arch',
                        opacity=0.7
                    )
                except:
                    pass
        else:
            # Only show active arch
            self.set_active_arch(self.current_arch)
    
    def enable_point_picking(self, num_points: int = 3):
        """
        Enable interactive point picking on the mesh.
        This is THE KEY FEATURE that makes PyVista superior to Open3D+Tkinter.
        """
        self.selected_points = []
        self.point_spheres = []
        self.picking_enabled = True
        
        # Clear any existing point markers
        for i in range(3):
            try:
                self.plotter.remove_actor(f'point_{i}')
                self.plotter.remove_actor(f'label_{i}')
            except:
                pass
        
        try:
            self.plotter.remove_actor('reference_plane')
        except:
            pass
        
        # Disable any previous picking first
        try:
            self.plotter.disable_picking()
        except:
            pass
        
        # Enable PyVista's built-in point picking
        # THIS IS THE MAGIC - no platform-specific hacks needed!
        self.plotter.enable_point_picking(
            callback=self._on_point_picked,
            use_picker='point',  # Use point picker specifically
            show_message=f"Right-click on mesh to select points (0/{num_points})",
            pickable_window=False,
            color='yellow',  # Color of temporary pick indicator
            point_size=10
        )
        
        # Update instructions
        self.plotter.add_text(
            f"Right-click to select points (0/{num_points})",
            position='upper_left',
            font_size=14,
            color='blue',
            name='instructions'
        )
        
        # Emit mode change
        self.interaction_mode_changed.emit('PLACE_POINTS')
    def _on_point_picked(self, point, picker=None):
        """
        Callback when user picks a point - called by PyVista automatically.
        
        Args:
            point: The 3D coordinates of the picked point (numpy array)
            picker: The picker object (optional, provided by PyVista)
        """
        if not self.picking_enabled or len(self.selected_points) >= 3:
            return
        
        # Rest of the method stays the same...
        self.selected_points.append(point)
        idx = len(self.selected_points) - 1
        
        # Add visual marker
        colors = ['red', 'green', 'blue']
        sphere = pv.Sphere(radius=0.8, center=point)
        self.plotter.add_mesh(
            sphere,
            color=colors[idx],
            name=f'point_{idx}'
        )
        
        # Add label
        self.plotter.add_point_labels(
            [point],
            [f"P{idx+1}"],
            point_size=20,
            font_size=24,
            name=f'label_{idx}'
        )
        
        # Update instructions
        n = len(self.selected_points)
        self.plotter.add_text(
            f"Right-click to select points ({n}/3)",
            position='upper_left',
            font_size=14,
            color='blue',
            name='instructions'
        )
        
        # Emit signal for main window - use 'control' type for compatibility
        self.point_added.emit(point, 'control')
        
        # If 3 points selected, finalize
        if n == 3:
            self.plotter.disable_picking()
            self.picking_enabled = False
            self._validate_plane()
        
    def _validate_plane(self):
        """Validate that 3 points form a proper plane."""
        p1, p2, p3 = self.selected_points
        
        # Check for colinearity
        v1 = p2 - p1
        v2 = p3 - p1
        cross = np.cross(v1, v2)
        magnitude = np.linalg.norm(cross)
        
        if magnitude < 1e-6:
            # Points are colinear - invalid
            self.plotter.add_text(
                "⚠️ Points are colinear! Please select again.",
                position='upper_left',
                font_size=14,
                color='red',
                name='instructions'
            )
            self.clear_selected_points()
            return
        
        # Calculate plane parameters
        normal = cross / magnitude
        center = np.mean(self.selected_points, axis=0)
        
        # Visualize the plane
        self._show_plane(center, normal)
        
        # Update instructions
        self.plotter.add_text(
            "✓ Plane defined! Ready to generate wire",
            position='upper_left',
            font_size=12,
            color='green',
            name='instructions'
        )
        
        # Store control points
        self.control_points = [p.copy() for p in self.selected_points]
        
        # Emit mode change back to view
        self.interaction_mode_changed.emit('VIEW')
    
    def _show_plane(self, center, normal, size=20):
        """Visualize the defined plane."""
        try:
            self.plotter.remove_actor('reference_plane')
        except:
            pass
        
        plane = pv.Plane(
            center=center,
            direction=normal,
            i_size=size,
            j_size=size,
            i_resolution=2,
            j_resolution=2
        )
        
        self.plotter.add_mesh(
            plane,
            color='lightblue',
            opacity=0.3,
            name='reference_plane'
        )
    
    def clear_selected_points(self):
        """Clear all selected points and restart selection."""
        self.selected_points = []
        
        # Remove visual markers
        for i in range(3):
            try:
                self.plotter.remove_actor(f'point_{i}')
                self.plotter.remove_actor(f'label_{i}')
            except:
                pass
        
        try:
            self.plotter.remove_actor('reference_plane')
        except:
            pass
        
        # DON'T re-enable picking automatically - let the caller decide
        # This was causing the "Picking already enabled" error

    def clear_control_points(self):
        """Clear control points (compatibility method)."""
        self.control_points = []
        
        # Disable picking if active before clearing
        if self.picking_enabled:
            try:
                self.plotter.disable_picking()
                self.picking_enabled = False
            except:
                pass
        
        # Clear visual markers
        for i in range(3):
            try:
                self.plotter.remove_actor(f'point_{i}')
                self.plotter.remove_actor(f'label_{i}')
            except:
                pass
        
        try:
            self.plotter.remove_actor('reference_plane')
        except:
            pass
    
    def display_wire_path(self, wire_points: np.ndarray, arch_type: str = None):
        """Display the generated wire as a 3D line for specific arch."""
        if arch_type is None:
            arch_type = self.current_arch

        # Store wire for this arch
        if arch_type == 'upper':
            self.upper_wire = wire_points
        else:
            self.lower_wire = wire_points

        # Remove old wire for this arch
        wire_name = f'{arch_type}_wire'
        try:
            self.plotter.remove_actor(wire_name)
        except:
            pass

        if wire_points is None or len(wire_points) < 2:
            return

        # Store generic wire path for backward compatibility
        self.wire_path = wire_points

        # Create wire as polyline with arch-specific color
        wire_line = pv.lines_from_points(wire_points)
        wire_color = 'red' if arch_type == 'upper' else 'blue'

        self.wire_actor = self.plotter.add_mesh(
            wire_line,
            color=wire_color,
            line_width=5,
            name=wire_name
        )
    
    def display_editable_control_points(self, control_points: list):
        """Display control points for hybrid mode editing."""
        self.control_points = control_points
        
        # Remove old control point markers
        for i in range(len(control_points)):
            try:
                self.plotter.remove_actor(f'cp_{i}')
            except:
                pass
        
        # Add control point spheres
        for i, point in enumerate(control_points):
            sphere = pv.Sphere(radius=1.0, center=point)
            self.plotter.add_mesh(
                sphere,
                color='yellow',
                name=f'cp_{i}'
            )
    
    def set_interaction_mode(self, mode: str):
        """Set the interaction mode."""
        # Always disable picking first to avoid conflicts
        try:
            self.plotter.disable_picking()
            self.picking_enabled = False
        except:
            pass
        
        if mode == 'DEFINE_PLANE' or mode == 'PLACE_POINTS':
            self.enable_point_picking()
        elif mode == 'VIEW':
            # Already disabled above
            pass
        
        self.interaction_mode_changed.emit(mode)
    
    def set_jaw_rotation(self, angle: int):
        """Rotate the lower jaw (for occlusal simulation)."""
        if self.lower_mesh is None:
            return

        # Store original mesh if not already stored
        if not hasattr(self, 'original_lower_mesh'):
            self.original_lower_mesh = self.lower_mesh.copy()
            if self.lower_wire is not None:
                self.original_lower_wire = self.lower_wire.copy()

        # Get the bounds and compute hinge point from original mesh
        bounds = self.original_lower_mesh.bounds
        hinge_point = np.array([
            (bounds[0] + bounds[1]) / 2,  # Center in X (left-right)
            bounds[3],  # Back of jaw (max Y - anterior-posterior)
            bounds[4]   # Bottom of jaw (min Z - height)
        ])

        # Create rotated mesh from original
        rotated_mesh = self.original_lower_mesh.copy()
        rotated_mesh.translate(-hinge_point, inplace=True)
        rotated_mesh.rotate_x(angle, inplace=True)
        rotated_mesh.translate(hinge_point, inplace=True)

        # Update the lower arch
        try:
            self.plotter.remove_actor('lower_arch')
        except:
            pass

        color = 'lightblue'
        opacity = 1.0 if self.current_arch == 'lower' else 0.3
        self.plotter.add_mesh(
            rotated_mesh,
            color=color,
            show_edges=True,
            pickable=(self.current_arch == 'lower'),
            name='lower_arch',
            opacity=opacity
        )

        # Also rotate wire if present (wire is numpy array of points)
        if self.lower_wire is not None and hasattr(self, 'original_lower_wire'):
            # Rotate wire points using rotation matrix
            angle_rad = np.radians(angle)
            rotation_matrix = np.array([
                [1, 0, 0],
                [0, np.cos(angle_rad), -np.sin(angle_rad)],
                [0, np.sin(angle_rad), np.cos(angle_rad)]
            ])

            # Translate to origin, rotate, translate back
            rotated_wire_points = self.original_lower_wire.copy()
            rotated_wire_points -= hinge_point
            rotated_wire_points = rotated_wire_points @ rotation_matrix.T
            rotated_wire_points += hinge_point

            try:
                self.plotter.remove_actor('lower_wire')
            except:
                pass

            wire_line = pv.lines_from_points(rotated_wire_points)
            self.plotter.add_mesh(
                wire_line,
                color='blue',
                line_width=5,
                name='lower_wire'
            )

        self.plotter.render()
    
    def update(self):
        """Force update of the visualization."""
        self.plotter.render()
    
    def _open3d_to_pyvista(self, o3d_mesh: o3d.geometry.TriangleMesh) -> pv.PolyData:
        """Convert Open3D mesh to PyVista format."""
        vertices = np.asarray(o3d_mesh.vertices)
        triangles = np.asarray(o3d_mesh.triangles)
        
        # PyVista faces format: [3, idx1, idx2, idx3, 3, ...]
        faces = np.hstack([
            np.full((triangles.shape[0], 1), 3),
            triangles
        ]).flatten()
        
        pv_mesh = pv.PolyData(vertices, faces)
        
        # Transfer normals if present
        if o3d_mesh.has_vertex_normals():
            normals = np.asarray(o3d_mesh.vertex_normals)
            pv_mesh.point_data['normals'] = normals
        
        return pv_mesh
    
    def reset_camera(self):
        """Reset camera to default view."""
        self.plotter.reset_camera()