#!/usr/bin/env python3
"""
wire/wire_generator.py

WireGenerator - Main Coordinator Class with Hidden Visual Elements
================================================================
This class orchestrates the entire wire generation process by coordinating
all the different components (mesh processing, tooth detection, wire drawing, etc.)
Updated to hide bracket boxes, control point spheres, and coordinate frame.
"""

import numpy as np
import open3d as o3d
from typing import List, Dict, Optional, Tuple
import os
import time

# Import our modular components
from core.mesh_processor import MeshProcessor
from core.tooth_detector import ToothDetector
from core.bracket_positioner import BracketPositioner
from core.constants import WIRE_SIZES

from wire.wire_path_creator import WirePathCreator
from wire.wire_mesh_builder import WireMeshBuilder
from wire.height_controller import HeightController

from visualization.visualizer_3d import Visualizer3D
from visualization.control_point_manager import ControlPointManager

from export.gcode_generator import GCodeGenerator
from export.esp32_generator import ESP32Generator
from export.stl_exporter import STLExporter

class WireGenerator:
    """
    Main coordinator class that orchestrates the entire wire generation process.
    
    This class brings together all the modular components to create a complete
    orthodontic wire generation system with hidden visual elements for clean display.
    """
    
    def __init__(self, stl_path: str, arch_type: str = 'auto', wire_size: str = '0.018'):
        """Initialize the wire generator with all components."""
        self.stl_path = stl_path
        self.arch_type = arch_type
        self.wire_size = wire_size
        
        # Initialize core components
        self.mesh_processor = MeshProcessor()
        self.tooth_detector = ToothDetector()
        self.bracket_positioner = BracketPositioner()
        
        # Initialize wire components
        self.wire_path_creator = WirePathCreator()
        self.wire_mesh_builder = WireMeshBuilder()
        self.height_controller = HeightController()
        
        # Initialize visualization components
        self.visualizer = None
        self.control_point_manager = ControlPointManager()
        
        # Initialize export components
        self.gcode_generator = GCodeGenerator()
        self.esp32_generator = ESP32Generator()
        self.stl_exporter = STLExporter()
        
        # Data storage
        self.mesh = None
        self.teeth = []
        self.bracket_positions = []
        self.wire_path = None
        self.wire_mesh = None
        self.arch_center = None
        
        # Visual elements (created but hidden)
        self.bracket_meshes = []
        self.control_point_meshes = []
        self.wire_control_points = []
        
        # Height axis (will be determined during tooth detection)
        self.height_axis = 2  # Default Z-axis
        self.wire_height_offset = 0.0
        
        # Get wire radius from size
        wire_data = WIRE_SIZES.get(wire_size, 0.4572)
        if isinstance(wire_data, tuple):
            wire_radius = wire_data[0] / 2  # Use first dimension for radius
        else:
            wire_radius = wire_data / 2
        self.wire_mesh_builder.wire_radius = wire_radius
        
        # Auto-detect arch type from filename
        if arch_type == 'auto':
            self.arch_type = 'lower' if 'lower' in stl_path.lower() else 'upper'
        
        print(f"Wire Generator initialized:")
        print(f"  STL: {os.path.basename(stl_path)}")
        print(f"  Arch: {self.arch_type}")
        print(f"  Wire Size: {wire_size}")
        print(f"  Wire Radius: {wire_radius:.3f}mm")
    
    def generate_wire(self) -> Dict:
        """
        Main method to generate the complete wire.
        
        This coordinates all the steps in the wire generation pipeline.
        
        Returns:
            Dictionary containing all generated data
        """
        print("\n" + "="*60)
        print("STARTING WIRE GENERATION PIPELINE")
        print("="*60)
        
        # Step 1: Load and process STL mesh
        if not self._load_and_process_mesh():
            return None
        
        # Step 2: Detect teeth
        if not self._detect_teeth():
            return None
        
        # Step 3: Position brackets
        if not self._position_brackets():
            return None
        
        # Step 4: Create wire path
        if not self._create_wire_path():
            return None
        
        # Step 5: Build wire mesh
        if not self._build_wire_mesh():
            return None
        
        # Step 6: Setup visualization with hidden elements
        self._setup_visualization()
        
        print("\n" + "="*60)
        print("WIRE GENERATION COMPLETE")
        print("="*60)
        
        return self._get_results_summary()
    
    def _load_and_process_mesh(self) -> bool:
        """Load and process the dental STL mesh."""
        print("\n--- STEP 1: MESH PROCESSING ---")
        
        self.mesh = self.mesh_processor.load_stl(self.stl_path)
        if self.mesh is None:
            print("ERROR: Failed to load STL file")
            return False
        
        # Process mesh
        self.mesh = self.mesh_processor.clean_mesh(self.mesh)
        self.arch_center = self.mesh_processor.calculate_arch_center(self.mesh)
        
        print(f"✓ Mesh loaded: {len(self.mesh.vertices)} vertices")
        print(f"✓ Arch center: [{self.arch_center[0]:.1f}, {self.arch_center[1]:.1f}, {self.arch_center[2]:.1f}]")
        return True
    
    def _detect_teeth(self) -> bool:
        """Detect and classify teeth."""
        print("\n--- STEP 2: TOOTH DETECTION ---")
        
        self.teeth = self.tooth_detector.detect_teeth(self.mesh, self.arch_type)
        if not self.teeth:
            print("ERROR: Failed to detect teeth")
            return False
        
        print(f"✓ Detected {len(self.teeth)} teeth")
        
        # Classify teeth
        self.teeth = self.tooth_detector.classify_teeth(self.teeth, self.arch_center)
        
        # Set height axis from tooth detector
        vertices = np.asarray(self.mesh.vertices)
        bbox = self.mesh.get_axis_aligned_bounding_box()
        extent = bbox.get_extent()
        self.height_axis = np.argmin(extent)  # Occlusal-Gingival (smallest)
        
        return True
    
    def _position_brackets(self) -> bool:
        """Calculate bracket positions."""
        print("\n--- STEP 3: BRACKET POSITIONING ---")
        
        self.bracket_positions = self.bracket_positioner.calculate_positions(
            self.teeth, self.mesh, self.arch_center, self.arch_type
        )
        
        if not self.bracket_positions:
            print("ERROR: Failed to position brackets")
            return False
        
        visible_count = sum(1 for b in self.bracket_positions if b.get('visible', True))
        print(f"✓ Positioned {len(self.bracket_positions)} brackets ({visible_count} visible)")
        return True
    
    def _create_wire_path(self) -> bool:
        """Create the wire path using the path creator."""
        print("\n--- STEP 4: WIRE PATH CREATION ---")
        
        # Get current height offset from height controller
        height_offset = self.height_controller.get_height_offset()
        
        # Create wire path using the WirePathCreator
        self.wire_path = self.wire_path_creator.create_smooth_path(
            self.bracket_positions,
            self.arch_center,
            height_offset
        )
        
        if self.wire_path is None or len(self.wire_path) < 2:
            print("ERROR: Failed to create wire path")
            return False
        
        # Store control points for visualization (but they'll be hidden)
        self.wire_control_points = self.wire_path_creator.control_points
        
        path_length = self.wire_path_creator.get_path_length()
        print(f"✓ Wire path created: {len(self.wire_path)} points, {path_length:.1f}mm length")
        return True
    
    def _build_wire_mesh(self) -> bool:
        """Build the 3D wire mesh."""
        print("\n--- STEP 5: WIRE MESH CREATION ---")
        
        self.wire_mesh = self.wire_mesh_builder.build_wire_mesh(self.wire_path)
        
        if self.wire_mesh is None:
            print("ERROR: Failed to create wire mesh")
            return False
        
        mesh_stats = self.wire_mesh_builder.get_mesh_statistics()
        print(f"✓ Wire mesh created:")
        print(f"  • Vertices: {mesh_stats.get('vertex_count', 0)}")
        print(f"  • Triangles: {mesh_stats.get('triangle_count', 0)}")
        print(f"  • Segments: {mesh_stats.get('segment_count', 0)}")
        return True
    
    def _setup_visualization(self):
        """Setup visualization components with hidden elements."""
        print("\n--- STEP 6: VISUALIZATION SETUP ---")
        
        # Create enhanced visualization meshes (hidden elements)
        self.create_enhanced_visualization_meshes()
        
        self.visualizer = Visualizer3D(
            mesh=self.mesh,
            wire_mesh=self.wire_mesh,
            bracket_positions=self.bracket_positions,
            control_points=self.wire_control_points
        )
        
        # Setup control point manager
        self.control_point_manager.setup(
            self.wire_control_points,
            self.wire_path_creator,
            self.wire_mesh_builder
        )
        
        print("✓ Clean visualization ready (visual elements hidden)")
    
    def create_enhanced_visualization_meshes(self):
        """Create 3D visualization meshes with hidden visual elements."""
        print(f"\n{'─'*50}")
        print("CREATING CLEAN 3D VISUALIZATION")
        print(f"{'─'*50}")
        
        # HIDDEN: Create bracket meshes internally but don't display them
        self.bracket_meshes = []
        visible_posteriors = [b for b in self.bracket_positions if b.get('visible', True) and b['tooth_type'] == 'posterior']
        
        for i, bracket in enumerate(self.bracket_positions):
            if not bracket.get('visible', True):
                continue
            
            # Create bracket box for internal tracking only
            bracket_mesh = o3d.geometry.TriangleMesh.create_box(1.8, 2.0, 1.2)
            bracket_mesh.translate([-0.9, -1.0, -0.6])
            
            # Orient bracket (if normal available)
            if 'normal' in bracket and np.linalg.norm(bracket['normal']) > 0:
                z_axis = np.array([0, 0, 1])
                normal = bracket['normal']
                
                rotation_axis = np.cross(z_axis, normal)
                if np.linalg.norm(rotation_axis) > 1e-6:
                    rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
                    angle = np.arccos(np.clip(np.dot(z_axis, normal), -1, 1))
                    R = o3d.geometry.get_rotation_matrix_from_axis_angle(rotation_axis * angle)
                    bracket_mesh.rotate(R, center=[0, 0, 0])
            
            bracket_mesh.translate(bracket['position'])
            
            # Color based on tooth type (for internal reference)
            color = [0.7, 0.7, 0.7] # Default gray
            if bracket['tooth_type'] == 'posterior' and visible_posteriors:
                if bracket is visible_posteriors[0] or bracket is visible_posteriors[-1]:
                    color = [0.9, 0.8, 0.1]  # Yellow for corner teeth
                else:
                    color = [0.1, 0.3, 0.8]  # Blue for middle teeth
            
            bracket_mesh.paint_uniform_color(color)
            bracket_mesh.compute_vertex_normals()
            
            self.bracket_meshes.append({
                'mesh': bracket_mesh,
                'index': i,
                'original_color': color,
                'bracket': bracket
            })
        
        # HIDDEN: Create control point meshes internally but don't display them
        self.control_point_meshes = []
        for i, cp in enumerate(self.wire_control_points):
            if cp['type'] == 'bracket':
                sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.8, resolution=8)
                color = [0.9, 0.1, 0.1]  # Red for bracket points
            else:
                sphere = o3d.geometry.TriangleMesh.create_sphere(radius=1.0, resolution=8)
                color = [0.1, 0.9, 0.1]  # Green for midpoint controls
            
            # Apply height offset to control point positions
            position = cp['position'].copy()
            position[self.height_axis] += self.wire_height_offset
            
            sphere.translate(position)
            sphere.paint_uniform_color(color)
            sphere.compute_vertex_normals()
            
            self.control_point_meshes.append({
                'mesh': sphere,
                'index': i,
                'original_color': color,
                'control_point': cp
            })
        
        # Create wire mesh (this WILL be displayed)
        self.wire_mesh = self._create_wire_mesh()
        
        print(f"✓ Created {len(self.bracket_meshes)} bracket meshes (hidden)")
        print(f"✓ Created {len(self.control_point_meshes)} control point meshes (hidden)")
        print(f"✓ Created wire mesh with {len(self.wire_mesh.vertices)} vertices (visible)")
        print("✓ Clean visualization ready - only dental mesh and wire will be shown")
        
        return self.wire_mesh, self.bracket_meshes, self.control_point_meshes
    
    def _create_wire_mesh(self):
        """Create wire mesh from current wire path."""
        wire_mesh = o3d.geometry.TriangleMesh()
        
        if self.wire_path is not None and len(self.wire_path) > 1:
            for i in range(len(self.wire_path) - 1):
                p1 = self.wire_path[i]
                p2 = self.wire_path[i + 1]
                segment_length = np.linalg.norm(p2 - p1)
                
                if segment_length < 0.01 or segment_length > 30.0:
                    continue
                
                cylinder = o3d.geometry.TriangleMesh.create_cylinder(
                    radius=self.wire_mesh_builder.wire_radius,
                    height=segment_length,
                    resolution=12
                )
                
                # Orient cylinder
                z_axis = np.array([0, 0, 1])
                segment_dir = (p2 - p1) / segment_length
                
                rotation_axis = np.cross(z_axis, segment_dir)
                if np.linalg.norm(rotation_axis) > 1e-6:
                    rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
                    angle = np.arccos(np.clip(np.dot(z_axis, segment_dir), -1, 1))
                    R = o3d.geometry.get_rotation_matrix_from_axis_angle(rotation_axis * angle)
                    cylinder.rotate(R, center=[0, 0, 0])
                
                cylinder.translate((p1 + p2) / 2)
                wire_mesh += cylinder
        
        # Color wire gold
        wire_mesh.paint_uniform_color([0.85, 0.75, 0.45])
        wire_mesh.compute_vertex_normals()
        
        return wire_mesh
    
    def _get_results_summary(self) -> Dict:
        """Get summary of generation results."""
        return {
            'mesh': self.mesh,
            'teeth': self.teeth,
            'bracket_positions': self.bracket_positions,
            'wire_control_points': self.wire_control_points,
            'wire_path': self.wire_path,
            'wire_mesh': self.wire_mesh,
            'arch_center': self.arch_center,
            'wire_length': self.wire_path_creator.get_path_length(),
            'bend_count': len(self.wire_path_creator.calculate_bends()),
            'height_offset': self.height_controller.get_height_offset(),
            'components': {
                'mesh_processor': self.mesh_processor,
                'tooth_detector': self.tooth_detector,
                'bracket_positioner': self.bracket_positioner,
                'wire_path_creator': self.wire_path_creator,
                'wire_mesh_builder': self.wire_mesh_builder,
                'height_controller': self.height_controller,
                'visualizer': self.visualizer,
                'control_point_manager': self.control_point_manager
            }
        }
    
    # Height Control Interface Methods
    def adjust_wire_height(self, delta_height: float):
        """Adjust wire height and update mesh."""
        # Update height controller
        self.height_controller.adjust_height(delta_height)
        
        # Regenerate wire path with new height
        height_offset = self.height_controller.get_height_offset()
        self.wire_height_offset = height_offset
        
        self.wire_path = self.wire_path_creator.create_smooth_path(
            self.bracket_positions,
            self.arch_center,
            height_offset
        )
        
        # Rebuild wire mesh
        old_mesh = self.wire_mesh
        self.wire_mesh = self._create_wire_mesh()
        
        # Update visualization if available
        if self.visualizer:
            self.visualizer.update_wire_mesh(self.wire_mesh)
        
        print(f"Wire height adjusted by {delta_height:.2f}mm (total offset: {height_offset:.2f}mm)")
    
    def reset_wire_height(self):
        """Reset wire height to original position."""
        self.height_controller.reset_height()
        self.wire_height_offset = 0.0
        self.adjust_wire_height(0)  # Trigger rebuild with zero offset
        print("Wire height reset to original position")
    
    def get_wire_height_offset(self) -> float:
        """Get current wire height offset."""
        return self.height_controller.get_height_offset()
    
    # Control Point Interface Methods
    def select_control_point(self, index: int):
        """Select a control point for editing."""
        if self.control_point_manager:
            self.control_point_manager.select_control_point(index)
        if self.visualizer:
            self.visualizer.highlight_selected_control_point(index)
    
    def move_control_point(self, direction: np.ndarray, step: float = 0.5):
        """Move selected control point."""
        if self.control_point_manager and self.control_point_manager.move_selected_point(direction, step):
            # Regenerate wire path and mesh
            height_offset = self.height_controller.get_height_offset()
            self.wire_path = self.wire_path_creator.create_smooth_path(
                self.bracket_positions,
                self.arch_center,
                height_offset
            )
            self.wire_mesh = self._create_wire_mesh()
            
            # Update visualization
            if self.visualizer:
                self.visualizer.update_wire_mesh(self.wire_mesh)
                self.visualizer.update_control_points(self.wire_path_creator.control_points)
    
    # Export Interface Methods
    def generate_gcode(self, filename: Optional[str] = None) -> str:
        """Generate G-code for the wire."""
        bends = self.wire_path_creator.calculate_bends()
        wire_length = self.wire_path_creator.get_path_length()
        height_offset = self.height_controller.get_height_offset()
        
        return self.gcode_generator.generate(
            wire_path=self.wire_path,
            bends=bends,
            wire_length=wire_length,
            height_offset=height_offset,
            arch_type=self.arch_type,
            wire_size=self.wire_size,
            filename=filename
        )
    
    def generate_esp32_code(self) -> str:
        """Generate ESP32 Arduino code."""
        return self.esp32_generator.generate(
            wire_path=self.wire_path,
            arch_type=self.arch_type,
            wire_size=self.wire_size
        )
    
    def export_stl(self, filename: str) -> bool:
        """Export wire mesh as STL."""
        if self.wire_mesh is None:
            return False
        
        return self.stl_exporter.export(self.wire_mesh, filename)
    
    def save_design(self, filename: Optional[str] = None) -> str:
        """Save complete design to JSON."""
        design_data = {
            'metadata': {
                'arch_type': self.arch_type,
                'wire_size': self.wire_size,
                'timestamp': time.strftime("%Y%m%d_%H%M%S"),
                'stl_file': os.path.basename(self.stl_path),
                'version': 'modular_v3.0_clean_visualization'
            },
            'teeth': [tooth for tooth in self.teeth],
            'brackets': [bracket for bracket in self.bracket_positions],
            'control_points': [cp for cp in self.wire_path_creator.control_points],
            'wire_path': self.wire_path.tolist() if self.wire_path is not None else [],
            'height_offset': self.height_controller.get_height_offset(),
            'wire_length': self.wire_path_creator.get_path_length(),
            'calculated_bends': self.wire_path_creator.calculate_bends(),
            'visualization_settings': {
                'brackets_hidden': True,
                'control_points_hidden': True,
                'coordinate_frame_hidden': True
            }
        }
        
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"wire_design_{self.arch_type}_{timestamp}.json"
        
        try:
            import json
            with open(filename, 'w') as f:
                json.dump(design_data, f, indent=2, default=str)
            print(f"✓ Design saved: {filename}")
            return filename
        except Exception as e:
            print(f"✗ Save failed: {e}")
            return None
    
    # Interactive Mode
    def launch_interactive_mode(self):
        """Launch interactive 3D editor with clean visualization."""
        if self.visualizer is None:
            print("ERROR: Visualization not setup. Run generate_wire() first.")
            return
        
        print("\n" + "="*60)
        print("LAUNCHING CLEAN INTERACTIVE 3D EDITOR")
        print("="*60)
        
        # Setup interactive callbacks
        self.visualizer.setup_interactive_mode(
            height_controller=self.height_controller,
            control_point_manager=self.control_point_manager,
            wire_generator=self  # Pass self for callbacks
        )
        
        print("Visual elements hidden for clean presentation:")
        print("• Bracket boxes: HIDDEN")
        print("• Control point spheres: HIDDEN")
        print("• Coordinate frame: HIDDEN")
        print("• Only dental mesh and wire displayed")
        
        # Launch visualization
        self.visualizer.run()
    
    def print_summary(self):
        """Print generation summary."""
        print(f"\n{'='*60}")
        print("WIRE GENERATION SUMMARY")
        print(f"{'='*60}")
        print(f"STL File: {os.path.basename(self.stl_path)}")
        print(f"Arch Type: {self.arch_type.upper()}")
        print(f"Wire Size: {self.wire_size}")
        print(f"Teeth Detected: {len(self.teeth)}")
        print(f"Brackets Positioned: {len(self.bracket_positions)}")
        if self.wire_path is not None:
            print(f"Wire Length: {self.wire_path_creator.get_path_length():.1f}mm")
            print(f"Wire Points: {len(self.wire_path)}")
        print(f"Height Offset: {self.height_controller.get_height_offset():.2f}mm")
        print(f"Calculated Bends: {len(self.wire_path_creator.calculate_bends())}")
        print(f"Visualization: Clean (hidden elements)")
        print(f"{'='*60}")


# Example usage function
def example_usage():
    """Example of how to use the modular wire generator with clean visualization."""
    stl_path = "sample_lower_arch.stl"
    
    # Create wire generator
    generator = WireGenerator(
        stl_path=stl_path,
        arch_type='auto',
        wire_size='0.018'
    )
    
    # Generate wire
    results = generator.generate_wire()
    
    if results:
        # Print summary
        generator.print_summary()
        
        # Adjust height
        generator.adjust_wire_height(1.0)  # Move up 1mm
        
        # Generate G-code
        gcode_file = generator.generate_gcode()
        print(f"G-code saved: {gcode_file}")
        
        # Save design
        design_file = generator.save_design()
        print(f"Design saved: {design_file}")
        
        # Launch clean interactive mode
        generator.launch_interactive_mode()
    
    return generator


if __name__ == "__main__":
    # Run example
    generator = example_usage()