#!/usr/bin/env python3
# ================================================================
# core/mesh_processor.py
"""STL mesh loading and preprocessing."""

import open3d as o3d
import numpy as np
from typing import Optional

class MeshProcessor:
    """Handles STL file loading and mesh preprocessing."""
    
    def __init__(self):
        """Initialize mesh processor."""
        self.cleaning_enabled = True
        self.verbose = True
        
    def load_stl(self, stl_path: str) -> Optional[o3d.geometry.TriangleMesh]:
        """Load STL file and return processed mesh."""
        try:
            mesh = o3d.io.read_triangle_mesh(stl_path)
            if not mesh.has_triangles():
                raise ValueError("No triangles found in mesh")
            
            if self.verbose:
                print(f"Loaded STL: {len(mesh.vertices)} vertices, {len(mesh.triangles)} triangles")
            
            return mesh
            
        except Exception as e:
            if self.verbose:
                print(f"Error loading STL: {e}")
            return None
    
    def clean_mesh(self, mesh: o3d.geometry.TriangleMesh) -> o3d.geometry.TriangleMesh:
        """Clean and prepare mesh for processing."""
        if not self.cleaning_enabled:
            return mesh
            
        # Remove duplicates and degenerates
        mesh.remove_duplicated_vertices()
        mesh.remove_degenerate_triangles()
        mesh.remove_duplicated_triangles()
        
        # Merge close vertices
        mesh.merge_close_vertices(1e-6)
        
        # Compute normals
        mesh.compute_vertex_normals()
        mesh.compute_triangle_normals()
        
        # Set natural tooth color
        mesh.paint_uniform_color([0.95, 0.93, 0.88])
        
        if self.verbose:
            print(f"Mesh cleaned: {len(mesh.vertices)} vertices, {len(mesh.triangles)} triangles")
        
        return mesh
    
    def calculate_arch_center(self, mesh: o3d.geometry.TriangleMesh) -> np.ndarray:
        """Calculate the center of the dental arch."""
        return mesh.get_center()
    
    def get_mesh_bounds(self, mesh: o3d.geometry.TriangleMesh) -> tuple:
        """Get mesh bounding box information."""
        bbox = mesh.get_axis_aligned_bounding_box()
        return bbox.min_bound, bbox.max_bound, bbox.get_extent()
    
    def get_mesh_statistics(self, mesh: o3d.geometry.TriangleMesh) -> dict:
        """Get comprehensive mesh statistics."""
        if not mesh.has_triangles():
            return {'valid': False}
        
        bbox = mesh.get_axis_aligned_bounding_box()
        
        return {
            'valid': True,
            'vertex_count': len(mesh.vertices),
            'triangle_count': len(mesh.triangles),
            'bounding_box': {
                'min': bbox.min_bound,
                'max': bbox.max_bound,
                'extent': bbox.get_extent(),
                'center': mesh.get_center()
            },
            'surface_area': mesh.get_surface_area(),
            'volume': mesh.get_volume(),
            'is_watertight': mesh.is_watertight(),
            'is_orientable': mesh.is_orientable()
        }

