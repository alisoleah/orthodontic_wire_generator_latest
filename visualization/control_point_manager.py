
# ================================================================
# visualization/control_point_manager.py
"""Control point selection and manipulation."""

import numpy as np
from typing import Optional, List, Dict

class ControlPointManager:
    """Manages control point selection and manipulation."""
    
    def __init__(self):
        """Initialize control point manager."""
        self.control_points = []
        self.selected_index = None
        self.wire_path_creator = None
        self.wire_mesh_builder = None
        self.selection_history = []
        
    def setup(self, control_points: List[Dict], 
              wire_path_creator, wire_mesh_builder):
        """Setup with control points and generators."""
        self.control_points = control_points
        self.wire_path_creator = wire_path_creator
        self.wire_mesh_builder = wire_mesh_builder
        
    def select_control_point(self, index: int) -> bool:
        """Select a control point by index."""
        if 0 <= index < len(self.control_points):
            self.selected_index = index
            self.selection_history.append(index)
            cp = self.control_points[index]
            print(f"Selected control point {index} ({cp['type']})")
            print(f"  Position: [{cp['position'][0]:.2f}, {cp['position'][1]:.2f}, {cp['position'][2]:.2f}]")
            return True
        return False
    
    def deselect_control_point(self):
        """Deselect current control point."""
        self.selected_index = None
        print("Control point deselected")
    
    def move_selected_point(self, direction: np.ndarray, step: float = 0.5) -> bool:
        """Move the selected control point."""
        if self.selected_index is None:
            return False
        
        # Update position in data model
        old_position = self.control_points[self.selected_index]['position'].copy()
        self.control_points[self.selected_index]['position'] += direction * step
        
        # Update in wire path creator
        if self.wire_path_creator:
            self.wire_path_creator.update_control_point(
                self.selected_index,
                self.control_points[self.selected_index]['position']
            )
        
        print(f"Moved control point {self.selected_index} by {direction * step}")
        print(f"  From: [{old_position[0]:.2f}, {old_position[1]:.2f}, {old_position[2]:.2f}]")
        print(f"  To: [{self.control_points[self.selected_index]['position'][0]:.2f}, {self.control_points[self.selected_index]['position'][1]:.2f}, {self.control_points[self.selected_index]['position'][2]:.2f}]")
        return True
    
    def adjust_bend_angle(self, angle_delta: float) -> bool:
        """Adjust bend angle at selected control point."""
        if self.selected_index is None:
            return False
        
        if self.wire_path_creator:
            self.wire_path_creator.adjust_bend_angle(self.selected_index, angle_delta)
            print(f"Adjusted bend angle by {angle_delta:.1f}°")
            return True
        return False
    
    def get_selected_control_point(self) -> Optional[Dict]:
        """Get currently selected control point."""
        if self.selected_index is not None:
            return self.control_points[self.selected_index]
        return None
    
    def get_control_point_info(self, index: int) -> Optional[Dict]:
        """Get information about a specific control point."""
        if 0 <= index < len(self.control_points):
            cp = self.control_points[index]
            return {
                'index': index,
                'type': cp['type'],
                'position': cp['position'].tolist(),
                'bend_angle': cp.get('bend_angle', 0.0),
                'vertical_offset': cp.get('vertical_offset', 0.0),
                'is_selected': index == self.selected_index
            }
        return None
    
    def reset_control_points(self):
        """Reset all control points to original positions."""
        for cp in self.control_points:
            if 'original_position' in cp:
                cp['position'] = cp['original_position'].copy()
                cp['bend_angle'] = 0.0
                cp['vertical_offset'] = 0.0
        
        print("All control points reset to original positions")
        
        # Update wire path creator
        if self.wire_path_creator:
            # Regenerate path with reset positions
            pass  # This would trigger regeneration in the wire generator

