#!/usr/bin/env python3
"""
wire/wire_mesh_builder.py

WireMeshBuilder - 3D Wire Mesh Creation
======================================
This class handles the actual 3D rendering of the wire mesh.
It takes the mathematical path and creates the visual 3D geometry.
"""

import numpy as np
import open3d as o3d
from typing import Optional, Tuple, List
import math

class WireMeshBuilder:
    """
    3D Wire Mesh Builder - Handles the actual wire drawing/rendering.
    
    This class converts the mathematical wire path into actual 3D geometry
    that can be visualized and exported.
    """
    
    def __init__(self, wire_radius: float = 0.2286):  # Default 0.018" wire
        """Initialize the wire mesh builder."""
        self.wire_radius = wire_radius
        self.mesh_resolution = 12  # Number of sides for cylindrical segments
        self.segment_length_threshold = 30.0  # Maximum segment length (mm)
        self.minimum_segment_length = 0.01  # Minimum segment length (mm)
        
        # Wire material properties
        self.wire_color = np.array([0.85, 0.75, 0.45])  # Gold color
        self.wire_metallic = True
        
        # Current mesh data
        self.wire_mesh = None
        self.mesh_segments = []
        
    def build_wire_mesh(self, wire_path: np.ndarray) -> Optional[o3d.geometry.TriangleMesh]:
        """
        Main method to build 3D wire mesh from path.
        
        This is the core wire drawing/rendering method that creates the actual
        3D geometry from the mathematical wire path.
        
        Args:
            wire_path: Array of 3D points representing the wire path
            
        Returns:
            Open3D TriangleMesh representing the 3D wire
        """
        if wire_path is None or len(wire_path) < 2:
            return None
        
        # Clear previous mesh data
        self.mesh_segments = []
        
        # Create wire segments along the path
        self.wire_mesh = self._create_wire_segments(wire_path)
        
        # Apply material properties
        self._apply_wire_material()
        
        # Optimize the mesh
        self._optimize_mesh()
        
        return self.wire_mesh
    
    def _create_wire_segments(self, wire_path: np.ndarray) -> o3d.geometry.TriangleMesh:
        """
        Create cylindrical segments along the wire path.
        
        This method handles the core 3D drawing by creating individual
        cylindrical segments and connecting them smoothly.
        """
        combined_mesh = o3d.geometry.TriangleMesh()
        
        for i in range(len(wire_path) - 1):
            segment_mesh = self._create_single_segment(
                wire_path[i], 
                wire_path[i + 1]
            )
            
            if segment_mesh is not None:
                combined_mesh += segment_mesh
                self.mesh_segments.append(segment_mesh)
        
        return combined_mesh
    
    def _create_single_segment(self, start_point: np.ndarray, 
                             end_point: np.ndarray) -> Optional[o3d.geometry.TriangleMesh]:
        """
        Create a single cylindrical segment between two points.
        
        This is the fundamental wire drawing operation - creating a cylinder
        between two 3D points with proper orientation.
        """
        # Calculate segment properties
        segment_vector = end_point - start_point
        segment_length = np.linalg.norm(segment_vector)
        
        # Validate segment
        if (segment_length < self.minimum_segment_length or 
            segment_length > self.segment_length_threshold):
            return None
        
        # Create base cylinder along Z-axis
        cylinder = o3d.geometry.TriangleMesh.create_cylinder(
            radius=self.wire_radius,
            height=segment_length,
            resolution=self.mesh_resolution,
            split=4  # Number of stacks along height
        )
        
        # Orient the cylinder to match segment direction
        self._orient_cylinder(cylinder, start_point, end_point, segment_vector, segment_length)
        
        return cylinder
    
    def _orient_cylinder(self, cylinder: o3d.geometry.TriangleMesh,
                        start_point: np.ndarray, end_point: np.ndarray,
                        segment_vector: np.ndarray, segment_length: float):
        """
        Orient a cylinder to align with the wire segment.
        
        This handles the 3D rotation mathematics to properly align
        each cylindrical segment with the wire path direction.
        """
        # Default cylinder is oriented along Z-axis
        z_axis = np.array([0, 0, 1])
        segment_direction = segment_vector / segment_length
        
        # Calculate rotation needed to align Z-axis with segment direction
        rotation_axis = np.cross(z_axis, segment_direction)
        
        if np.linalg.norm(rotation_axis) > 1e-6:
            # Normalize rotation axis
            rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)
            
            # Calculate rotation angle
            dot_product = np.clip(np.dot(z_axis, segment_direction), -1.0, 1.0)
            rotation_angle = np.arccos(dot_product)
            
            # Create rotation matrix
            rotation_matrix = o3d.geometry.get_rotation_matrix_from_axis_angle(
                rotation_axis * rotation_angle
            )
            
            # Apply rotation around origin
            cylinder.rotate(rotation_matrix, center=[0, 0, 0])
        
        # Translate cylinder to proper position (midpoint of segment)
        cylinder.translate((start_point + end_point) / 2)
    
    def _apply_wire_material(self):
        """Apply material properties to the wire mesh."""
        if self.wire_mesh is not None:
            # Set wire color
            self.wire_mesh.paint_uniform_color(self.wire_color)
            
            # Compute normals for proper lighting
            self.wire_mesh.compute_vertex_normals()
            self.wire_mesh.compute_triangle_normals()
    
    def _optimize_mesh(self):
        """Optimize the wire mesh for better performance and quality."""
        if self.wire_mesh is not None:
            # Remove duplicate vertices
            self.wire_mesh.remove_duplicated_vertices()
            
            # Remove degenerate triangles
            self.wire_mesh.remove_degenerate_triangles()
            
            # Merge close vertices
            self.wire_mesh.merge_close_vertices(1e-6)
    
    def update_wire_radius(self, new_radius: float):
        """Update wire radius and rebuild if mesh exists."""
        self.wire_radius = new_radius
        # Note: Would need to rebuild mesh with new radius
    
    def update_wire_color(self, new_color: np.ndarray):
        """Update wire color."""
        self.wire_color = new_color
        if self.wire_mesh is not None:
            self.wire_mesh.paint_uniform_color(self.wire_color)
    
    def create_wire_endpoints(self, wire_path: np.ndarray) -> Tuple[o3d.geometry.TriangleMesh, o3d.geometry.TriangleMesh]:
        """Create spherical end caps for the wire."""
        if wire_path is None or len(wire_path) < 2:
            return None, None
        
        start_cap = o3d.geometry.TriangleMesh.create_sphere(
            radius=self.wire_radius * 1.1,
            resolution=self.mesh_resolution
        )
        start_cap.translate(wire_path[0])
        start_cap.paint_uniform_color(self.wire_color)
        
        end_cap = o3d.geometry.TriangleMesh.create_sphere(
            radius=self.wire_radius * 1.1,
            resolution=self.mesh_resolution
        )
        end_cap.translate(wire_path[-1])
        end_cap.paint_uniform_color(self.wire_color)
        
        return start_cap, end_cap
    
    def create_wire_with_caps(self, wire_path: np.ndarray) -> o3d.geometry.TriangleMesh:
        """Create complete wire mesh with end caps."""
        main_mesh = self.build_wire_mesh(wire_path)
        if main_mesh is None:
            return None
        
        start_cap, end_cap = self.create_wire_endpoints(wire_path)
        
        if start_cap is not None:
            main_mesh += start_cap
        if end_cap is not None:
            main_mesh += end_cap
        
        return main_mesh
    
    def get_mesh_statistics(self) -> dict:
        """Get statistics about the current wire mesh - handles non-watertight meshes."""
        if self.wire_mesh is None:
            return {'valid': False}
        
        try:
            volume = self.wire_mesh.get_volume()
        except Exception as e:
            print(f"Warning: Could not calculate volume (mesh may not be watertight): {e}")
            volume = 0.0
        
        try:
            surface_area = self.wire_mesh.get_surface_area()
        except Exception as e:
            print(f"Warning: Could not calculate surface area: {e}")
            surface_area = 0.0
        
        try:
            bounding_box = self.wire_mesh.get_axis_aligned_bounding_box()
        except Exception as e:
            print(f"Warning: Could not calculate bounding box: {e}")
            bounding_box = None
        
        return {
            'vertex_count': len(self.wire_mesh.vertices),
            'triangle_count': len(self.wire_mesh.triangles),
            'segment_count': len(self.mesh_segments),
            'bounding_box': bounding_box,
            'surface_area': surface_area,
            'volume': volume,
            'valid': True
        }