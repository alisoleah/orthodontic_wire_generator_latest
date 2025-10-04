#!/usr/bin/env python3
"""
visualization/visualizer_optimized.py

Optimized Visualization Updates for Smooth Real-Time Interaction
=================================================================
Performance improvements:
1. Update geometry in-place instead of remove/add
2. Batched vertex updates
3. Reduced rendering overhead
"""

import open3d as o3d
import numpy as np


class VisualizationOptimizer:
    """
    Optimizes Open3D visualization updates for real-time wire adjustment.

    Key technique: Update mesh vertices in-place instead of recreating geometry.
    """

    @staticmethod
    def update_wire_mesh_fast(visualizer, old_wire_mesh, new_wire_mesh):
        """
        Fast wire mesh update using in-place vertex modification when possible.

        Strategy:
        - If mesh topology is same: Update vertices only
        - If topology changed: Full remove/add (slower but necessary)
        """
        if not visualizer.vis:
            return

        # Check if we can do fast update (same topology)
        can_fast_update = False
        if old_wire_mesh and new_wire_mesh:
            old_verts = len(old_wire_mesh.vertices)
            new_verts = len(new_wire_mesh.vertices)
            old_tris = len(old_wire_mesh.triangles)
            new_tris = len(new_wire_mesh.triangles)

            # If vertex/triangle counts match, we can update in-place
            if old_verts == new_verts and old_tris == new_tris:
                can_fast_update = True

        if can_fast_update:
            # FAST PATH: Update vertices in-place
            try:
                old_wire_mesh.vertices = new_wire_mesh.vertices
                old_wire_mesh.vertex_normals = new_wire_mesh.vertex_normals
                old_wire_mesh.vertex_colors = new_wire_mesh.vertex_colors

                # Tell visualizer to update existing geometry
                visualizer.vis.update_geometry(old_wire_mesh)
                # Force render update
                visualizer.vis.poll_events()
                visualizer.vis.update_renderer()
                return
            except Exception as e:
                # Fall back to slow path if fast update fails
                pass

        # SLOW PATH: Remove old, add new (topology changed)
        if old_wire_mesh:
            try:
                visualizer.vis.remove_geometry(old_wire_mesh, reset_bounding_box=False)
            except:
                pass

        visualizer.wire_mesh = new_wire_mesh

        if new_wire_mesh:
            try:
                visualizer.vis.add_geometry(new_wire_mesh, reset_bounding_box=False)
                visualizer.vis.poll_events()
                visualizer.vis.update_renderer()
            except Exception as e:
                print(f"Visualization update error: {e}")


def add_optimized_visualization_methods(visualizer_instance):
    """
    Monkey-patch optimized visualization methods onto existing Visualizer3D instance.
    """
    visualizer_instance._viz_optimizer = VisualizationOptimizer()

    # Store original method
    visualizer_instance._original_update_wire_mesh = visualizer_instance.update_wire_mesh

    # Add optimized update method
    def update_wire_mesh_optimized(new_wire_mesh):
        """Optimized wire mesh update."""
        visualizer_instance._viz_optimizer.update_wire_mesh_fast(
            visualizer_instance,
            visualizer_instance.wire_mesh,
            new_wire_mesh
        )

    # Replace method
    visualizer_instance.update_wire_mesh = update_wire_mesh_optimized

    # Also optimize the key callbacks to avoid duplicate updates
    def setup_key_callbacks_optimized():
        """Setup keyboard callbacks with optimized wire updates."""

        def key_quit(vis):
            vis.close()
            return True

        def key_help(vis):
            visualizer_instance.print_help()
            return False

        # Optimized wire movement callbacks
        def key_wire_up(vis):
            if visualizer_instance.wire_generator:
                visualizer_instance.wire_generator.adjust_wire_position(y_offset=0.5)
                # Update is now handled efficiently
                visualizer_instance.update_wire_mesh(visualizer_instance.wire_generator.wire_mesh)
            return False

        def key_wire_down(vis):
            if visualizer_instance.wire_generator:
                visualizer_instance.wire_generator.adjust_wire_position(y_offset=-0.5)
                visualizer_instance.update_wire_mesh(visualizer_instance.wire_generator.wire_mesh)
            return False

        def key_wire_forward(vis):
            if visualizer_instance.wire_generator:
                visualizer_instance.wire_generator.adjust_wire_position(z_offset=0.5)
                visualizer_instance.update_wire_mesh(visualizer_instance.wire_generator.wire_mesh)
            return False

        def key_wire_backward(vis):
            if visualizer_instance.wire_generator:
                visualizer_instance.wire_generator.adjust_wire_position(z_offset=-0.5)
                visualizer_instance.update_wire_mesh(visualizer_instance.wire_generator.wire_mesh)
            return False

        def key_reset_position(vis):
            if visualizer_instance.wire_generator:
                visualizer_instance.wire_generator.reset_wire_position()
                visualizer_instance.update_wire_mesh(visualizer_instance.wire_generator.wire_mesh)
            return False

        def key_select_cp(vis, index):
            if visualizer_instance.control_point_manager:
                visualizer_instance.control_point_manager.select_control_point(index)
                visualizer_instance.highlight_selected_control_point(index)
            return False

        def key_move_cp(vis, direction):
            if visualizer_instance.control_point_manager and visualizer_instance.wire_generator:
                visualizer_instance.wire_generator.move_control_point(direction, 0.5)
                visualizer_instance.update_control_points(visualizer_instance.wire_generator.wire_path_creator.control_points)
                visualizer_instance.update_wire_mesh(visualizer_instance.wire_generator.wire_mesh)
            return False

        # Register callbacks
        vis = visualizer_instance.vis
        vis.register_key_callback(ord('Q'), key_quit)
        vis.register_key_callback(ord('H'), key_help)
        vis.register_key_callback(265, key_wire_up)
        vis.register_key_callback(264, key_wire_down)
        vis.register_key_callback(ord('W'), key_wire_forward)
        vis.register_key_callback(ord('S'), key_wire_backward)
        vis.register_key_callback(ord('R'), key_reset_position)

        # Control point selection
        for i in range(1, 10):
            vis.register_key_callback(ord(str(i)),
                                     lambda v, idx=i-1: key_select_cp(v, idx))

        # Control point movement
        vis.register_key_callback(262, lambda v: key_move_cp(v, np.array([1, 0, 0])))
        vis.register_key_callback(263, lambda v: key_move_cp(v, np.array([-1, 0, 0])))
        vis.register_key_callback(266, lambda v: key_move_cp(v, np.array([0, 0, 1])))
        vis.register_key_callback(267, lambda v: key_move_cp(v, np.array([0, 0, -1])))

    # Replace setup method
    visualizer_instance.setup_key_callbacks = setup_key_callbacks_optimized

    return visualizer_instance
