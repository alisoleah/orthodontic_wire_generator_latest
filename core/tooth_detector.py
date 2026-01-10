
# ================================================================
# core/tooth_detector.py
"""Tooth detection and classification algorithms."""

import numpy as np
from typing import List, Dict

class ToothDetector:
    """Detects and classifies teeth from dental meshes."""
    
    def __init__(self):
        """Initialize tooth detector."""
        self.detection_parameters = {
            'crown_ratio_upper': 0.25,
            'crown_ratio_lower': 0.75,
            'height_tolerance': 2.0,
            'min_tooth_vertices': 30,
            'min_tooth_spacing': 3.0,
            'expected_teeth': 14,
            'max_teeth': 16
        }
        
    def detect_teeth(self, mesh, arch_type: str) -> List[Dict]:
        """Detect teeth from mesh using angular segmentation."""
        if mesh is None:
            print("Error: Mesh is None, cannot detect teeth")
            return []

        if not hasattr(mesh, 'vertices') or len(mesh.vertices) == 0:
            print("Error: Mesh has no vertices")
            return []

        vertices = np.asarray(mesh.vertices)
        bbox = mesh.get_axis_aligned_bounding_box()
        center = mesh.get_center()
        extent = bbox.get_extent()
        
        # Identify anatomical axes
        lr_axis = np.argmax(extent)  # Left-Right (widest)
        height_axis = np.argmin(extent)  # Occlusal-Gingival (smallest)
        ap_axis = 3 - lr_axis - height_axis  # Anterior-Posterior
        
        print(f"Anatomical axes - LR: {lr_axis}, AP: {ap_axis}, Height: {height_axis}")
        
        # Sample at crown level
        crown_ratio = (self.detection_parameters['crown_ratio_upper'] if arch_type == 'upper' 
                      else self.detection_parameters['crown_ratio_lower'])
        crown_level = bbox.min_bound[height_axis] + extent[height_axis] * crown_ratio
        
        # Get crown vertices
        height_tolerance = self.detection_parameters['height_tolerance']
        crown_mask = np.abs(vertices[:, height_axis] - crown_level) < height_tolerance
        crown_vertices = vertices[crown_mask]
        
        if len(crown_vertices) < 100:
            print("Warning: Very few crown vertices detected")
            return []
        
        print(f"Crown level: {crown_level:.1f}mm, Crown vertices: {len(crown_vertices)}")
        
        # Angular segmentation
        teeth = self._angular_segmentation(crown_vertices, center, lr_axis, ap_axis)
        
        print(f"Detected {len(teeth)} teeth using angular segmentation")
        return teeth
    
    def _angular_segmentation(self, crown_vertices: np.ndarray, center: np.ndarray,
                            lr_axis: int, ap_axis: int) -> List[Dict]:
        """Segment teeth using angular analysis."""
        # Calculate angles
        angles = np.arctan2(
            crown_vertices[:, ap_axis] - center[ap_axis],
            crown_vertices[:, lr_axis] - center[lr_axis]
        )
        
        # Find posterior gap (largest gap between teeth)
        sorted_angles = np.sort(angles)
        angle_diffs = np.diff(sorted_angles)
        angle_diffs = np.append(angle_diffs, sorted_angles[0] + 2*np.pi - sorted_angles[-1])
        
        posterior_gap_idx = np.argmax(angle_diffs)
        posterior_gap_size = angle_diffs[posterior_gap_idx]
        
        # Define segments
        expected_teeth = self.detection_parameters['expected_teeth']
        active_angle_range = 2 * np.pi - posterior_gap_size
        angle_per_tooth = active_angle_range / expected_teeth
        start_angle = sorted_angles[(posterior_gap_idx + 1) % len(sorted_angles)]
        
        teeth = []
        for i in range(expected_teeth + 2):
            tooth_start = start_angle + i * angle_per_tooth
            tooth_end = tooth_start + angle_per_tooth
            
            # Normalize angles
            tooth_start = np.mod(tooth_start + np.pi, 2*np.pi) - np.pi
            tooth_end = np.mod(tooth_end + np.pi, 2*np.pi) - np.pi
            
            # Get vertices in segment
            if tooth_start < tooth_end:
                angle_mask = (angles >= tooth_start) & (angles < tooth_end)
            else:
                angle_mask = (angles >= tooth_start) | (angles < tooth_end)
            
            segment_vertices = crown_vertices[angle_mask]
            
            if len(segment_vertices) < self.detection_parameters['min_tooth_vertices']:
                continue
            
            # Calculate tooth center
            tooth_center = np.mean(segment_vertices, axis=0)
            tooth_angle = np.arctan2(
                tooth_center[ap_axis] - center[ap_axis],
                tooth_center[lr_axis] - center[lr_axis]
            )
            
            teeth.append({
                'center': tooth_center,
                'vertices': segment_vertices,
                'angle': tooth_angle,
                'ap_position': tooth_center[ap_axis],
                'lr_position': tooth_center[lr_axis],
                'index': len(teeth),
                'type': 'posterior'  # Will be classified later
            })
        
        # Filter teeth that are too close together
        filtered_teeth = self._filter_close_teeth(teeth)

        # Classify teeth into incisors, canines, and posterior
        classified_teeth = self.classify_teeth(filtered_teeth, center)

        return classified_teeth
    
    def _filter_close_teeth(self, teeth: List[Dict]) -> List[Dict]:
        """Remove teeth that are too close to each other."""
        if not teeth:
            return []
        
        filtered_teeth = []
        sorted_teeth = sorted(teeth, key=lambda t: t['angle'])
        min_spacing = self.detection_parameters['min_tooth_spacing']
        
        for tooth in sorted_teeth:
            if not filtered_teeth:
                filtered_teeth.append(tooth)
            else:
                # Check distance to previous tooth
                prev_tooth = filtered_teeth[-1]
                dist = np.linalg.norm(tooth['center'] - prev_tooth['center'])
                if dist > min_spacing:
                    filtered_teeth.append(tooth)
        
        # Limit to reasonable number of teeth
        max_teeth = self.detection_parameters['max_teeth']
        if len(filtered_teeth) > max_teeth:
            filtered_teeth = filtered_teeth[:max_teeth]
        
        return filtered_teeth
    
    def classify_teeth(self, teeth: List[Dict], arch_center: np.ndarray) -> List[Dict]:
        """Classify teeth into incisors, canines, and posterior."""
        if len(teeth) < 6:
            print("Not enough teeth for classification")
            return teeth
        
        # Reset all to posterior
        for tooth in teeth:
            tooth['type'] = 'posterior'
        
        # Sort by anterior position (most anterior first)
        # Lower ap_position values are more anterior (front), higher are posterior (back)
        teeth_by_ap = sorted(teeth, key=lambda t: t['ap_position'], reverse=False)
        
        # Take the 6 most anterior teeth
        anterior_count = min(6, len(teeth_by_ap))
        anterior_teeth = teeth_by_ap[:anterior_count]
        
        # Sort by left-right position
        anterior_teeth_by_lr = sorted(anterior_teeth, key=lambda t: t['lr_position'])
        
        # Assign types to anterior teeth
        if len(anterior_teeth_by_lr) >= 6:
            # Canines (outermost)
            anterior_teeth_by_lr[0]['type'] = 'canine'
            anterior_teeth_by_lr[5]['type'] = 'canine'
            
            # Incisors (inner 4)
            for i in range(1, 5):
                anterior_teeth_by_lr[i]['type'] = 'incisor'
        elif len(anterior_teeth_by_lr) >= 4:
            # If we have at least 4 anterior teeth, make the middle ones incisors
            start_idx = (len(anterior_teeth_by_lr) - 2) // 2
            end_idx = start_idx + 2
            for i in range(start_idx, min(end_idx, len(anterior_teeth_by_lr))):
                anterior_teeth_by_lr[i]['type'] = 'incisor'
        
        # Count classification results
        classification_counts = {}
        for tooth in teeth:
            tooth_type = tooth['type']
            classification_counts[tooth_type] = classification_counts.get(tooth_type, 0) + 1
        
        print("Tooth classification:")
        for tooth_type, count in classification_counts.items():
            print(f"  • {tooth_type.title()}: {count}")
        
        return teeth


    # ============================================
    # PHASE 3: IMPROVED DETECTION METHODS
    # ============================================
    
    def detect_overlaps(self, teeth: List[Dict]) -> List[tuple]:
        """
        Detect overlapping teeth (crowding).
        
        Returns list of (tooth1_idx, tooth2_idx, overlap_score) tuples
        """
        overlaps = []
        
        for i, tooth1 in enumerate(teeth):
            for j, tooth2 in enumerate(teeth[i+1:], start=i+1):
                # Calculate distance between tooth centers
                dist = np.linalg.norm(tooth1['center'] - tooth2['center'])
                
                # If centers are very close, teeth likely overlap
                if dist < 5.0:  # 5mm threshold
                    overlap_score = 1.0 - (dist / 5.0)
                    overlaps.append((i, j, overlap_score))
        
        return overlaps
    
    def detect_missing_teeth(self, teeth: List[Dict], expected_count: int = 14) -> List[Dict]:
        """
        Detect missing teeth by analyzing gaps in angular distribution.
        
        Returns list of dictionaries with 'position' and 'gap_size'
        """
        if len(teeth) >= expected_count:
            return []  # No missing teeth
        
        # Calculate angular positions
        angles = []
        for tooth in teeth:
            center = tooth['center']
            angle = np.arctan2(center[1], center[0])  # Assuming XY plane
            angles.append(np.degrees(angle) % 360)
        
        angles.sort()
        
        # Expected spacing between teeth
        expected_spacing = 360.0 / expected_count
        
        # Find large gaps
        missing = []
        for i in range(len(angles)):
            next_angle = angles[(i + 1) % len(angles)]
            if i == len(angles) - 1:
                gap = (360 - angles[i]) + angles[0]
            else:
                gap = next_angle - angles[i]
            
            # If gap is significantly larger than expected
            if gap > expected_spacing * 1.5:
                num_missing = int(round(gap / expected_spacing)) - 1
                if num_missing > 0:
                    missing.append({
                        'position': (angles[i] + gap / 2) % 360,
                        'gap_size': gap,
                        'estimated_missing': num_missing
                    })
        
        return missing
    
    def calculate_tooth_confidence(self, tooth: Dict) -> float:
        """
        Calculate detection confidence score (0-100%).
        
        Based on:
        - Vertex count (more = better)
        - Compactness (tighter cluster = better)
        - Size (appropriate size = better)
        """
        # Vertex count score
        vertex_count = len(tooth.get('vertices', []))
        vertex_score = min(vertex_count / 1000.0, 1.0)  # Normalize to 1.0
        
        # Compactness score
        if 'vertices' in tooth and 'center' in tooth:
            vertices = tooth['vertices']
            center = tooth['center']
            distances = np.linalg.norm(vertices - center, axis=1)
            std_dev = np.std(distances)
            compactness_score = 1.0 / (1.0 + std_dev / 10.0)  # Normalize
        else:
            compactness_score = 0.5
        
        # Size score (teeth should be reasonable size)
        if 'vertices' in tooth:
            bbox_size = np.ptp(tooth['vertices'], axis=0)
            avg_size = np.mean(bbox_size)
            # Ideal tooth size is around 8-12mm
            size_score = 1.0 - abs(avg_size - 10.0) / 10.0
            size_score = max(0.0, min(1.0, size_score))
        else:
            size_score = 0.5
        
        # Combine scores
        confidence = (vertex_score * 0.4 + compactness_score * 0.4 + size_score * 0.2) * 100
        return max(0.0, min(100.0, confidence))
    
    def detect_tooth_rotation(self, tooth_vertices: np.ndarray) -> float:
        """
        Detect tooth rotation angle using PCA.
        
        Returns rotation angle in degrees (0 = no rotation)
        """
        if len(tooth_vertices) < 3:
            return 0.0
        
        # Use only XY plane (ignore Z for rotation)
        xy_vertices = tooth_vertices[:, :2]
        
        # Center the vertices
        centered = xy_vertices - np.mean(xy_vertices, axis=0)
        
        # Calculate covariance matrix
        cov_matrix = np.cov(centered.T)
        
        # Get eigenvectors (principal components)
        eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
        
        # Principal axis is the eigenvector with largest eigenvalue
        principal_idx = np.argmax(eigenvalues)
        principal_axis = eigenvectors[:, principal_idx]
        
        # Calculate angle from expected orientation (AP axis = [0, 1])
        expected_axis = np.array([0, 1])
        cos_angle = np.dot(principal_axis, expected_axis)
        rotation_angle = np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
        
        # Return absolute rotation (0-90 degrees)
        return min(rotation_angle, 180 - rotation_angle)
