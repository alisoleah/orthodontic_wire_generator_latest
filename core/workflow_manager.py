"""
Workflow Manager for Hybrid Automatic/Manual Orthodontic Wire Generator

Manages the workflow state and coordinates between different components.
Supports three modes: Automatic, Manual, and Hybrid.
"""

import numpy as np
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple
import open3d as o3d

from core.mesh_processor import MeshProcessor
from core.tooth_detector import ToothDetector
from core.bracket_positioner import BracketPositioner
from wire.wire_path_creator import WirePathCreator


class WorkflowMode(Enum):
    """Workflow modes for wire generation"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    HYBRID = "hybrid"


class WorkflowManager:
    """
    Manages the workflow for orthodontic wire generation.
    Coordinates between automatic detection, manual design, and hybrid approaches.
    """
    
    def __init__(self):
        """Initialize the workflow manager"""
        # Core components
        self.mesh_processor = MeshProcessor()
        self.tooth_detector = ToothDetector()
        self.bracket_positioner = BracketPositioner()
        self.wire_path_creator = WirePathCreator()
        
        # State management
        self.current_mode = WorkflowMode.AUTOMATIC
        self.active_arch = 'upper'
        self.global_height_offset = 0.0
        
        # Data storage for both arches
        self.arch_data = {
            'upper': {
                'mesh': None,
                'file_path': None,
                'teeth_detected': [],
                'bracket_positions': [],
                'control_points': [],
                'wire_path': None,
                'arch_center': None
            },
            'lower': {
                'mesh': None,
                'file_path': None,
                'teeth_detected': [],
                'bracket_positions': [],
                'control_points': [],
                'wire_path': None,
                'arch_center': None
            }
        }
        
        # Opposing arch for collision detection
        self.opposing_arch_mesh = None
    
    # ============================================
    # MODE AND STATE MANAGEMENT
    # ============================================
    
    def set_mode(self, mode: WorkflowMode):
        """Set the current workflow mode"""
        self.current_mode = mode
        print(f"Workflow mode changed to: {mode.value}")
    
    def set_active_arch(self, arch_type: str):
        """Set which arch is currently active for editing"""
        if arch_type in ['upper', 'lower']:
            self.active_arch = arch_type
            print(f"Active arch set to: {arch_type}")
    
    def get_active_arch(self) -> str:
        """Get the currently active arch"""
        return self.active_arch
    
    def get_arch_data(self, arch_type: str) -> Optional[Dict]:
        """Get data for a specific arch"""
        if arch_type in self.arch_data:
            return self.arch_data[arch_type]
        return None
    
    def get_active_arch_data(self) -> Optional[Dict]:
        """Get data for the currently active arch"""
        return self.arch_data[self.active_arch]
    
    def set_global_height(self, height_offset: float):
        """Set global height offset for wire"""
        self.global_height_offset = height_offset
        print(f"Global height offset set to: {height_offset:.2f}mm")
    
    # ============================================
    # MESH LOADING
    # ============================================
    
    def load_arch(self, file_path: str, arch_type: str):
        """
        Load a dental arch STL file.
        
        Args:
            file_path: Path to STL file
            arch_type: 'upper' or 'lower'
        """
        if arch_type not in ['upper', 'lower']:
            raise ValueError(f"Invalid arch type: {arch_type}")
        
        # Load and process mesh
        mesh = o3d.io.read_triangle_mesh(file_path)
        
        if not mesh.has_vertices():
            raise ValueError(f"Failed to load mesh from {file_path}")
        
        print(f"Loaded STL: {len(mesh.vertices)} vertices, {len(mesh.triangles)} triangles")
        
        # Clean and process mesh
        mesh = self.mesh_processor.clean_mesh(mesh)
        mesh.compute_vertex_normals()
        
        print(f"Mesh cleaned: {len(mesh.vertices)} vertices, {len(mesh.triangles)} triangles")
        
        # Store mesh data
        self.arch_data[arch_type]['mesh'] = mesh
        self.arch_data[arch_type]['file_path'] = file_path
        
        # Calculate arch center for reference
        vertices = np.asarray(mesh.vertices)
        arch_center = np.mean(vertices, axis=0)
        self.arch_data[arch_type]['arch_center'] = arch_center
        
        print(f"Successfully loaded {arch_type} arch: {len(mesh.vertices)} vertices")
    
    def load_opposing_arch(self, file_path: str):
        """Load opposing arch for collision detection"""
        mesh = o3d.io.read_triangle_mesh(file_path)
        
        if not mesh.has_vertices():
            raise ValueError(f"Failed to load opposing arch from {file_path}")
        
        mesh = self.mesh_processor.clean_mesh(mesh)
        mesh.compute_vertex_normals()
        
        self.opposing_arch_mesh = mesh
        print(f"Loaded opposing arch: {len(mesh.vertices)} vertices")
    
    def has_opposing_arch(self) -> bool:
        """Check if opposing arch is loaded"""
        return self.opposing_arch_mesh is not None
    
    # ============================================
    # AUTOMATIC WORKFLOW
    # ============================================
    
    def run_automatic_detection(self, arch_type: str = None) -> Tuple[List, List, np.ndarray]:
        """
        Run automatic tooth detection and wire generation.
        
        Args:
            arch_type: 'upper' or 'lower', defaults to active arch
            
        Returns:
            Tuple of (detected_teeth, bracket_positions, wire_path)
        """
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.arch_data[arch_type]
        mesh = arch_data['mesh']
        
        if mesh is None:
            raise ValueError(f"No mesh loaded for {arch_type} arch")
        
        # Step 1: Detect teeth
        print(f"Detecting teeth for {arch_type} arch...")
        detected_teeth = self.tooth_detector.detect_teeth(mesh, arch_type)
        arch_data['teeth_detected'] = detected_teeth
        print(f"Detected {len(detected_teeth)} teeth using angular segmentation")
        
        # Step 2: Position brackets
        print(f"Positioning brackets...")
        bracket_positions = self.bracket_positioner.calculate_positions(
            detected_teeth,
            mesh,
            arch_data['arch_center'],
            arch_type
        )
        arch_data['bracket_positions'] = bracket_positions
        print(f"Positioned {len(bracket_positions)} brackets ({sum(1 for b in bracket_positions if b.get('visible', True))} visible)")
        
        # Step 3: Generate wire path
        print(f"Generating wire path...")
        wire_path = self.generate_wire_from_brackets(arch_type)
        arch_data['wire_path'] = wire_path
        
        return detected_teeth, bracket_positions, wire_path
    
    def generate_wire_from_brackets(self, arch_type: str = None) -> np.ndarray:
        """
        ✅ FIXED: Generate wire path from bracket positions.
        Now includes arch_center parameter and correct return value handling.
        """
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.arch_data[arch_type]
        bracket_positions = arch_data.get('bracket_positions', [])
        arch_center = arch_data.get('arch_center')
        
        if not bracket_positions:
            raise ValueError(f"No bracket positions found for {arch_type} arch")
        
        if arch_center is None:
            raise ValueError(f"No arch center found for {arch_type} arch")
        
        # Get visible brackets only
        visible_brackets = [b for b in bracket_positions if b.get('visible', True)]
        
        if len(visible_brackets) < 2:
            raise ValueError(f"Need at least 2 visible brackets, found {len(visible_brackets)}")
        
        # Extract control points from bracket positions
        control_points = []
        for bracket in visible_brackets:
            # Use the current position (with height offset applied)
            pos = bracket['position'].copy()
            
            # Apply global height offset
            if self.global_height_offset != 0.0:
                normal = bracket['normal']
                pos = pos + normal * self.global_height_offset
            
            control_points.append({
                'position': pos,
                'original_position': bracket['original_position'].copy(),
                'type': 'bracket',
                'index': bracket['tooth_index'],
                'bend_angle': 0.0,
                'vertical_offset': self.global_height_offset
            })
        
        # ✅ FIXED: Handle single return value
        wire_path = self.wire_path_creator.create_smooth_path(
            control_points,
            arch_center
        )
        
        return wire_path
    
    # ============================================
    # MANUAL WORKFLOW
    # ============================================
    
    def add_control_point(self, point: np.ndarray, arch_type: str = None):
        """
        Add a manually selected control point.
        
        Args:
            point: 3D point coordinates
            arch_type: 'upper' or 'lower', defaults to active arch
        """
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.arch_data[arch_type]
        
        control_point = {
            'position': point.copy(),
            'original_position': point.copy(),
            'type': 'manual',
            'index': len(arch_data['control_points']),
            'bend_angle': 0.0,
            'vertical_offset': 0.0
        }
        
        arch_data['control_points'].append(control_point)
        print(f"Added control point {len(arch_data['control_points'])} for {arch_type} arch")
    
    def update_control_point(self, index: int, new_position: np.ndarray, arch_type: str = None):
        """Update position of a control point"""
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.arch_data[arch_type]
        control_points = arch_data['control_points']
        
        if 0 <= index < len(control_points):
            control_points[index]['position'] = new_position.copy()
            print(f"Updated control point {index + 1} for {arch_type} arch")
    
    def clear_control_points(self, arch_type: str = None):
        """Clear all manually placed control points"""
        if arch_type is None:
            arch_type = self.active_arch
        
        self.arch_data[arch_type]['control_points'] = []
        print(f"Cleared control points for {arch_type} arch")
    
    def generate_wire_from_control_points(self, arch_type: str = None) -> np.ndarray:
        """
        ✅ UPDATED METHOD: Generate wire from manually placed control points.
        Now uses bracket positions to follow teeth between the 3 points.
        
        Args:
            arch_type: 'upper' or 'lower', defaults to active arch
            
        Returns:
            Wire path as numpy array of 3D points
        """
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.arch_data[arch_type]
        manual_points = arch_data.get('control_points', [])
        
        if len(manual_points) < 3:
            raise ValueError(f"Need at least 3 control points, have {len(manual_points)}")
        
        # ✅ FIX: Use bracket positions if available (follows teeth)
        bracket_positions = arch_data.get('bracket_positions', [])
        
        if bracket_positions and len(bracket_positions) > 0:
            # Wire follows teeth using bracket positions
            wire_path = self._generate_wire_following_teeth(manual_points, bracket_positions)
        else:
            # Fallback: Simple spline through the 3 points
            wire_path = self._generate_simple_spline(manual_points)
        
        arch_data['wire_path'] = wire_path
        return wire_path
    
    def _generate_wire_following_teeth(self, manual_points: List[Dict], 
                                   bracket_positions: List[Dict]) -> np.ndarray:
        """
        ✅ FIXED: Generate wire that follows teeth between manually selected points.
        Now includes arch_center parameter and correct return value handling.
        """
        # Get arch center
        arch_type = self.active_arch
        arch_data = self.arch_data[arch_type]
        arch_center = arch_data.get('arch_center')
        
        if arch_center is None:
            print("Warning: No arch center found, falling back to simple spline")
            return self._generate_simple_spline(manual_points)
        
        # Extract positions from manual points
        p1 = manual_points[0]['position']
        p2 = manual_points[1]['position']
        p3 = manual_points[2]['position']
        
        # Get visible brackets
        visible_brackets = [b for b in bracket_positions if b.get('visible', True)]
        
        if len(visible_brackets) < 2:
            # Not enough brackets, fall back to simple spline
            return self._generate_simple_spline(manual_points)
        
        # Sort brackets by position along the arch
        # Use the first manual point as reference
        bracket_distances = []
        for bracket in visible_brackets:
            dist = np.linalg.norm(bracket['position'] - p1)
            bracket_distances.append((dist, bracket))
        
        bracket_distances.sort(key=lambda x: x[0])
        sorted_brackets = [b[1] for b in bracket_distances]
        
        # Find brackets between p1 and p3
        # Simple approach: use all brackets that are within the bounding box
        min_coords = np.minimum(np.minimum(p1, p2), p3)
        max_coords = np.maximum(np.maximum(p1, p2), p3)
        
        relevant_brackets = []
        for bracket in sorted_brackets:
            pos = bracket['position']
            if np.all(pos >= min_coords - 5) and np.all(pos <= max_coords + 5):
                relevant_brackets.append(bracket)
        
        # Build control points: manual points + relevant brackets
        all_control_points = []
        
        # Add first manual point
        all_control_points.append({
            'position': p1.copy(),
            'original_position': p1.copy(),
            'type': 'manual',
            'index': 0,
            'bend_angle': 0.0,
            'vertical_offset': self.global_height_offset
        })
        
        # Add brackets between p1 and p2
        for bracket in relevant_brackets[:len(relevant_brackets)//2]:
            pos = bracket['position'].copy()
            if self.global_height_offset != 0.0:
                pos = pos + bracket['normal'] * self.global_height_offset
            
            all_control_points.append({
                'position': pos,
                'original_position': bracket['original_position'].copy(),
                'type': 'bracket',
                'index': bracket['tooth_index'],
                'bend_angle': 0.0,
                'vertical_offset': self.global_height_offset
            })
        
        # Add second manual point
        all_control_points.append({
            'position': p2.copy(),
            'original_position': p2.copy(),
            'type': 'manual',
            'index': 1,
            'bend_angle': 0.0,
            'vertical_offset': self.global_height_offset
        })
        
        # Add brackets between p2 and p3
        for bracket in relevant_brackets[len(relevant_brackets)//2:]:
            pos = bracket['position'].copy()
            if self.global_height_offset != 0.0:
                pos = pos + bracket['normal'] * self.global_height_offset
            
            all_control_points.append({
                'position': pos,
                'original_position': bracket['original_position'].copy(),
                'type': 'bracket',
                'index': bracket['tooth_index'],
                'bend_angle': 0.0,
                'vertical_offset': self.global_height_offset
            })
        
        # Add third manual point
        all_control_points.append({
            'position': p3.copy(),
            'original_position': p3.copy(),
            'type': 'manual',
            'index': 2,
            'bend_angle': 0.0,
            'vertical_offset': self.global_height_offset
        })
        
        # ✅ FIXED: Handle single return value
        wire_path = self.wire_path_creator.create_smooth_path(
            all_control_points,
            arch_center
        )
        
        return wire_path
    
    def _generate_simple_spline(self, manual_points: List[Dict]) -> np.ndarray:
        """
        ✅ FIXED: Generate simple spline through manual points (fallback).
        Now includes arch_center parameter and correct return value handling.
        """
        # Get arch center
        arch_type = self.active_arch
        arch_data = self.arch_data[arch_type]
        arch_center = arch_data.get('arch_center')
        
        if arch_center is None:
            # Fallback: calculate center from manual points
            positions = [mp['position'] for mp in manual_points]
            arch_center = np.mean(positions, axis=0)
            print(f"Warning: Using calculated center from manual points: {arch_center}")
        
        # ✅ FIXED: Handle single return value
        wire_path = self.wire_path_creator.create_smooth_path(
            manual_points,
            arch_center
        )
        
        return wire_path
    
    # ============================================
    # HYBRID WORKFLOW
    # ============================================
    
    def extract_control_points_from_auto(self, arch_type: str = None) -> List[np.ndarray]:
        """
        Extract control points from automatically generated wire path.
        Used for hybrid workflow to convert automatic wire to manual editing.
        
        Args:
            arch_type: 'upper' or 'lower', defaults to active arch
            
        Returns:
            List of 3D points as numpy arrays
        """
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.arch_data[arch_type]
        
        if not arch_data:
            raise ValueError(f"{arch_type} arch not loaded")
        
        wire_path = arch_data.get('wire_path')
        
        if wire_path is None or len(wire_path) == 0:
            raise ValueError(f"No wire path found for {arch_type} arch")
        
        # Extract evenly spaced points from wire path
        # Use 10-15 control points for good editability
        num_control_points = min(15, max(5, len(wire_path) // 20))
        
        indices = np.linspace(0, len(wire_path) - 1, num_control_points, dtype=int)
        control_points = [wire_path[i] for i in indices]
        
        # Store these as control points in the arch data
        arch_data['control_points'] = [
            {
                'position': pt.copy(),
                'original_position': pt.copy(),
                'type': 'converted',
                'index': i,
                'bend_angle': 0.0,
                'vertical_offset': 0.0
            }
            for i, pt in enumerate(control_points)
        ]
        
        return control_points
    
    # ============================================
    # COLLISION DETECTION
    # ============================================
    
    def detect_collisions(self, arch_type: str = None) -> List[np.ndarray]:
        """
        Detect collisions between wire and opposing arch.
        
        Args:
            arch_type: 'upper' or 'lower', defaults to active arch
            
        Returns:
            List of collision points
        """
        if arch_type is None:
            arch_type = self.active_arch
        
        if not self.has_opposing_arch():
            raise ValueError("No opposing arch loaded for collision detection")
        
        arch_data = self.arch_data[arch_type]
        wire_path = arch_data.get('wire_path')
        
        if wire_path is None or len(wire_path) == 0:
            raise ValueError(f"No wire path found for {arch_type} arch")
        
        # Simple collision detection: check if wire points are inside opposing mesh
        collisions = []
        
        # Convert opposing mesh to point cloud for distance calculations
        opposing_vertices = np.asarray(self.opposing_arch_mesh.vertices)
        
        # For each wire point, check distance to nearest opposing mesh vertex
        collision_threshold = 2.0  # mm - adjust based on wire diameter
        
        for wire_point in wire_path:
            distances = np.linalg.norm(opposing_vertices - wire_point, axis=1)
            min_distance = np.min(distances)
            
            if min_distance < collision_threshold:
                collisions.append(wire_point.copy())
        
        print(f"Found {len(collisions)} collision points")
        return collisions
    
    # ============================================
    # EXPORT FUNCTIONS
    # ============================================
    
    def export_gcode(self, wire_size: float = 0.9, arch_type: str = None) -> str:
        """Export wire path as G-code"""
        if arch_type is None:
            arch_type = self.active_arch
        
        arch_data = self.arch_data[arch_type]
        wire_path = arch_data.get('wire_path')
        
        if wire_path is None or len(wire_path) == 0:
            return ""
        
        # Generate G-code
        gcode_lines = [
            "; Orthodontic Wire G-Code",
            f"; Arch: {arch_type}",
            f"; Wire Size: {wire_size}mm",
            f"; Points: {len(wire_path)}",
            "",
            "G21 ; mm",
            "G90 ; absolute",
            "G28 ; home",
            ""
        ]
        
        # Add wire path movements
        for i, point in enumerate(wire_path):
            x, y, z = point
            gcode_lines.append(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f} F1000")
        
        gcode_lines.append("")
        gcode_lines.append("M30 ; end")
        
        return "\n".join(gcode_lines)
    
    def export_esp32(self, wire_size: float = 0.9, arch_type: str = None) -> str:
        """Export wire path as ESP32 Arduino code and return the code as string"""
        from export.esp32_generator import ESP32Generator

        if arch_type is None:
            arch_type = self.active_arch

        arch_data = self.arch_data[arch_type]
        wire_path = arch_data.get('wire_path')

        if wire_path is None or len(wire_path) == 0:
            return ""

        # Generate ESP32 code
        generator = ESP32Generator()
        esp32_code = generator.generate(
            wire_path=wire_path,
            arch_type=arch_type,
            wire_size=f"{wire_size}mm"
        )

        return esp32_code
    
    def export_stl(self, file_path: str, arch_type: str = None):
        """Export wire as STL mesh"""
        # Placeholder implementation
        print(f"STL export to {file_path} - not yet implemented")
    
    # ============================================
    # STATUS AND UTILITIES
    # ============================================
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        upper_data = self.arch_data['upper']
        lower_data = self.arch_data['lower']
        
        return {
            'mode': self.current_mode.value,
            'active_arch': self.active_arch,
            'upper_loaded': upper_data['mesh'] is not None,
            'lower_loaded': lower_data['mesh'] is not None,
            'upper_teeth': len(upper_data['teeth_detected']),
            'lower_teeth': len(lower_data['teeth_detected']),
            'upper_wire': upper_data['wire_path'] is not None,
            'lower_wire': lower_data['wire_path'] is not None,
            'height_offset': self.global_height_offset,
            'opposing_arch': self.has_opposing_arch()
        }
    
    def reset_workflow(self):
        """Reset all workflow data"""
        self.arch_data = {
            'upper': {
                'mesh': None,
                'file_path': None,
                'teeth_detected': [],
                'bracket_positions': [],
                'control_points': [],
                'wire_path': None,
                'arch_center': None
            },
            'lower': {
                'mesh': None,
                'file_path': None,
                'teeth_detected': [],
                'bracket_positions': [],
                'control_points': [],
                'wire_path': None,
                'arch_center': None
            }
        }
        self.opposing_arch_mesh = None
        self.global_height_offset = 0.0
        print("Workflow reset")