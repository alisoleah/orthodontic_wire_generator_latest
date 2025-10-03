#!/usr/bin/env python3
"""
visualization/visualizer_3d.py
=============================
3D visualization system for interactive wire editing.
"""

import open3d as o3d
import numpy as np
from typing import List, Dict, Optional, Callable

class Visualizer3D:
    """3D visualization manager for interactive wire editing."""
    
    def __init__(self, mesh=None, wire_mesh=None, bracket_positions=None, control_points=None):
        """Initialize 3D visualizer."""
        self.mesh = mesh
        self.wire_mesh = wire_mesh
        self.bracket_positions = bracket_positions or []
        self.control_points = control_points or []
        
        # Visualization components
        self.vis = None
        self.bracket_meshes = []
        self.control_point_meshes = []
        self.selected_control_point = None
        
        # Callbacks
        self.height_controller = None
        self.control_point_manager = None
        self.wire_generator = None
        
        print("3D Visualizer initialized")
    
    def setup_interactive_mode(self, height_controller, control_point_manager, wire_generator):
        """Setup interactive mode with callback handlers."""
        self.height_controller = height_controller
        self.control_point_manager = control_point_manager
        self.wire_generator = wire_generator
    
    def create_bracket_meshes(self):
        """Create 3D meshes for brackets."""
        self.bracket_meshes = []
        
        for i, bracket in enumerate(self.bracket_positions):
            if not bracket.get('visible', True):
                continue
            
            # Create bracket box
            bracket_mesh = o3d.geometry.TriangleMesh.create_box(1.8, 2.0, 1.2)
            bracket_mesh.translate([-0.9, -1.0, -0.6])
            
            # Position and orient bracket
            bracket_mesh.translate(bracket['position'])
            
            # Color based on tooth type
            if bracket['tooth_type'] == 'incisor':
                color = [0.2, 0.8, 0.2]  # Green
            elif bracket['tooth_type'] == 'canine':
                color = [0.8, 0.8, 0.2]  # Yellow
            else:
                color = [0.2, 0.3, 0.8]  # Blue
            
            bracket_mesh.paint_uniform_color(color)
            bracket_mesh.compute_vertex_normals()
            
            self.bracket_meshes.append({
                'mesh': bracket_mesh,
                'index': i,
                'bracket': bracket,
                'original_color': color
            })
    
    def create_control_point_meshes(self):
        """Create 3D meshes for control points."""
        self.control_point_meshes = []
        
        for i, cp in enumerate(self.control_points):
            if cp['type'] == 'bracket':
                sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.8, resolution=8)
                color = [0.9, 0.1, 0.1]  # Red for bracket points
            else:
                sphere = o3d.geometry.TriangleMesh.create_sphere(radius=1.0, resolution=8)
                color = [0.1, 0.9, 0.1]  # Green for intermediate points
            
            sphere.translate(cp['position'])
            sphere.paint_uniform_color(color)
            sphere.compute_vertex_normals()
            
            self.control_point_meshes.append({
                'mesh': sphere,
                'index': i,
                'control_point': cp,
                'original_color': color
            })
    
    def setup_key_callbacks(self):
        """Setup keyboard callbacks for interactive control."""
        
        def key_quit(vis):
            vis.close()
            return True
        
        def key_help(vis):
            self.print_help()
            return False
        
        def key_wire_up(vis):
            if self.height_controller:
                self.height_controller.adjust_height(0.5)
                self.wire_generator.adjust_wire_height(0)  # Trigger rebuild
                self.update_wire_mesh(self.wire_generator.wire_mesh)
            return False
        
        def key_wire_down(vis):
            if self.height_controller:
                self.height_controller.adjust_height(-0.5)
                self.wire_generator.adjust_wire_height(0)  # Trigger rebuild
                self.update_wire_mesh(self.wire_generator.wire_mesh)
            return False
        
        def key_reset_height(vis):
            if self.height_controller:
                self.height_controller.reset_height()
                self.wire_generator.adjust_wire_height(0)  # Trigger rebuild
                self.update_wire_mesh(self.wire_generator.wire_mesh)
            return False
        
        def key_select_cp(vis, index):
            if self.control_point_manager:
                self.control_point_manager.select_control_point(index)
                self.highlight_selected_control_point(index)
            return False
        
        def key_move_cp(vis, direction):
            if self.control_point_manager and self.wire_generator:
                self.wire_generator.move_control_point(direction, 0.5)
                self.update_control_points(self.wire_generator.wire_path_creator.control_points)
                self.update_wire_mesh(self.wire_generator.wire_mesh)
            return False
        
        # Register callbacks
        self.vis.register_key_callback(ord('Q'), key_quit)
        self.vis.register_key_callback(ord('H'), key_help)
        self.vis.register_key_callback(265, key_wire_up)      # Up arrow
        self.vis.register_key_callback(264, key_wire_down)    # Down arrow
        self.vis.register_key_callback(ord('R'), key_reset_height)
        
        # Control point selection (1-9)
        for i in range(1, 10):
            self.vis.register_key_callback(ord(str(i)), 
                lambda v, idx=i-1: key_select_cp(v, idx))
        
        # Control point movement
        self.vis.register_key_callback(262, lambda v: key_move_cp(v, np.array([1, 0, 0])))  # Right
        self.vis.register_key_callback(263, lambda v: key_move_cp(v, np.array([-1, 0, 0]))) # Left
        self.vis.register_key_callback(266, lambda v: key_move_cp(v, np.array([0, 0, 1])))  # Page Up
        self.vis.register_key_callback(267, lambda v: key_move_cp(v, np.array([0, 0, -1]))) # Page Down
    
    def run(self):
        """Launch interactive 3D visualization."""
        self.vis = o3d.visualization.VisualizerWithKeyCallback()
        self.vis.create_window(
            window_name="Interactive Wire Editor - Modular Architecture",
            width=1600,
            height=1000
        )
        
        # Add main geometries
        if self.mesh:
            self.vis.add_geometry(self.mesh)
        
        # HIDE: Create bracket meshes but don't add them
        # self.create_bracket_meshes()
        # for bm in self.bracket_meshes:
        #     self.vis.add_geometry(bm['mesh'])
        
        # HIDE: Create control point meshes but don't add them
        # self.create_control_point_meshes()
        # for cpm in self.control_point_meshes:
        #     self.vis.add_geometry(cpm['mesh'])
        
        # Add wire mesh only
        if self.wire_mesh:
            self.vis.add_geometry(self.wire_mesh)
        
        # HIDE: Coordinate frame
        # coord_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=20.0)
        # self.vis.add_geometry(coord_frame)
        
        # Setup callbacks
        self.setup_key_callbacks()
        
        # Configure rendering
        opt = self.vis.get_render_option()
        opt.background_color = np.array([0.92, 0.92, 0.95])
        opt.mesh_show_back_face = True
        
        # Set initial view
        ctr = self.vis.get_view_control()
        ctr.set_zoom(0.7)
        
        print("\nInteractive 3D Editor Launched")
        print("Press H for help, Q to quit")
        self.print_help()
        
        # Run visualization
        self.vis.run()
        self.vis.destroy_window()
    
    def update_wire_mesh(self, new_wire_mesh):
        """Update wire mesh in visualization."""
        if self.vis and self.wire_mesh:
            self.vis.remove_geometry(self.wire_mesh, reset_bounding_box=False)
        
        self.wire_mesh = new_wire_mesh
        
        if self.vis and self.wire_mesh:
            self.vis.add_geometry(self.wire_mesh, reset_bounding_box=False)
    
    def update_control_points(self, new_control_points):
        """Update control point meshes."""
        self.control_points = new_control_points
        
        if self.vis:
            # Remove old control point meshes
            for cpm in self.control_point_meshes:
                self.vis.remove_geometry(cpm['mesh'], reset_bounding_box=False)
            
            # Create new ones
            self.create_control_point_meshes()
            
            # Add new meshes
            for cpm in self.control_point_meshes:
                self.vis.add_geometry(cpm['mesh'], reset_bounding_box=False)
    
    def highlight_selected_control_point(self, index):
        """Highlight selected control point."""
        # Reset all colors
        for cpm in self.control_point_meshes:
            cpm['mesh'].paint_uniform_color(cpm['original_color'])
        
        # Highlight selected
        if 0 <= index < len(self.control_point_meshes):
            self.control_point_meshes[index]['mesh'].paint_uniform_color([1.0, 1.0, 0.0])
            self.selected_control_point = index
        
        # Update visualization
        if self.vis:
            for cpm in self.control_point_meshes:
                self.vis.update_geometry(cpm['mesh'])
    
    def print_help(self):
        """Print interactive controls help."""
        print("\n" + "="*60)
        print("INTERACTIVE 3D EDITOR - MODULAR ARCHITECTURE")
        print("="*60)
        print("\nWIRE HEIGHT CONTROLS:")
        print("  Up Arrow      - Move wire up")
        print("  Down Arrow    - Move wire down")
        print("  R             - Reset wire height")
        print("\nCONTROL POINT CONTROLS:")
        print("  1-9           - Select control point")
        print("  Left/Right    - Move selected point horizontally")
        print("  Page Up/Down  - Move selected point vertically")
        print("\nVIEW CONTROLS:")
        print("  Mouse Drag    - Rotate view")
        print("  Mouse Scroll  - Zoom")
        print("  Mouse Right   - Pan view")
        print("\nOTHER:")
        print("  H             - Show this help")
        print("  Q             - Quit editor")
        print("="*60)


