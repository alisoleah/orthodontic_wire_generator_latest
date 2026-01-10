
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
        self.clinical_offset = CLINICAL_OFFSETS.get(surface_type, 2.0)
        self.positioning_parameters = {
            'height_tolerance': 1.5,  # Reduced for more precise positioning
            'percentile_threshold': 10,  # Use 10th percentile for true lingual surface
            'min_vertices_for_positioning': 10,
            'surface_offset': 0.5  # mm - minimal offset to prevent penetration
        }
        
    def calculate_positions(self, teeth: List[Dict], mesh, arch_center: np.ndarray, 
                          arch_type: str) -> List[Dict]:
        """Calculate bracket positions for all teeth."""
        bracket_positions = []
        
        for i, tooth in enumerate(teeth):
            bracket_pos = self._calculate_single_bracket(
                tooth, mesh, arch_center, arch_type, i
            )
            bracket_positions.append(bracket_pos)
        
        visible_count = sum(1 for b in bracket_positions if b['visible'])
        print(f"Positioned {len(bracket_positions)} brackets ({visible_count} visible)")
        
        return bracket_positions
    
    def _calculate_single_bracket(self, tooth: Dict, mesh, arch_center: np.ndarray,
                                arch_type: str, tooth_index: int) -> Dict:
        """Calculate bracket position for a single tooth using ACTUAL tooth surface."""
        tooth_type = tooth.get('type', 'posterior')
        tooth_center = tooth['center']
        tooth_vertices = tooth['vertices']
        
        # Get bracket height based on tooth type
        bracket_height = BRACKET_HEIGHTS.get(tooth_type, 3.5)
        
        # Calculate target height on tooth - USE TOOTH CENTER HEIGHT
        height_axis = 2  # Z-axis
        
        # Use tooth center height as reference (more stable)
        center_height = tooth_center[height_axis]
        
        # Position bracket at center height (not min/max)
        # This keeps wire at mid-tooth level, preventing collision
        target_height = center_height
        
        # Find TRUE lingual surface position
        bracket_pos = self._find_true_lingual_surface(
            tooth_vertices, tooth_center, arch_center, target_height, height_axis
        )
        
        # Calculate surface normal pointing OUTWARD from tooth
        normal = self._calculate_tooth_surface_normal(
            bracket_pos, tooth_vertices, arch_center
        )
        
        # Apply MINIMAL offset to prevent penetration (0.5mm)
        # This keeps wire very close to tooth surface
        surface_offset = self.positioning_parameters['surface_offset']
        bracket_pos = bracket_pos + normal * surface_offset
        
        # Determine visibility (only frontal teeth get brackets: incisors and canines)
        visible = tooth_type in ['incisor', 'canine']
        
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
    
    def _find_true_lingual_surface(self, tooth_vertices: np.ndarray, tooth_center: np.ndarray,
                             arch_center: np.ndarray, target_height: float, 
                             height_axis: int) -> np.ndarray:
        """
        Find TRUE lingual (inner) surface position using proper surface detection.
        
        This method finds the actual innermost surface of the tooth at the target height.
        """
        # Get vertices at bracket level (tight tolerance for precision)
        height_tolerance = self.positioning_parameters['height_tolerance']
        bracket_level_mask = np.abs(tooth_vertices[:, height_axis] - target_height) < height_tolerance
        bracket_level_vertices = tooth_vertices[bracket_level_mask]
        
        min_vertices = self.positioning_parameters['min_vertices_for_positioning']
        if len(bracket_level_vertices) < min_vertices:
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
        
        # Calculate radial distances for all vertices at this height
        radial_distances = []
        for vertex in bracket_level_vertices:
            vertex_horizontal = vertex.copy()
            vertex_horizontal[height_axis] = 0
            vertex_radial = vertex_horizontal - center_horizontal
            radial_dist = np.dot(vertex_radial, radial_direction)
            radial_distances.append(radial_dist)
        
        radial_distances = np.array(radial_distances)
        
        # Use 10th percentile to find TRUE innermost surface (more aggressive)
        percentile_threshold = self.positioning_parameters['percentile_threshold']
        percentile_value = np.percentile(radial_distances, percentile_threshold)
        lingual_mask = radial_distances <= percentile_value
        lingual_vertices = bracket_level_vertices[lingual_mask]
        
        if len(lingual_vertices) > 3:
            # Average of innermost vertices = true lingual surface
            return np.mean(lingual_vertices, axis=0)
        else:
            # Use single innermost vertex
            return bracket_level_vertices[np.argmin(radial_distances)]
    
    def _calculate_tooth_surface_normal(self, surface_point: np.ndarray,
                                       tooth_vertices: np.ndarray,
                                       arch_center: np.ndarray) -> np.ndarray:
        """
        Calculate surface normal at the bracket position pointing OUTWARD from tooth.
        
        This ensures the wire sits outside the tooth surface, preventing penetration.
        """
        # Find nearby vertices to estimate local surface normal
        distances = np.linalg.norm(tooth_vertices - surface_point, axis=1)
        nearby_indices = np.argsort(distances)[:10]  # 10 nearest vertices
        nearby_vertices = tooth_vertices[nearby_indices]
        
        # Calculate normal using PCA of nearby vertices
        centered = nearby_vertices - surface_point
        cov_matrix = np.cov(centered.T)
        eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
        
        # Normal is the eigenvector with smallest eigenvalue (perpendicular to surface)
        normal_idx = np.argmin(eigenvalues)
        normal = eigenvectors[:, normal_idx].real
        
        # Ensure normal points OUTWARD (away from arch center)
        to_center = arch_center - surface_point
        if np.dot(normal, to_center) > 0:
            normal = -normal  # Flip if pointing inward
        
        # Normalize
        if np.linalg.norm(normal) > 0:
            normal = normal / np.linalg.norm(normal)
        else:
            # Fallback: radial direction
            horizontal_vector = surface_point - arch_center
            horizontal_vector[2] = 0
            if np.linalg.norm(horizontal_vector) > 0:
                normal = horizontal_vector / np.linalg.norm(horizontal_vector)
            else:
                normal = np.array([0, 1, 0])
        
        return normal