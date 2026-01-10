#!/usr/bin/env python3
"""
wire/arch_form_optimizer.py

Professional Arch Form Optimizer
================================
Implements anatomically-accurate dental arch form fitting using the beta function
and other clinically-validated mathematical models.

Based on:
- Braun et al. (1998) - "The form of the human dental arch"
- Clinical dental arch dimension studies
- ISO standards for orthodontic arch forms

The beta function provides superior fit to natural dental arch forms compared
to parabolic or catenary approximations.
"""

import numpy as np
from scipy.optimize import curve_fit, minimize
from scipy.special import beta as beta_func
from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass
from enum import Enum


class ArchFormType(Enum):
    """Standard arch form classifications."""
    OVOID = "ovoid"
    TAPERED = "tapered"
    SQUARE = "square"
    NARROW = "narrow"
    WIDE = "wide"


@dataclass
class ArchFormParameters:
    """
    Parameters defining a dental arch form.
    """
    # Beta function parameters
    alpha: float = 2.0  # Shape parameter 1
    beta_param: float = 2.0  # Shape parameter 2
    
    # Dimensional parameters (mm)
    inter_canine_width: float = 35.0
    inter_molar_width: float = 50.0
    arch_depth: float = 30.0
    
    # Derived parameters
    arch_form_type: ArchFormType = ArchFormType.OVOID
    
    # Quality metrics
    fit_r_squared: float = 0.0
    fit_rmse: float = 0.0


@dataclass
class ArchDimensions:
    """
    Standard dental arch dimensions based on clinical studies.
    """
    # Upper arch (maxillary) - mean values from PMC5885126
    UPPER_INTER_CANINE: float = 34.99  # mm
    UPPER_INTER_CANINE_SD: float = 3.8
    UPPER_INTER_MOLAR: float = 35.97  # mm (first molar)
    UPPER_INTER_MOLAR_SD: float = 4.6
    
    # Lower arch (mandibular)
    LOWER_INTER_CANINE: float = 26.5  # mm
    LOWER_INTER_CANINE_SD: float = 2.5
    LOWER_INTER_MOLAR: float = 35.0  # mm
    LOWER_INTER_MOLAR_SD: float = 3.5
    
    # Arch depth
    UPPER_ARCH_DEPTH: float = 28.0  # mm
    LOWER_ARCH_DEPTH: float = 25.0  # mm


STANDARD_ARCH_DIMENSIONS = ArchDimensions()


