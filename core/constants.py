#!/usr/bin/env python3
"""
Supporting Classes for the Modular Wire Generator
================================================
This file contains several key supporting classes that work together
to provide the core functionality.
"""

# core/constants.py
"""Constants and configurations for the wire generator."""

import numpy as np

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

# Tooth classification constants
TOOTH_TYPES = {
    'incisor': {'count_range': (2, 4), 'position': 'anterior'},
    'canine': {'count_range': (1, 2), 'position': 'anterior'},
    'premolar': {'count_range': (0, 4), 'position': 'posterior'},
    'molar': {'count_range': (0, 6), 'position': 'posterior'}
}

# Clinical parameters
BRACKET_HEIGHTS = {
    'incisor': 3.5,   # mm from gum line
    'canine': 4.0,
    'premolar': 4.5,
    'molar': 5.0
}

CLINICAL_OFFSETS = {
    'lingual': 2.0,   # mm inward from tooth surface
    'labial': 1.5     # mm outward from tooth surface
}


# ================================================================
# core/mesh_processor.py
"""STL mesh loading and preprocessing."""

import open3d as o3d
import numpy as np

class MeshProcessor:
    """Handles STL file loading and mesh preprocessing."""
    
    def __init__(self):
        """Initialize mesh processor."""
        pass
    
    def load_stl(self, stl_path: str) -> o3d.geometry.TriangleMesh:
        """Load STL file and return processed mesh."""
        try:
            mesh = o3d.io.read_triangle_mesh(stl_path)
            if not mesh.has_triangles():
                raise ValueError("No triangles found in mesh")
            
            print(f"Loaded STL: {len(mesh.vertices)} vertices, {len(mesh.triangles)} triangles")
            return mesh
            
        except Exception as e:
            print(f"Error loading STL: {e}")
            return None
    
    def clean_mesh(self, mesh: o3d.geometry.TriangleMesh) -> o3d.geometry.TriangleMesh:
        """Clean and prepare mesh for processing."""
        # Remove duplicates and degenerates
        mesh.remove_duplicated_vertices()
        mesh.remove_degenerate_triangles()
        
        # Compute normals
        mesh.compute_vertex_normals()
        mesh.compute_triangle_normals()
        
        # Set natural tooth color
        mesh.paint_uniform_color([0.95, 0.93, 0.88])
        
        return mesh
    
    def calculate_arch_center(self, mesh: o3d.geometry.TriangleMesh) -> np.ndarray:
        """Calculate the center of the dental arch."""
        return mesh.get_center()


# ================================================================
# wire/height_controller.py
"""Wire height adjustment controller."""

class HeightController:
    """Manages wire height adjustments and offsets."""
    
    def __init__(self, initial_offset: float = 0.0, step_size: float = 0.5):
        """Initialize height controller."""
        self.height_offset = initial_offset
        self.step_size = step_size
        self.original_offset = initial_offset
    
    def adjust_height(self, delta: float):
        """Adjust wire height by delta amount."""
        self.height_offset += delta
        print(f"Height adjusted by {delta:.2f}mm (total: {self.height_offset:.2f}mm)")
    
    def set_height(self, new_height: float):
        """Set absolute height offset."""
        self.height_offset = new_height
    
    def reset_height(self):
        """Reset height to original position."""
        self.height_offset = self.original_offset
    
    def get_height_offset(self) -> float:
        """Get current height offset."""
        return self.height_offset
    
    def get_step_size(self) -> float:
        """Get current step size."""
        return self.step_size
    
    def set_step_size(self, step: float):
        """Set height adjustment step size."""
        self.step_size = max(0.1, min(5.0, step))  # Clamp between 0.1 and 5.0mm


# ================================================================
# visualization/control_point_manager.py
"""Control point selection and manipulation."""

import numpy as np
from typing import Optional, List, Dict

