
# ================================================================
# export/stl_exporter.py
"""STL export functionality for wire meshes."""

import open3d as o3d
import numpy as np
import time
from pathlib import Path
from typing import Optional

class STLExporter:
    """Handles STL file export for wire meshes and components."""
    
    def __init__(self):
        """Initialize STL exporter."""
        self.export_settings = {
            'binary': True,  # Use binary STL format (smaller files)
            'precision': 6,  # Decimal precision for ASCII format
        }
    
    def export(self, mesh: o3d.geometry.TriangleMesh, filename: str, 
               include_metadata: bool = True) -> bool:
        """Export mesh to STL file."""
        try:
            # Ensure mesh is valid
            if not mesh.has_triangles():
                print("Error: Mesh has no triangles to export")
                return False
            
            # Clean mesh before export
            cleaned_mesh = self._prepare_mesh_for_export(mesh)
            
            # Add metadata to filename if requested
            if include_metadata:
                filename = self._add_metadata_to_filename(filename)
            
            # Export to STL
            success = o3d.io.write_triangle_mesh(filename, cleaned_mesh, 
                                               write_ascii=not self.export_settings['binary'])
            
            if success:
                file_size = Path(filename).stat().st_size
                print(f"STL exported successfully: {filename}")
                print(f"File size: {file_size / 1024:.1f} KB")
                print(f"Vertices: {len(cleaned_mesh.vertices)}")
                print(f"Triangles: {len(cleaned_mesh.triangles)}")
                return True
            else:
                print(f"Failed to export STL: {filename}")
                return False
                
        except Exception as e:
            print(f"STL export error: {e}")
            return False
    
    def _prepare_mesh_for_export(self, mesh: o3d.geometry.TriangleMesh) -> o3d.geometry.TriangleMesh:
        """Prepare mesh for export by cleaning and optimizing."""
        cleaned_mesh = mesh.copy()
        
        # Remove duplicated vertices and triangles
        cleaned_mesh.remove_duplicated_vertices()
        cleaned_mesh.remove_duplicated_triangles()
        cleaned_mesh.remove_degenerate_triangles()
        
        # Merge close vertices
        cleaned_mesh.merge_close_vertices(1e-6)
        
        # Compute normals for proper STL export
        cleaned_mesh.compute_vertex_normals()
        cleaned_mesh.compute_triangle_normals()
        
        return cleaned_mesh
    
    def _add_metadata_to_filename(self, filename: str) -> str:
        """Add timestamp and metadata to filename."""
        path = Path(filename)
        stem = path.stem
        suffix = path.suffix
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        new_filename = f"{stem}_{timestamp}{suffix}"
        
        return str(path.parent / new_filename)
    
    def get_mesh_info(self, mesh: o3d.geometry.TriangleMesh) -> dict:
        """Get detailed information about a mesh."""
        if not mesh.has_triangles():
            return {'valid': False}
        
        bbox = mesh.get_axis_aligned_bounding_box()
        extent = bbox.get_extent()
        
        return {
            'valid': True,
            'vertex_count': len(mesh.vertices),
            'triangle_count': len(mesh.triangles),
            'surface_area': mesh.get_surface_area(),
            'volume': mesh.get_volume(),
            'bounding_box': {
                'min': bbox.min_bound.tolist(),
                'max': bbox.max_bound.tolist(),
                'extent': extent.tolist(),
                'center': mesh.get_center().tolist()
            },
            'is_watertight': mesh.is_watertight(),
            'is_orientable': mesh.is_orientable()
        }

