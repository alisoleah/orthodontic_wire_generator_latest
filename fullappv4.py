#!/usr/bin/env python3
"""
Enhanced Interactive Orthodontic Wire Generator GUI with Height Control
======================================================================
Added wire height adjustment via arrow keys and mouse dragging
MODIFIED: Hides bracket boxes, control points, and coordinate frame in the visualization.
"""

# --- Imports (from both files) ---
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import numpy as np
import open3d as o3d
import os
from scipy import interpolate, signal
from scipy.spatial import distance_matrix, KDTree
import json
import time
from typing import List, Dict, Tuple, Optional
import math
import threading
from pathlib import Path

# --- Enhanced Wire Generator with Height Control ---

class EnhancedInteractiveWireGenerator:
    """Enhanced interactive lingual orthodontic wire generator with height control."""
    
    # Standard wire dimensions (in inches, converted to mm)
    WIRE_SIZES = {
        '0.012': 0.3048,
        '0.014': 0.3556,
        '0.016': 0.4064,
        '0.018': 0.4572,
        '0.020': 0.5080,
        '0.016x0.022': (0.4064, 0.5588),
        '0.018x0.025': (0.4572, 0.6350),
        '0.019x0.025': (0.4826, 0.6350),
        '0.021x0.025': (0.5334, 0.6350)
    }
    
    def __init__(self, stl_path: str, arch_type: str = 'auto', wire_size: str = '0.018'):
        """Initialize the enhanced wire generator."""
        self.stl_path = stl_path
        self.wire_size = wire_size
        self.wire_radius = self.WIRE_SIZES.get(wire_size, 0.4572) / 2
        
        # Detect arch type
        if arch_type == 'auto':
            self.arch_type = 'lower' if 'lower' in stl_path.lower() else 'upper'
        else:
            self.arch_type = arch_type
            
        # Core data structures
        self.mesh = None
        self.teeth = []
        self.bracket_positions = []
        self.wire_path = []
        self.wire_control_points = []
        
        # Interactive components
        self.vis = None
        self.bracket_meshes = []
        self.wire_mesh = None
        self.control_point_meshes = []
        self.selected_control_point = None
        self.is_editing = False
        
        # Wire bending parameters
        self.bend_radius = 2.0  # mm
        self.bend_tolerance = 0.1  # mm
        self.wire_tension = 1.0
        
        # NEW: Wire height control
        self.wire_height_offset = 0.0  # Global height offset for entire wire
        self.height_adjustment_step = 0.5  # mm per adjustment
        self.is_dragging_wire = False
        self.last_mouse_y = 0
        
        # G-code parameters
        self.gcode_settings = {
            'feed_rate': 1000,
            'bend_speed': 500,
            'home_position': [0, 0, 0],
            'wire_clamp_position': [10, 0, 0],
            'bend_positions': [],
            'safety_height': 10.0,
        }
        
        # Anatomical axes
        self.lr_axis = None
        self.ap_axis = None
        self.height_axis = None
        
        print(f"\n{'='*70}")
        print("ENHANCED INTERACTIVE ORTHODONTIC WIRE GENERATOR")
        print("WITH HEIGHT CONTROL AND G-CODE GENERATION")
        print(f"{'='*70}")
    
    def load_mesh(self) -> bool:
        """Load and preprocess the dental STL mesh."""
        print(f"\n{'─'*50}")
        print("LOADING DENTAL MODEL")
        print(f"{'─'*50}")
        print(f"File: {os.path.basename(self.stl_path)}")
        print(f"Arch Type: {self.arch_type.upper()}")
        print(f"Wire Size: {self.wire_size}")
        print(f"Wire Position: LINGUAL (Inner/Tongue Side)")
        
        try:
            self.mesh = o3d.io.read_triangle_mesh(self.stl_path)
            if not self.mesh.has_triangles():
                raise ValueError("No triangles found in mesh")
            
            # Clean and prepare mesh
            self.mesh.remove_duplicated_vertices()
            self.mesh.remove_degenerate_triangles()
            self.mesh.compute_vertex_normals()
            self.mesh.compute_triangle_normals()
            
            # Natural tooth color
            self.mesh.paint_uniform_color([0.95, 0.93, 0.88])
            
            print(f"✓ Loaded: {len(self.mesh.vertices)} vertices, {len(self.mesh.triangles)} triangles")
            return True
            
        except Exception as e:
            print(f"✗ Error loading mesh: {e}")
            return False
    
    def detect_teeth_simple(self):
        """Simple but reliable tooth detection method."""
        print(f"\n{'─'*50}")
        print("TOOTH DETECTION")
        print(f"{'─'*50}")
        
        vertices = np.asarray(self.mesh.vertices)
        bbox = self.mesh.get_axis_aligned_bounding_box()
        center = self.mesh.get_center()
        extent = bbox.get_extent()
        
        # Identify anatomical axes
        self.lr_axis = np.argmax(extent)  # Left-Right (widest)
        self.height_axis = np.argmin(extent)  # Occlusal-Gingival (smallest)
        self.ap_axis = 3 - self.lr_axis - self.height_axis  # Anterior-Posterior
        
        print(f"Anatomical axes identified:")
        print(f"  • Left-Right axis: {self.lr_axis}")
        print(f"  • Anterior-Posterior axis: {self.ap_axis}")
        print(f"  • Occlusal-Gingival axis: {self.height_axis}")
        
        # Sample at crown level
        crown_ratio = 0.25 if self.arch_type == 'upper' else 0.75
        crown_level = bbox.min_bound[self.height_axis] + extent[self.height_axis] * crown_ratio
        
        # Get crown vertices
        height_tolerance = max(2.0, extent[self.height_axis] * 0.15)
        crown_mask = np.abs(vertices[:, self.height_axis] - crown_level) < height_tolerance
        crown_vertices = vertices[crown_mask]
        
        print(f"Crown level: {crown_level:.1f}mm")
        print(f"Vertices at crown: {len(crown_vertices)}")
        
        # Simple angular segmentation
        self.teeth = self._simple_angular_segmentation(crown_vertices, center)
        
        # Apply classification
        self._apply_simple_classification()
        
        print(f"\nDetected {len(self.teeth)} teeth")
        
        return len(self.teeth) >= 6
    
    def _simple_angular_segmentation(self, crown_vertices, center):
        """Simple angular segmentation to find teeth."""
        # Calculate angles
        angles = np.arctan2(
            crown_vertices[:, self.ap_axis] - center[self.ap_axis],
            crown_vertices[:, self.lr_axis] - center[self.lr_axis]
        )
        
        # Find posterior gap
        sorted_angles = np.sort(angles)
        angle_diffs = np.diff(sorted_angles)
        angle_diffs = np.append(angle_diffs, sorted_angles[0] + 2*np.pi - sorted_angles[-1])
        
        posterior_gap_idx = np.argmax(angle_diffs)
        posterior_gap_size = angle_diffs[posterior_gap_idx]
        
        # Define segments
        expected_teeth = 14
        active_angle_range = 2 * np.pi - posterior_gap_size
        angle_per_tooth = active_angle_range / expected_teeth
        start_angle = sorted_angles[(posterior_gap_idx + 1) % len(sorted_angles)]
        
        teeth = []
        for i in range(expected_teeth + 2):
            tooth_start = start_angle + i * angle_per_tooth
            tooth_end = tooth_start + angle_per_tooth
            
            # Normalize angles
            tooth_start = np.mod(tooth_start + np.pi, 2*np.pi) - np.pi
            tooth_end = np.mod(tooth_end + np.pi, 2*np.pi) - np.pi
            
            # Get vertices in segment
            if tooth_start < tooth_end:
                angle_mask = (angles >= tooth_start) & (angles < tooth_end)
            else:
                angle_mask = (angles >= tooth_start) | (angles < tooth_end)
            
            segment_vertices = crown_vertices[angle_mask]
            
            if len(segment_vertices) < 30:
                continue
            
            # Calculate tooth center
            tooth_center = np.mean(segment_vertices, axis=0)
            
            tooth_angle = np.arctan2(
                tooth_center[self.ap_axis] - center[self.ap_axis],
                tooth_center[self.lr_axis] - center[self.lr_axis]
            )
            
            teeth.append({
                'center': tooth_center,
                'vertices': segment_vertices,
                'angle': tooth_angle,
                'ap_position': tooth_center[self.ap_axis],
                'lr_position': tooth_center[self.lr_axis],
                'index': len(teeth),
                'type': 'posterior'
            })
        
        # Filter too-close teeth
        filtered_teeth = []
        sorted_teeth = sorted(teeth, key=lambda t: t['angle'])
        
        for i, tooth in enumerate(sorted_teeth):
            if i == 0:
                filtered_teeth.append(tooth)
            else:
                prev_tooth = filtered_teeth[-1]
                dist = np.linalg.norm(tooth['center'] - prev_tooth['center'])
                if dist > 3.0:
                    filtered_teeth.append(tooth)
        
        return filtered_teeth
    
    def _apply_simple_classification(self):
        """Classify teeth into incisors, canines, and posterior."""
        print(f"\n{'─'*40}")
        print("TOOTH CLASSIFICATION")
        print(f"{'─'*40}")
        
        if len(self.teeth) < 6:
            print("Not enough teeth for classification")
            return
        
        # Reset all to posterior
        for tooth in self.teeth:
            tooth['type'] = 'posterior'
        
        # Sort by anterior position
        teeth_by_ap = sorted(self.teeth, key=lambda t: t['ap_position'], reverse=True)
        
        # Take the 6 most anterior teeth
        anterior_6 = teeth_by_ap[:6]
        
        # Sort by left-right position
        anterior_6_by_lr = sorted(anterior_6, key=lambda t: t['lr_position'])
        
        # Assign types
        if len(anterior_6_by_lr) >= 6:
            # Canines (outermost)
            anterior_6_by_lr[0]['type'] = 'canine'
            anterior_6_by_lr[5]['type'] = 'canine'
            
            # Incisors (inner 4)
            for i in range(1, 5):
                anterior_6_by_lr[i]['type'] = 'incisor'
        
        # Count types
        incisor_count = sum(1 for t in self.teeth if t['type'] == 'incisor')
        canine_count = sum(1 for t in self.teeth if t['type'] == 'canine')
        posterior_count = sum(1 for t in self.teeth if t['type'] == 'posterior')
        
        print(f"Classification result:")
        print(f"  • Incisors: {incisor_count}")
        print(f"  • Canines: {canine_count}")
        print(f"  • Posterior: {posterior_count}")
    
    def calculate_lingual_bracket_positions(self):
        """Calculate bracket positions on lingual surface."""
        print(f"\n{'─'*50}")
        print("LINGUAL BRACKET POSITIONING")
        print(f"{'─'*50}")
        
        self.bracket_positions = []
        mesh_center = self.mesh.get_center()
        
        for i, tooth in enumerate(self.teeth):
            # Bracket height based on tooth type
            if tooth['type'] == 'incisor':
                bracket_height = 3.5
            elif tooth['type'] == 'canine':
                bracket_height = 4.0
            else:
                bracket_height = 4.5
            
            tooth_vertices = tooth['vertices']
            tooth_center = tooth['center']
            
            # Calculate target height
            if self.arch_type == 'upper':
                target_height = np.min(tooth_vertices[:, self.height_axis]) + bracket_height
            else:
                target_height = np.max(tooth_vertices[:, self.height_axis]) - bracket_height
            
            # Get vertices at bracket level
            height_tolerance = 2.0
            bracket_level_mask = np.abs(tooth_vertices[:, self.height_axis] - target_height) < height_tolerance
            bracket_level_vertices = tooth_vertices[bracket_level_mask]
            
            if len(bracket_level_vertices) < 10:
                bracket_pos = tooth_center.copy()
                bracket_pos[self.height_axis] = target_height
                
                # Inward direction for lingual
                horizontal_vector = bracket_pos - mesh_center
                horizontal_vector[self.height_axis] = 0
                if np.linalg.norm(horizontal_vector) > 0:
                    inward_normal = -horizontal_vector / np.linalg.norm(horizontal_vector)
                else:
                    inward_normal = np.array([0, -1, 0])
            else:
                # Find innermost vertices (lingual side)
                tooth_horizontal = tooth_center.copy()
                tooth_horizontal[self.height_axis] = 0
                center_horizontal = mesh_center.copy()
                center_horizontal[self.height_axis] = 0
                
                radial_vector = tooth_horizontal - center_horizontal
                if np.linalg.norm(radial_vector) > 0:
                    radial_direction = radial_vector / np.linalg.norm(radial_vector)
                else:
                    radial_direction = np.array([1, 0, 0])
                
                # Project vertices
                radial_distances = []
                for vertex in bracket_level_vertices:
                    vertex_horizontal = vertex.copy()
                    vertex_horizontal[self.height_axis] = 0
                    vertex_radial = vertex_horizontal - center_horizontal
                    radial_dist = np.dot(vertex_radial, radial_direction)
                    radial_distances.append(radial_dist)
                
                radial_distances = np.array(radial_distances)
                
                # Get lingual vertices (15th percentile = innermost)
                percentile_15 = np.percentile(radial_distances, 15)
                lingual_mask = radial_distances <= percentile_15
                lingual_vertices = bracket_level_vertices[lingual_mask]
                
                if len(lingual_vertices) > 3:
                    bracket_pos = np.mean(lingual_vertices, axis=0)
                else:
                    bracket_pos = bracket_level_vertices[np.argmin(radial_distances)]
                
                inward_normal = -radial_direction.copy()
            
            # Apply clinical offset
            clinical_offset = 2.0
            bracket_pos = bracket_pos + inward_normal * clinical_offset
            
            # Determine visibility (only posterior teeth get brackets in this example)
            visible = tooth['type'] == 'posterior'
            
            # Store bracket
            self.bracket_positions.append({
                'position': bracket_pos,
                'tooth_type': tooth['type'],
                'tooth_index': i,
                'tooth_center': tooth_center,
                'normal': inward_normal,
                'height': bracket_height,
                'surface': 'lingual',
                'visible': visible,
                'original_position': bracket_pos.copy()
            })
        
        print(f"✓ Positioned {len(self.bracket_positions)} LINGUAL brackets")
        visible_count = sum(1 for b in self.bracket_positions if b['visible'])
        print(f"  • Visible brackets: {visible_count}")
    
    def create_smooth_wire_path_with_control_points(self):
        """Create smooth wire path with interactive control points."""
        print(f"\n{'─'*50}")
        print("WIRE PATH GENERATION WITH CONTROL POINTS")
        print(f"{'─'*50}")
        
        if not self.bracket_positions:
            return None
        
        # Get only visible bracket positions
        visible_brackets = [b for b in self.bracket_positions if b['visible']]
        
        if len(visible_brackets) < 2:
            print("Not enough visible brackets for wire")
            return None
        
        # Extract positions and sort by angle
        positions = np.array([b['position'] for b in visible_brackets])
        mesh_center = self.mesh.get_center()
        
        angles = []
        for pos in positions:
            angle = np.arctan2(
                pos[self.ap_axis] - mesh_center[self.ap_axis],
                pos[self.lr_axis] - mesh_center[self.lr_axis]
            )
            angles.append(angle)
        
        sorted_indices = np.argsort(angles)
        sorted_positions = positions[sorted_indices]
        
        # Create control points at bracket positions and midpoints
        self.wire_control_points = []
        
        # Add bracket positions as control points
        for i, pos in enumerate(sorted_positions):
            self.wire_control_points.append({
                'position': pos.copy(),
                'type': 'bracket',
                'index': i,
                'original_position': pos.copy(),
                'bend_angle': 0.0,
                'vertical_offset': 0.0
            })
        
        # Add midpoint control points for wire shaping
        for i in range(len(sorted_positions) - 1):
            midpoint = (sorted_positions[i] + sorted_positions[i + 1]) / 2
            # Slightly offset inward for natural wire curve
            direction_to_center = mesh_center - midpoint
            direction_to_center[self.height_axis] = 0
            if np.linalg.norm(direction_to_center) > 0:
                direction_to_center = direction_to_center / np.linalg.norm(direction_to_center)
                midpoint += direction_to_center * 1.0  # 1mm inward offset
            
            self.wire_control_points.append({
                'position': midpoint,
                'type': 'midpoint',
                'index': len(self.wire_control_points),
                'original_position': midpoint.copy(),
                'bend_angle': 0.0,
                'vertical_offset': 0.0
            })
        
        # Sort control points by angle for proper wire path
        self.wire_control_points.sort(key=lambda cp: np.arctan2(
            cp['position'][self.ap_axis] - mesh_center[self.ap_axis],
            cp['position'][self.lr_axis] - mesh_center[self.lr_axis]
        ))
        
        # Generate smooth wire path
        self._generate_smooth_wire_path()
        
        print(f"✓ Created {len(self.wire_control_points)} control points")
        print(f"✓ Generated wire path with {len(self.wire_path)} points")
        
        return self.wire_path
    
    def _generate_smooth_wire_path(self):
        """Generate smooth wire path from control points with height offset."""
        if len(self.wire_control_points) < 2:
            return
        
        control_positions = np.array([cp['position'] for cp in self.wire_control_points])
        
        # Apply global height offset to all control points
        control_positions[:, self.height_axis] += self.wire_height_offset
        
        # Create spline interpolation
        if len(control_positions) >= 4:
            # Use cubic spline for smooth curve
            t = np.linspace(0, 1, len(control_positions))
            t_smooth = np.linspace(0, 1, len(control_positions) * 20)
            
            # Interpolate each dimension
            wire_points = []
            for dim in range(3):
                tck = interpolate.splrep(t, control_positions[:, dim], s=0, k=min(3, len(control_positions)-1))
                smooth_dim = interpolate.splev(t_smooth, tck)
                wire_points.append(smooth_dim)
            
            self.wire_path = np.array(wire_points).T
        else:
            # Simple linear interpolation for few points
            self.wire_path = control_positions
    
    # NEW: Wire height adjustment methods
    def adjust_wire_height(self, delta_height: float):
        """Adjust the height of the entire wire path."""
        self.wire_height_offset += delta_height
        
        # Regenerate wire path with new height
        self._generate_smooth_wire_path()
        
        # Force complete wire mesh recreation to avoid ghosting
        if hasattr(self, 'wire_mesh'):
            if self.wire_mesh is not None:
                # Clear existing mesh data
                self.wire_mesh.clear()
                self.wire_mesh = None
            
            # Create fresh wire mesh
            self.wire_mesh = self._create_wire_mesh()
        
        print(f"Wire height adjusted by {delta_height:.2f}mm (total offset: {self.wire_height_offset:.2f}mm)")
    
    def reset_wire_height(self):
        """Reset wire height to original position."""
        self.wire_height_offset = 0.0
        self._generate_smooth_wire_path()
        
        # Force complete wire mesh recreation
        if hasattr(self, 'wire_mesh'):
            if self.wire_mesh is not None:
                # Clear existing mesh data
                self.wire_mesh.clear()
                self.wire_mesh = None
            
            # Create fresh wire mesh
            self.wire_mesh = self._create_wire_mesh()
        
        print("Wire height reset to original position")
    
    def start_wire_drag(self, mouse_y: int):
        """Start wire dragging mode."""
        self.is_dragging_wire = True
        self.last_mouse_y = mouse_y
        print("Wire dragging started - move mouse vertically to adjust height")
    
    def update_wire_drag(self, mouse_y: int):
        """Update wire position during drag."""
        if not self.is_dragging_wire:
            return
        
        # Calculate height change based on mouse movement
        delta_pixels = mouse_y - self.last_mouse_y
        delta_height = -delta_pixels * 0.1  # Convert pixels to mm (negative for intuitive direction)
        
        if abs(delta_height) > 0.1:  # Only update if significant movement
            self.adjust_wire_height(delta_height)
            self.last_mouse_y = mouse_y
    
    def stop_wire_drag(self):
        """Stop wire dragging mode."""
        self.is_dragging_wire = False
        print("Wire dragging stopped")
    
    def create_enhanced_visualization_meshes(self):
        """Create 3D visualization meshes including control points."""
        print(f"\n{'─'*50}")
        print("CREATING ENHANCED 3D VISUALIZATION")
        print(f"{'─'*50}")
        
        # Create bracket meshes
        self.bracket_meshes = []
        
        visible_posteriors = [b for b in self.bracket_positions if b['visible'] and b['tooth_type'] == 'posterior']
        
        for i, bracket in enumerate(self.bracket_positions):
            if not bracket['visible']:
                continue
            
            # Create bracket box
            bracket_mesh = o3d.geometry.TriangleMesh.create_box(1.8, 2.0, 1.2)
            bracket_mesh.translate([-0.9, -1.0, -0.6])
            
            # Orient bracket (if normal available)
            if 'normal' in bracket and np.linalg.norm(bracket['normal']) > 0:
                z_axis = np.array([0, 0, 1])
                normal = bracket['normal']
                
                rotation_axis = np.cross(z_axis, normal)
                if np.linalg.norm(rotation_axis) > 1e-6:
                    rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
                    angle = np.arccos(np.clip(np.dot(z_axis, normal), -1, 1))
                    R = o3d.geometry.get_rotation_matrix_from_axis_angle(rotation_axis * angle)
                    bracket_mesh.rotate(R, center=[0, 0, 0])
            
            bracket_mesh.translate(bracket['position'])
            
            # Color based on tooth type and position
            color = [0.7, 0.7, 0.7] # Default gray
            if bracket['tooth_type'] == 'posterior' and visible_posteriors:
                if bracket is visible_posteriors[0] or bracket is visible_posteriors[-1]:
                    color = [0.9, 0.8, 0.1]  # Yellow for corner teeth
                else:
                    color = [0.1, 0.3, 0.8]  # Blue for middle teeth
            
            bracket_mesh.paint_uniform_color(color)
            bracket_mesh.compute_vertex_normals()
            
            self.bracket_meshes.append({
                'mesh': bracket_mesh,
                'index': i,
                'original_color': color,
                'bracket': bracket
            })
        
        # Create control point meshes
        self.control_point_meshes = []
        for i, cp in enumerate(self.wire_control_points):
            if cp['type'] == 'bracket':
                # Bracket control points - small spheres
                sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.8, resolution=8)
                color = [0.9, 0.1, 0.1]  # Red for bracket points
            else:
                # Midpoint control points - slightly larger spheres
                sphere = o3d.geometry.TriangleMesh.create_sphere(radius=1.0, resolution=8)
                color = [0.1, 0.9, 0.1]  # Green for midpoint controls
            
            # Apply height offset to control point positions
            position = cp['position'].copy()
            position[self.height_axis] += self.wire_height_offset
            
            sphere.translate(position)
            sphere.paint_uniform_color(color)
            sphere.compute_vertex_normals()
            
            self.control_point_meshes.append({
                'mesh': sphere,
                'index': i,
                'original_color': color,
                'control_point': cp
            })
        
        # Create wire mesh
        self.wire_mesh = self._create_wire_mesh()
        
        print(f"✓ Created {len(self.bracket_meshes)} bracket meshes")
        print(f"✓ Created {len(self.control_point_meshes)} control point meshes")
        print(f"✓ Created wire mesh with {len(self.wire_mesh.vertices)} vertices")
        
        return self.wire_mesh, self.bracket_meshes, self.control_point_meshes
    
    def _create_wire_mesh(self):
        """Create wire mesh from current wire path."""
        wire_mesh = o3d.geometry.TriangleMesh()
        
        if self.wire_path is not None and len(self.wire_path) > 1:
            for i in range(len(self.wire_path) - 1):
                p1 = self.wire_path[i]
                p2 = self.wire_path[i + 1]
                segment_length = np.linalg.norm(p2 - p1)
                
                if segment_length < 0.01 or segment_length > 30.0:
                    continue
                
                cylinder = o3d.geometry.TriangleMesh.create_cylinder(
                    radius=self.wire_radius,
                    height=segment_length,
                    resolution=12
                )
                
                # Orient cylinder
                z_axis = np.array([0, 0, 1])
                segment_dir = (p2 - p1) / segment_length
                
                rotation_axis = np.cross(z_axis, segment_dir)
                if np.linalg.norm(rotation_axis) > 1e-6:
                    rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
                    angle = np.arccos(np.clip(np.dot(z_axis, segment_dir), -1, 1))
                    R = o3d.geometry.get_rotation_matrix_from_axis_angle(rotation_axis * angle)
                    cylinder.rotate(R, center=[0, 0, 0])
                
                cylinder.translate((p1 + p2) / 2)
                wire_mesh += cylinder
        
        # Color wire gold
        wire_mesh.paint_uniform_color([0.85, 0.75, 0.45])
        wire_mesh.compute_vertex_normals()
        
        return wire_mesh
    
    def select_control_point(self, index: int):
        """Select a control point for editing."""
        # Deselect previous
        if self.selected_control_point is not None:
            for cpm in self.control_point_meshes:
                if cpm['index'] == self.selected_control_point:
                    cpm['mesh'].paint_uniform_color(cpm['original_color'])
                    break
        
        # Select new
        self.selected_control_point = index
        
        # Highlight selected control point
        for cpm in self.control_point_meshes:
            if cpm['index'] == index:
                cpm['mesh'].paint_uniform_color([1.0, 1.0, 0.0])  # Bright yellow
                cp = cpm['control_point']
                print(f"Selected control point {index} ({cp['type']})")
                print(f"  Position: [{cp['position'][0]:.2f}, {cp['position'][1]:.2f}, {cp['position'][2]:.2f}]")
                print(f"  Bend angle: {cp['bend_angle']:.1f}°")
                print(f"  Vertical offset: {cp['vertical_offset']:.2f}mm")
                break
    
    def move_selected_control_point(self, direction: np.ndarray, step: float = 0.5):
        """Move the selected control point."""
        if self.selected_control_point is None:
            return
        
        # Find the correct control point mesh to update
        target_cpm = None
        for cpm in self.control_point_meshes:
            if cpm['index'] == self.selected_control_point:
                target_cpm = cpm
                break
        
        if not target_cpm:
            return
        
        # Get original center to calculate translation
        original_center = target_cpm['mesh'].get_center()
        
        # Update data model position
        self.wire_control_points[self.selected_control_point]['position'] += direction * step
        new_center = self.wire_control_points[self.selected_control_point]['position']
        
        # Apply height offset for display
        display_center = new_center.copy()
        display_center[self.height_axis] += self.wire_height_offset
        
        # Update vertical offset if moving vertically
        if abs(direction[self.height_axis]) > 0.5:
            self.wire_control_points[self.selected_control_point]['vertical_offset'] += direction[self.height_axis] * step
        
        # Translate the mesh
        translation = display_center - original_center
        target_cpm['mesh'].translate(translation, relative=True)
        
        # Regenerate wire path and mesh
        self._generate_smooth_wire_path()
        self.wire_mesh = self._create_wire_mesh()
        
        print(f"Moved control point {self.selected_control_point} by {direction * step}")
    
    def adjust_wire_bending(self, bend_adjustment: float):
        """Adjust bending at selected control point."""
        if self.selected_control_point is None:
            return
        
        cp = self.wire_control_points[self.selected_control_point]
        cp['bend_angle'] += bend_adjustment
        cp['bend_angle'] = np.clip(cp['bend_angle'], -45, 45)  # Limit bend angle
        
        # Apply bend effect to position (simplified)
        mesh_center = self.mesh.get_center()
        direction_to_center = mesh_center - cp['position']
        direction_to_center[self.height_axis] = 0
        
        if np.linalg.norm(direction_to_center) > 0:
            direction_to_center = direction_to_center / np.linalg.norm(direction_to_center)
            bend_offset = direction_to_center * (cp['bend_angle'] / 45.0) * 2.0  # Max 2mm offset
            
            # Update position with bend
            old_pos = cp['position'].copy()
            cp['position'] = cp['original_position'] + bend_offset
            cp['position'][self.height_axis] += cp['vertical_offset']
            
            # Update visual mesh with height offset
            for cpm in self.control_point_meshes:
                if cpm['index'] == self.selected_control_point:
                    display_pos = cp['position'].copy()
                    display_pos[self.height_axis] += self.wire_height_offset
                    translation = display_pos - old_pos
                    translation[self.height_axis] += self.wire_height_offset
                    cpm['mesh'].translate(translation, relative=True)
                    break
            
            # Regenerate wire
            self._generate_smooth_wire_path()
            self.wire_mesh = self._create_wire_mesh()
        
        print(f"Adjusted bend at control point {self.selected_control_point}: {cp['bend_angle']:.1f}°")
    
    def calculate_wire_bends(self):
        """Calculate bend angles and positions for G-code generation."""
        if len(self.wire_path) < 3:
            return []
        
        bends = []
        bend_threshold = 5.0  # degrees
        
        for i in range(1, len(self.wire_path) - 1):
            p1 = self.wire_path[i - 1]
            p2 = self.wire_path[i]
            p3 = self.wire_path[i + 1]
            
            # Calculate vectors
            v1 = p2 - p1
            v2 = p3 - p2
            
            # Normalize vectors
            if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                v1_norm = v1 / np.linalg.norm(v1)
                v2_norm = v2 / np.linalg.norm(v2)
                
                # Calculate angle between vectors
                dot_product = np.clip(np.dot(v1_norm, v2_norm), -1, 1)
                angle = np.degrees(np.arccos(dot_product))
                bend_angle = 180 - angle
                
                if abs(bend_angle) > bend_threshold:
                    # Calculate bend direction (left/right)
                    cross_product = np.cross(v1_norm, v2_norm)
                    bend_direction = 'left' if cross_product[self.height_axis] > 0 else 'right'
                    
                    bends.append({
                        'position': p2.copy(),
                        'angle': bend_angle,
                        'direction': bend_direction,
                        'wire_length': np.sum([np.linalg.norm(self.wire_path[j+1] - self.wire_path[j]) 
                                               for j in range(i)]),
                        'radius': self.bend_radius
                    })
        
        self.gcode_settings['bend_positions'] = bends
        print(f"Calculated {len(bends)} wire bends for G-code generation")
        return bends
    
    def get_esp32_arduino_code(self, steps_per_mm=(80, 80, 400), pins=((26, 27), (32, 33), (14, 12)), max_feed_mm_s=5.0) -> str:
        """Returns the ESP32 Arduino code as a string."""
        path = np.array(self.wire_path)
        if path is None or len(path) == 0:
            return ""
        arr_lines = []
        for p in path:
            arr_lines.append(f"  {{ {p[0]:.4f}f, {p[1]:.4f}f, {p[2]:.4f}f }}")
        arr_body = ",\n".join(arr_lines)
        code = f"""\
/*
 * Auto-generated by wire_generator_gui_advanced.py on {time.strftime('%Y-%m-%d %H:%M:%S')}
 * Purpose: Move 3 steppers along a 3D wire path (mm) using ESP32 + AccelStepper.
 * NOTE: Tune pins, steps/mm, max speeds, and acceleration for your hardware.
 */

#include <AccelStepper.h>

// ---------------- Hardware config (EDIT ME) ----------------
#define X_STEP_PIN {pins[0][0]}
#define X_DIR_PIN  {pins[0][1]}
#define Y_STEP_PIN {pins[1][0]}
#define Y_DIR_PIN  {pins[1][1]}
#define Z_STEP_PIN {pins[2][0]}
#define Z_DIR_PIN  {pins[2][1]}

// Steps per mm (EDIT to match lead screw or belt)
const float X_STEPS_PER_MM = {float(steps_per_mm[0])}f;
const float Y_STEPS_PER_MM = {float(steps_per_mm[1])}f;
const float Z_STEPS_PER_MM = {float(steps_per_mm[2])}f;

// Motion params
const float MAX_FEED_MM_S = {max_feed_mm_s:.3f}f;  // cap feed
const float ACCEL_STEPS_S2 = 800.0f;                       // accel (adjust)

// ---------------- Path data (absolute mm) ----------------
struct Waypoint {{ float x, y, z; }};
const Waypoint PATH[] = {{
{arr_body}
}};
const int PATH_LEN = sizeof(PATH) / sizeof(PATH[0]);

// ---------------- Steppers ----------------
AccelStepper stepperX(AccelStepper::DRIVER, X_STEP_PIN, X_DIR_PIN);
AccelStepper stepperY(AccelStepper::DRIVER, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper stepperZ(AccelStepper::DRIVER, Z_STEP_PIN, Z_DIR_PIN);

long mm_to_steps(float mm, float steps_per_mm) {{
  return (long) llround(mm * steps_per_mm);
}}

void syncMoveTo(float x_mm, float y_mm, float z_mm, float feed_mm_s) {{
  if (feed_mm_s <= 0) feed_mm_s = MAX_FEED_MM_S;
  if (feed_mm_s > MAX_FEED_MM_S) feed_mm_s = MAX_FEED_MM_S;

  long tx = mm_to_steps(x_mm, X_STEPS_PER_MM);
  long ty = mm_to_steps(y_mm, Y_STEPS_PER_MM);
  long tz = mm_to_steps(z_mm, Z_STEPS_PER_MM);

  long dx = tx - stepperX.currentPosition();
  long dy = ty - stepperY.currentPosition();
  long dz = tz - stepperZ.currentPosition();

  // Length in steps for vector (dominant axis)
  double L = sqrt((double)dx*dx + (double)dy*dy + (double)dz*dz);
  if (L < 1.0) {{
    stepperX.moveTo(tx); stepperY.moveTo(ty); stepperZ.moveTo(tz);
    stepperX.runToPosition(); stepperY.runToPosition(); stepperZ.runToPosition();
    return;
  }}

  // Convert desired feed (mm/s) to steps/s along the vector
  double feed_steps_s = feed_mm_s * (X_STEPS_PER_MM + Y_STEPS_PER_MM + Z_STEPS_PER_MM) / 3.0; // conservative estimate

  // Speeds per axis proportional to vector components
  double vx = feed_steps_s * (double)dx / L;
  double vy = feed_steps_s * (double)dy / L;
  double vz = feed_steps_s * (double)dz / L;

  stepperX.moveTo(tx); stepperY.moveTo(ty); stepperZ.moveTo(tz);

  stepperX.setMaxSpeed(fabs(vx)); stepperY.setMaxSpeed(fabs(vy)); stepperZ.setMaxSpeed(fabs(vz));
  stepperX.setAcceleration(ACCEL_STEPS_S2);
  stepperY.setAcceleration(ACCEL_STEPS_S2);
  stepperZ.setAcceleration(ACCEL_STEPS_S2);

  // Use run() loop; runSpeedToPosition offers less accel control across 3 axes
  while (stepperX.distanceToGo()!=0 || stepperY.distanceToGo()!=0 || stepperZ.distanceToGo()!=0) {{
    stepperX.run();
    stepperY.run();
    stepperZ.run();
  }}
}}

void homeAll() {{
  // TODO: add homing logic if you have endstops
  stepperX.setCurrentPosition(0);
  stepperY.setCurrentPosition(0);
  stepperZ.setCurrentPosition(0);
}}

void setup() {{
  // Serial optional
  Serial.begin(115200);
  // Direction polarity may need flipping depending on mechanics
  stepperX.setMaxSpeed(2000); stepperX.setAcceleration(800);
  stepperY.setMaxSpeed(2000); stepperY.setAcceleration(800);
  stepperZ.setMaxSpeed(2000); stepperZ.setAcceleration(800);

  homeAll();

  // Move to first point at safe feed
  if (PATH_LEN > 0) {{
    syncMoveTo(PATH[0].x, PATH[0].y, PATH[0].z, MAX_FEED_MM_S * 0.5f);
  }}
  for (int i = 1; i < PATH_LEN; ++i) {{
    syncMoveTo(PATH[i].x, PATH[i].y, PATH[i].z, MAX_FEED_MM_S);
  }}
  Serial.println("Path complete.");
}}

void loop() {{
  // Idle
}}
"""
        return code
    
    def export_esp32_arduino(self, out_dir: str, steps_per_mm=(80, 80, 400), pins=((26, 27), (32, 33), (14, 12)), max_feed_mm_s=5.0) -> Optional[str]:
        """Generates an Arduino sketch (.ino) for ESP32 using AccelStepper."""
        path = np.array(self.wire_path)
        if path is None or len(path) == 0:
            return None

        ts = time.strftime("%Y%m%d_%H%M%S")
        fname = f"esp32_wire_path_{self.arch_type}_{ts}.ino"
        fpath = os.path.join(out_dir, fname)

        code = self.get_esp32_arduino_code(steps_per_mm, pins, max_feed_mm_s)
        
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(code)
        return fpath
    
    def generate_gcode(self, filename: Optional[str] = None) -> str:
        """Generate G-code for Arduino-controlled wire bending machine."""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"wire_gcode_{self.arch_type}_{timestamp}.gcode"
        
        # Calculate bends
        bends = self.calculate_wire_bends()
        
        # Calculate total wire length
        total_length = 0
        if len(self.wire_path) > 1:
            for i in range(len(self.wire_path) - 1):
                total_length += np.linalg.norm(self.wire_path[i+1] - self.wire_path[i])
        
        # Generate G-code
        gcode_lines = []
        
        # Header
        gcode_lines.extend([
            "; Generated by Enhanced Interactive Orthodontic Wire Generator",
            f"; File: {filename}",
            f"; Date: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"; Arch Type: {self.arch_type.upper()}",
            f"; Wire Size: {self.wire_size}",
            f"; Total Wire Length: {total_length:.2f}mm",
            f"; Wire Height Offset: {self.wire_height_offset:.2f}mm",
            f"; Number of Bends: {len(bends)}",
            ";",
            "; Wire Bending Machine Commands:",
            "; G0 - Rapid positioning",
            "; G1 - Linear interpolation",
            "; M3 - Clamp wire",
            "; M4 - Release wire",
            "; M5 - Bend wire (with parameters)",
            "; M6 - Feed wire",
            ";",
            "",
            "; Initialize machine",
            "G21 ; Set units to millimeters",
            "G90 ; Absolute positioning",
            "G28 ; Home all axes",
            f"F{self.gcode_settings['feed_rate']} ; Set feed rate",
            "",
            "; Safety checks",
            "M117 Wire Bending Started",
            "",
        ])
        
        # Wire preparation
        gcode_lines.extend([
            "; Prepare wire",
            f"G0 X{self.gcode_settings['wire_clamp_position'][0]} Y{self.gcode_settings['wire_clamp_position'][1]} Z{self.gcode_settings['safety_height']}",
            "M3 ; Clamp wire",
            "G4 P500 ; Wait 0.5 seconds",
            "",
        ])
        
        # Process each bend
        current_wire_length = 0
        
        for i, bend in enumerate(bends):
            # Calculate wire feed length to this bend
            feed_length = bend['wire_length'] - current_wire_length
            
            gcode_lines.extend([
                f"; Bend {i+1}: {bend['angle']:.1f}° {bend['direction']} at {bend['wire_length']:.1f}mm",
                f"M6 S{feed_length:.2f} ; Feed wire {feed_length:.2f}mm",
                "G4 P200 ; Wait for wire feed",
                "",
                f"; Position bending mechanism",
                f"G0 Z{self.gcode_settings['safety_height']} ; Move to safety height",
                f"G0 X{bend['position'][0]:.2f} Y{bend['position'][1]:.2f}",
                f"G1 Z{bend['position'][2]:.2f} F{self.gcode_settings['bend_speed']}",
                "",
                f"; Execute bend",
                f"M5 A{bend['angle']:.1f} R{bend['radius']:.1f} D{bend['direction'][0].upper()} ; Bend wire",
                "G4 P1000 ; Wait for bend completion",
                "",
                f"; Return to safe position",
                f"G0 Z{self.gcode_settings['safety_height']}",
                "",
            ])
            
            current_wire_length = bend['wire_length']
        
        # Final wire feed and cleanup
        remaining_length = total_length - current_wire_length
        
        gcode_lines.extend([
            "; Final wire feed",
            f"M6 S{remaining_length:.2f} ; Feed remaining wire {remaining_length:.2f}mm",
            "G4 P500 ; Wait for final feed",
            "",
            "; Cleanup and finish",
            "M4 ; Release wire clamp",
            f"G0 Z{self.gcode_settings['safety_height']} ; Move to safety height",
            "G28 ; Return to home position",
            "M117 Wire Bending Complete",
            "",
            f"; Total wire used: {total_length:.2f}mm",
            f"; Total bends: {len(bends)}",
            f"; Estimated time: {self._estimate_bend_time(bends, total_length):.1f} minutes",
            "",
            "M30 ; Program end",
        ])
        
        # Write G-code to file
        gcode_content = '\n'.join(gcode_lines)
        
        try:
            with open(filename, 'w') as f:
                f.write(gcode_content)
            print(f"✓ Generated G-code file: {filename}")
            print(f"  • Total wire length: {total_length:.2f}mm")
            print(f"  • Wire height offset: {self.wire_height_offset:.2f}mm")
            print(f"  • Number of bends: {len(bends)}")
            print(f"  • Estimated time: {self._estimate_bend_time(bends, total_length):.1f} minutes")
            return filename
        except Exception as e:
            print(f"✗ Error generating G-code: {e}")
            return None
    
    def _estimate_bend_time(self, bends, total_length):
        """Estimate total bending time in minutes."""
        # Time estimates (in seconds)
        setup_time = 30
        wire_feed_time = total_length / 10  # 10mm/second feed rate
        bend_time = len(bends) * 5  # 5 seconds per bend
        positioning_time = len(bends) * 3  # 3 seconds positioning per bend
        
        total_seconds = setup_time + wire_feed_time + bend_time + positioning_time
        return total_seconds / 60  # Convert to minutes
    
    def save_enhanced_design(self):
        """Save enhanced design with control points and G-code info."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_wire_design_{self.arch_type}_{timestamp}.json"
        
        data = {
            'metadata': {
                'arch_type': self.arch_type,
                'wire_size': self.wire_size,
                'timestamp': timestamp,
                'stl_file': os.path.basename(self.stl_path),
                'version': 'enhanced_v2.1_height_control'
            },
            'brackets': [],
            'control_points': [],
            'wire_path': [],
            'wire_height_offset': self.wire_height_offset,
            'bending_parameters': {
                'bend_radius': self.bend_radius,
                'bend_tolerance': self.bend_tolerance,
                'wire_tension': self.wire_tension,
                'height_adjustment_step': self.height_adjustment_step
            },
            'gcode_settings': self.gcode_settings
        }
        
        # Save bracket positions
        for i, bracket in enumerate(self.bracket_positions):
            data['brackets'].append({
                'index': i,
                'position': bracket['position'].tolist(),
                'original_position': bracket['original_position'].tolist(),
                'tooth_type': bracket['tooth_type'],
                'visible': bracket['visible']
            })
        
        # Save control points
        for i, cp in enumerate(self.wire_control_points):
            data['control_points'].append({
                'index': i,
                'position': cp['position'].tolist(),
                'original_position': cp['original_position'].tolist(),
                'type': cp['type'],
                'bend_angle': cp['bend_angle'],
                'vertical_offset': cp['vertical_offset']
            })
        
        # Save wire path
        if self.wire_path is not None:
            data['wire_path'] = self.wire_path.tolist()
        
        # Calculate and save bend information
        bends = self.calculate_wire_bends()
        data['calculated_bends'] = []
        for bend in bends:
            data['calculated_bends'].append({
                'position': bend['position'].tolist(),
                'angle': bend['angle'],
                'direction': bend['direction'],
                'wire_length': bend['wire_length'],
                'radius': bend['radius']
            })
        
        # Write to file
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✓ Saved enhanced wire design to: {filename}")
            return filename
        except Exception as e:
            print(f"✗ Error saving file: {e}")
            return None
    
    def print_enhanced_help(self):
        """Print enhanced interactive controls help."""
        print("\n" + "="*70)
        print("ENHANCED INTERACTIVE CONTROLS WITH WIRE HEIGHT ADJUSTMENT")
        print("="*70)
        print("\nWIRE HEIGHT CONTROLS (NEW):")
        print("  • Up Arrow: Move entire wire UP")
        print("  • Down Arrow: Move entire wire DOWN")
        print("  • Shift + Mouse Drag: Drag wire vertically with mouse")
        print("  • Ctrl + R: Reset wire to original height")
        print("  • Ctrl + H: Display current height offset")
        print("\nCONTROL POINT SELECTION:")
        print("  • C + 1-9: Select control point by number")
        print("  • C + 0: Deselect control point")
        print("\nCONTROL POINT MOVEMENT (for selected control point):")
        print("  • Left/Right Arrow: Move control point horizontally")
        print("  • Page Up/Down: Move control point up/down (individual)")
        print("  • +/-: Increase/decrease movement step size")
        print("\nWIRE BENDING CONTROLS:")
        print("  • B + Up/Down: Increase/decrease bend angle at selected point")
        print("  • B + Left/Right: Adjust bend direction")
        print("  • T + Up/Down: Adjust wire tension")
        print("  • V + Up/Down: Vertical offset adjustment")
        print("\nBRACKET SELECTION (Legacy):")
        print("  • 1-9: Select bracket by number")
        print("  • 0: Deselect bracket")
        print("\nACTIONS:")
        print("  • S: Save enhanced design to JSON")
        print("  • G: Generate G-code for Arduino")
        print("  • R: Reset all control points to original positions")
        print("  • H: Show this help message")
        print("  • Q: Quit application")
        print("\nWIRE PROPERTIES:")
        print("  • W + R: Adjust bend radius")
        print("  • W + T: Adjust bend tolerance")
        print("\nVIEW NAVIGATION:")
        print("  • Mouse Left + Drag: Rotate view")
        print("  • Mouse Right + Drag: Pan view")
        print("  • Mouse Scroll: Zoom in/out")
        print("  • Shift + Mouse Drag: Adjust wire height")
        print("="*70 + "\n")
    
    def visualize_enhanced_interactive(self):
        """Launch enhanced interactive 3D visualization with height control."""
        print(f"\n{'='*70}")
        print("LAUNCHING ENHANCED INTERACTIVE 3D EDITOR WITH HEIGHT CONTROL")
        print(f"{'='*70}")
        
        # Create visualizer with key callbacks
        vis = o3d.visualization.VisualizerWithKeyCallback()
        vis.create_window(
            window_name=f"Enhanced Wire Editor with Height Control - {self.arch_type.upper()} Arch",
            width=1600,
            height=1000
        )
        
        # Add geometries
        vis.add_geometry(self.mesh)
        
        # --- MODIFICATION: Hide Blue/Yellow bracket boxes ---
        # for bracket_data in self.bracket_meshes:
        #     vis.add_geometry(bracket_data['mesh'])
        
        # --- MODIFICATION: Hide Red/Green control point spheres ---
        # for cp_data in self.control_point_meshes:
        #     vis.add_geometry(cp_data['mesh'])
        
        if self.wire_mesh:
            vis.add_geometry(self.wire_mesh)
        
        # --- MODIFICATION: Hide XYZ coordinate frame ---
        # coord_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
        #     size=20.0, origin=[0, 0, 0]
        # )
        # vis.add_geometry(coord_frame)
        
        move_step = [0.5]
        bend_step = [2.0]  # degrees
        
        def update_all_geometries(vis_obj):
            """Helper to update all dynamic geometries."""
            for bm in self.bracket_meshes:
                vis_obj.update_geometry(bm['mesh'])
            for cpm in self.control_point_meshes:
                vis_obj.update_geometry(cpm['mesh'])
            if self.wire_mesh:
                vis_obj.update_geometry(self.wire_mesh)
        
        def update_wire_height_display(vis_obj):
            """Update all meshes when wire height changes."""
            # --- MODIFICATION: Hide control points during movement ---
            # # Recreate control point meshes with new height
            # for i, cpm in enumerate(self.control_point_meshes):
            #     cp = cpm['control_point']
                
            #     # Remove old mesh
            #     vis_obj.remove_geometry(cpm['mesh'], reset_bounding_box=False)
                
            #     # Create new mesh at updated position
            #     if cp['type'] == 'bracket':
            #         sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.8, resolution=8)
            #         color = [0.9, 0.1, 0.1]
            #     else:
            #         sphere = o3d.geometry.TriangleMesh.create_sphere(radius=1.0, resolution=8)
            #         color = [0.1, 0.9, 0.1]
                
            #     # Apply height offset
            #     position = cp['position'].copy()
            #     position[self.height_axis] += self.wire_height_offset
                
            #     sphere.translate(position)
            #     sphere.paint_uniform_color(color)
            #     sphere.compute_vertex_normals()
                
            #     # Update stored mesh
            #     cpm['mesh'] = sphere
            #     vis_obj.add_geometry(sphere, reset_bounding_box=False)
            
            # Update wire mesh
            if self.wire_mesh:
                vis_obj.remove_geometry(self.wire_mesh, reset_bounding_box=False)
                self.wire_mesh = self._create_wire_mesh()
                vis_obj.add_geometry(self.wire_mesh, reset_bounding_box=False)
        
        # NEW: Wire height adjustment callbacks
        def key_callback_wire_up(vis_obj):
            self.adjust_wire_height(self.height_adjustment_step)
            update_wire_height_display(vis_obj)
            return False
        
        def key_callback_wire_down(vis_obj):
            self.adjust_wire_height(-self.height_adjustment_step)
            update_wire_height_display(vis_obj)
            return False
        
        def key_callback_reset_height(vis_obj):
            self.reset_wire_height()
            update_wire_height_display(vis_obj)
            return False
        
        def key_callback_show_height(vis_obj):
            print(f"Current wire height offset: {self.wire_height_offset:.2f}mm")
            return False
        
        # Existing callbacks
        def key_callback_quit(vis_obj):
            vis_obj.close()
            return True
        
        def key_callback_help(vis_obj):
            self.print_enhanced_help()
            return False
        
        def key_callback_save(vis_obj):
            self.save_enhanced_design()
            return False
        
        def key_callback_generate_gcode(vis_obj):
            self.generate_gcode()
            return False
        
        def key_callback_select_cp(vis_obj, cp_idx):
            if 0 <= cp_idx < len(self.control_point_meshes):
                self.select_control_point(cp_idx)
                update_all_geometries(vis_obj)
            return False
        
        def key_callback_deselect_cp(vis_obj):
            if self.selected_control_point is not None:
                self.selected_control_point = None
                # Reset all control point colors
                for cpm in self.control_point_meshes:
                    cpm['mesh'].paint_uniform_color(cpm['original_color'])
                update_all_geometries(vis_obj)
                print("Deselected control point")
            return False
        
        def key_callback_move_cp(vis_obj, direction_vector):
            if self.selected_control_point is not None:
                self.move_selected_control_point(direction_vector, move_step[0])
                update_all_geometries(vis_obj)
            return False
        
        def key_callback_bend_adjust(vis_obj, bend_change):
            if self.selected_control_point is not None:
                self.adjust_wire_bending(bend_change * bend_step[0])
                update_all_geometries(vis_obj)
            return False
        
        def key_callback_step_increase(vis_obj):
            move_step[0] = min(move_step[0] * 1.5, 5.0)
            print(f"Movement step: {move_step[0]:.2f}mm")
            return False
        
        def key_callback_step_decrease(vis_obj):
            move_step[0] = max(move_step[0] / 1.5, 0.1)
            print(f"Movement step: {move_step[0]:.2f}mm")
            return False
        
        # Register enhanced key callbacks
        vis.register_key_callback(ord('Q'), key_callback_quit)
        vis.register_key_callback(ord('H'), key_callback_help)
        vis.register_key_callback(ord('S'), key_callback_save)
        vis.register_key_callback(ord('G'), key_callback_generate_gcode)
        
        # NEW: Wire height control key callbacks
        vis.register_key_callback(265, key_callback_wire_up)      # Up Arrow
        vis.register_key_callback(264, key_callback_wire_down)    # Down Arrow
        vis.register_key_callback(ord('R'), key_callback_reset_height)  # Reset height (Ctrl+R concept)
        vis.register_key_callback(ord('O'), key_callback_show_height)   # Show height offset
        
        # Control point selection
        for i in range(1, 10):
            vis.register_key_callback(ord(str(i)), lambda v, idx=i-1: key_callback_select_cp(v, idx))
        vis.register_key_callback(ord('0'), key_callback_deselect_cp)
        
        # Movement controls (for individual control points)
        vis.register_key_callback(262, lambda v: key_callback_move_cp(v, np.array([1, 0, 0])))  # Right
        vis.register_key_callback(263, lambda v: key_callback_move_cp(v, np.array([-1, 0, 0]))) # Left
        vis.register_key_callback(266, lambda v: key_callback_move_cp(v, np.array([0, 0, 1])))  # Page Up
        vis.register_key_callback(267, lambda v: key_callback_move_cp(v, np.array([0, 0, -1]))) # Page Down
        
        # Bending controls
        vis.register_key_callback(ord('B'), lambda v: key_callback_bend_adjust(v, 1))  # Increase bend
        vis.register_key_callback(ord('N'), lambda v: key_callback_bend_adjust(v, -1)) # Decrease bend
        
        # Step size adjustment
        vis.register_key_callback(ord('='), key_callback_step_increase)
        vis.register_key_callback(ord('-'), key_callback_step_decrease)
        
        # Set up mouse callback for wire dragging
        def mouse_move_callback(vis_obj, x, y):
            # This is a simplified mouse callback - in practice, you'd need to track
            # modifier keys (Shift) and mouse button states for proper drag functionality
            if self.is_dragging_wire:
                self.update_wire_drag(y)
                update_wire_height_display(vis_obj)
            return False
        
        def mouse_button_callback(vis_obj, button, action, x, y):
            # Simple implementation - in real scenario you'd check for Shift key
            if button == 0 and action == 1:  # Left button pressed
                # Could implement shift+click for wire dragging here
                pass
            elif button == 0 and action == 0:  # Left button released
                if self.is_dragging_wire:
                    self.stop_wire_drag()
            return False
        
        # Note: Open3D's mouse callbacks are limited, so this is a simplified implementation
        # In a full implementation, you'd need more sophisticated event handling
        
        opt = vis.get_render_option()
        opt.background_color = np.array([0.92, 0.92, 0.95])
        opt.mesh_show_back_face = True
        
        ctr = vis.get_view_control()
        ctr.set_zoom(0.7)
        
        print("\n🎮 ENHANCED INTERACTIVE MODE WITH HEIGHT CONTROL ACTIVE")
        print("📟 G-CODE GENERATION READY")
        print("🔺 WIRE HEIGHT CONTROL: Use Up/Down arrows")
        print(f"📏 Current wire height offset: {self.wire_height_offset:.2f}mm")
        self.print_enhanced_help()
        
        vis.run()
        vis.destroy_window()
    
    def generate_enhanced_wire(self):
        """Main pipeline for enhanced wire generation with height control."""
        print("\n" + "="*70)
        print("STARTING ENHANCED INTERACTIVE WIRE GENERATION PIPELINE")
        print("WITH HEIGHT CONTROL CAPABILITIES")
        print("="*70)
        
        if not self.load_mesh():
            return None
        
        if not self.detect_teeth_simple():
            return None
        
        self.calculate_lingual_bracket_positions()
        
        if self.create_smooth_wire_path_with_control_points() is None:
            return None
        
        self.create_enhanced_visualization_meshes()
        self.visualize_enhanced_interactive()
        
        result = {
            'mesh': self.mesh,
            'teeth': self.teeth,
            'bracket_positions': self.bracket_positions,
            'wire_control_points': self.wire_control_points,
            'wire_path': self.wire_path,
            'wire_mesh': self.wire_mesh,
            'bracket_meshes': self.bracket_meshes,
            'control_point_meshes': self.control_point_meshes,
            'gcode_settings': self.gcode_settings,
            'wire_height_offset': self.wire_height_offset
        }
        
        print("\n" + "="*70)
        print("ENHANCED INTERACTIVE SESSION WITH HEIGHT CONTROL COMPLETE")
        print("="*70)
        
        return result


# --- Enhanced GUI with Height Control Integration ---

class WireGeneratorGUI:
    """Enhanced GUI for orthodontic wire generator with height control integration."""
    
    # Standard wire dimensions (in inches, converted to mm)
    WIRE_SIZES = {
        '0.012': 0.3048,
        '0.014': 0.3556,
        '0.016': 0.4064,
        '0.018': 0.4572,
        '0.020': 0.5080,
        '0.016x0.022': (0.4064, 0.5588),
        '0.018x0.025': (0.4572, 0.6350),
        '0.019x0.025': (0.4826, 0.6350),
        '0.021x0.025': (0.5334, 0.6350)
    }
    
    def __init__(self):
        """Initialize the GUI application."""
        self.root = tk.Tk()
        self.root.title("Enhanced Orthodontic Wire Generator - Height Control Ready")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Data structures
        self.generator = None
        self.stl_path = None
        self.current_gcode = ""
        
        # Wire generation parameters
        self.wire_size = tk.StringVar(value='0.018')
        self.arch_type = tk.StringVar(value='auto')
        self.bend_radius = tk.DoubleVar(value=2.0)
        self.wire_tension = tk.DoubleVar(value=1.0)
        self.feed_rate = tk.IntVar(value=1000)
        self.bend_speed = tk.IntVar(value=500)
        self.safety_height = tk.DoubleVar(value=10.0)
        
        # NEW: Height control parameters
        self.wire_height_offset = tk.DoubleVar(value=0.0)
        self.height_step = tk.DoubleVar(value=0.5)
        
        # Status variables
        self.processing_status = tk.StringVar(value="Ready")
        self.teeth_count = tk.StringVar(value="0")
        self.brackets_count = tk.StringVar(value="0")
        self.wire_length = tk.StringVar(value="0.0")
        self.bend_count = tk.StringVar(value="0")
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the main GUI interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Enhanced Orthodontic Wire Generator with Height Control",
            font=("Arial", 16, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Left panel - Controls
        self.setup_control_panel(main_frame)
        
        # Center panel - Status and 3D View
        self.setup_status_panel(main_frame)
        
        # Right panel - G-code Display
        self.setup_gcode_panel(main_frame)
        
        # Bottom panel - Action buttons
        self.setup_action_panel(main_frame)
    
    def setup_control_panel(self, parent):
        """Setup the left control panel."""
        control_frame = ttk.LabelFrame(parent, text="Wire Generation Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # STL File Loading
        stl_frame = ttk.LabelFrame(control_frame, text="STL File", padding="5")
        stl_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        stl_frame.columnconfigure(1, weight=1)
        
        ttk.Button(
            stl_frame,
            text="Load STL File",
            command=self.load_stl_file,
            style="Accent.TButton"
        ).grid(row=0, column=0, padx=(0, 10))
        
        self.stl_label = ttk.Label(stl_frame, text="No file selected", foreground="gray")
        self.stl_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Wire Parameters
        params_frame = ttk.LabelFrame(control_frame, text="Wire Parameters", padding="5")
        params_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Wire Size
        ttk.Label(params_frame, text="Wire Size:").grid(row=0, column=0, sticky=tk.W, pady=2)
        wire_combo = ttk.Combobox(
            params_frame,
            textvariable=self.wire_size,
            values=list(self.WIRE_SIZES.keys()),
            state="readonly",
            width=15
        )
        wire_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Arch Type
        ttk.Label(params_frame, text="Arch Type:").grid(row=1, column=0, sticky=tk.W, pady=2)
        arch_combo = ttk.Combobox(
            params_frame,
            textvariable=self.arch_type,
            values=["auto", "upper", "lower"],
            state="readonly",
            width=15
        )
        arch_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Bend Radius
        ttk.Label(params_frame, text="Bend Radius (mm):").grid(row=2, column=0, sticky=tk.W, pady=2)
        bend_radius_spin = ttk.Spinbox(
            params_frame,
            from_=0.5,
            to=10.0,
            increment=0.1,
            textvariable=self.bend_radius,
            width=15
        )
        bend_radius_spin.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Wire Tension
        ttk.Label(params_frame, text="Wire Tension:").grid(row=3, column=0, sticky=tk.W, pady=2)
        tension_spin = ttk.Spinbox(
            params_frame,
            from_=0.1,
            to=2.0,
            increment=0.1,
            textvariable=self.wire_tension,
            width=15
        )
        tension_spin.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # NEW: Height Control Parameters
        height_frame = ttk.LabelFrame(control_frame, text="Wire Height Control", padding="5")
        height_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Height Offset Display
        ttk.Label(height_frame, text="Height Offset (mm):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.height_display = ttk.Label(height_frame, textvariable=self.wire_height_offset, foreground="blue")
        self.height_display.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Height Step
        ttk.Label(height_frame, text="Height Step (mm):").grid(row=1, column=0, sticky=tk.W, pady=2)
        height_step_spin = ttk.Spinbox(
            height_frame,
            from_=0.1,
            to=2.0,
            increment=0.1,
            textvariable=self.height_step,
            width=15
        )
        height_step_spin.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Height Control Buttons
        height_buttons_frame = ttk.Frame(height_frame)
        height_buttons_frame.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        
        ttk.Button(
            height_buttons_frame,
            text="↑ UP",
            command=self.wire_up,
            width=8
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            height_buttons_frame,
            text="↓ DOWN", 
            command=self.wire_down,
            width=8
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            height_buttons_frame,
            text="Reset",
            command=self.reset_wire_height,
            width=8
        ).pack(side=tk.LEFT)
        
        # G-code Parameters
        gcode_frame = ttk.LabelFrame(control_frame, text="G-code Parameters", padding="5")
        gcode_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Feed Rate
        ttk.Label(gcode_frame, text="Feed Rate (mm/min):").grid(row=0, column=0, sticky=tk.W, pady=2)
        feed_spin = ttk.Spinbox(
            gcode_frame,
            from_=100,
            to=5000,
            increment=100,
            textvariable=self.feed_rate,
            width=15
        )
        feed_spin.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Bend Speed
        ttk.Label(gcode_frame, text="Bend Speed (mm/min):").grid(row=1, column=0, sticky=tk.W, pady=2)
        bend_spin = ttk.Spinbox(
            gcode_frame,
            from_=50,
            to=2000,
            increment=50,
            textvariable=self.bend_speed,
            width=15
        )
        bend_spin.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Safety Height
        ttk.Label(gcode_frame, text="Safety Height (mm):").grid(row=2, column=0, sticky=tk.W, pady=2)
        safety_spin = ttk.Spinbox(
            gcode_frame,
            from_=5.0,
            to=50.0,
            increment=1.0,
            textvariable=self.safety_height,
            width=15
        )
        safety_spin.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
    
    # NEW: Height control methods
    def wire_up(self):
        """Move wire up by step amount."""
        if not self.generator:
            messagebox.showerror("Error", "Please generate wire first!")
            return
        
        step = self.height_step.get()
        self.generator.adjust_wire_height(step)
        self.wire_height_offset.set(self.generator.wire_height_offset)
        print(f"Wire moved up by {step:.2f}mm")
    
    def wire_down(self):
        """Move wire down by step amount."""
        if not self.generator:
            messagebox.showerror("Error", "Please generate wire first!")
            return
        
        step = self.height_step.get()
        self.generator.adjust_wire_height(-step)
        self.wire_height_offset.set(self.generator.wire_height_offset)
        print(f"Wire moved down by {step:.2f}mm")
    
    def reset_wire_height(self):
        """Reset wire to original height."""
        if not self.generator:
            messagebox.showerror("Error", "Please generate wire first!")
            return
        
        self.generator.reset_wire_height()
        self.wire_height_offset.set(self.generator.wire_height_offset)
        print("Wire height reset to original position")
    
    def setup_status_panel(self, parent):
        """Setup the center status panel."""
        status_frame = ttk.LabelFrame(parent, text="Generation Status & 3D View", padding="10")
        status_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(1, weight=1)
        
        # Status Information
        info_frame = ttk.Frame(status_frame)
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        info_frame.columnconfigure(3, weight=1)
        
        # Status indicators
        ttk.Label(info_frame, text="Status:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W)
        status_label = ttk.Label(info_frame, textvariable=self.processing_status, foreground="blue")
        status_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(info_frame, text="Teeth:", font=("Arial", 9, "bold")).grid(row=0, column=2, sticky=tk.W)
        ttk.Label(info_frame, textvariable=self.teeth_count).grid(row=0, column=3, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(info_frame, text="Brackets:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W)
        ttk.Label(info_frame, textvariable=self.brackets_count).grid(row=1, column=1, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(info_frame, text="Wire Length:", font=("Arial", 9, "bold")).grid(row=1, column=2, sticky=tk.W)
        length_label = ttk.Label(info_frame, textvariable=self.wire_length)
        length_label.grid(row=1, column=3, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(info_frame, text="Bends:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky=tk.W)
        ttk.Label(info_frame, textvariable=self.bend_count).grid(row=2, column=1, sticky=tk.W, padx=(5, 20))
        
        # NEW: Height offset display
        ttk.Label(info_frame, text="Height Offset:", font=("Arial", 9, "bold")).grid(row=2, column=2, sticky=tk.W)
        ttk.Label(info_frame, textvariable=self.wire_height_offset, foreground="red").grid(row=2, column=3, sticky=tk.W, padx=(5, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(info_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 3D View placeholder
        view_frame = ttk.Frame(status_frame, relief="sunken", borderwidth=2)
        view_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        view_frame.columnconfigure(0, weight=1)
        view_frame.rowconfigure(0, weight=1)
        
        self.view_label = tk.Label(
            view_frame,
            text="3D Visualization with Height Control\n\nClick 'Launch 3D Editor'\nto open interactive view\n\nUse Up/Down arrows for height adjustment",
            bg="white",
            fg="gray",
            font=("Arial", 12),
            justify=tk.CENTER
        )
        self.view_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 3D Editor Button
        editor_btn = ttk.Button(
            status_frame,
            text="Launch 3D Interactive Editor with Height Control",
            command=self.launch_3d_editor,
            style="Accent.TButton"
        )
        editor_btn.grid(row=2, column=0, pady=(10, 0))
    
    def setup_gcode_panel(self, parent):
        """Setup the right G-code display panel."""
        gcode_frame = ttk.LabelFrame(parent, text="G-code Output", padding="10")
        gcode_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        gcode_frame.columnconfigure(0, weight=1)
        gcode_frame.rowconfigure(1, weight=1)
        
        # G-code controls
        controls_frame = ttk.Frame(gcode_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(
            controls_frame,
            text="Show G-code",
            command=self.display_gcode,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            controls_frame,
            text="Show ESP32 Code",
            command=self.display_esp32_code,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            controls_frame,
            text="Export Code",
            command=self.export_displayed_code,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            controls_frame,
            text="Clear",
            command=self.clear_gcode
        ).pack(side=tk.LEFT)

        # G-code display
        self.gcode_text = scrolledtext.ScrolledText(
            gcode_frame,
            width=50,
            height=30,
            font=("Consolas", 9),
            bg="black",
            fg="lime",
            insertbackground="lime",
            wrap=tk.NONE
        )
        self.gcode_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def display_gcode(self):
        """Display G-code in the text area."""
        if not self.generator:
            messagebox.showerror("Error", "Please generate wire first!")
            return
        gcode_content = self._generate_gcode_content()
        self.gcode_text.delete(1.0, tk.END)
        self.gcode_text.insert(1.0, gcode_content)
        self.displayed_code_type = 'gcode'
        self.displayed_code_content = gcode_content

    def display_esp32_code(self):
        """Display ESP32 Arduino code in the text area."""
        if not self.generator or self.generator.wire_path is None or len(self.generator.wire_path) < 2:
            messagebox.showerror("Error", "Please generate the wire first!")
            return
        code = self.generator.get_esp32_arduino_code()
        self.gcode_text.delete(1.0, tk.END)
        self.gcode_text.insert(1.0, code)
        self.displayed_code_type = 'esp32'
        self.displayed_code_content = code

    def export_displayed_code(self):
        """Export the currently displayed code to a file."""
        if not hasattr(self, 'displayed_code_content') or not self.displayed_code_content:
            messagebox.showerror("Error", "No code to export. Please display G-code or ESP32 code first.")
            return
        if self.displayed_code_type == 'gcode':
            filetypes = [("G-code files", "*.gcode"), ("Text files", "*.txt"), ("All files", "*.*")]
            defext = ".gcode"
        else:
            filetypes = [("Arduino INO files", "*.ino"), ("Text files", "*.txt"), ("All files", "*.*")]
            defext = ".ino"
        fpath = filedialog.asksaveasfilename(
            title="Export Displayed Code",
            defaultextension=defext,
            filetypes=filetypes
        )
        if not fpath:
            return
        try:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(self.displayed_code_content)
            messagebox.showinfo("Success", f"Code exported to:\n{os.path.basename(fpath)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export code:\n{str(e)}")
    
    def clear_gcode(self):
        """Clear G-code display."""
        self.gcode_text.delete(1.0, tk.END)
        self.current_gcode = ""
    
    def setup_action_panel(self, parent):
        """Setup the bottom action buttons."""
        action_frame = ttk.Frame(parent, padding="10")
        action_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Main action buttons
        ttk.Button(
            action_frame,
            text="Generate Wire",
            command=self.generate_wire,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            action_frame,
            text="Load Design",
            command=self.load_design
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            action_frame,
            text="Save Design",
            command=self.save_design
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            action_frame,
            text="Export STL",
            command=self.export_stl
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Right side buttons
        ttk.Button(
            action_frame,
            text="Help",
            command=self.show_help
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(
            action_frame,
            text="About",
            command=self.show_about
        ).pack(side=tk.RIGHT, padx=(10, 0))
    
    def load_stl_file(self):
        """Load STL file using file dialog."""
        file_path = filedialog.askopenfilename(
            title="Select STL File",
            filetypes=[
                ("STL files", "*.stl"),
                ("All files", "*.*")
            ],
            initialdir=os.getcwd()
        )
        
        if file_path:
            self.stl_path = file_path
            filename = os.path.basename(file_path)
            self.stl_label.config(text=f"✓ {filename}", foreground="green")
            
            # Auto-detect arch type from filename
            if 'lower' in filename.lower():
                self.arch_type.set('lower')
            elif 'upper' in filename.lower():
                self.arch_type.set('upper')
            else:
                self.arch_type.set('auto')
            
            self.processing_status.set("STL file loaded")
            messagebox.showinfo("Success", f"STL file loaded successfully:\n{filename}")
    
    def generate_wire(self):
        """Generate wire in a separate thread."""
        if not self.stl_path:
            messagebox.showerror("Error", "Please load an STL file first!")
            return
        
        # Start progress indication
        self.progress.start()
        self.processing_status.set("Generating wire...")
        
        # Run generation in separate thread to keep GUI responsive
        thread = threading.Thread(target=self._generate_wire_thread, daemon=True)
        thread.start()
    
    def _generate_wire_thread(self):
        """Wire generation thread."""
        try:
            # Create generator instance
            self.generator = EnhancedInteractiveWireGenerator(
                stl_path=self.stl_path,
                arch_type=self.arch_type.get(),
                wire_size=self.wire_size.get()
            )
            
            # Set parameters
            self.generator.bend_radius = self.bend_radius.get()
            self.generator.wire_tension = self.wire_tension.get()
            self.generator.height_adjustment_step = self.height_step.get()
            self.generator.gcode_settings.update({
                'feed_rate': self.feed_rate.get(),
                'bend_speed': self.bend_speed.get(),
                'safety_height': self.safety_height.get()
            })
            
            # Update status
            self.root.after(0, lambda: self.processing_status.set("Loading mesh..."))
            
            if not self.generator.load_mesh():
                raise Exception("Failed to load mesh")
            
            self.root.after(0, lambda: self.processing_status.set("Detecting teeth..."))
            
            if not self.generator.detect_teeth_simple():
                raise Exception("Failed to detect teeth")
            
            self.root.after(0, lambda: self.processing_status.set("Positioning brackets..."))
            self.generator.calculate_lingual_bracket_positions()
            
            self.root.after(0, lambda: self.processing_status.set("Creating wire path..."))
            if self.generator.create_smooth_wire_path_with_control_points() is None:
                raise Exception("Failed to create wire path")
            
            self.root.after(0, lambda: self.processing_status.set("Creating visualization..."))
            self.generator.create_enhanced_visualization_meshes()
            
            # Update GUI with results
            self.root.after(0, self._update_generation_results)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self._handle_generation_error(msg))
    
    def _update_generation_results(self):
        """Update GUI with generation results."""
        self.progress.stop()
        
        if self.generator:
            # Update status
            self.processing_status.set("Wire generated successfully!")
            self.teeth_count.set(str(len(self.generator.teeth)))
            self.brackets_count.set(str(sum(1 for b in self.generator.bracket_positions if b['visible'])))
            
            # Update height offset display
            self.wire_height_offset.set(self.generator.wire_height_offset)
            
            # Calculate wire length
            if self.generator.wire_path is not None:
                total_length = 0
                for i in range(len(self.generator.wire_path) - 1):
                    total_length += np.linalg.norm(
                        self.generator.wire_path[i+1] - self.generator.wire_path[i]
                    )
                self.wire_length.set(f"{total_length:.1f}mm")
            
            # Update 3D view placeholder
            self.view_label.config(
                text="3D Model Generated!\n\nTooth detection: ✓\nBracket positioning: ✓\nWire path: ✓\nHeight control: ✓\n\nClick 'Launch 3D Editor'\nfor interactive height adjustment",
                fg="green"
            )
            
            messagebox.showinfo(
                "Success",
                f"Wire generated successfully!\n\n"
                f"Teeth detected: {len(self.generator.teeth)}\n"
                f"Brackets positioned: {sum(1 for b in self.generator.bracket_positions if b['visible'])}\n"
                f"Wire length: {self.wire_length.get()}\n"
                f"Height control: Ready\n\n"
                f"You can now:\n"
                f"• Use Up/Down buttons for height adjustment\n"
                f"• Launch 3D Editor for interactive editing\n"
                f"• Generate G-code with height information\n"
                f"• Save the design"
            )
    
    def _handle_generation_error(self, error_msg):
        """Handle generation errors."""
        self.progress.stop()
        self.processing_status.set("Generation failed")
        messagebox.showerror("Generation Error", f"Failed to generate wire:\n\n{error_msg}")
    
    def launch_3d_editor(self):
        """Launch the 3D interactive editor."""
        if not self.generator:
            messagebox.showerror("Error", "Please generate wire first!")
            return
        
        try:
            # Sync GUI height settings with generator
            self.generator.height_adjustment_step = self.height_step.get()
            
            # Launch 3D editor in separate thread
            thread = threading.Thread(
                target=self.generator.visualize_enhanced_interactive,
                daemon=True
            )
            thread.start()
            
            messagebox.showinfo(
                "3D Editor with Height Control",
                "3D Interactive Editor launched!\n\n"
                "Height Control Features:\n"
                "• Up/Down arrows: Move entire wire\n"
                "• Shift + Mouse: Drag wire height\n"
                "• Individual control point editing\n"
                "• Real-time G-code updates\n\n"
                "See console for complete keyboard controls."
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch 3D editor:\n{str(e)}")
    
    def _generate_gcode_content(self):
        """Generate G-code content string with height information."""
        # Calculate bends
        bends = self.generator.calculate_wire_bends()
        
        # Calculate total wire length
        total_length = 0
        if len(self.generator.wire_path) > 1:
            for i in range(len(self.generator.wire_path) - 1):
                total_length += np.linalg.norm(
                    self.generator.wire_path[i+1] - self.generator.wire_path[i]
                )
        
        # Generate G-code lines
        lines = []
        
        # Header with height information
        lines.extend([
            "; Generated by Enhanced Interactive Orthodontic Wire Generator GUI",
            f"; Date: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"; Arch Type: {self.generator.arch_type.upper()}",
            f"; Wire Size: {self.generator.wire_size}",
            f"; Total Wire Length: {total_length:.2f}mm",
            f"; Wire Height Offset: {self.generator.wire_height_offset:.2f}mm",
            f"; Number of Bends: {len(bends)}",
            f"; Feed Rate: {self.feed_rate.get()} mm/min",
            f"; Bend Speed: {self.bend_speed.get()} mm/min",
            f"; Safety Height: {self.safety_height.get()}mm",
            ";",
            "G21 ; Set units to millimeters",
            "G90 ; Absolute positioning",
            "G28 ; Home all axes",
            f"F{self.feed_rate.get()} ; Set feed rate",
            "M117 Wire Bending Started",
            "",
        ])
        
        # Wire preparation
        lines.extend([
            "; Prepare wire",
            f"G0 X10 Y0 Z{self.safety_height.get()}",
            "M3 ; Clamp wire",
            "G4 P500 ; Wait 0.5 seconds",
            "",
        ])
        
        # Process each bend with height offset information
        current_wire_length = 0
        
        for i, bend in enumerate(bends):
            feed_length = bend['wire_length'] - current_wire_length
            
            lines.extend([
                f"; Bend {i+1}: {bend['angle']:.1f}° {bend['direction']} (Height offset: {self.generator.wire_height_offset:.2f}mm)",
                f"M6 S{feed_length:.2f} ; Feed wire {feed_length:.2f}mm",
                "G4 P200 ; Wait for wire feed",
                f"G0 Z{self.safety_height.get()} ; Safety height",
                f"G0 X{bend['position'][0]:.2f} Y{bend['position'][1]:.2f}",
                f"G1 Z{bend['position'][2]:.2f} F{self.bend_speed.get()}",
                f"M5 A{bend['angle']:.1f} R{bend['radius']:.1f} D{bend['direction'][0].upper()}",
                "G4 P1000 ; Wait for bend",
                f"G0 Z{self.safety_height.get()}",
                "",
            ])
            
            current_wire_length = bend['wire_length']
        
        # Finish
        remaining_length = total_length - current_wire_length
        lines.extend([
            "; Final operations",
            f"M6 S{remaining_length:.2f} ; Feed remaining wire",
            "M4 ; Release wire clamp",
            "G28 ; Home position",
            "M117 Wire Bending Complete",
            f"; Total time: {self.generator._estimate_bend_time(bends, total_length):.1f} minutes",
            f"; Final wire height offset: {self.generator.wire_height_offset:.2f}mm",
            "M30 ; Program end",
        ])
        
        return '\n'.join(lines)
    
    def save_design(self):
        """Save wire design to JSON file."""
        if not self.generator:
            messagebox.showerror("Error", "No design to save! Generate wire first.")
            return
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        default_filename = f"wire_design_height_{self.generator.arch_type}_{timestamp}.json"
        
        file_path = filedialog.asksaveasfilename(
            title="Save Design File",
            defaultextension=".json",
            initialfile=default_filename,
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                filename = self.generator.save_enhanced_design()
                if filename:
                    # Copy to selected location if different
                    if filename != file_path:
                        import shutil
                        shutil.copy(filename, file_path)
                    messagebox.showinfo("Success", f"Design with height control saved:\n{os.path.basename(file_path)}")
                else:
                    messagebox.showerror("Error", "Failed to save design file.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save design:\n{str(e)}")
    
    def load_design(self):
        """Load wire design from JSON file."""
        file_path = filedialog.askopenfilename(
            title="Load Design File",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    design_data = json.load(f)
                
                # Update GUI parameters from loaded design
                if 'metadata' in design_data:
                    metadata = design_data['metadata']
                    if 'wire_size' in metadata:
                        self.wire_size.set(metadata['wire_size'])
                    if 'arch_type' in metadata:
                        self.arch_type.set(metadata['arch_type'])
                
                # Load height control data
                if 'wire_height_offset' in design_data:
                    self.wire_height_offset.set(design_data['wire_height_offset'])
                
                if 'bending_parameters' in design_data:
                    params = design_data['bending_parameters']
                    if 'bend_radius' in params:
                        self.bend_radius.set(params['bend_radius'])
                    if 'wire_tension' in params:
                        self.wire_tension.set(params['wire_tension'])
                    if 'height_adjustment_step' in params:
                        self.height_step.set(params['height_adjustment_step'])
                
                if 'gcode_settings' in design_data:
                    settings = design_data['gcode_settings']
                    if 'feed_rate' in settings:
                        self.feed_rate.set(settings['feed_rate'])
                    if 'bend_speed' in settings:
                        self.bend_speed.set(settings['bend_speed'])
                    if 'safety_height' in settings:
                        self.safety_height.set(settings['safety_height'])
                
                messagebox.showinfo(
                    "Design Loaded",
                    f"Design with height control loaded!\n\n"
                    f"File: {os.path.basename(file_path)}\n"
                    f"Wire Size: {self.wire_size.get()}\n"
                    f"Arch Type: {self.arch_type.get()}\n"
                    f"Height Offset: {self.wire_height_offset.get():.2f}mm\n\n"
                    f"Please load the corresponding STL file and regenerate the wire."
                )
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load design:\n{str(e)}")
    
    def export_stl(self):
        """Export wire mesh as STL file."""
        if not self.generator or not hasattr(self.generator, 'wire_mesh'):
            messagebox.showerror("Error", "No wire mesh to export! Generate wire first.")
            return
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        height_suffix = f"_h{self.generator.wire_height_offset:.1f}mm".replace(".", "p")
        default_filename = f"orthodontic_wire_{self.generator.arch_type}{height_suffix}_{timestamp}.stl"
        
        file_path = filedialog.asksaveasfilename(
            title="Export Wire STL",
            defaultextension=".stl",
            initialfile=default_filename,
            filetypes=[
                ("STL files", "*.stl"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                o3d.io.write_triangle_mesh(file_path, self.generator.wire_mesh)
                messagebox.showinfo("Success", f"Wire STL exported with height offset:\n{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export STL:\n{str(e)}")
    
    def show_help(self):
        """Show help dialog."""
        help_text = """
