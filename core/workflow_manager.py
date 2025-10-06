"""
Workflow Manager for Hybrid Automatic/Manual Orthodontic Wire Generator

This module manages different workflow modes and transitions between them:
- Automatic Detection: Quick wire generation using existing algorithms
- Manual Design: Full FixR-style control point placement
- Hybrid: Start with automatic, then manually refine

Plus: Dual-arch support for loading both upper and lower jaws simultaneously.
"""

from enum import Enum
import numpy as np
from typing import Optional, Dict, List, Tuple, Any

try:
    from .mesh_processor import MeshProcessor
    from .tooth_detector import ToothDetector
    from .bracket_positioner import BracketPositioner
    from ..wire.wire_path_creator import WirePathCreator
    from ..wire.wire_path_creator_enhanced import WirePathCreatorEnhanced
    from ..export.gcode_generator import GCodeGenerator
    from ..export.esp32_generator import ESP32Generator
    from ..export.stl_exporter import STLExporter
except ImportError:
    # Fallback to absolute imports when run as top-level script
    from core.mesh_processor import MeshProcessor
    from core.tooth_detector import ToothDetector
    from core.bracket_positioner import BracketPositioner
    from wire.wire_path_creator import WirePathCreator
    from wire.wire_path_creator_enhanced import WirePathCreatorEnhanced
    from export.gcode_generator import GCodeGenerator
    from export.esp32_generator import ESP32Generator
    from export.stl_exporter import STLExporter