class ArchFormOptimizer:
    """
    Optimizes wire path to follow anatomically-accurate arch forms.
    
    Uses the beta function model which has been shown to provide
    superior fit to natural dental arch forms.
    """
    
    def __init__(self):
        """Initialize arch form optimizer."""
        self.arch_params: Optional[ArchFormParameters] = None
        self.fitted_curve: Optional[np.ndarray] = None
        
    def fit_arch_form(
        self,
        bracket_positions: np.ndarray,
        arch_type: str = 'upper'
    ) -> ArchFormParameters:
        """
        Fit optimal arch form to bracket positions.
        
        Args:
            bracket_positions: Nx3 array of bracket positions
            arch_type: 'upper' or 'lower'
            
        Returns:
            Optimized arch form parameters
        """
        if len(bracket_positions) < 4:
            return self._get_default_parameters(arch_type)
        
        # Extract 2D positions (ignore height)
        positions_2d = bracket_positions[:, :2]
        
        # Calculate arch center
        center = np.mean(positions_2d, axis=0)
        
        # Transform to arch-centered coordinates
        relative_pos = positions_2d - center
        
        # Calculate arch dimensions
        inter_canine, inter_molar, arch_depth = self._calculate_arch_dimensions(
            relative_pos, bracket_positions
        )
        
        # Fit beta function
        alpha, beta_param, r_squared, rmse = self._fit_beta_function(
            relative_pos, arch_depth
        )
        
        # Classify arch form
        arch_form_type = self._classify_arch_form(
            inter_canine, inter_molar, arch_depth, arch_type
        )
        
        self.arch_params = ArchFormParameters(
            alpha=alpha,
            beta_param=beta_param,
            inter_canine_width=inter_canine,
            inter_molar_width=inter_molar,
            arch_depth=arch_depth,
            arch_form_type=arch_form_type,
            fit_r_squared=r_squared,
            fit_rmse=rmse
        )
        
        return self.arch_params
    
    def _calculate_arch_dimensions(
        self,
        relative_pos: np.ndarray,
        full_positions: np.ndarray
    ) -> Tuple[float, float, float]:
        """Calculate key arch dimensions from positions."""
        # Sort by x-coordinate (left-right)
        sorted_by_x = relative_pos[np.argsort(relative_pos[:, 0])]
        
        # Inter-canine width (approximately positions 3-4 from each side)
        n = len(sorted_by_x)
        if n >= 6:
            # Canines are typically 3rd from center
            canine_idx = min(2, n // 4)
            inter_canine = abs(sorted_by_x[-canine_idx-1, 0] - sorted_by_x[canine_idx, 0])
        else:
            inter_canine = abs(sorted_by_x[-1, 0] - sorted_by_x[0, 0]) * 0.7
        
        # Inter-molar width (outermost positions)
        inter_molar = abs(sorted_by_x[-1, 0] - sorted_by_x[0, 0])
        
        # Arch depth (anterior-posterior extent)
        arch_depth = np.max(relative_pos[:, 1]) - np.min(relative_pos[:, 1])
        
        return float(inter_canine), float(inter_molar), float(arch_depth)
    
    def _fit_beta_function(
        self,
        relative_pos: np.ndarray,
        arch_depth: float
    ) -> Tuple[float, float, float, float]:
        """
        Fit beta function to arch form.
        
        The beta function arch form is:
        y = D * (1 - |x/W|^α)^β
        
        Where:
        - D = arch depth
        - W = half arch width
        - α, β = shape parameters
        """
        # Normalize positions
        x = relative_pos[:, 0]
        y = relative_pos[:, 1]
        
        # Shift y so minimum is at 0
        y_shifted = y - np.min(y)
        
        # Normalize x to [-1, 1]
        x_max = np.max(np.abs(x))
        if x_max > 0:
            x_norm = x / x_max
        else:
            x_norm = x
        
        # Define beta function model
        def beta_arch(x_norm, alpha, beta_param, depth):
            # Avoid numerical issues
            x_abs = np.clip(np.abs(x_norm), 0, 0.9999)
            return depth * (1 - x_abs**alpha)**beta_param
        
        try:
            # Initial guess
            p0 = [2.0, 2.0, np.max(y_shifted)]
            
            # Bounds
            bounds = ([0.5, 0.5, 0.1], [10.0, 10.0, arch_depth * 2])
            
            # Fit
            popt, pcov = curve_fit(
                beta_arch, x_norm, y_shifted,
                p0=p0, bounds=bounds, maxfev=5000
            )
            
            alpha, beta_param, depth = popt
            
            # Calculate fit quality
            y_pred = beta_arch(x_norm, *popt)
            ss_res = np.sum((y_shifted - y_pred)**2)
            ss_tot = np.sum((y_shifted - np.mean(y_shifted))**2)
            
            if ss_tot > 0:
                r_squared = 1 - (ss_res / ss_tot)
            else:
                r_squared = 0.0
            
            rmse = np.sqrt(np.mean((y_shifted - y_pred)**2))
            
            return float(alpha), float(beta_param), float(r_squared), float(rmse)
            
        except Exception:
            # Return default values on failure
            return 2.0, 2.0, 0.0, float('inf')
    
    def _classify_arch_form(
        self,
        inter_canine: float,
        inter_molar: float,
        arch_depth: float,
        arch_type: str
    ) -> ArchFormType:
        """Classify arch form based on dimensions."""
        # Get reference dimensions
        if arch_type == 'upper':
            ref_canine = STANDARD_ARCH_DIMENSIONS.UPPER_INTER_CANINE
            ref_molar = STANDARD_ARCH_DIMENSIONS.UPPER_INTER_MOLAR
        else:
            ref_canine = STANDARD_ARCH_DIMENSIONS.LOWER_INTER_CANINE
            ref_molar = STANDARD_ARCH_DIMENSIONS.LOWER_INTER_MOLAR
        
        # Calculate ratios
        canine_ratio = inter_canine / ref_canine
        molar_ratio = inter_molar / ref_molar
        
        # Width ratio (canine to molar)
        width_ratio = inter_canine / inter_molar if inter_molar > 0 else 0.7
        
        # Classify based on ratios
        if width_ratio > 0.75:
            return ArchFormType.SQUARE
        elif width_ratio < 0.55:
            return ArchFormType.TAPERED
        elif canine_ratio < 0.9 and molar_ratio < 0.9:
            return ArchFormType.NARROW
        elif canine_ratio > 1.1 and molar_ratio > 1.1:
            return ArchFormType.WIDE
        else:
            return ArchFormType.OVOID
    
    def _get_default_parameters(self, arch_type: str) -> ArchFormParameters:
        """Get default parameters for arch type."""
        if arch_type == 'upper':
            return ArchFormParameters(
                alpha=2.2,
                beta_param=2.0,
                inter_canine_width=STANDARD_ARCH_DIMENSIONS.UPPER_INTER_CANINE,
                inter_molar_width=STANDARD_ARCH_DIMENSIONS.UPPER_INTER_MOLAR,
                arch_depth=STANDARD_ARCH_DIMENSIONS.UPPER_ARCH_DEPTH,
                arch_form_type=ArchFormType.OVOID
            )
        else:
            return ArchFormParameters(
                alpha=2.0,
                beta_param=1.8,
                inter_canine_width=STANDARD_ARCH_DIMENSIONS.LOWER_INTER_CANINE,
                inter_molar_width=STANDARD_ARCH_DIMENSIONS.LOWER_INTER_MOLAR,
                arch_depth=STANDARD_ARCH_DIMENSIONS.LOWER_ARCH_DEPTH,
                arch_form_type=ArchFormType.OVOID
            )
    
    def generate_ideal_arch_curve(
        self,
        params: ArchFormParameters,
        num_points: int = 100,
        center: np.ndarray = None,
        height: float = 0.0
    ) -> np.ndarray:
        """
        Generate ideal arch curve from parameters.
        
        Args:
            params: Arch form parameters
            num_points: Number of points to generate
            center: Center point of arch (default: origin)
            height: Z-coordinate for all points
            
        Returns:
            Nx3 array of points along ideal arch
        """
        if center is None:
            center = np.array([0.0, 0.0, 0.0])
        
        # Generate x values across arch width
        half_width = params.inter_molar_width / 2
        x = np.linspace(-half_width, half_width, num_points)
        
        # Normalize x
        x_norm = x / half_width
        
        # Calculate y using beta function
        x_abs = np.clip(np.abs(x_norm), 0, 0.9999)
        y = params.arch_depth * (1 - x_abs**params.alpha)**params.beta_param
        
        # Shift y so posterior is at 0
        y = y - np.min(y)
        
        # Create 3D points
        points = np.zeros((num_points, 3))
        points[:, 0] = x + center[0]
        points[:, 1] = y + center[1]
        points[:, 2] = height + center[2]
        
        self.fitted_curve = points
        return points
    
    def project_points_to_arch(
        self,
        points: np.ndarray,
        params: ArchFormParameters,
        center: np.ndarray
    ) -> np.ndarray:
        """
        Project points onto ideal arch form.
        
        Args:
            points: Nx3 array of points to project
            params: Arch form parameters
            center: Arch center
            
        Returns:
            Nx3 array of projected points
        """
        projected = points.copy()
        half_width = params.inter_molar_width / 2
        
        for i, point in enumerate(points):
            # Get relative x position
            x_rel = point[0] - center[0]
            
            # Clamp to arch width
            x_rel = np.clip(x_rel, -half_width * 0.99, half_width * 0.99)
            
            # Calculate ideal y from beta function
            x_norm = x_rel / half_width
            x_abs = np.abs(x_norm)
            y_ideal = params.arch_depth * (1 - x_abs**params.alpha)**params.beta_param
            
            # Update y coordinate
            projected[i, 1] = y_ideal + center[1]
        
        return projected
    
    def optimize_wire_path_to_arch(
        self,
        wire_path: np.ndarray,
        bracket_positions: np.ndarray,
        arch_type: str = 'upper',
        blend_factor: float = 0.3
    ) -> np.ndarray:
        """
        Optimize wire path to better follow ideal arch form.
        
        Args:
            wire_path: Current wire path (Nx3)
            bracket_positions: Bracket positions to fit
            arch_type: 'upper' or 'lower'
            blend_factor: How much to blend toward ideal (0-1)
            
        Returns:
            Optimized wire path
        """
        # Fit arch form to brackets
        params = self.fit_arch_form(bracket_positions, arch_type)
        
        # Calculate center
        center = np.mean(bracket_positions, axis=0)
        
        # Project wire path to ideal arch
        projected = self.project_points_to_arch(wire_path, params, center)
        
        # Blend between original and projected
        optimized = wire_path * (1 - blend_factor) + projected * blend_factor
        
        return optimized
    
    def get_arch_form_report(self) -> Dict:
        """Get detailed arch form analysis report."""
        if self.arch_params is None:
            return {'error': 'No arch form fitted'}
        
        params = self.arch_params
        
        return {
            'arch_form_type': params.arch_form_type.value,
            'dimensions': {
                'inter_canine_width_mm': round(params.inter_canine_width, 2),
                'inter_molar_width_mm': round(params.inter_molar_width, 2),
                'arch_depth_mm': round(params.arch_depth, 2)
            },
            'beta_function': {
                'alpha': round(params.alpha, 3),
                'beta': round(params.beta_param, 3)
            },
            'fit_quality': {
                'r_squared': round(params.fit_r_squared, 4),
                'rmse_mm': round(params.fit_rmse, 3)
            }
        }


def create_standard_arch_form(
    arch_type: str = 'upper',
    form_type: ArchFormType = ArchFormType.OVOID,
    num_points: int = 100
) -> np.ndarray:
    """
    Create a standard arch form curve.
    
    Args:
        arch_type: 'upper' or 'lower'
        form_type: Type of arch form
        num_points: Number of points
        
    Returns:
        Nx3 array of arch form points
    """
    optimizer = ArchFormOptimizer()
    
    # Get default parameters
    params = optimizer._get_default_parameters(arch_type)
    
    # Adjust for form type
    if form_type == ArchFormType.SQUARE:
        params.alpha = 3.0
        params.beta_param = 1.5
    elif form_type == ArchFormType.TAPERED:
        params.alpha = 1.5
        params.beta_param = 2.5
    elif form_type == ArchFormType.NARROW:
        params.inter_canine_width *= 0.9
        params.inter_molar_width *= 0.9
    elif form_type == ArchFormType.WIDE:
        params.inter_canine_width *= 1.1
        params.inter_molar_width *= 1.1
    
    return optimizer.generate_ideal_arch_curve(params, num_points)
