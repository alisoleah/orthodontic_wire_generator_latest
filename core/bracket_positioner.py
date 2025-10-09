
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
            'height_tolerance': 2.0,
            'percentile_threshold': 15,  # For lingual surface detection
            'min_vertices_for_positioning': 10
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
    
    def _find_lingual_position(self, tooth_vertices: np.ndarray, tooth_center: np.ndarray,
                             arch_center: np.ndarray, target_height: float, 
                             height_axis: int) -> np.ndarray:
        """Find position on lingual (inner) surface of tooth."""
        # Get vertices at bracket level
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
        percentile_threshold = self.positioning_parameters['percentile_threshold']
        percentile_value = np.percentile(radial_distances, percentile_threshold)
        lingual_mask = radial_distances <= percentile_value
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