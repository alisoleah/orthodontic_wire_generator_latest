#!/usr/bin/env python3
"""
wire/wire_path_creator.py

WirePathCreator - Core Wire Drawing Algorithm
============================================
This class contains the main algorithm for generating the wire path.
It handles spline interpolation, control points, and path smoothing.
"""

import numpy as np
from scipy import interpolate
from typing import List, Dict, Tuple, Optional
import math
from utils.catmull_rom import catmull_rom_spline

class WirePathCreator:
    """
    Core wire path generation algorithm.
    
    This is the main drawing algorithm class that creates the mathematical
    path the wire should follow through the bracket positions.
    """
    
    def __init__(self, bend_radius: float = 2.0, wire_tension: float = 1.0):
        """Initialize the wire path creator."""
        self.bend_radius = bend_radius
        self.wire_tension = wire_tension
        self.control_points = []
        self.wire_path = None

        # Path generation parameters
        self.path_resolution = 300  # Points per segment (can be changed by smoothness)
        self.smoothing_factor = 0.1
        self.minimum_segment_length = 0.5  # mm
        self.wire_diameter = 0.9  # mm (default)
        
    def create_smooth_path(self, bracket_positions: List[Dict], 
                          arch_center: np.ndarray,
                          height_offset: float = 0.0) -> Optional[np.ndarray]:
        """
        Main wire path generation algorithm.
        
        This is the core drawing algorithm that creates a smooth wire path
        through the bracket positions using spline interpolation.
        
        Args:
            bracket_positions: List of bracket position dictionaries
            arch_center: Center point of the dental arch
            height_offset: Global height adjustment for the wire
            
        Returns:
            numpy array of 3D points representing the wire path
        """
        if not bracket_positions:
            return None
            
        # Step 1: Extract and sort bracket positions
        visible_brackets = [b for b in bracket_positions if b.get('visible', True)]
        if len(visible_brackets) < 2:
            return None
            
        # Step 2: Sort brackets by angular position around arch center
        sorted_brackets = self._sort_brackets_by_angle(visible_brackets, arch_center)
        
        # Step 3: Generate control points for wire shaping
        self.control_points = self._generate_control_points(sorted_brackets, arch_center)
        
        # Step 4: Apply height offset to all control points
        self._apply_height_offset(height_offset)
        
        # Step 5: Generate smooth path using spline interpolation
        self.wire_path = self._interpolate_spline_path()
        
        # Step 6: Apply wire tension and smoothing
        self.wire_path = self._apply_wire_tension()
        
        # Step 7: Validate and clean the path
        self.wire_path = self._validate_and_clean_path()
        
        return self.wire_path
    
    def _sort_brackets_by_angle(self, brackets: List[Dict], 
                               center: np.ndarray) -> List[Dict]:
        """Sort brackets by angular position around the dental arch."""
        def calculate_angle(bracket):
            pos = bracket['position']
            # Calculate angle in the horizontal plane
            dx = pos[0] - center[0]  # Left-Right axis
            dy = pos[1] - center[1]  # Anterior-Posterior axis
            return np.arctan2(dy, dx)
        
        return sorted(brackets, key=calculate_angle)
    
    def _generate_control_points(self, sorted_brackets: List[Dict], 
                               center: np.ndarray) -> List[Dict]:
        """
        Generate control points for wire path creation.
        
        This creates both bracket control points and intermediate points
        for natural wire curvature.
        """
        control_points = []
        
        # Add bracket positions as primary control points
        for i, bracket in enumerate(sorted_brackets):
            control_points.append({
                'position': bracket['position'].copy(),
                'type': 'bracket',
                'index': i,
                'original_position': bracket['position'].copy(),
                'bend_angle': 0.0,
                'vertical_offset': 0.0,
                'bracket_data': bracket
            })
        
        # Add intermediate control points for smooth curves
        intermediate_points = self._create_intermediate_points(sorted_brackets, center)
        control_points.extend(intermediate_points)
        
        # Sort all control points by angle for proper wire sequence
        control_points.sort(key=lambda cp: np.arctan2(
            cp['position'][1] - center[1],
            cp['position'][0] - center[0]
        ))
        
        return control_points
    
    def _create_intermediate_points(self, brackets: List[Dict],
                                  center: np.ndarray) -> List[Dict]:
        """
        Create intermediate control points between brackets for smoother wire.

        Algorithm:
        1. For each bracket pair, create 2 intermediate points (at 33% and 67%)
        2. Apply gentle inward offset toward arch center for natural curvature
        3. Gaussian smoothing will handle the rest

        This ensures smooth wire flow without over-complication.
        """
        intermediate_points = []

        for i in range(len(brackets) - 1):
            pos1 = brackets[i]['position']
            pos2 = brackets[i + 1]['position']

            # Create 4 intermediate points for ultra-smooth transitions
            for t in [0.2, 0.4, 0.6, 0.8]:  # At 20%, 40%, 60%, 80% positions
                # Linear interpolation between brackets (NO INWARD OFFSET)
                interp_pos = pos1 + t * (pos2 - pos1)

                intermediate_points.append({
                    'position': interp_pos.copy(),
                    'type': 'intermediate',
                    'index': len(self.control_points) + len(intermediate_points),
                    'original_position': interp_pos.copy(),
                    'bend_angle': 0.0,
                    'vertical_offset': 0.0
                })

        return intermediate_points

    def _fit_dental_arch_curve(self, brackets: List[Dict], center: np.ndarray) -> Dict:
        """
        Fit a parabolic curve through bracket positions to model dental arch.

        Algorithm: Uses least-squares fitting to find best-fit parabola y = ax^2 + bx + c
        in the horizontal plane (X-Y coordinates relative to arch center).

        Returns: Dictionary with curve parameters (a, b, c, radius)
        """
        if len(brackets) < 3:
            return {'type': 'linear', 'center': center}

        # Extract bracket positions relative to center
        positions = np.array([b['position'] for b in brackets])
        relative_pos = positions[:, :2] - center[:2]  # X-Y coordinates only

        # Calculate angles and distances for circular fit
        angles = np.arctan2(relative_pos[:, 1], relative_pos[:, 0])
        distances = np.linalg.norm(relative_pos, axis=1)

        # Average radius for circular arch approximation
        avg_radius = np.mean(distances)

        # Try parabolic fit: y = ax^2 + bx + c
        try:
            # Rotate coordinates so arch faces forward
            rotation_angle = -np.mean(angles)
            cos_r = np.cos(rotation_angle)
            sin_r = np.sin(rotation_angle)

            rotated_x = relative_pos[:, 0] * cos_r - relative_pos[:, 1] * sin_r
            rotated_y = relative_pos[:, 0] * sin_r + relative_pos[:, 1] * cos_r

            # Fit parabola
            coeffs = np.polyfit(rotated_x, rotated_y, 2)

            return {
                'type': 'parabolic',
                'coeffs': coeffs,
                'rotation': rotation_angle,
                'center': center,
                'radius': avg_radius
            }
        except:
            # Fallback to circular arch
            return {
                'type': 'circular',
                'radius': avg_radius,
                'center': center
            }

    def _project_onto_arch_curve(self, point: np.ndarray, arch_params: Dict,
                                 center: np.ndarray) -> np.ndarray:
        """
        Project a point onto the fitted dental arch curve.

        Algorithm:
        - For parabolic arch: Find nearest point on parabola
        - For circular arch: Project onto circle of given radius
        - Preserve Z-coordinate (height)
        """
        projected = point.copy()

        if arch_params['type'] == 'parabolic':
            # Transform to rotated coordinate system
            relative = point[:2] - center[:2]
            rotation = arch_params['rotation']
            cos_r = np.cos(rotation)
            sin_r = np.sin(rotation)

            x_rot = relative[0] * cos_r - relative[1] * sin_r

            # Calculate y from parabola equation
            coeffs = arch_params['coeffs']
            y_rot = coeffs[0] * x_rot**2 + coeffs[1] * x_rot + coeffs[2]

            # Transform back to original coordinates
            x_orig = x_rot * cos_r + y_rot * sin_r
            y_orig = -x_rot * sin_r + y_rot * cos_r

            projected[0] = center[0] + x_orig
            projected[1] = center[1] + y_orig

        elif arch_params['type'] == 'circular':
            # Project onto circle
            relative = point[:2] - center[:2]
            distance = np.linalg.norm(relative)

            if distance > 0:
                # Scale to arch radius
                scale = arch_params['radius'] / distance
                projected[0] = center[0] + relative[0] * scale
                projected[1] = center[1] + relative[1] * scale

        return projected
    
    def _apply_height_offset(self, height_offset: float):
        """Apply global height offset to all control points."""
        for cp in self.control_points:
            cp['position'][2] += height_offset  # Z-axis is typically height
    
    def _interpolate_spline_path(self) -> np.ndarray:
        """
        Generate smooth wire path using spline interpolation.
        
        This is the core mathematical algorithm for creating smooth curves
        through the control points.
        """
        if len(self.control_points) < 2:
            return np.array([])
        
        # Extract positions from control points
        positions = np.array([cp['position'] for cp in self.control_points])
        
        if len(positions) < 4:
            # Use linear interpolation for few points
            return self._linear_interpolation(positions)
        else:
            # Use Catmull-Rom for smooth curves that pass through the points
            return self._catmull_rom_interpolation(positions)

    def _catmull_rom_interpolation(self, positions: np.ndarray) -> np.ndarray:
        """
        Create smooth path using Catmull-Rom spline interpolation.

        Adaptive resolution: More points = smoother curves.
        Default: 300 points per control point (4200 total for 14 teeth).
        """
        # The utility function expects a list of arrays
        point_list = [p for p in positions]
        # Calculate the number of points for the spline (adaptive based on path_resolution)
        # More control points = more detail needed
        num_points = len(point_list) * self.path_resolution
        return catmull_rom_spline(point_list, num_points=num_points)
    
    def _cubic_spline_interpolation(self, positions: np.ndarray) -> np.ndarray:
        """Create smooth path using cubic spline interpolation."""
        # Parameter values for interpolation
        t = np.linspace(0, 1, len(positions))
        t_smooth = np.linspace(0, 1, len(positions) * self.path_resolution)
        
        # Interpolate each dimension separately
        smooth_path = []
        for dim in range(3):  # X, Y, Z coordinates
            # Create cubic spline
            tck = interpolate.splrep(t, positions[:, dim], s=self.smoothing_factor, 
                                   k=min(3, len(positions) - 1))
            # Evaluate spline at high resolution
            smooth_dim = interpolate.splev(t_smooth, tck)
            smooth_path.append(smooth_dim)
        
        return np.array(smooth_path).T
    
    def _linear_interpolation(self, positions: np.ndarray) -> np.ndarray:
        """Simple linear interpolation for few control points."""
        if len(positions) < 2:
            return positions
        
        interpolated_points = []
        for i in range(len(positions) - 1):
            start = positions[i]
            end = positions[i + 1]
            
            # Create interpolated points between start and end
            for j in range(self.path_resolution):
                t = j / self.path_resolution
                point = start + t * (end - start)
                interpolated_points.append(point)
        
        # Add final point
        interpolated_points.append(positions[-1])
        
        return np.array(interpolated_points)
    
    def _apply_wire_tension(self) -> np.ndarray:
        """
        Apply wire tension effects and Gaussian smoothing to the path.

        Algorithm:
        1. Apply physical tension simulation (reduces sharp curves)
        2. Apply Gaussian blur smoothing for ultra-smooth curves
        3. Preserve endpoints (brackets positions remain fixed)

        This creates extremely smooth, natural-looking orthodontic wire paths.
        """
        if self.wire_path is None or len(self.wire_path) < 3:
            return self.wire_path

        smoothed_path = self.wire_path.copy()

        # Step 1: Physical tension simulation
        tension_factor = self.wire_tension

        for i in range(1, len(smoothed_path) - 1):
            # Calculate curvature at this point
            p1 = smoothed_path[i - 1]
            p2 = smoothed_path[i]
            p3 = smoothed_path[i + 1]

            # Vector from previous to next point (chord)
            chord = p3 - p1

            # Current deviation from chord
            deviation = p2 - (p1 + chord / 2)

            # Apply tension - reduce deviation based on tension
            tension_adjustment = deviation * (1.0 - tension_factor)
            smoothed_path[i] = p2 - tension_adjustment

        # Step 2: Gaussian smoothing for ultra-smooth curves
        smoothed_path = self._apply_gaussian_smoothing(smoothed_path)

        return smoothed_path

    def _apply_gaussian_smoothing(self, path: np.ndarray, sigma: float = 12.0) -> np.ndarray:
        """
        Apply MAXIMUM Gaussian smoothing for perfectly smooth curves.

        Algorithm:
        1. Apply very strong Gaussian filter (sigma=12.0)
        2. Apply MULTIPLE passes (5 times) for extra smoothness
        3. No endpoint preservation - full smoothing everywhere

        This creates the smoothest possible wire at the cost of slight deviation from brackets.

        Args:
            path: Wire path points (Nx3 array)
            sigma: Gaussian kernel standard deviation (12.0 = maximum smoothness)

        Returns:
            Maximum-smoothed wire path with NO sharp edges
        """
        from scipy.ndimage import gaussian_filter1d

        if len(path) < 5:
            return path

        smoothed = path.copy()

        # Apply Gaussian filter to each dimension
        for dim in range(3):  # X, Y, Z
            # Apply smoothing 5 times for maximum effect
            temp = path[:, dim].copy()

            for pass_num in range(5):  # 5 passes of smoothing
                temp = gaussian_filter1d(
                    temp,
                    sigma=sigma,  # Maximum sigma = 12.0
                    mode='nearest'
                )

            smoothed[:, dim] = temp

        return smoothed
    
    def _validate_and_clean_path(self) -> np.ndarray:
        """Validate and clean the generated wire path."""
        if self.wire_path is None or len(self.wire_path) == 0:
            return np.array([])
        
        cleaned_path = []
        
        for i, point in enumerate(self.wire_path):
            # Skip if too close to previous point
            if cleaned_path and np.linalg.norm(point - cleaned_path[-1]) < self.minimum_segment_length:
                continue
            
            # Check for valid coordinates
            if np.any(np.isnan(point)) or np.any(np.isinf(point)):
                continue
            
            cleaned_path.append(point)
        
        return np.array(cleaned_path) if cleaned_path else np.array([])
    
    def update_control_point(self, index: int, new_position: np.ndarray):
        """Update a control point position and regenerate path."""
        if 0 <= index < len(self.control_points):
            self.control_points[index]['position'] = new_position.copy()
            # Regenerate path with updated control point
            self.wire_path = self._interpolate_spline_path()
            self.wire_path = self._apply_wire_tension()
            self.wire_path = self._validate_and_clean_path()
    
    def adjust_bend_angle(self, control_point_index: int, bend_adjustment: float):
        """Adjust bending at a specific control point."""
        if 0 <= control_point_index < len(self.control_points):
            cp = self.control_points[control_point_index]
            cp['bend_angle'] += bend_adjustment
            cp['bend_angle'] = np.clip(cp['bend_angle'], -45, 45)
            
            # Apply bend effect to position
            # This is a simplified bend simulation
            if cp['type'] == 'bracket':
                original_pos = cp['original_position']
                bend_factor = cp['bend_angle'] / 45.0  # Normalize to [-1, 1]
                
                # Apply small positional adjustment based on bend
                bend_offset = np.array([0, bend_factor * 0.5, 0])  # 0.5mm max offset
                cp['position'] = original_pos + bend_offset
                
                # Regenerate path
                self.wire_path = self._interpolate_spline_path()
                self.wire_path = self._apply_wire_tension()
                self.wire_path = self._validate_and_clean_path()
    
    def get_path_length(self) -> float:
        """Calculate total length of the wire path."""
        if self.wire_path is None or len(self.wire_path) < 2:
            return 0.0
        
        total_length = 0.0
        for i in range(len(self.wire_path) - 1):
            segment_length = np.linalg.norm(self.wire_path[i + 1] - self.wire_path[i])
            total_length += segment_length
        
        return total_length
    
    def calculate_bends(self, bend_threshold: float = 5.0) -> List[Dict]:
        """
        Calculate bend positions and angles for manufacturing.
        
        Args:
            bend_threshold: Minimum angle (degrees) to consider a bend
            
        Returns:
            List of bend information dictionaries
        """
        if self.wire_path is None or len(self.wire_path) < 3:
            return []
        
        bends = []
        
        for i in range(1, len(self.wire_path) - 1):
            p1 = self.wire_path[i - 1]
            p2 = self.wire_path[i]
            p3 = self.wire_path[i + 1]
            
            # Calculate vectors
            v1 = p2 - p1
            v2 = p3 - p2
            
            # Skip if vectors are too short
            if np.linalg.norm(v1) < 0.01 or np.linalg.norm(v2) < 0.01:
                continue
            
            # Normalize vectors
            v1_norm = v1 / np.linalg.norm(v1)
            v2_norm = v2 / np.linalg.norm(v2)
            
            # Calculate angle between vectors
            dot_product = np.clip(np.dot(v1_norm, v2_norm), -1, 1)
            angle = np.degrees(np.arccos(dot_product))
            bend_angle = 180 - angle
            
            if abs(bend_angle) > bend_threshold:
                # Calculate bend direction
                cross_product = np.cross(v1_norm, v2_norm)
                bend_direction = 'left' if cross_product[2] > 0 else 'right'
                
                # Calculate wire length to this point
                wire_length = 0.0
                for j in range(i):
                    wire_length += np.linalg.norm(self.wire_path[j + 1] - self.wire_path[j])
                
                bends.append({
                    'position': p2.copy(),
                    'angle': bend_angle,
                    'direction': bend_direction,
                    'wire_length': wire_length,
                    'radius': self.bend_radius,
                    'path_index': i
                })

        return bends

    def set_smoothness(self, smoothness_points: int):
        """
        Set the curve smoothness (number of interpolation points).

        Args:
            smoothness_points: Number of points (10-1000)
        """
        self.path_resolution = max(10, min(1000, smoothness_points))

    def set_wire_diameter(self, diameter_mm: float):
        """
        Set the wire diameter.

        Args:
            diameter_mm: Wire diameter in millimeters (0.3-2.0)
        """
        self.wire_diameter = max(0.3, min(2.0, diameter_mm))