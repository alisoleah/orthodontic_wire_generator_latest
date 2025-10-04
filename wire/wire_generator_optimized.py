#!/usr/bin/env python3
"""
wire/wire_generator_optimized.py

Optimized Wire Generator with Smooth Real-Time Interaction
===========================================================
Performance improvements:
1. Persistent raycasting scene (create once, reuse)
2. Optimized raycasting with fewer rays
3. Cached computations
4. Efficient visualization updates
"""

import numpy as np
import open3d as o3d
from typing import Optional

class WireAdjustmentOptimizer:
    """
    Optimizes real-time wire position adjustments for smooth interaction.

    Key optimizations:
    - Persistent raycasting scene (created once)
    - Reduced ray count with smarter search
    - Cached bracket normals
    - Incremental position updates
    """

    def __init__(self, mesh: o3d.geometry.TriangleMesh, arch_type: str = 'upper'):
        """Initialize optimizer with mesh and arch type."""
        self.mesh = mesh
        self.arch_type = arch_type
        self.raycasting_scene = None
        self.mesh_legacy = None
        self._initialize_raycasting_scene()

    def _initialize_raycasting_scene(self):
        """Create raycasting scene ONCE for reuse."""
        self.mesh_legacy = o3d.t.geometry.TriangleMesh.from_legacy(self.mesh)
        self.raycasting_scene = o3d.t.geometry.RaycastingScene()
        self.raycasting_scene.add_triangles(self.mesh_legacy)

    def find_surface_position_fast(self, target_pos: np.ndarray,
                                   normal: np.ndarray,
                                   orig_pos: np.ndarray) -> Optional[np.ndarray]:
        """
        Fast surface finding using optimized raycasting.

        Strategy: Only 2 rays instead of 8+
        1. Cast from outside inward (primary)
        2. Cast from inside outward (fallback)
        """
        valid_hits = []

        # Strategy 1: Primary ray from outside
        ray_origin_outside = target_pos + normal * 15.0  # 15mm outside
        ray_dir_inward = -normal

        rays = o3d.core.Tensor([[*ray_origin_outside, *ray_dir_inward]],
                              dtype=o3d.core.Dtype.Float32)
        result = self.raycasting_scene.cast_rays(rays)

        if result['t_hit'][0] != np.inf and result['t_hit'][0] > 0:
            hit_pos = ray_origin_outside + ray_dir_inward * float(result['t_hit'][0].numpy())
            # Quick distance check to target
            if np.linalg.norm(hit_pos - target_pos) < 10.0:  # Within 10mm
                return hit_pos
            valid_hits.append(hit_pos)

        # Strategy 2: Fallback ray from inside
        ray_origin_inside = target_pos - normal * 8.0  # 8mm inside
        ray_dir_outward = normal

        rays = o3d.core.Tensor([[*ray_origin_inside, *ray_dir_outward]],
                              dtype=o3d.core.Dtype.Float32)
        result = self.raycasting_scene.cast_rays(rays)

        if result['t_hit'][0] != np.inf and result['t_hit'][0] > 0:
            hit_pos = ray_origin_inside + ray_dir_outward * float(result['t_hit'][0].numpy())
            valid_hits.append(hit_pos)

        # Choose hit closest to gums (upper surface in vertical direction)
        # For upper arch: prefer higher Z (toward palate/gums)
        # For lower arch: prefer lower Z (toward floor of mouth/gums)
        if valid_hits:
            if self.arch_type == 'upper':
                # Upper arch: higher Z = closer to gums
                return valid_hits[np.argmax([hit[2] for hit in valid_hits])]
            else:
                # Lower arch: lower Z = closer to gums
                return valid_hits[np.argmin([hit[2] for hit in valid_hits])]

        # Ultimate fallback: interpolate between orig and target
        return orig_pos + (target_pos - orig_pos) * 0.7

    def get_surface_normal_fast(self, point: np.ndarray,
                               fallback_normal: np.ndarray) -> np.ndarray:
        """Get surface normal with single raycast."""
        ray_origin = point + fallback_normal * 2.0
        ray_dir = -fallback_normal

        rays = o3d.core.Tensor([[*ray_origin, *ray_dir]],
                              dtype=o3d.core.Dtype.Float32)
        result = self.raycasting_scene.cast_rays(rays)

        if result['t_hit'][0] != np.inf and 't_hit' in result:
            if 'primitive_normals' in result:
                normal = result['primitive_normals'][0].numpy()
                return normal / np.linalg.norm(normal)

        return fallback_normal


