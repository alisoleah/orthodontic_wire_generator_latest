
# ================================================================
# core/bracket_positioner.py
"""Bracket positioning using ACTUAL lingual surface detection (clinical approach)."""

import numpy as np
from typing import List, Dict
from .constants import BRACKET_HEIGHTS, CLINICAL_OFFSETS
from .arch_modeling import create_arch_form

class BracketPositioner:
    """Calculates optimal bracket positions on ACTUAL tooth lingual surfaces."""
    
    def __init__(self, surface_type: str = 'lingual'):
        """Initialize bracket positioner."""
        self.surface_type = surface_type
        self.clinical_offset = CLINICAL_OFFSETS.get(surface_type, 0.5)  # Minimal offset
        self.arch_form = None  # For reference only
        self.positioning_parameters = {
            'height_tolerance': 1.5,  # mm - vertical range for surface detection
            'percentile_threshold': 10,  # Use 10th percentile for true lingual surface
            'min_vertices_for_positioning': 10,
            'surface_offset': 0.5  # mm - MINIMAL offset to prevent penetration
        }
        
    def calculate_positions(self, teeth: List[Dict], mesh, arch_center: np.ndarray, 
                          arch_type: str) -> List[Dict]:
        """
        Calculate bracket positions on ACTUAL tooth lingual surfaces.
        
        PROFESSIONAL APPROACH (from reference image):
        1. Find TRUE lingual surface of each tooth
        2. Position bracket ON surface (not on polynomial)
        3. Add minimal offset (0.5mm) for clearance
        4. Wire follows actual tooth geometry
        """
        if not teeth:
            return []
        
        # Fit polynomial arch for reference (but don't use for positioning)
        tooth_centers_2d = np.array([[t['center'][0], t['center'][1]] for t in teeth])
        try:
            self.arch_form = create_arch_form(tooth_centers_2d)
            print(f"Arch form (reference): {self.arch_form.classification}")
            print(f"  R² = {self.arch_form.r_squared:.4f}")
        except Exception as e:
            print(f"Warning: Polynomial fit failed: {e}")
            self.arch_form = None
        
        # Calculate bracket positions using ACTUAL tooth surfaces
        bracket_positions = []
        for i, tooth in enumerate(teeth):
            bracket_pos = self._calculate_single_bracket(
                tooth, mesh, arch_center, arch_type, i
            )
            bracket_positions.append(bracket_pos)
        
        visible_count = sum(1 for b in bracket_positions if b['visible'])
        print(f"Positioned {len(bracket_positions)} brackets on lingual surfaces ({visible_count} visible)")
        
        return bracket_positions
    
    def _calculate_single_bracket(self, tooth: Dict, mesh, arch_center: np.ndarray,
                                arch_type: str, tooth_index: int) -> Dict:
        """
        Calculate bracket position on ACTUAL tooth lingual surface.
        
        This matches the reference image: wire sits ON tooth surface.
        """
        tooth_type = tooth.get('type', 'posterior')
        tooth_center = tooth['center']
        tooth_vertices = tooth['vertices']
        
        # Target height: mid-tooth level for stability
        height_axis = 2  # Z-axis
        target_height = tooth_center[height_axis]
        
        # Find TRUE lingual surface position
        bracket_pos = self._find_true_lingual_surface(
            tooth_vertices, tooth_center, arch_center, target_height, height_axis
        )
        
        # Calculate surface normal pointing OUTWARD from tooth
        normal = self._calculate_tooth_surface_normal(
            bracket_pos, tooth_vertices, arch_center
        )
        
        # Apply MINIMAL offset (0.5mm) - just enough to prevent penetration
        # This matches reference image: wire very close to teeth
        surface_offset = self.positioning_parameters['surface_offset']
        bracket_pos = bracket_pos + normal * surface_offset
        
        # CRITICAL FIX: Show ALL brackets for lingual wire (not just incisors/canines)
        # Lingual wires go across all teeth
        visible = True  # Show all teeth
        
        return {
            'position': bracket_pos,
            'tooth_type': tooth_type,
            'tooth_index': tooth_index,
            'tooth_center': tooth_center,
            'normal': normal,
            'height': BRACKET_HEIGHTS.get(tooth_type, 3.5),
            'surface': self.surface_type,
            'visible': visible,
            'original_position': bracket_pos.copy(),
            'on_surface': True  # Key flag: positioned on actual surface
        }
    
    def _find_true_lingual_surface(self, tooth_vertices: np.ndarray, tooth_center: np.ndarray,
                             arch_center: np.ndarray, target_height: float, 
                             height_axis: int) -> np.ndarray:
        """
        Find TRUE lingual (inner) surface position at target height.
        
        This is the actual innermost surface of the tooth.
        """
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
        
        # Calculate radial distances for all vertices at this height
        radial_distances = []
        for vertex in bracket_level_vertices:
            vertex_horizontal = vertex.copy()
            vertex_horizontal[height_axis] = 0
            vertex_radial = vertex_horizontal - center_horizontal
            radial_dist = np.dot(vertex_radial, radial_direction)
            radial_distances.append(radial_dist)
        
        radial_distances = np.array(radial_distances)
        
        # CRITICAL FIX: Use 90th percentile to find TRUE innermost surface
        # 10th percentile gives OUTERMOST points (wrong!)
        # 90th percentile gives INNERMOST points (correct for lingual!)
        percentile_threshold = 90  # Changed from 10 to 90
        percentile_value = np.percentile(radial_distances, percentile_threshold)
        lingual_mask = radial_distances >= percentile_value  # Changed <= to >=
        lingual_vertices = bracket_level_vertices[lingual_mask]
        
        if len(lingual_vertices) > 3:
            # Average of innermost vertices = true lingual surface
            return np.mean(lingual_vertices, axis=0)
        else:
            # Use single innermost vertex (maximum radial distance for lingual)
            return bracket_level_vertices[np.argmax(radial_distances)]
    
    def _calculate_tooth_surface_normal(self, surface_point: np.ndarray,
                                       tooth_vertices: np.ndarray,
                                       arch_center: np.ndarray) -> np.ndarray:
        """
        Calculate surface normal at bracket position pointing OUTWARD from tooth.
        
        Uses PCA on nearby vertices for accurate normal estimation.
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