
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

