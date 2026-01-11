
# ================================================================
# core/bracket_positioner.py
"""Bracket positioning using polynomial arch form (research-based approach)."""

import numpy as np
from typing import List, Dict
from .constants import BRACKET_HEIGHTS, CLINICAL_OFFSETS
from .arch_modeling import fit_arch_polynomial, evaluate_polynomial, create_arch_form

class BracketPositioner:
    """Calculates optimal bracket positions using polynomial arch form."""
    
    def __init__(self, surface_type: str = 'lingual'):
        """Initialize bracket positioner."""
        self.surface_type = surface_type
        self.clinical_offset = CLINICAL_OFFSETS.get(surface_type, 1.5)
        self.arch_form = None  # Will store fitted polynomial
        
    def calculate_positions(self, teeth: List[Dict], mesh, arch_center: np.ndarray, 
                          arch_type: str) -> List[Dict]:
        """
        Calculate bracket positions using polynomial arch form.
        
        NEW APPROACH:
        1. Fit 6th order polynomial to tooth centers
        2. Position brackets ON polynomial arch (not on tooth surfaces)
        3. Wire follows arch = automatic clearance
        """
        if not teeth:
            return []
        
        # Extract 2D tooth positions (X-Y plane)
        tooth_centers_2d = np.array([[t['center'][0], t['center'][1]] for t in teeth])
        
        # Fit polynomial arch form
        try:
            self.arch_form = create_arch_form(tooth_centers_2d)
            print(f"Arch form: {self.arch_form.classification}")
            print(f"  Polynomial: Y = {self.arch_form.A:.3e}·x^6 + {self.arch_form.B:.4f}·x^2")
            print(f"  Fit quality: R² = {self.arch_form.r_squared:.4f}")
        except Exception as e:
            print(f"Warning: Polynomial fit failed: {e}")
            print("Falling back to direct tooth positions")
            self.arch_form = None
        
        # Calculate bracket positions
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
        """
        Calculate bracket position ON polynomial arch (not on tooth surface).
        
        KEY DIFFERENCE: Position is calculated from arch form, not tooth surface.
        """
        tooth_type = tooth.get('type', 'posterior')
        tooth_center = tooth['center']
        
        # Get X position from tooth
        x_pos = tooth_center[0]
        
        # Calculate Y position from polynomial arch (if available)
        if self.arch_form is not None:
            y_pos = evaluate_polynomial(
                self.arch_form.A, 
                self.arch_form.B, 
                np.array([x_pos])
            )[0]
        else:
            # Fallback: use tooth center Y
            y_pos = tooth_center[1]
        
        # Z position: use tooth center height (mid-tooth level)
        z_pos = tooth_center[2]
        
        # Bracket position ON polynomial arch
        bracket_pos = np.array([x_pos, y_pos, z_pos])
        
        # Calculate normal vector (points away from arch center)
        normal = self._calculate_arch_normal(bracket_pos, arch_center)
        
        # Add small outward offset for clearance (1-2mm)
        # This ensures wire sits OUTSIDE teeth
        clearance_offset = 1.5  # mm
        bracket_pos = bracket_pos + normal * clearance_offset
        
        # Determine visibility (only frontal teeth: incisors and canines)
        visible = tooth_type in ['incisor', 'canine']
        
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
            'on_arch': True  # Key flag: positioned on arch, not surface
        }
    
    def _calculate_arch_normal(self, bracket_pos: np.ndarray, 
                              arch_center: np.ndarray) -> np.ndarray:
        """
        Calculate normal vector pointing AWAY from arch center.
        
        This ensures wire sits OUTSIDE the arch (and teeth).
        """
        # Vector from arch center to bracket (in horizontal plane)
        to_bracket = bracket_pos - arch_center
        to_bracket[2] = 0  # Remove Z component (horizontal only)
        
        # Normalize
        if np.linalg.norm(to_bracket) > 0:
            normal = to_bracket / np.linalg.norm(to_bracket)
        else:
            # Fallback: point anteriorly
            normal = np.array([0, 1, 0])
        
        return normal