# ================================================================
# visualization/mesh_factory.py
"""Factory for creating various 3D mesh objects."""

import open3d as o3d
import numpy as np
from typing import Tuple

class MeshFactory:
    """Factory class for creating standardized 3D mesh objects."""
    
    @staticmethod
    def create_bracket_mesh(position: np.ndarray, size: Tuple[float, float, float] = (1.8, 2.0, 1.2),
                           color: np.ndarray = None) -> o3d.geometry.TriangleMesh:
        """Create a bracket mesh at specified position."""
        bracket = o3d.geometry.TriangleMesh.create_box(size[0], size[1], size[2])
        bracket.translate([-size[0]/2, -size[1]/2, -size[2]/2])
        bracket.translate(position)
        
        if color is not None:
            bracket.paint_uniform_color(color)
        else:
            bracket.paint_uniform_color([0.7, 0.7, 0.7])  # Default gray
        
        bracket.compute_vertex_normals()
        return bracket
    
    @staticmethod
    def create_control_point_sphere(position: np.ndarray, radius: float = 1.0,
                                  color: np.ndarray = None) -> o3d.geometry.TriangleMesh:
        """Create a control point sphere at specified position."""
        sphere = o3d.geometry.TriangleMesh.create_sphere(radius=radius, resolution=8)
        sphere.translate(position)
        
        if color is not None:
            sphere.paint_uniform_color(color)
        else:
            sphere.paint_uniform_color([0.1, 0.9, 0.1])  # Default green
        
        sphere.compute_vertex_normals()
        return sphere
    
    @staticmethod
    def create_tooth_mesh(vertices: np.ndarray, color: np.ndarray = None) -> o3d.geometry.TriangleMesh:
        """Create a mesh representation of a tooth from point cloud."""
        if len(vertices) < 4:
            return None
        
        # Create point cloud
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(vertices)
        
        # Estimate normals
        pcd.estimate_normals()
        
        # Create mesh using Poisson reconstruction
        try:
            mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8)
            
            if color is not None:
                mesh.paint_uniform_color(color)
            else:
                mesh.paint_uniform_color([0.9, 0.9, 0.8])  # Tooth color
            
            mesh.compute_vertex_normals()
            return mesh
        except:
            return None
    
    @staticmethod
    def create_wire_segment(start: np.ndarray, end: np.ndarray, radius: float = 0.25) -> o3d.geometry.TriangleMesh:
        """Create a single wire segment between two points."""
        segment_vector = end - start
        segment_length = np.linalg.norm(segment_vector)
        
        if segment_length < 0.01:
            return None
        
        # Create cylinder
        cylinder = o3d.geometry.TriangleMesh.create_cylinder(
            radius=radius, height=segment_length, resolution=12
        )
        
        # Orient cylinder
        z_axis = np.array([0, 0, 1])
        segment_direction = segment_vector / segment_length
        
        rotation_axis = np.cross(z_axis, segment_direction)
        if np.linalg.norm(rotation_axis) > 1e-6:
            rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
            angle = np.arccos(np.clip(np.dot(z_axis, segment_direction), -1, 1))
            R = o3d.geometry.get_rotation_matrix_from_axis_angle(rotation_axis * angle)
            cylinder.rotate(R, center=[0, 0, 0])
        
        # Position cylinder
        cylinder.translate((start + end) / 2)
        
        # Set color
        cylinder.paint_uniform_color([0.85, 0.75, 0.45])  # Gold wire color
        cylinder.compute_vertex_normals()
        
        return cylinder