Enhanced Orthodontic Wire Generator - Help (with Height Control)

WORKFLOW:
1. Load STL File - Click 'Load STL File' to select dental model
2. Set Parameters - Configure wire size, arch type, and height controls
3. Generate Wire - Click 'Generate Wire' to process the model
4. Height Adjustment - Use Up/Down buttons or 3D editor for height control
5. Launch 3D Editor - Interactive editing with real-time height adjustment
6. Generate G-code - Create Arduino-compatible commands with height data
7. Save/Export - Save design or export wire mesh with height information

NEW HEIGHT CONTROL FEATURES:
• Up/Down Buttons: Quickly adjust wire height in GUI
• Height Step: Configurable step size for adjustments
• 3D Editor Height Control: Up/Down arrow keys for real-time adjustment
• Mouse Dragging: Shift + Mouse drag for precise height control
• Height Reset: Return wire to original position
• G-code Integration: Height offset included in generated G-code

3D EDITOR CONTROLS:
• Up/Down Arrows: Move entire wire up/down
• Shift + Mouse Drag: Drag wire height with mouse
• Left/Right Arrows: Move selected control point horizontally
• Page Up/Down: Move selected control point vertically (individual)
• Q: Quit 3D editor
• H: Show help in 3D editor
• R: Reset wire height to original position
• O: Display current height offset
• Mouse: Navigate (rotate, pan, zoom)