class WorkflowMode(Enum):
    """Enumeration of available workflow modes"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    HYBRID = "hybrid"


class WorkflowManager:
    """
    Manages different workflow modes and transitions between them
    """
    
    def __init__(self):
        self.current_mode = WorkflowMode.AUTOMATIC
        self.upper_arch_data = None
        self.lower_arch_data = None
        self.opposing_arch_data = None
        self.active_arch = 'upper'
        self.global_height_offset = 0.0
        
        # Initialize processors
        self.mesh_processor = MeshProcessor()
        self.tooth_detector = ToothDetector()
        self.bracket_positioner = BracketPositioner()
        self.wire_path_creator = WirePathCreator()
        self.wire_path_creator_enhanced = WirePathCreatorEnhanced()
        
        # Initialize exporters
        self.gcode_generator = GCodeGenerator()
        self.esp32_generator = ESP32Generator()
        self.stl_exporter = STLExporter()
        
        # Occlusal plane for manual mode
        self.occlusal_plane_points = []
        self.occlusal_plane_normal = None
        
    def set_mode(self, mode: WorkflowMode):
        """Switch between workflow modes"""
        self.current_mode = mode
        self.notify_mode_change()
    
    def notify_mode_change(self):
        """Notify observers of mode change"""
        # This can be extended to emit signals or call callbacks
        print(f"Workflow mode changed to: {self.current_mode.value}")
    
    def is_dual_arch_loaded(self):
        """Check if both arches are loaded"""
        return self.upper_arch_data is not None and self.lower_arch_data is not None
    
    def has_opposing_arch(self):
        """Check if opposing arch is loaded for collision detection"""
        return self.opposing_arch_data is not None
    
    def load_arch(self, stl_path: str, arch_type: str = 'upper') -> Dict[str, Any]:
        """
        Load STL file for upper or lower arch
        
        Args:
            stl_path: Path to STL file
            arch_type: 'upper' or 'lower'
            
        Returns:
            Dictionary containing mesh data and metadata
        """
        try:
            # Load the mesh
            mesh_data = self.mesh_processor.load_mesh(stl_path)

            if mesh_data is None:
                print(f"Error: Failed to load mesh from {stl_path}")
                return None

            # Clean the mesh
            mesh_data = self.mesh_processor.clean_mesh(mesh_data)

            arch_data = {
                'mesh': mesh_data,
                'stl_path': stl_path,
                'control_points': [],
                'wire_path': None,
                'teeth_detected': None,
                'bracket_positions': None,
                'last_modified': None
            }

            if arch_type == 'upper':
                self.upper_arch_data = arch_data
            else:
                self.lower_arch_data = arch_data

            print(f"Successfully loaded {arch_type} arch: {len(mesh_data.vertices)} vertices")
            return mesh_data

        except Exception as e:
            print(f"Error loading arch {arch_type}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def load_opposing_arch(self, stl_path: str) -> Dict[str, Any]:
        """
        Load opposing arch for collision detection

        Args:
            stl_path: Path to opposing arch STL file

        Returns:
            Dictionary containing opposing arch mesh data
        """
        try:
            # Load the mesh
            mesh_data = self.mesh_processor.load_mesh(stl_path)

            if mesh_data is None:
                print(f"Error: Failed to load opposing arch from {stl_path}")
                return None

            # Clean the mesh
            mesh_data = self.mesh_processor.clean_mesh(mesh_data)

            self.opposing_arch_data = {
                'mesh': mesh_data,
                'stl_path': stl_path
            }

            print(f"Successfully loaded opposing arch: {len(mesh_data.vertices)} vertices")
            return mesh_data

        except Exception as e:
            print(f"Error loading opposing arch: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_arch_data(self, arch_type: str) -> Optional[Dict[str, Any]]:
        """Get arch data for specified arch type"""
        if arch_type == 'upper':
            return self.upper_arch_data
        elif arch_type == 'lower':
            return self.lower_arch_data
        else:
            return None
    
    def set_active_arch(self, arch_type: str):
        """Set which arch is currently being designed"""
        if arch_type in ['upper', 'lower']:
            self.active_arch = arch_type
    
    def get_active_arch(self) -> str:
        """Get currently active arch"""
        return self.active_arch
    
    def get_active_arch_data(self) -> Optional[Dict[str, Any]]:
        """Get data for currently active arch"""
        return self.get_arch_data(self.active_arch)
    
    def set_global_height(self, height_mm: float):
        """Set global height offset for wire"""
        self.global_height_offset = height_mm
    
    # ============================================
    # AUTOMATIC MODE FUNCTIONS
    # ============================================
    
    def run_automatic_detection(self, arch_type: str = None) -> Tuple[List, List, np.ndarray]:
        """
        Run automatic tooth detection and wire generation
        
        Args:
            arch_type: 'upper' or 'lower', defaults to active arch
            
        Returns:
            Tuple of (detected_teeth, bracket_positions, wire_path)
        """
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.get_arch_data(arch_type)
        if arch_data is None:
            raise ValueError(f"No {arch_type} arch loaded")

        # Step 1: Detect teeth
        detected_teeth = self.tooth_detector.detect_teeth(arch_data['mesh'], arch_type)
        arch_data['teeth_detected'] = detected_teeth

        # Get arch center for bracket positioning
        arch_center = arch_data['mesh'].get_center()

        # Step 2: Position brackets
        bracket_positions = self.bracket_positioner.calculate_positions(
            detected_teeth,
            arch_data['mesh'],
            arch_center,
            arch_type
        )
        arch_data['bracket_positions'] = bracket_positions
        
        # Step 3: Generate wire path
        wire_path = self.wire_path_creator_enhanced.create_smooth_path(
            bracket_positions,
            arch_center,
            height_offset=self.global_height_offset
        )
        arch_data['wire_path'] = wire_path
        
        return detected_teeth, bracket_positions, wire_path
    
    def extract_control_points_from_auto(self, arch_type: str = None) -> List[np.ndarray]:
        """
        Extract control points from automatic wire for manual editing
        
        Args:
            arch_type: 'upper' or 'lower', defaults to active arch
            
        Returns:
            List of control points
        """
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.get_arch_data(arch_type)
        if arch_data is None or arch_data['bracket_positions'] is None:
            raise ValueError(f"No automatic wire generated for {arch_type} arch")
        
        # Convert bracket positions to control points
        control_points = []
        for bracket_pos in arch_data['bracket_positions']:
            # Add height offset
            control_point = bracket_pos.copy()
            control_point[2] += self.global_height_offset  # Assuming Z is up
            control_points.append(control_point)
        
        arch_data['control_points'] = control_points
        return control_points
    
    # ============================================
    # MANUAL MODE FUNCTIONS
    # ============================================
    
    def set_occlusal_plane_points(self, points: List[np.ndarray]):
        """
        Set the three points that define the occlusal plane
        
        Args:
            points: List of 3 points defining the occlusal plane
        """
        if len(points) != 3:
            raise ValueError("Occlusal plane requires exactly 3 points")
        
        self.occlusal_plane_points = points
        self.occlusal_plane_normal = self._calculate_plane_normal(points)
    
    def _calculate_plane_normal(self, points: List[np.ndarray]) -> np.ndarray:
        """Calculate normal vector from 3 points"""
        if len(points) < 3:
            return None
        
        v1 = points[1] - points[0]
        v2 = points[2] - points[0]
        normal = np.cross(v1, v2)
        return normal / np.linalg.norm(normal)
    
    def reset_occlusal_plane(self):
        """Reset occlusal plane definition"""
        self.occlusal_plane_points = []
        self.occlusal_plane_normal = None
    
    def add_control_point(self, point: np.ndarray, arch_type: str = None):
        """
        Add a control point for manual wire design
        
        Args:
            point: 3D point coordinates
            arch_type: 'upper' or 'lower', defaults to active arch
        """
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.get_arch_data(arch_type)
        if arch_data is None:
            raise ValueError(f"No {arch_type} arch loaded")
        
        # Project point to occlusal plane if defined
        if self.occlusal_plane_normal is not None:
            projected_point = self._project_to_occlusal_plane(point)
        else:
            projected_point = point.copy()
        
        # Add height offset
        projected_point[2] += self.global_height_offset
        
        arch_data['control_points'].append(projected_point)
    
    def _project_to_occlusal_plane(self, point: np.ndarray) -> np.ndarray:
        """Project a point onto the defined occlusal plane"""
        if len(self.occlusal_plane_points) < 3:
            return point
        
        plane_point = self.occlusal_plane_points[0]
        normal = self.occlusal_plane_normal
        
        # Project point onto plane
        v = point - plane_point
        distance = np.dot(v, normal)
        projected = point - distance * normal
        
        return projected
    
    def remove_last_control_point(self, arch_type: str = None):
        """Remove the last placed control point"""
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.get_arch_data(arch_type)
        if arch_data is not None and len(arch_data['control_points']) > 0:
            arch_data['control_points'].pop()
    
    def clear_control_points(self, arch_type: str = None):
        """Clear all control points"""
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.get_arch_data(arch_type)
        if arch_data is not None:
            arch_data['control_points'] = []
    
    def update_control_point(self, index: int, new_position: np.ndarray, arch_type: str = None):
        """
        Update position of a specific control point
        
        Args:
            index: Index of control point to update
            new_position: New 3D position
            arch_type: 'upper' or 'lower', defaults to active arch
        """
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.get_arch_data(arch_type)
        if arch_data is None:
            raise ValueError(f"No {arch_type} arch loaded")
        
        if 0 <= index < len(arch_data['control_points']):
            # Apply height offset
            adjusted_position = new_position.copy()
            adjusted_position[2] += self.global_height_offset
            arch_data['control_points'][index] = adjusted_position
    
    def generate_wire_from_control_points(self, arch_type: str = None) -> np.ndarray:
        """
        Generate wire path from manually placed control points
        
        Args:
            arch_type: 'upper' or 'lower', defaults to active arch
            
        Returns:
            Wire path as numpy array
        """
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.get_arch_data(arch_type)
        if arch_data is None or len(arch_data['control_points']) < 2:
            raise ValueError(f"Need at least 2 control points for {arch_type} arch")

        # Get arch center for proper wire generation
        arch_center = arch_data['mesh'].get_center()
        
        # Convert control points (numpy arrays) to the dictionary format expected by the wire path creator
        control_points_as_dicts = [{'position': p} for p in arch_data['control_points']]

        # Generate smooth wire path through control points
        wire_path = self.wire_path_creator_enhanced.create_smooth_path(
            control_points_as_dicts,
            arch_center,
            height_offset=0.0  # Height already applied to control points
        )
        
        arch_data['wire_path'] = wire_path
        return wire_path
    
    # ============================================
    # COLLISION DETECTION
    # ============================================
    
    def detect_collisions(self, arch_type: str = None) -> List[np.ndarray]:
        """
        Detect collisions between wire and opposing arch
        
        Args:
            arch_type: 'upper' or 'lower', defaults to active arch
            
        Returns:
            List of collision points
        """
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.get_arch_data(arch_type)
        if arch_data is None or arch_data['wire_path'] is None:
            raise ValueError(f"No wire path generated for {arch_type} arch")
        
        if self.opposing_arch_data is None:
            raise ValueError("No opposing arch loaded for collision detection")
        
        # Use collision detector to find intersections
        from .collision_detector2 import CollisionDetector2
        collision_detector = CollisionDetector2()
        
        collisions = collision_detector.detect_wire_mesh_collisions(
            arch_data['wire_path'],
            self.opposing_arch_data['mesh']
        )
        
        return collisions
    
    # ============================================
    # EXPORT FUNCTIONS
    # ============================================
    
    def export_gcode(self, file_path: str, arch_type: str = None):
        """Export wire as G-code"""
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.get_arch_data(arch_type)
        if arch_data is None or arch_data['wire_path'] is None:
            raise ValueError(f"No wire path to export for {arch_type} arch")
        
        self.gcode_generator.generate_gcode(arch_data['wire_path'], file_path)
    
    def export_esp32(self, file_path: str, arch_type: str = None):
        """Export wire as ESP32 Arduino code"""
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.get_arch_data(arch_type)
        if arch_data is None or arch_data['wire_path'] is None:
            raise ValueError(f"No wire path to export for {arch_type} arch")
        
        self.esp32_generator.generate_code(arch_data['wire_path'], file_path)
    
    def export_stl(self, file_path: str, arch_type: str = None):
        """Export wire as STL file"""
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.get_arch_data(arch_type)
        if arch_data is None or arch_data['wire_path'] is None:
            raise ValueError(f"No wire path to export for {arch_type} arch")
        
        self.stl_exporter.export_wire_stl(arch_data['wire_path'], file_path)
    
    # ============================================
    # UTILITY FUNCTIONS
    # ============================================
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            'mode': self.current_mode.value,
            'active_arch': self.active_arch,
            'upper_loaded': self.upper_arch_data is not None,
            'lower_loaded': self.lower_arch_data is not None,
            'opposing_loaded': self.opposing_arch_data is not None,
            'dual_arch_loaded': self.is_dual_arch_loaded(),
            'height_offset': self.global_height_offset,
            'occlusal_plane_defined': len(self.occlusal_plane_points) == 3
        }
    
    def reset_workflow(self):
        """Reset all workflow data"""
        self.upper_arch_data = None
        self.lower_arch_data = None
        self.opposing_arch_data = None
        self.active_arch = 'upper'
        self.global_height_offset = 0.0
        self.occlusal_plane_points = []
        self.occlusal_plane_normal = None
        self.current_mode = WorkflowMode.AUTOMATIC
