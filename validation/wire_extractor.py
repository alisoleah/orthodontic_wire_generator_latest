"""
Wire Extractor - Extract wire centerline from 3D printed reference STL

This module extracts the wire path from a 3D printed wire STL file
by identifying the thin cylindrical structure and computing its centerline.
"""

import numpy as np
import trimesh
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter1d
from typing import Optional, Tuple
import open3d as o3d


class WireExtractor:
    """
    Extract wire centerline from 3D printed reference STL files.
    """
    
    def __init__(self, wire_diameter_mm: float = 0.9):
        """
        Initialize wire extractor.
        
        Args:
            wire_diameter_mm: Expected wire diameter in mm
        """
        self.wire_diameter = wire_diameter_mm
    
    def extract_from_stl(self, stl_path: str, num_points: int = 500) -> np.ndarray:
        """
        Extract wire centerline from STL file.
        
        Args:
            stl_path: Path to reference wire STL file
            num_points: Number of points to resample the centerline to
            
        Returns:
            numpy array of shape (num_points, 3) representing wire centerline
        """
        print(f"Loading reference wire from: {stl_path}")
        
        # Load mesh using trimesh
        mesh = trimesh.load(stl_path)
        
        # If mesh has multiple bodies, take the largest one
        if isinstance(mesh, trimesh.Scene):
            mesh = max(mesh.geometry.values(), key=lambda m: len(m.vertices))
        
        print(f"Mesh loaded: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
        
        # Extract centerline using medial axis approximation
        centerline = self._extract_centerline_medial_axis(mesh)
        
        # Smooth the centerline
        centerline = self._smooth_centerline(centerline)
        
        # Resample to desired number of points
        centerline = self._resample_curve(centerline, num_points)
        
        print(f"Extracted centerline: {len(centerline)} points")
        
        return centerline
    
    def _extract_centerline_medial_axis(self, mesh: trimesh.Trimesh) -> np.ndarray:
        """
        Extract centerline using medial axis approximation.
        
        Strategy:
        1. Sample points along the mesh surface
        2. For each point, find the local "center" by averaging nearby points
        3. Filter to keep only points that are roughly centered
        4. Order points along the curve
        """
        # Sample points from mesh surface
        points, face_indices = trimesh.sample.sample_surface(mesh, count=5000)
        
        # Build KD-tree for efficient nearest neighbor search
        tree = cKDTree(points)
        
        # For each point, compute local center
        centerline_points = []
        radius_threshold = self.wire_diameter * 1.5  # Points within this radius
        
        for point in points:
            # Find nearby points
            indices = tree.query_ball_point(point, radius_threshold)
            
            if len(indices) > 10:  # Need enough neighbors
                nearby = points[indices]
                
                # Compute local center (mean of nearby points)
                local_center = np.mean(nearby, axis=0)
                
                # Check if this point is close to the local center (i.e., it's centerline-like)
                distance_to_center = np.linalg.norm(point - local_center)
                
                if distance_to_center < self.wire_diameter * 0.3:
                    centerline_points.append(local_center)
        
        centerline_points = np.array(centerline_points)
        
        # Remove duplicates (points too close together)
        centerline_points = self._remove_duplicates(centerline_points, min_distance=0.5)
        
        # Order points along the curve
        centerline_points = self._order_points_along_curve(centerline_points)
        
        return centerline_points
    
    def _remove_duplicates(self, points: np.ndarray, min_distance: float) -> np.ndarray:
        """Remove points that are too close together."""
        if len(points) == 0:
            return points
        
        unique_points = [points[0]]
        
        for point in points[1:]:
            # Check distance to all existing unique points
            distances = np.linalg.norm(np.array(unique_points) - point, axis=1)
            if np.min(distances) > min_distance:
                unique_points.append(point)
        
        return np.array(unique_points)
    
    def _order_points_along_curve(self, points: np.ndarray) -> np.ndarray:
        """
        Order points along the curve using nearest neighbor traversal.
        """
        if len(points) < 2:
            return points
        
        # Start from the point with minimum Y coordinate (posterior)
        current_idx = np.argmin(points[:, 1])
        ordered = [points[current_idx]]
        remaining = list(range(len(points)))
        remaining.remove(current_idx)
        
        # Greedily add nearest unvisited point
        while remaining:
            current_point = ordered[-1]
            distances = np.linalg.norm(points[remaining] - current_point, axis=1)
            nearest_idx = remaining[np.argmin(distances)]
            ordered.append(points[nearest_idx])
            remaining.remove(nearest_idx)
        
        return np.array(ordered)
    
    def _smooth_centerline(self, centerline: np.ndarray, sigma: float = 2.0) -> np.ndarray:
        """
        Smooth the centerline using Gaussian filter.
        """
        if len(centerline) < 3:
            return centerline
        
        # Apply Gaussian smoothing to each coordinate
        smoothed = np.zeros_like(centerline)
        for i in range(3):
            smoothed[:, i] = gaussian_filter1d(centerline[:, i], sigma=sigma)
        
        return smoothed
    
    def _resample_curve(self, curve: np.ndarray, num_points: int) -> np.ndarray:
        """
        Resample curve to have exactly num_points evenly spaced along arc length.
        """
        if len(curve) < 2:
            return curve
        
        # Calculate cumulative arc length
        segments = np.diff(curve, axis=0)
        segment_lengths = np.linalg.norm(segments, axis=1)
        cumulative_length = np.concatenate([[0], np.cumsum(segment_lengths)])
        total_length = cumulative_length[-1]
        
        # Create evenly spaced arc length samples
        target_lengths = np.linspace(0, total_length, num_points)
        
        # Interpolate to find points at target arc lengths
        resampled = np.zeros((num_points, 3))
        for i in range(3):
            resampled[:, i] = np.interp(target_lengths, cumulative_length, curve[:, i])
        
        return resampled


def extract_wire_from_stl(stl_path: str, num_points: int = 500) -> np.ndarray:
    """
    Convenience function to extract wire from STL file.
    
    Args:
        stl_path: Path to reference wire STL
        num_points: Number of points in output
        
    Returns:
        Wire centerline as numpy array
    """
    extractor = WireExtractor()
    return extractor.extract_from_stl(stl_path, num_points)