HEIGHT CONTROL PARAMETERS:
• Height Offset: Current vertical offset of wire (displayed in real-time)
• Height Step: Amount wire moves per button press (0.1-2.0mm)
• Reset Function: Returns wire to original anatomical position

G-CODE FEATURES:
• Arduino-compatible commands with height information
• Wire feeding control (M6)
• Wire clamping (M3/M4)
• Precision bending (M5) with height-adjusted coordinates
• Safety positioning with height offset consideration
• Height offset documentation in G-code comments

SUPPORTED FILES:
• Input: STL dental models
• Output: JSON design files (with height data), G-code, STL wire mesh

The height control system allows precise vertical positioning of the wire
relative to the dental anatomy, enabling optimal clinical fit and comfort.

For technical support, refer to the documentation or contact support.
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Wire Generator with Height Control")
        help_window.geometry("700x600")
        help_window.configure(bg='#f0f0f0')
        
        help_frame = ttk.Frame(help_window, padding="20")
        help_frame.pack(fill=tk.BOTH, expand=True)
        
        help_display = scrolledtext.ScrolledText(
            help_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            height=30
        )
        help_display.pack(fill=tk.BOTH, expand=True)
        help_display.insert(1.0, help_text)
        help_display.config(state=tk.DISABLED)
        
        ttk.Button(
            help_frame,
            text="Close",
            command=help_window.destroy
        ).pack(pady=(10, 0))
    
    def show_about(self):
        """Show about dialog."""
        about_text = """Enhanced Orthodontic Wire Generator v2.1 - Height Control Edition

A comprehensive solution for generating custom orthodontic wires with:
• Advanced tooth detection and bracket positioning
• Interactive 3D wire editing with height control
• Real-time G-code generation for Arduino-controlled machines
• Professional-grade visualization and export capabilities

NEW HEIGHT CONTROL FEATURES:
✓ Real-time wire height adjustment
✓ GUI-based Up/Down controls
✓ 3D editor height manipulation
✓ Mouse drag height adjustment
✓ Height offset tracking and display
✓ G-code integration with height data

Core Features:
✓ STL dental model processing
✓ Automatic tooth classification
✓ Lingual bracket positioning
✓ Interactive control point editing
✓ Wire bending simulation
✓ G-code generation for CNC/Arduino
✓ Design save/load functionality
✓ STL wire mesh export with height information

Developed for precision orthodontic wire manufacturing and research
with enhanced clinical control over wire positioning.

© 2024 Enhanced Wire Generator Project - Height Control Edition
Licensed under MIT License"""
        
        messagebox.showinfo("About - Height Control Edition", about_text)
    
    def run(self):
        """Start the GUI application."""
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure(
            "Accent.TButton",
            background="#0078d4",
            foreground="white",
            font=("Arial", 9, "bold")
        )
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap('wire_icon.ico')
        except:
            pass
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1400x900+{x}+{y}")
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        print("\n" + "="*70)
        print("ENHANCED ORTHODONTIC WIRE GENERATOR GUI - HEIGHT CONTROL EDITION")
        print("Height Control • Interactive 3D Editing • G-code Ready • Professional Grade")
        print("="*70)
        
        # Start the GUI
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing."""
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.root.destroy()


# --- Main entry point ---
def main():
    """Main entry point for the enhanced wire generator with height control."""
    app = WireGeneratorGUI()
    app.run()

if __name__ == "__main__":
    main()

