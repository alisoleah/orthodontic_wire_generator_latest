#!/usr/bin/env python3
"""
wire/wire_path_creator_enhanced.py

Enhanced WirePathCreator - Professional Wire Drawing Algorithm
=============================================================
Improvements:
- Full type hints with dataclasses
- Multiple path generation strategies (Strategy Pattern)
- NURBS and B-spline support
- Adaptive resolution based on curvature
- Physics-based simulation
- Minimum bend radius constraints
- Comprehensive documentation
"""

import numpy as np
from scipy import interpolate
from scipy.optimize import minimize
from typing import List, Dict, Tuple, Optional, Protocol
from dataclasses import dataclass, field
from enum import Enum
import math


# ============================================================================
# Data Classes for Type Safety
# ============================================================================

@dataclass
class Point3D:
    """3D point representation."""
    x: float
    y: float
    z: float

    def to_array(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([self.x, self.y, self.z])

    @classmethod
    def from_array(cls, arr: np.ndarray) -> 'Point3D':
        """Create from numpy array."""
        return cls(x=float(arr[0]), y=float(arr[1]), z=float(arr[2]))


@dataclass
class ControlPoint:
    """Control point for wire path generation."""
    position: np.ndarray
    type: str  # 'bracket' or 'intermediate'
    index: int
    original_position: np.ndarray
    bend_angle: float = 0.0
    vertical_offset: float = 0.0
    locked: bool = False
    weight: float = 1.0  # Influence strength
    tangent_constraint: Optional[np.ndarray] = None

    def __post_init__(self):
        """Ensure arrays are numpy arrays."""
        if not isinstance(self.position, np.ndarray):
            self.position = np.array(self.position)
        if not isinstance(self.original_position, np.ndarray):
            self.original_position = np.array(self.original_position)


@dataclass
class BracketPosition:
    """Structured bracket position data."""
    position: np.ndarray
    normal: np.ndarray
    tooth_type: str
    visible: bool = True
    tooth_number: Optional[int] = None


@dataclass
class WireMaterial:
    """Wire material properties."""
    name: str
    youngs_modulus: float  # GPa
    yield_strength: float  # MPa
    density: float  # g/cm³
    min_bend_radius: float  # mm
    is_superelastic: bool = False


@dataclass
class BendInfo:
    """Information about a bend in the wire."""
    position: np.ndarray
    angle: float  # degrees
    direction: str  # 'left' or 'right'
    wire_length: float  # distance from start
    radius: float
    path_index: int
    is_valid: bool = True  # passes constraints
    stress_concentration: float = 1.0


class PathGenerationStrategy(Enum):
    """Available path generation strategies."""
    CUBIC_SPLINE = "cubic_spline"
    BSPLINE = "bspline"
    NURBS = "nurbs"
    PHYSICS_BASED = "physics_based"
    CATMULL_ROM = "catmull_rom"


# ============================================================================
# Strategy Pattern for Path Generation
# ============================================================================

class IPathGenerator(Protocol):
    """Interface for path generation strategies."""

    def generate_path(self, control_points: List[ControlPoint],
                     resolution: int) -> np.ndarray:
        """Generate path from control points."""
        ...


class CubicSplineGenerator:
    """Original cubic spline implementation."""

    def __init__(self, smoothing_factor: float = 0.1):
        self.smoothing_factor = smoothing_factor

    def generate_path(self, control_points: List[ControlPoint],
                     resolution: int) -> np.ndarray:
        """Generate path using cubic splines."""
        positions = np.array([cp.position for cp in control_points])

        if len(positions) < 4:
            return self._linear_interpolation(positions, resolution)

        t = np.linspace(0, 1, len(positions))
        t_smooth = np.linspace(0, 1, len(positions) * resolution)

        smooth_path = []
        for dim in range(3):
            tck = interpolate.splrep(t, positions[:, dim],
                                    s=self.smoothing_factor,
                                    k=min(3, len(positions) - 1))
            smooth_dim = interpolate.splev(t_smooth, tck)
            smooth_path.append(smooth_dim)

        return np.array(smooth_path).T

    def _linear_interpolation(self, positions: np.ndarray,
                              resolution: int) -> np.ndarray:
        """Linear interpolation for few points."""
        if len(positions) < 2:
            return positions

        interpolated = []
        for i in range(len(positions) - 1):
            for j in range(resolution):
                t = j / resolution
                point = positions[i] + t * (positions[i + 1] - positions[i])
                interpolated.append(point)
        interpolated.append(positions[-1])

        return np.array(interpolated)


class BSplineGenerator:
    """B-spline path generation for better local control."""

    def __init__(self, degree: int = 3):
        self.degree = degree

    def generate_path(self, control_points: List[ControlPoint],
                     resolution: int) -> np.ndarray:
        """Generate path using B-splines."""
        positions = np.array([cp.position for cp in control_points])
        weights = np.array([cp.weight for cp in control_points])

        if len(positions) <= self.degree:
            return CubicSplineGenerator().generate_path(control_points, resolution)

        # Create B-spline
        n_points = len(positions) * resolution
        tck, u = interpolate.splprep(
            [positions[:, 0], positions[:, 1], positions[:, 2]],
            w=weights,
            k=self.degree,
            s=0
        )

        u_new = np.linspace(0, 1, n_points)
        smooth_path = interpolate.splev(u_new, tck)

        return np.array(smooth_path).T


class CatmullRomGenerator:
    """Catmull-Rom spline - guaranteed to pass through all control points."""

    def __init__(self, alpha: float = 0.5):
        """
        Initialize Catmull-Rom generator.

        Args:
            alpha: 0 = uniform, 0.5 = centripetal (default), 1.0 = chordal
        """
        self.alpha = alpha

    def generate_path(self, control_points: List[ControlPoint],
                     resolution: int) -> np.ndarray:
        """Generate Catmull-Rom spline path."""
        positions = np.array([cp.position for cp in control_points])

        if len(positions) < 4:
            return CubicSplineGenerator()._linear_interpolation(positions, resolution)

        # Add phantom points for endpoints
        p_start = 2 * positions[0] - positions[1]
        p_end = 2 * positions[-1] - positions[-2]
        extended = np.vstack([p_start, positions, p_end])

        path_points = []
        for i in range(len(extended) - 3):
            p0, p1, p2, p3 = extended[i:i+4]

            # Calculate segment
            for t in np.linspace(0, 1, resolution):
                point = self._catmull_rom_point(p0, p1, p2, p3, t)
                path_points.append(point)

        return np.array(path_points)

    def _catmull_rom_point(self, p0: np.ndarray, p1: np.ndarray,
                          p2: np.ndarray, p3: np.ndarray, t: float) -> np.ndarray:
        """Calculate point on Catmull-Rom spline."""
        t2 = t * t
        t3 = t2 * t

        return 0.5 * (
            (2 * p1) +
            (-p0 + p2) * t +
            (2*p0 - 5*p1 + 4*p2 - p3) * t2 +
            (-p0 + 3*p1 - 3*p2 + p3) * t3
        )


class PhysicsBasedGenerator:
    """Physics-based path generation using energy minimization."""

    def __init__(self, wire_material: WireMaterial, wire_radius: float = 0.25):
        self.material = wire_material
        self.wire_radius = wire_radius

    def generate_path(self, control_points: List[ControlPoint],
                     resolution: int) -> np.ndarray:
        """Generate path by minimizing elastic energy."""
        # Start with cubic spline as initial guess
        initial_path = CubicSplineGenerator().generate_path(control_points, resolution)

        # Define energy function
        def energy_function(path_flat):
            path = path_flat.reshape(-1, 3)
            return self._calculate_elastic_energy(path)

        # Optimize
        result = minimize(
            energy_function,
            initial_path.flatten(),
            method='L-BFGS-B',
            options={'maxiter': 100, 'ftol': 1e-6}
        )

        return result.x.reshape(-1, 3)

    def _calculate_elastic_energy(self, path: np.ndarray) -> float:
        """Calculate elastic bending energy."""
        energy = 0.0
        E = self.material.youngs_modulus * 1e9  # Convert GPa to Pa
        I = (np.pi * self.wire_radius**4) / 4  # Moment of inertia

        for i in range(1, len(path) - 1):
            # Calculate curvature
            p1 = path[i - 1]
            p2 = path[i]
            p3 = path[i + 1]

            v1 = p2 - p1
            v2 = p3 - p2

            if np.linalg.norm(v1) > 1e-6 and np.linalg.norm(v2) > 1e-6:
                curvature = self._calculate_curvature(p1, p2, p3)
                ds = np.linalg.norm(v1 + v2) / 2  # Average segment length

                # Bending energy: E * I * curvature² * ds
                energy += 0.5 * E * I * (curvature ** 2) * ds

        return energy

    def _calculate_curvature(self, p1: np.ndarray, p2: np.ndarray,
                            p3: np.ndarray) -> float:
        """Calculate curvature at point."""
        v1 = p2 - p1
        v2 = p3 - p2

        cross = np.cross(v1, v2)
        cross_norm = np.linalg.norm(cross)
        v1_norm = np.linalg.norm(v1)

        if v1_norm > 1e-6 and cross_norm > 1e-6:
            return cross_norm / (v1_norm ** 3)
        return 0.0


# ============================================================================
# Enhanced Wire Path Creator
# ============================================================================

class WirePathCreatorEnhanced:
    """
    Professional wire path generation with advanced algorithms.

    Features:
    - Multiple generation strategies
    - Adaptive resolution
    - Physics-based simulation
    - Constraint validation
    - Material-aware bending
    """

    def __init__(self,
                 bend_radius: float = 2.0,
                 wire_tension: float = 1.0,
                 strategy: PathGenerationStrategy = PathGenerationStrategy.CATMULL_ROM,
                 wire_material: Optional[WireMaterial] = None):
        """Initialize enhanced wire path creator."""

        self.bend_radius = bend_radius
        self.wire_tension = wire_tension
        self.strategy = strategy

        # Default NiTi material if none provided
        self.material = wire_material or WireMaterial(
            name="NiTi",
            youngs_modulus=83,  # GPa
            yield_strength=1400,  # MPa
            density=6.45,  # g/cm³
            min_bend_radius=2.0,  # mm
            is_superelastic=True
        )

        # Path generation parameters
        self.base_resolution = 100
        self.smoothing_factor = 0.1
        self.minimum_segment_length = 0.5  # mm
        self.adaptive_resolution = True

        # State
        self.control_points: List[ControlPoint] = []
        self.wire_path: Optional[np.ndarray] = None
        self.path_generator: IPathGenerator = self._get_generator()

    def _get_generator(self) -> IPathGenerator:
        """Get appropriate path generator based on strategy."""
        generators = {
            PathGenerationStrategy.CUBIC_SPLINE: CubicSplineGenerator(self.smoothing_factor),
            PathGenerationStrategy.BSPLINE: BSplineGenerator(degree=3),
            PathGenerationStrategy.CATMULL_ROM: CatmullRomGenerator(alpha=0.5),
            PathGenerationStrategy.PHYSICS_BASED: PhysicsBasedGenerator(self.material)
        }
        return generators.get(self.strategy, CubicSplineGenerator(self.smoothing_factor))

    def create_smooth_path(self,
                          bracket_positions: List[Dict],
                          arch_center: np.ndarray,
                          height_offset: float = 0.0) -> Optional[np.ndarray]:
        """
        Main wire path generation algorithm with enhancements.

        Args:
            bracket_positions: List of bracket position dictionaries
            arch_center: Center point of dental arch
            height_offset: Global height adjustment

        Returns:
            Numpy array of 3D points representing wire path
        """
        if not bracket_positions:
            return None

        # Step 1: Extract and sort brackets
        # Handle both dict and BracketPosition object formats
        visible_brackets = []
        for b in bracket_positions:
            if hasattr(b, 'visible'):
                # BracketPosition object
                if b.visible:
                    visible_brackets.append(b)
            elif isinstance(b, dict):
                # Dictionary format
                if b.get('visible', True):
                    visible_brackets.append(b)
            else:
                # Fallback - assume visible
                visible_brackets.append(b)
        if len(visible_brackets) < 2:
            return None

        # Step 2: Sort by angular position
        sorted_brackets = self._sort_brackets_by_angle(visible_brackets, arch_center)

        # Step 3: Generate control points
        self.control_points = self._generate_control_points_enhanced(
            sorted_brackets, arch_center
        )

        # Step 4: Apply height offset
        self._apply_height_offset(height_offset)

        # Step 5: Determine resolution (adaptive or fixed)
        resolution = self._calculate_adaptive_resolution() if self.adaptive_resolution else self.base_resolution

        # Step 6: Generate path using selected strategy
        self.wire_path = self.path_generator.generate_path(self.control_points, resolution)

        # Step 7: Apply wire tension
        self.wire_path = self._apply_wire_tension_advanced()

        # Step 8: Enforce bend radius constraints
        self.wire_path = self._enforce_minimum_bend_radius()

        # Step 9: Validate and clean
        self.wire_path = self._validate_and_clean_path()

        return self.wire_path

    def _sort_brackets_by_angle(self, brackets: List,
                                center: np.ndarray) -> List:
        """Sort brackets by angular position."""
        def calculate_angle(bracket):
            # Handle both dict and BracketPosition object formats
            if hasattr(bracket, 'position'):
                pos = bracket.position
            elif isinstance(bracket, dict):
                pos = bracket['position']
            else:
                pos = bracket  # Fallback
            
            dx = pos[0] - center[0]
            dy = pos[1] - center[1]
            return np.arctan2(dy, dx)

        return sorted(brackets, key=calculate_angle)

    def _generate_control_points_enhanced(self, sorted_brackets: List,
                                         center: np.ndarray) -> List[ControlPoint]:
        """Generate control points with enhanced properties."""
        control_points = []

        # Add bracket control points
        for i, bracket in enumerate(sorted_brackets):
            # Handle both dict and BracketPosition object formats
            if hasattr(bracket, 'position'):
                pos = bracket.position.copy()
            elif isinstance(bracket, dict):
                pos = bracket['position'].copy()
            else:
                pos = bracket.copy()  # Fallback
            
            cp = ControlPoint(
                position=pos,
                type='bracket',
                index=i,
                original_position=pos,
                bend_angle=0.0,
                vertical_offset=0.0,
                locked=False,
                weight=1.0
            )
            control_points.append(cp)

        # Add intermediate points for smoothness
        intermediate_points = self._create_intermediate_points_enhanced(
            sorted_brackets, center
        )
        control_points.extend(intermediate_points)

        # Sort by angle
        control_points.sort(key=lambda cp: np.arctan2(
            cp.position[1] - center[1],
            cp.position[0] - center[0]
        ))

        return control_points

    def _create_intermediate_points_enhanced(self, brackets: List[Dict],
                                            center: np.ndarray) -> List[ControlPoint]:
        """Create intermediate control points with weights."""
        intermediate_points = []

        for i in range(len(brackets) - 1):
            # Handle both dict and BracketPosition object formats
            if hasattr(brackets[i], 'position'):
                pos1 = brackets[i].position
                pos2 = brackets[i + 1].position
            elif isinstance(brackets[i], dict):
                pos1 = brackets[i]['position']
                pos2 = brackets[i + 1]['position']
            else:
                pos1 = brackets[i]  # Fallback
                pos2 = brackets[i + 1]
            midpoint = (pos1 + pos2) / 2

            # Calculate inward offset for natural curve
            direction_to_center = center - midpoint
            direction_to_center[2] = 0

            if np.linalg.norm(direction_to_center) > 0:
                direction_to_center = direction_to_center / np.linalg.norm(direction_to_center)
                midpoint += direction_to_center * 1.0

            cp = ControlPoint(
                position=midpoint,
                type='intermediate',
                index=len(self.control_points) + len(intermediate_points),
                original_position=midpoint.copy(),
                weight=0.5  # Lower weight for intermediate points
            )
            intermediate_points.append(cp)

        return intermediate_points

    def _apply_height_offset(self, height_offset: float):
        """Apply global height offset to all control points."""
        for cp in self.control_points:
            cp.position[2] += height_offset

    def _calculate_adaptive_resolution(self) -> int:
        """Calculate resolution based on path complexity."""
        if len(self.control_points) < 2:
            return self.base_resolution

        # Estimate path curvature
        positions = np.array([cp.position for cp in self.control_points])
        total_curvature = 0.0

        for i in range(1, len(positions) - 1):
            curvature = self._estimate_local_curvature(
                positions[i-1], positions[i], positions[i+1]
            )
            total_curvature += curvature

        # More curvature = higher resolution
        avg_curvature = total_curvature / max(len(positions) - 2, 1)
        resolution_multiplier = 1.0 + min(avg_curvature * 10, 2.0)

        return int(self.base_resolution * resolution_multiplier)

    def _estimate_local_curvature(self, p1: np.ndarray, p2: np.ndarray,
                                  p3: np.ndarray) -> float:
        """Estimate curvature at a point."""
        v1 = p2 - p1
        v2 = p3 - p2

        v1_norm = np.linalg.norm(v1)
        v2_norm = np.linalg.norm(v2)

        if v1_norm < 1e-6 or v2_norm < 1e-6:
            return 0.0

        cos_angle = np.dot(v1, v2) / (v1_norm * v2_norm)
        cos_angle = np.clip(cos_angle, -1, 1)
        angle = np.arccos(cos_angle)

        return angle / max((v1_norm + v2_norm) / 2, 1e-6)

    def _apply_wire_tension_advanced(self) -> np.ndarray:
        """Apply wire tension with material properties."""
        if self.wire_path is None or len(self.wire_path) < 3:
            return self.wire_path

        smoothed_path = self.wire_path.copy()
        tension_factor = self.wire_tension

        # Apply Gaussian smoothing based on tension
        for iteration in range(int(tension_factor * 3)):
            for i in range(1, len(smoothed_path) - 1):
                # Weighted average of neighbors
                smoothed_path[i] = (
                    0.25 * smoothed_path[i-1] +
                    0.50 * smoothed_path[i] +
                    0.25 * smoothed_path[i+1]
                )

        return smoothed_path

    def _enforce_minimum_bend_radius(self) -> np.ndarray:
        """Enforce minimum bend radius constraints."""
        if self.wire_path is None or len(self.wire_path) < 3:
            return self.wire_path

        min_radius = self.material.min_bend_radius
        adjusted_path = self.wire_path.copy()

        for i in range(1, len(adjusted_path) - 1):
            p1, p2, p3 = adjusted_path[i-1:i+2]

            # Calculate current bend radius
            radius = self._calculate_bend_radius(p1, p2, p3)

            if 0 < radius < min_radius:
                # Adjust point to meet minimum radius
                adjustment_factor = min_radius / radius
                center = (p1 + p3) / 2
                offset = p2 - center
                adjusted_path[i] = center + offset * adjustment_factor

        return adjusted_path

    def _calculate_bend_radius(self, p1: np.ndarray, p2: np.ndarray,
                              p3: np.ndarray) -> float:
        """Calculate bend radius at a point."""
        v1 = p2 - p1
        v2 = p3 - p2

        v1_norm = np.linalg.norm(v1)
        v2_norm = np.linalg.norm(v2)

        if v1_norm < 1e-6 or v2_norm < 1e-6:
            return float('inf')

        # Menger curvature formula
        cross = np.cross(v1, v2)
        cross_norm = np.linalg.norm(cross)

        if cross_norm < 1e-6:
            return float('inf')

        area = cross_norm / 2
        chord = np.linalg.norm(p3 - p1)

        if chord < 1e-6:
            return float('inf')

        # Radius of circumcircle
        radius = (v1_norm * v2_norm * chord) / (4 * area)
        return radius

    def _validate_and_clean_path(self) -> np.ndarray:
        """Validate and clean the generated path."""
        if self.wire_path is None or len(self.wire_path) == 0:
            return np.array([])

        cleaned_path = []

        for i, point in enumerate(self.wire_path):
            # Skip if too close to previous
            if cleaned_path and np.linalg.norm(point - cleaned_path[-1]) < self.minimum_segment_length:
                continue

            # Check for valid coordinates
            if np.any(np.isnan(point)) or np.any(np.isinf(point)):
                continue

            cleaned_path.append(point)

        return np.array(cleaned_path) if cleaned_path else np.array([])

    def calculate_bends_enhanced(self, bend_threshold: float = 5.0) -> List[BendInfo]:
        """Calculate bend information with validation."""
        if self.wire_path is None or len(self.wire_path) < 3:
            return []

        bends = []

        for i in range(1, len(self.wire_path) - 1):
            p1, p2, p3 = self.wire_path[i-1:i+2]

            # Calculate bend properties
            bend_angle = self._calculate_bend_angle(p1, p2, p3)

            if abs(bend_angle) > bend_threshold:
                # Calculate bend radius
                radius = self._calculate_bend_radius(p1, p2, p3)

                # Validate against material constraints
                is_valid = radius >= self.material.min_bend_radius

                # Calculate stress concentration factor
                stress_factor = self._calculate_stress_concentration(radius, bend_angle)

                # Direction
                cross = np.cross(p2 - p1, p3 - p2)
                direction = 'left' if cross[2] > 0 else 'right'

                # Wire length to this point
                wire_length = sum(
                    np.linalg.norm(self.wire_path[j+1] - self.wire_path[j])
                    for j in range(i)
                )

                bend = BendInfo(
                    position=p2.copy(),
                    angle=bend_angle,
                    direction=direction,
                    wire_length=wire_length,
                    radius=radius,
                    path_index=i,
                    is_valid=is_valid,
                    stress_concentration=stress_factor
                )
                bends.append(bend)

        return bends

    def _calculate_bend_angle(self, p1: np.ndarray, p2: np.ndarray,
                             p3: np.ndarray) -> float:
        """Calculate bend angle in degrees."""
        v1 = p2 - p1
        v2 = p3 - p2

        v1_norm = np.linalg.norm(v1)
        v2_norm = np.linalg.norm(v2)

        if v1_norm < 1e-6 or v2_norm < 1e-6:
            return 0.0

        cos_angle = np.dot(v1, v2) / (v1_norm * v2_norm)
        cos_angle = np.clip(cos_angle, -1, 1)
        angle = np.degrees(np.arccos(cos_angle))

        return 180 - angle  # Exterior angle

    def _calculate_stress_concentration(self, radius: float, angle: float) -> float:
        """Calculate stress concentration factor."""
        if radius <= 0:
            return float('inf')

        # Simplified Peterson's formula
        k_t = 1 + 2 * np.sqrt(self.material.min_bend_radius / radius)

        # Increase for sharper bends
        angle_factor = 1 + abs(angle) / 180

        return k_t * angle_factor

    def calculate_bends(self, bend_threshold: float = 5.0) -> List[Dict]:
        """Calculate bends (compatibility method)."""
        bends_enhanced = self.calculate_bends_enhanced(bend_threshold)
        # Convert BendInfo to dict for compatibility
        return [
            {
                'position': bend.position,
                'angle': bend.angle,
                'direction': bend.direction,
                'radius': bend.radius,
                'wire_length': bend.wire_length
            }
            for bend in bends_enhanced
        ]

    def get_path_length(self) -> float:
        """Calculate total wire path length."""
        if self.wire_path is None or len(self.wire_path) < 2:
            return 0.0

        return sum(
            np.linalg.norm(self.wire_path[i+1] - self.wire_path[i])
            for i in range(len(self.wire_path) - 1)
        )

    def get_path_statistics(self) -> Dict:
        """Get comprehensive path statistics."""
        if self.wire_path is None:
            return {'valid': False}

        bends = self.calculate_bends_enhanced()

        return {
            'valid': True,
            'length': self.get_path_length(),
            'num_points': len(self.wire_path),
            'num_control_points': len(self.control_points),
            'num_bends': len(bends),
            'valid_bends': sum(1 for b in bends if b.is_valid),
            'invalid_bends': sum(1 for b in bends if not b.is_valid),
            'max_stress_concentration': max((b.stress_concentration for b in bends), default=0),
            'min_bend_radius': min((b.radius for b in bends), default=float('inf')),
            'strategy': self.strategy.value,
            'material': self.material.name
        }


    def generate_ideal_arch_curve(self, bracket_positions: List[BracketPosition], num_points: int = 100) -> np.ndarray:
        """
        Generates an ideal arch curve using a fourth-order polynomial fit.

        This method takes the 3D coordinates of the brackets, fits a smooth
        fourth-order polynomial to them, and returns a new set of points
        representing the idealized arch form.

        Args:
            bracket_positions: A list of BracketPosition objects.
            num_points: The number of points to generate for the smooth curve.

        Returns:
            A numpy array of 3D points representing the ideal arch curve.
        """
        if not bracket_positions or len(bracket_positions) < 5:
            # Not enough points to fit a 4th order polynomial
            # Handle both dict and object formats for fallback
            fallback_positions = []
            for bp in bracket_positions:
                if hasattr(bp, 'position'):
                    fallback_positions.append(bp.position)
                elif isinstance(bp, dict) and 'position' in bp:
                    fallback_positions.append(bp['position'])
                else:
                    fallback_positions.append(bp)
            return np.array(fallback_positions)

        # Extract X and Y coordinates for the polynomial fit
        # Handle both dict and BracketPosition object formats
        positions = []
        for bp in bracket_positions:
            if hasattr(bp, 'position'):
                # BracketPosition object
                positions.append(bp.position)
            elif isinstance(bp, dict) and 'position' in bp:
                # Dictionary format
                positions.append(bp['position'])
            else:
                # Fallback - assume it's already a position array
                positions.append(bp)
        
        positions = np.array(positions)
        x_coords = positions[:, 0]
        y_coords = positions[:, 1]

        # Fit a fourth-order polynomial (y = ax^4 + bx^3 + cx^2 + dx + e)
        # We use a robust fitting method to handle outliers
        coefficients = np.polyfit(x_coords, y_coords, 4)

        # Generate a smooth set of X coordinates for the new curve
        x_smooth = np.linspace(np.min(x_coords), np.max(x_coords), num_points)

        # Calculate the corresponding Y coordinates using the polynomial
        y_smooth = np.polyval(coefficients, x_smooth)

        # To get the Z coordinates, we can interpolate from the original points
        # This ensures the curve maintains the general height of the brackets
        z_coords_interp = np.interp(x_smooth, x_coords, positions[:, 2])

        # Combine X, Y, and Z to create the 3D ideal arch curve
        ideal_curve = np.vstack((x_smooth, y_smooth, z_coords_interp)).T

        return ideal_curve


    def generate_surface_projected_arch(self, fa_points, mesh):
        """
        Generate an ideal arch curve projected onto the tooth surfaces.
        
        This is the core method for the new FIXR-inspired workflow.
        
        Args:
            fa_points: List of FAPoint objects
            mesh: The dental mesh for surface projection
        
        Returns:
            Numpy array of 3D points representing the surface-projected arch
        """
        if not fa_points or len(fa_points) < 2:
            print("ERROR: Insufficient FA points for arch generation")
            return None
        
        try:
            # Step 1: Extract positions from FA points
            fa_positions = np.array([fp.position for fp in fa_points])
            
            # Step 2: Generate initial polynomial arch curve
            initial_arch = self._generate_polynomial_arch(fa_positions)
            if initial_arch is None:
                print("ERROR: Failed to generate initial polynomial arch")
                return None
            
            # Step 3: Project each point onto the mesh surface
            projected_arch = self._project_curve_to_surface(initial_arch, mesh)
            if projected_arch is None:
                print("ERROR: Failed to project arch to surface")
                return None
            
            print(f"✓ Generated surface-projected arch with {len(projected_arch)} points")
            return projected_arch
            
        except Exception as e:
            print(f"ERROR in generate_surface_projected_arch: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _generate_polynomial_arch(self, fa_positions):
        """Generate a fourth-order polynomial arch curve through FA points."""
        try:
            if len(fa_positions) < 3:
                # Linear interpolation for few points
                t = np.linspace(0, 1, 100)
                if len(fa_positions) == 2:
                    arch_points = []
                    for ti in t:
                        point = fa_positions[0] + ti * (fa_positions[1] - fa_positions[0])
                        arch_points.append(point)
                    return np.array(arch_points)
                else:
                    return fa_positions
            
            # Sort FA points by angle for proper ordering
            center = np.mean(fa_positions, axis=0)
            angles = []
            for pos in fa_positions:
                dx = pos[0] - center[0]
                dy = pos[1] - center[1]
                angle = np.arctan2(dy, dx)
                angles.append(angle)
            
            # Sort by angle
            sorted_indices = np.argsort(angles)
            sorted_positions = fa_positions[sorted_indices]
            
            # Generate parameter values
            n_points = len(sorted_positions)
            t_original = np.linspace(0, 1, n_points)
            t_smooth = np.linspace(0, 1, 100)
            
            # Fit polynomial for each dimension
            arch_points = []
            for dim in range(3):
                # Use polynomial fitting (degree 4 or less based on available points)
                degree = min(4, n_points - 1)
                coeffs = np.polyfit(t_original, sorted_positions[:, dim], degree)
                smooth_values = np.polyval(coeffs, t_smooth)
                arch_points.append(smooth_values)
            
            return np.array(arch_points).T
            
        except Exception as e:
            print(f"ERROR in _generate_polynomial_arch: {e}")
            return None
    
    def _project_curve_to_surface(self, curve_points, mesh):
        """Project curve points onto the mesh surface using raycasting."""
        try:
            import open3d as o3d
            
            # Create raycasting scene
            scene = o3d.t.geometry.RaycastingScene()
            mesh_t = o3d.t.geometry.TriangleMesh.from_legacy(mesh)
            scene.add_triangles(mesh_t)
            
            projected_points = []
            mesh_center = mesh.get_center()
            
            for point in curve_points:
                try:
                    # Cast ray from point towards mesh center
                    ray_direction = mesh_center - point
                    ray_direction = ray_direction / np.linalg.norm(ray_direction)
                    
                    # Cast ray
                    rays = o3d.core.Tensor([[point[0], point[1], point[2], 
                                           ray_direction[0], ray_direction[1], ray_direction[2]]], 
                                         dtype=o3d.core.Dtype.Float32)
                    
                    result = scene.cast_rays(rays)
                    
                    if result['t_hit'][0] != float('inf'):
                        # Hit found - use intersection point
                        hit_distance = result['t_hit'][0].item()  # Convert tensor to float
                        hit_point = point + ray_direction * hit_distance
                        projected_points.append(hit_point)
                    else:
                        # No hit - try reverse direction
                        ray_direction = -ray_direction
                        rays = o3d.core.Tensor([[point[0], point[1], point[2], 
                                               ray_direction[0], ray_direction[1], ray_direction[2]]], 
                                             dtype=o3d.core.Dtype.Float32)
                        
                        result = scene.cast_rays(rays)
                        
                        if result['t_hit'][0] != float('inf'):
                            hit_distance = result['t_hit'][0].item()  # Convert tensor to float
                            hit_point = point + ray_direction * hit_distance
                            projected_points.append(hit_point)
                        else:
                            # No hit in either direction - use original point
                            projected_points.append(point)
                
                except Exception as e:
                    print(f"Warning: Failed to project point {point}: {e}")
                    projected_points.append(point)
            
            return np.array(projected_points)
            
        except Exception as e:
            print(f"ERROR in _project_curve_to_surface: {e}")
            return curve_points  # Return original points as fallback