def add_optimized_adjustment_methods(wire_generator_instance):
    """
    Monkey-patch optimized methods onto existing WireGenerator instance.

    This allows us to enhance the existing class without modifying the original file.
    """

    # Create optimizer
    wire_generator_instance._adjustment_optimizer = WireAdjustmentOptimizer(
        wire_generator_instance.mesh,
        wire_generator_instance.arch_type
    )

    # Store original methods
    wire_generator_instance._original_adjust = wire_generator_instance.adjust_wire_position

    # Add optimized adjustment method
    def adjust_wire_position_optimized(y_offset: float = 0.0, z_offset: float = 0.0):
        """Optimized wire position adjustment with smooth real-time performance."""
        wg = wire_generator_instance

        # Initialize state
        if not hasattr(wg, 'wire_y_offset'):
            wg.wire_y_offset = 0.0
        if not hasattr(wg, 'wire_z_offset'):
            wg.wire_z_offset = 0.0
        if not hasattr(wg, 'original_bracket_positions'):
            wg.original_bracket_positions = [b.copy() if isinstance(b, dict) else b
                                            for b in wg.bracket_positions]

        # Update offsets
        wg.wire_y_offset += y_offset
        wg.wire_z_offset += z_offset

        # Adjust brackets using optimized raycasting
        if y_offset != 0 or z_offset != 0:
            _adjust_bracket_positions_optimized(wg, y_offset, z_offset)

        # Regenerate wire path
        try:
            wg.wire_path = wg.wire_path_creator.create_smooth_path(
                wg.bracket_positions,
                wg.arch_center,
                0.0
            )

            if wg.wire_path is None or len(wg.wire_path) < 2:
                return

            # Rebuild wire mesh
            wg.wire_mesh = wg._create_wire_mesh()

            if wg.wire_mesh is None:
                return

            # Update visualization - REMOVED duplicate call
            # (visualizer callbacks will handle update)

        except Exception as e:
            print(f"Adjustment error: {e}")

    def _adjust_bracket_positions_optimized(wg, y_offset: float, z_offset: float):
        """Optimized bracket position adjustment using persistent raycasting scene."""
        optimizer = wg._adjustment_optimizer
        movement_vector = np.array([0, wg.wire_y_offset, wg.wire_z_offset])

        for i, bracket in enumerate(wg.bracket_positions):
            # Get original data
            if isinstance(bracket, dict):
                orig_pos = wg.original_bracket_positions[i]['position'].copy()
                orig_normal = wg.original_bracket_positions[i]['normal'].copy()
            else:
                orig_pos = wg.original_bracket_positions[i].position.copy()
                orig_normal = wg.original_bracket_positions[i].normal.copy()

            # Normalize
            orig_normal = orig_normal / (np.linalg.norm(orig_normal) + 1e-6)

            # Project movement parallel to surface
            movement_parallel = movement_vector - np.dot(movement_vector, orig_normal) * orig_normal
            surface_target = orig_pos + movement_parallel

            # Fast surface finding (2 rays instead of 8+)
            new_position = optimizer.find_surface_position_fast(
                surface_target, orig_normal, orig_pos
            )

            if new_position is not None:
                # Update position
                if isinstance(bracket, dict):
                    bracket['position'] = new_position
                    # Optional: update normal (can skip for performance)
                    # new_normal = optimizer.get_surface_normal_fast(new_position, orig_normal)
                    # bracket['normal'] = new_normal
                else:
                    bracket.position = new_position

    # Replace methods
    wire_generator_instance.adjust_wire_position = adjust_wire_position_optimized

    return wire_generator_instance
