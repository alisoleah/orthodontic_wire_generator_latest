#!/usr/bin/env python3
"""
Quick test to verify Open3D works on your Mac
"""

import sys

print("Testing Open3D installation...")
print(f"Python: {sys.version}")

try:
    import open3d as o3d
    print(f"✅ Open3D version: {o3d.__version__}")

    # Test basic visualization
    print("\nTesting basic visualization...")

    # Create simple mesh
    mesh = o3d.geometry.TriangleMesh.create_sphere(radius=1.0)
    mesh.paint_uniform_color([0.5, 0.5, 1.0])
    mesh.compute_vertex_normals()

    print("Created test sphere mesh")

    # Try to create visualizer
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="Open3D Test", width=800, height=600)
    vis.add_geometry(mesh)

    print("\n✅ Open3D visualization working!")
    print("A blue sphere should appear in a window")
    print("Close the window to finish the test")

    vis.run()
    vis.destroy_window()

    print("\n✅ Test completed successfully!")
    print("Open3D is working properly on your Mac")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nOpen3D may not be working properly.")
    print("Try reinstalling: pip3 install --upgrade open3d")
    sys.exit(1)