class ControlPointManager:
    """Manages control point selection and manipulation."""
    
    def __init__(self):
        """Initialize control point manager."""
        self.control_points = []
        self.selected_index = None
        self.wire_path_creator = None
        self.wire_mesh_builder = None
    
    def setup(self, control_points: List[Dict], 
              wire_path_creator, wire_mesh_builder):
        """Setup with control points and generators."""
        self.control_points = control_points
        self.wire_path_creator = wire_path_creator
        self.wire_mesh_builder = wire_mesh_builder
    
    def select_control_point(self, index: int) -> bool:
        """Select a control point by index."""
        if 0 <= index < len(self.control_points):
            self.selected_index = index
            cp = self.control_points[index]
            print(f"Selected control point {index} ({cp['type']})")
            return True
        return False
    
    def deselect_control_point(self):
        """Deselect current control point."""
        self.selected_index = None
        print("Control point deselected")
    
    def move_selected_point(self, direction: np.ndarray, step: float = 0.5) -> bool:
        """Move the selected control point."""
        if self.selected_index is None:
            return False
        
        # Update position in data model
        self.control_points[self.selected_index]['position'] += direction * step
        
        # Update in wire path creator
        if self.wire_path_creator:
            self.wire_path_creator.update_control_point(
                self.selected_index,
                self.control_points[self.selected_index]['position']
            )
        
        print(f"Moved control point {self.selected_index} by {direction * step}")
        return True
    
    def adjust_bend_angle(self, angle_delta: float) -> bool:
        """Adjust bend angle at selected control point."""
        if self.selected_index is None:
            return False
        
        if self.wire_path_creator:
            self.wire_path_creator.adjust_bend_angle(self.selected_index, angle_delta)
            print(f"Adjusted bend angle by {angle_delta:.1f}°")
            return True
        return False
    
    def get_selected_control_point(self) -> Optional[Dict]:
        """Get currently selected control point."""
        if self.selected_index is not None:
            return self.control_points[self.selected_index]
        return None


# ================================================================
# core/tooth_detector.py
"""Tooth detection and classification algorithms."""

import numpy as np
from typing import List, Dict

