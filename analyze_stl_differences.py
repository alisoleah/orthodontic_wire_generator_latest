#!/usr/bin/env python3
"""
Analyze geometric differences between STL files to understand
why wire generation works for some but not others.
"""

import numpy as np
import open3d as o3d
import sys

def analyze_stl(file_path):
    """Analyze STL file properties."""
    print(f"\n{'='*60}")
    print(f"Analyzing: {file_path}")
    print(f"{'='*60}")

    mesh = o3d.io.read_triangle_mesh(file_path)

    if not mesh.has_vertices():
        print("ERROR: No vertices found!")
        return None

    vertices = np.asarray(mesh.vertices)

    # Basic stats
    print(f"\nBasic Properties:")
    print(f"  Vertices: {len(vertices):,}")
    print(f"  Triangles: {len(mesh.triangles):,}")

    # Bounding box
    bbox = mesh.get_axis_aligned_bounding_box()
    bbox_extent = bbox.get_extent()
    print(f"\nBounding Box:")
    print(f"  Min: [{bbox.min_bound[0]:.2f}, {bbox.min_bound[1]:.2f}, {bbox.min_bound[2]:.2f}]")
    print(f"  Max: [{bbox.max_bound[0]:.2f}, {bbox.max_bound[1]:.2f}, {bbox.max_bound[2]:.2f}]")
    print(f"  Extent: [{bbox_extent[0]:.2f}, {bbox_extent[1]:.2f}, {bbox_extent[2]:.2f}]")

    # Z-axis statistics (critical for upper/lower surface detection)
    z_values = vertices[:, 2]
    print(f"\nZ-axis Statistics (critical for gum-side detection):")
    print(f"  Min Z: {np.min(z_values):.2f}")
    print(f"  Max Z: {np.max(z_values):.2f}")
    print(f"  Mean Z: {np.mean(z_values):.2f}")
    print(f"  Std Z: {np.std(z_values):.2f}")
    print(f"  Range: {np.max(z_values) - np.min(z_values):.2f}")

    # Center of mass
    center = np.mean(vertices, axis=0)
    print(f"\nCenter of Mass:")
    print(f"  [{center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}]")

    # Check for mesh quality
    mesh.compute_vertex_normals()
    normals = np.asarray(mesh.vertex_normals)

    # Check if Z component of normals varies (indicating curved surface)
    normal_z = normals[:, 2]
    print(f"\nNormal Z-component Statistics:")
    print(f"  Min: {np.min(normal_z):.3f}")
    print(f"  Max: {np.max(normal_z):.3f}")
    print(f"  Mean: {np.mean(normal_z):.3f}")
    print(f"  Std: {np.std(normal_z):.3f}")

    # Check orientation: for lower jaw, expect normals pointing generally downward
    print(f"\nOrientation Check (for lower jaw):")
    downward_normals = np.sum(normals[:, 2] < 0)
    upward_normals = np.sum(normals[:, 2] > 0)
    print(f"  Downward-pointing normals: {downward_normals:,} ({100*downward_normals/len(normals):.1f}%)")
    print(f"  Upward-pointing normals: {upward_normals:,} ({100*upward_normals/len(normals):.1f}%)")

    return {
        'vertices': len(vertices),
        'triangles': len(mesh.triangles),
        'bbox_min': bbox.min_bound,
        'bbox_max': bbox.max_bound,
        'z_range': np.max(z_values) - np.min(z_values),
        'center': center,
        'normal_z_std': np.std(normal_z)
    }

if __name__ == "__main__":
    # Analyze both files
    working_file = "STLfiles/assets/AyaKhairy_LowerJaw.stl"
    failing_file = "STLfiles/assets/Amina Imam scan for retainers LowerJawScan.stl"

    print("COMPARISON: Working vs Failing STL Files")

    working_stats = analyze_stl(working_file)
    failing_stats = analyze_stl(failing_file)

    print(f"\n{'='*60}")
    print("KEY DIFFERENCES:")
    print(f"{'='*60}")

    if working_stats and failing_stats:
        print(f"\nVertex count ratio: {failing_stats['vertices'] / working_stats['vertices']:.2f}x")
        print(f"Z-range ratio: {failing_stats['z_range'] / working_stats['z_range']:.2f}x")

        z_diff = abs(working_stats['center'][2] - failing_stats['center'][2])
        print(f"Center Z difference: {z_diff:.2f}mm")
