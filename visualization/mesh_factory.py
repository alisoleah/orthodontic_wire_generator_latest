
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
    
    @staticmethod
    def create_coordinate_frame(size: float = 10.0, origin: np.ndarray = None) -> o3d.geometry.TriangleMesh:
        """Create a coordinate frame for reference."""
        if origin is None:
            origin = np.array([0, 0, 0])
        
        frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=size, origin=origin)
        return frame
    
    @staticmethod
    def create_arrow(start: np.ndarray, end: np.ndarray, color: np.ndarray = None) -> o3d.geometry.TriangleMesh:
        """Create an arrow mesh from start to end point."""
        direction = end - start
        length = np.linalg.norm(direction)
        
        if length < 0.01:
            return None
        
        # Create arrow geometry (simplified as cylinder + cone)
        cylinder_height = length * 0.8
        cone_height = length * 0.2
        cylinder_radius = length * 0.02
        cone_radius = length * 0.04
        
        # Create cylinder shaft
        cylinder = o3d.geometry.TriangleMesh.create_cylinder(
            radius=cylinder_radius, height=cylinder_height, resolution=8
        )
        
        # Create cone head
        cone = o3d.geometry.TriangleMesh.create_cone(
            radius=cone_radius, height=cone_height, resolution=8
        )
        cone.translate([0, 0, cylinder_height/2 + cone_height/2])
        
        # Combine
        arrow = cylinder + cone
        
        # Orient arrow
        z_axis = np.array([0, 0, 1])
        arrow_direction = direction / length
        
        rotation_axis = np.cross(z_axis, arrow_direction)
        if np.linalg.norm(rotation_axis) > 1e-6:
            rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
            angle = np.arccos(np.clip(np.dot(z_axis, arrow_direction), -1, 1))
            R = o3d.geometry.get_rotation_matrix_from_axis_angle(rotation_axis * angle)
            arrow.rotate(R, center=[0, 0, 0])
        
        # Position arrow
        arrow.translate(start + direction/2)
        
        # Set color
        if color is not None:
            arrow.paint_uniform_color(color)
        else:
            arrow.paint_uniform_color([1.0, 0.0, 0.0])  # Red
        
        arrow.compute_vertex_normals()
        return arrow