class ToothDetector:
    """Detects and classifies teeth from dental meshes."""
    
    def __init__(self):
        """Initialize tooth detector."""
        self.detection_parameters = {
            'crown_ratio_upper': 0.25,
            'crown_ratio_lower': 0.75,
            'height_tolerance': 2.0,
            'min_tooth_vertices': 30,
            'min_tooth_spacing': 3.0
        }
    
    def detect_teeth(self, mesh, arch_type: str) -> List[Dict]:
        """Detect teeth from mesh using angular segmentation."""
        vertices = np.asarray(mesh.vertices)
        bbox = mesh.get_axis_aligned_bounding_box()
        center = mesh.get_center()
        extent = bbox.get_extent()
        
        # Identify anatomical axes
        lr_axis = np.argmax(extent)  # Left-Right (widest)
        height_axis = np.argmin(extent)  # Occlusal-Gingival (smallest)
        ap_axis = 3 - lr_axis - height_axis  # Anterior-Posterior
        
        # Sample at crown level
        crown_ratio = (self.detection_parameters['crown_ratio_upper'] if arch_type == 'upper' 
                      else self.detection_parameters['crown_ratio_lower'])
        crown_level = bbox.min_bound[height_axis] + extent[height_axis] * crown_ratio
        
        # Get crown vertices
        height_tolerance = self.detection_parameters['height_tolerance']
        crown_mask = np.abs(vertices[:, height_axis] - crown_level) < height_tolerance
        crown_vertices = vertices[crown_mask]
        
        if len(crown_vertices) < 100:
            print("Warning: Very few crown vertices detected")
            return []
        
        # Angular segmentation
        teeth = self._angular_segmentation(crown_vertices, center, lr_axis, ap_axis)
        
        print(f"Detected {len(teeth)} teeth using angular segmentation")
        return teeth
    
    def _angular_segmentation(self, crown_vertices: np.ndarray, center: np.ndarray,
                            lr_axis: int, ap_axis: int) -> List[Dict]:
        """Segment teeth using angular analysis."""
        # Calculate angles
        angles = np.arctan2(
            crown_vertices[:, ap_axis] - center[ap_axis],
            crown_vertices[:, lr_axis] - center[lr_axis]
        )
        
        # Find posterior gap (largest gap between teeth)
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
            
            if len(segment_vertices) < self.detection_parameters['min_tooth_vertices']:
                continue
            
            # Calculate tooth center
            tooth_center = np.mean(segment_vertices, axis=0)
            tooth_angle = np.arctan2(
                tooth_center[ap_axis] - center[ap_axis],
                tooth_center[lr_axis] - center[lr_axis]
            )
            
            teeth.append({
                'center': tooth_center,
                'vertices': segment_vertices,
                'angle': tooth_angle,
                'ap_position': tooth_center[ap_axis],
                'lr_position': tooth_center[lr_axis],
                'index': len(teeth),
                'type': 'posterior'  # Will be classified later
            })
        
        # Filter teeth that are too close together
        return self._filter_close_teeth(teeth)
    
    def _filter_close_teeth(self, teeth: List[Dict]) -> List[Dict]:
        """Remove teeth that are too close to each other."""
        if not teeth:
            return []
        
        filtered_teeth = []
        sorted_teeth = sorted(teeth, key=lambda t: t['angle'])
        min_spacing = self.detection_parameters['min_tooth_spacing']
        
        for tooth in sorted_teeth:
            if not filtered_teeth:
                filtered_teeth.append(tooth)
            else:
                # Check distance to previous tooth
                prev_tooth = filtered_teeth[-1]
                dist = np.linalg.norm(tooth['center'] - prev_tooth['center'])
                if dist > min_spacing:
                    filtered_teeth.append(tooth)
        
        return filtered_teeth
    
    def classify_teeth(self, teeth: List[Dict], arch_center: np.ndarray) -> List[Dict]:
        """Classify teeth into incisors, canines, and posterior."""
        if len(teeth) < 6:
            print("Not enough teeth for classification")
            return teeth
        
        # Reset all to posterior
        for tooth in teeth:
            tooth['type'] = 'posterior'
        
        # Sort by anterior position (most anterior first)
        teeth_by_ap = sorted(teeth, key=lambda t: t['ap_position'], reverse=True)
        
        # Take the 6 most anterior teeth
        anterior_6 = teeth_by_ap[:6]
        
        # Sort by left-right position
        anterior_6_by_lr = sorted(anterior_6, key=lambda t: t['lr_position'])
        
        # Assign types to anterior teeth
        if len(anterior_6_by_lr) >= 6:
            # Canines (outermost)
            anterior_6_by_lr[0]['type'] = 'canine'
            anterior_6_by_lr[5]['type'] = 'canine'
            
            # Incisors (inner 4)
            for i in range(1, 5):
                anterior_6_by_lr[i]['type'] = 'incisor'
        
        # Count classification results
        classification_counts = {}
        for tooth in teeth:
            tooth_type = tooth['type']
            classification_counts[tooth_type] = classification_counts.get(tooth_type, 0) + 1
        
        print("Tooth classification:")
        for tooth_type, count in classification_counts.items():
            print(f"  • {tooth_type.title()}: {count}")
        
        return teeth


# ================================================================
# core/bracket_positioner.py
"""Bracket positioning algorithms for lingual orthodontics."""

import numpy as np
from typing import List, Dict
from .constants import BRACKET_HEIGHTS, CLINICAL_OFFSETS

