import numpy as np
import open3d as o3d
import pyvista as pv
from typing import Optional

def open3d_to_pyvista(o3d_mesh: o3d.geometry.TriangleMesh) -> Optional[pv.PolyData]:
    """
    Convert an Open3D TriangleMesh to a PyVista PolyData object.

    Args:
        o3d_mesh: The Open3D mesh to convert.

    Returns:
        The converted PyVista mesh, or None if the input is invalid.
    """
    if not isinstance(o3d_mesh, o3d.geometry.TriangleMesh):
        return None

    vertices = np.asarray(o3d_mesh.vertices)
    triangles = np.asarray(o3d_mesh.triangles)

    # PyVista faces format requires a count before each face's indices
    # e.g., [3, idx1, idx2, idx3, 3, idx4, idx5, idx6, ...]
    faces = np.hstack([
        np.full((triangles.shape[0], 1), 3, dtype=np.int64),
        triangles
    ]).flatten()

    pv_mesh = pv.PolyData(vertices, faces)

    # Transfer vertex colors if they exist
    if o3d_mesh.has_vertex_colors():
        colors = np.asarray(o3d_mesh.vertex_colors)
        pv_mesh.point_data['colors'] = (colors * 255).astype(np.uint8)

    # Transfer vertex normals if they exist
    if o3d_mesh.has_vertex_normals():
        normals = np.asarray(o3d_mesh.vertex_normals)
        pv_mesh.point_data['normals'] = normals

    return pv_mesh