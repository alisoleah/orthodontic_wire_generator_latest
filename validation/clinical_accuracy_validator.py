"""
Clinical Accuracy Validator

Validates generated wires against reference wires using:
- ICP (Iterative Closest Point) alignment
- RMS deviation calculation
- Maximum deviation analysis
- Clinical acceptability criteria
"""

import numpy as np
from scipy.spatial import cKDTree
from typing import Dict, Tuple, Optional
import copy


class ClinicalAccuracyValidator:
    """
    Validate generated wire accuracy against reference wires.
    """
    
    # Clinical acceptability thresholds (in mm)
    RMS_THRESHOLD = 0.15  # ±0.15mm RMS deviation
    MAX_THRESHOLD = 0.30  # No point > 0.30mm deviation
    BRACKET_THRESHOLD = 0.20  # Per-bracket deviation < 0.20mm
    
    def __init__(self):
        """Initialize validator."""
        pass
    
    def validate(self, generated_wire: np.ndarray, reference_wire: np.ndarray) -> Dict:
        """
        Validate generated wire against reference wire.
        
        Args:
            generated_wire: Generated wire path (N, 3)
            reference_wire: Reference wire path (M, 3)
            
        Returns:
            Dictionary with validation results:
            - rms_deviation_mm: RMS deviation in mm
            - max_deviation_mm: Maximum deviation in mm
            - mean_deviation_mm: Mean deviation in mm
            - acceptable: Boolean indicating clinical acceptability
            - aligned_wire: Aligned generated wire
            - deviations: Point-wise deviations
        """
        print("\\n" + "="*60)
        print("CLINICAL ACCURACY VALIDATION")
        print("="*60)
        
        # Ensure both wires have the same number of points for comparison
        if len(generated_wire) != len(reference_wire):
            print(f"Resampling wires to match: gen={len(generated_wire)}, ref={len(reference_wire)}")
            # Resample both to 500 points
            generated_wire = self._resample_curve(generated_wire, 500)
            reference_wire = self._resample_curve(reference_wire, 500)
        
        # Align wires using ICP
        print("Aligning wires using ICP...")
        aligned_wire, transformation = self.align_wires_icp(generated_wire, reference_wire)
        
        # Calculate deviations
        deviations = np.linalg.norm(aligned_wire - reference_wire, axis=1)
        
        # Calculate metrics
        rms_deviation = np.sqrt(np.mean(deviations ** 2))
        max_deviation = np.max(deviations)
        mean_deviation = np.mean(deviations)
        
        # Clinical acceptability
        acceptable = (
            rms_deviation < self.RMS_THRESHOLD and
            max_deviation < self.MAX_THRESHOLD
        )
        
        # Print results
        print(f"\\nValidation Results:")
        print(f"  RMS Deviation:  {rms_deviation:.3f} mm {'✓' if rms_deviation < self.RMS_THRESHOLD else '✗'}")
        print(f"  Max Deviation:  {max_deviation:.3f} mm {'✓' if max_deviation < self.MAX_THRESHOLD else '✗'}")
        print(f"  Mean Deviation: {mean_deviation:.3f} mm")
        print(f"  Clinical Status: {'✓ ACCEPTABLE' if acceptable else '✗ NOT ACCEPTABLE'}")
        print("="*60 + "\\n")
        
        return {
            'rms_deviation_mm': float(rms_deviation),
            'max_deviation_mm': float(max_deviation),
            'mean_deviation_mm': float(mean_deviation),
            'acceptable': acceptable,
            'aligned_wire': aligned_wire,
            'deviations': deviations,
            'transformation': transformation
        }
    
    def align_wires_icp(self, source: np.ndarray, target: np.ndarray, 
                        max_iterations: int = 50, tolerance: float = 1e-6) -> Tuple[np.ndarray, np.ndarray]:
        """
        Align source wire to target wire using Iterative Closest Point (ICP).
        
        Args:
            source: Source point cloud (N, 3)
            target: Target point cloud (M, 3)
            max_iterations: Maximum ICP iterations
            tolerance: Convergence tolerance
            
        Returns:
            (aligned_source, transformation_matrix)
        """
        # Initialize
        current_source = source.copy()
        prev_error = float('inf')
        
        # Build KD-tree for target for fast nearest neighbor search
        tree = cKDTree(target)
        
        # Cumulative transformation
        cumulative_transform = np.eye(4)
        
        for iteration in range(max_iterations):
            # Find nearest neighbors
            distances, indices = tree.query(current_source)
            
            # Calculate current error
            current_error = np.mean(distances)
            
            # Check convergence
            if abs(prev_error - current_error) < tolerance:
                break
            
            prev_error = current_error
            
            # Get corresponding points
            corresponding_target = target[indices]
            
            # Calculate transformation
            transform = self._calculate_transformation(current_source, corresponding_target)
            
            # Apply transformation
            current_source = self._apply_transformation(current_source, transform)
            
            # Update cumulative transformation
            cumulative_transform = transform @ cumulative_transform
        
        return current_source, cumulative_transform
    
    def _calculate_transformation(self, source: np.ndarray, target: np.ndarray) -> np.ndarray:
        """
        Calculate rigid transformation (rotation + translation) between point sets.
        Uses SVD-based method.
        """
        # Center the point clouds
        source_center = np.mean(source, axis=0)
        target_center = np.mean(target, axis=0)
        
        source_centered = source - source_center
        target_centered = target - target_center
        
        # Calculate cross-covariance matrix
        H = source_centered.T @ target_centered
        
        # SVD
        U, S, Vt = np.linalg.svd(H)
        
        # Calculate rotation
        R = Vt.T @ U.T
        
        # Handle reflection case
        if np.linalg.det(R) < 0:
            Vt[-1, :] *= -1
            R = Vt.T @ U.T
        
        # Calculate translation
        t = target_center - R @ source_center
        
        # Build 4x4 transformation matrix
        transform = np.eye(4)
        transform[:3, :3] = R
        transform[:3, 3] = t
        
        return transform
    
    def _apply_transformation(self, points: np.ndarray, transform: np.ndarray) -> np.ndarray:
        """Apply 4x4 transformation matrix to 3D points."""
        # Convert to homogeneous coordinates
        ones = np.ones((len(points), 1))
        points_homogeneous = np.hstack([points, ones])
        
        # Apply transformation
        transformed = (transform @ points_homogeneous.T).T
        
        # Convert back to 3D
        return transformed[:, :3]
    
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
    
    def calculate_per_bracket_deviation(self, aligned_wire: np.ndarray, 
                                       reference_wire: np.ndarray,
                                       num_brackets: int = 14) -> np.ndarray:
        """
        Calculate deviation at each bracket position.
        
        Assumes brackets are evenly spaced along the wire.
        """
        # Sample bracket positions (evenly spaced along wire)
        bracket_indices = np.linspace(0, len(aligned_wire) - 1, num_brackets, dtype=int)
        
        # Calculate deviations at bracket positions
        bracket_deviations = np.linalg.norm(
            aligned_wire[bracket_indices] - reference_wire[bracket_indices],
            axis=1
        )
        
        return bracket_deviations


def validate_wire(generated_wire: np.ndarray, reference_wire: np.ndarray) -> Dict:
    """
    Convenience function to validate a wire.
    
    Args:
        generated_wire: Generated wire path
        reference_wire: Reference wire path
        
    Returns:
        Validation results dictionary
    """
    validator = ClinicalAccuracyValidator()
    return validator.validate(generated_wire, reference_wire)