class BracketPositioner:
    """Calculates optimal bracket positions on teeth."""
    
    def __init__(self, surface_type: str = 'lingual'):
        """Initialize bracket positioner."""
        self.surface_type = surface_type
        self.clinical_offset = CLINICAL_OFFSETS[surface_type]
    
    def calculate_positions(self, teeth: List[Dict], mesh, arch_center: np.ndarray, 
                          arch_type: str) -> List[Dict]:
        """Calculate bracket positions for all teeth."""
        bracket_positions = []
        
        for i, tooth in enumerate(teeth):
            bracket_pos = self._calculate_single_bracket(
                tooth, mesh, arch_center, arch_type, i
            )
            bracket_positions.append(bracket_pos)
        
        print(f"Positioned {len(bracket_positions)} brackets ({self.surface_type})")
        return bracket_positions
    
    def _calculate_single_bracket(self, tooth: Dict, mesh, arch_center: np.ndarray,
                                arch_type: str, tooth_index: int) -> Dict:
        """Calculate bracket position for a single tooth."""
        tooth_type = tooth.get('type', 'posterior')
        tooth_center = tooth['center']
        tooth_vertices = tooth['vertices']
        
        # Get bracket height based on tooth type
        bracket_height = BRACKET_HEIGHTS.get(tooth_type, 4.5)
        
        # Calculate target height on tooth
        height_axis = 2  # Typically Z-axis
        if arch_type == 'upper':
            target_height = np.min(tooth_vertices[:, height_axis]) + bracket_height
        else:
            target_height = np.max(tooth_vertices[:, height_axis]) - bracket_height
        
        # Find bracket position on lingual surface
        bracket_pos = self._find_lingual_position(
            tooth_vertices, tooth_center, arch_center, target_height, height_axis
        )
        
        # Calculate surface normal
        normal = self._calculate_surface_normal(tooth_center, arch_center)
        
        # Apply clinical offset
        bracket_pos = bracket_pos + normal * self.clinical_offset
        
        # Determine visibility (only posterior teeth get brackets in this example)
        visible = tooth_type == 'posterior'
        
        return {
            'position': bracket_pos,
            'tooth_type': tooth_type,
            'tooth_index': tooth_index,
            'tooth_center': tooth_center,
            'normal': normal,
            'height': bracket_height,
            'surface': self.surface_type,
            'visible': visible,
            'original_position': bracket_pos.copy()
        }
    
    def _find_lingual_position(self, tooth_vertices: np.ndarray, tooth_center: np.ndarray,
                             arch_center: np.ndarray, target_height: float, 
                             height_axis: int) -> np.ndarray:
        """Find position on lingual (inner) surface of tooth."""
        # Get vertices at bracket level
        height_tolerance = 2.0
        bracket_level_mask = np.abs(tooth_vertices[:, height_axis] - target_height) < height_tolerance
        bracket_level_vertices = tooth_vertices[bracket_level_mask]
        
        if len(bracket_level_vertices) < 10:
            # Fallback to tooth center at target height
            bracket_pos = tooth_center.copy()
            bracket_pos[height_axis] = target_height
            return bracket_pos
        
        # Calculate radial direction (outward from arch center)
        tooth_horizontal = tooth_center.copy()
        tooth_horizontal[height_axis] = 0
        center_horizontal = arch_center.copy()
        center_horizontal[height_axis] = 0
        
        radial_vector = tooth_horizontal - center_horizontal
        if np.linalg.norm(radial_vector) > 0:
            radial_direction = radial_vector / np.linalg.norm(radial_vector)
        else:
            radial_direction = np.array([1, 0, 0])
        
        # Find innermost vertices (lingual side)
        radial_distances = []
        for vertex in bracket_level_vertices:
            vertex_horizontal = vertex.copy()
            vertex_horizontal[height_axis] = 0
            vertex_radial = vertex_horizontal - center_horizontal
            radial_dist = np.dot(vertex_radial, radial_direction)
            radial_distances.append(radial_dist)
        
        radial_distances = np.array(radial_distances)
        
        # Get lingual vertices (15th percentile = innermost)
        percentile_15 = np.percentile(radial_distances, 15)
        lingual_mask = radial_distances <= percentile_15
        lingual_vertices = bracket_level_vertices[lingual_mask]
        
        if len(lingual_vertices) > 3:
            return np.mean(lingual_vertices, axis=0)
        else:
            return bracket_level_vertices[np.argmin(radial_distances)]
    
    def _calculate_surface_normal(self, tooth_center: np.ndarray, 
                                arch_center: np.ndarray) -> np.ndarray:
        """Calculate surface normal for bracket orientation."""
        # For lingual surface, normal points inward (toward arch center)
        horizontal_vector = tooth_center - arch_center
        horizontal_vector[2] = 0  # Remove height component
        
        if np.linalg.norm(horizontal_vector) > 0:
            if self.surface_type == 'lingual':
                return -horizontal_vector / np.linalg.norm(horizontal_vector)  # Inward
            else:
                return horizontal_vector / np.linalg.norm(horizontal_vector)   # Outward
        else:
            return np.array([0, -1, 0])  # Default direction