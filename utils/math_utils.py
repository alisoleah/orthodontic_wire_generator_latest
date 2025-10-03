
# ================================================================
# utils/math_utils.py
"""Mathematical utility functions for wire generation."""

import numpy as np
from typing import List, Tuple
from scipy import interpolate

class MathUtils:
    """Mathematical utilities for wire path calculations."""
    
    @staticmethod
    def calculate_arc_length(points: np.ndarray) -> float:
        """Calculate total arc length of a path."""
        if len(points) < 2:
            return 0.0
        
        total_length = 0.0
        for i in range(len(points) - 1):
            segment_length = np.linalg.norm(points[i + 1] - points[i])
            total_length += segment_length
        
        return total_length
    
    @staticmethod
    def calculate_curvature(points: np.ndarray, index: int) -> float:
        """Calculate curvature at a specific point."""
        if index < 1 or index >= len(points) - 1:
            return 0.0
        
        p1 = points[index - 1]
        p2 = points[index]
        p3 = points[index + 1]
        
        # Calculate vectors
        v1 = p2 - p1
        v2 = p3 - p2
        
        # Calculate curvature using the formula: |v1 × v2| / |v1|³
        cross_product = np.cross(v1, v2)
        v1_magnitude = np.linalg.norm(v1)
        
        if v1_magnitude < 1e-6:
            return 0.0
        
        if len(cross_product.shape) == 0:  # 2D case
            curvature = abs(cross_product) / (v1_magnitude ** 3)
        else:  # 3D case
            curvature = np.linalg.norm(cross_product) / (v1_magnitude ** 3)
        
        return curvature
    
    @staticmethod
    def smooth_path(points: np.ndarray, smoothing_factor: float = 0.1) -> np.ndarray:
        """Apply smoothing to a path using moving average."""
        if len(points) < 3:
            return points
        
        smoothed = points.copy()
        
        for i in range(1, len(points) - 1):
            # Simple moving average smoothing
            neighbor_avg = (points[i - 1] + points[i + 1]) / 2
            smoothed[i] = (1 - smoothing_factor) * points[i] + smoothing_factor * neighbor_avg
        
        return smoothed
    
    @staticmethod
    def resample_path(points: np.ndarray, target_spacing: float) -> np.ndarray:
        """Resample path to have uniform spacing between points."""
        if len(points) < 2:
            return points
        
        # Calculate cumulative distances
        distances = [0.0]
        for i in range(1, len(points)):
            dist = np.linalg.norm(points[i] - points[i - 1])
            distances.append(distances[-1] + dist)
        
        total_length = distances[-1]
        if total_length < target_spacing:
            return points
        
        # Create target distances
        num_points = int(total_length / target_spacing) + 1
        target_distances = np.linspace(0, total_length, num_points)
        
        # Interpolate points at target distances
        resampled_points = []
        for target_dist in target_distances:
            # Find the segment containing this distance
            for i in range(len(distances) - 1):
                if distances[i] <= target_dist <= distances[i + 1]:
                    # Interpolate within this segment
                    segment_progress = (target_dist - distances[i]) / (distances[i + 1] - distances[i])
                    interpolated_point = points[i] + segment_progress * (points[i + 1] - points[i])
                    resampled_points.append(interpolated_point)
                    break
        
        return np.array(resampled_points) if resampled_points else points
    
    @staticmethod
    def calculate_bending_angle(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """Calculate bending angle at point p2."""
        v1 = p2 - p1
        v2 = p3 - p2
        
        if np.linalg.norm(v1) < 1e-6 or np.linalg.norm(v2) < 1e-6:
            return 0.0
        
        v1_norm = v1 / np.linalg.norm(v1)
        v2_norm = v2 / np.linalg.norm(v2)
        
        dot_product = np.clip(np.dot(v1_norm, v2_norm), -1, 1)
        angle = np.degrees(np.arccos(dot_product))
        
        return 180 - angle  # Return supplement of angle

