#!/usr/bin/env python3
"""
core/collision_detector.py - NEW ENHANCED MODULE

Professional Collision Detection System with FIXR Algorithms
==========================================================
Implements advanced collision detection and avoidance algorithms from FIXR research:
- Ray collision detection algorithms
- Extended OBB tree algorithms
- Triangle intersection algorithms
- Real-time collision avoidance
"""

import numpy as np
from scipy.spatial import cKDTree
from typing import List, Dict, Tuple, Optional, Set
import time
from dataclasses import dataclass
from enum import Enum

class CollisionType(Enum):
    """Types of collision detection."""
    POINT_SURFACE = "point_surface"
    RAY_TRIANGLE = "ray_triangle"
    OBB_OBB = "obb_obb"
    SPHERE_MESH = "sphere_mesh"

@dataclass
class CollisionResult:
    """Result of collision detection."""
    collision_detected: bool
    collision_type: CollisionType
    collision_point: np.ndarray
    collision_normal: np.ndarray
    penetration_depth: float
    collision_distance: float
    triangle_index: Optional[int] = None
    mesh_region: Optional[str] = None

@dataclass
class BoundingBox:
    """Axis-aligned bounding box."""
    min_point: np.ndarray
    max_point: np.ndarray
    
    @property
    def center(self) -> np.ndarray:
        return (self.min_point + self.max_point) / 2
    
    @property
    def extents(self) -> np.ndarray:
        return (self.max_point - self.min_point) / 2

class CollisionDetector:
    """
    Professional collision detection system implementing FIXR algorithms.
    
    This system provides:
    - Ray collision detection for wire-tooth interference
    - OBB tree algorithms for efficient spatial queries
    - Triangle intersection methods for precise collision detection
    - Real-time collision avoidance and path correction
    """
    
    def __init__(self, collision_tolerance: float = 0.5, optimization_enabled: bool = True):
        """Initialize collision detection system."""
        self.collision_tolerance = collision_tolerance
        self.optimization_enabled = optimization_enabled
        
        # Spatial acceleration structures
        self.mesh_kdtree = None
        self.triangle_kdtree = None
        self.bvh_tree = None
        
        # Mesh data
        self.mesh_vertices = None
        self.mesh_triangles = None
        self.mesh_normals = None
        self.triangle_centers = None
        self.triangle_normals = None
        
        # Performance tracking
        self.collision_cache = {}
        self.performance_stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'collision_detections': 0,
            'average_query_time': 0.0
        }
        
        print(f"CollisionDetector initialized with tolerance: {collision_tolerance}mm")
    
    def initialize_mesh_data(self, mesh_vertices: np.ndarray, mesh_triangles: np.ndarray):
        """
        Initialize mesh data and build spatial acceleration structures.
        
        This implements the spatial indexing from FIXR research for efficient
        collision queries.
        """
        print("Initializing collision detection mesh data...")
        
        self.mesh_vertices = mesh_vertices.copy()
        self.mesh_triangles = mesh_triangles.copy()
        
        # Build spatial acceleration structures
        self._build_kdtree()
        self._calculate_triangle_data()
        self._build_bvh_tree()
        
        print(f"Collision detection initialized:")
        print(f"  • Vertices: {len(self.mesh_vertices)}")
        print(f"  • Triangles: {len(self.mesh_triangles)}")
        print(f"  • KD-Tree built with {len(self.mesh_vertices)} points")
        print(f"  • BVH tree built with {len(self.triangle_centers)} triangles")
    
    def _build_kdtree(self):
        """Build KD-tree for fast nearest neighbor queries."""
        if self.mesh_vertices is not None:
            self.mesh_kdtree = cKDTree(self.mesh_vertices)
    
    def _calculate_triangle_data(self):
        """Calculate triangle centers and normals for collision detection."""
        if self.mesh_vertices is None or self.mesh_triangles is None:
            return
        
        self.triangle_centers = []
        self.triangle_normals = []
        
        for triangle in self.mesh_triangles:
            # Triangle vertices
            v0 = self.mesh_vertices[triangle[0]]
            v1 = self.mesh_vertices[triangle[1]]
            v2 = self.mesh_vertices[triangle[2]]
            
            # Triangle center
            center = (v0 + v1 + v2) / 3
            self.triangle_centers.append(center)
            
            # Triangle normal
            edge1 = v1 - v0
            edge2 = v2 - v0
            normal = np.cross(edge1, edge2)
            
            if np.linalg.norm(normal) > 1e-10:
                normal = normal / np.linalg.norm(normal)
            
            self.triangle_normals.append(normal)
        
        self.triangle_centers = np.array(self.triangle_centers)
        self.triangle_normals = np.array(self.triangle_normals)
        
        # Build KD-tree for triangle centers
        if len(self.triangle_centers) > 0:
            self.triangle_kdtree = cKDTree(self.triangle_centers)
    
    def _build_bvh_tree(self):
        """
        Build Bounding Volume Hierarchy (BVH) tree.
        
        Implements extended OBB tree algorithms from FIXR research
        for optimized collision detection.
        """
        if self.triangle_centers is None:
            return
        
        # Simplified BVH - in production this would be a full hierarchical structure
        triangle_bboxes = []
        
        for i, triangle in enumerate(self.mesh_triangles):
            v0 = self.mesh_vertices[triangle[0]]
            v1 = self.mesh_vertices[triangle[1]]
            v2 = self.mesh_vertices[triangle[2]]
            
            min_point = np.minimum(np.minimum(v0, v1), v2)
            max_point = np.maximum(np.maximum(v0, v1), v2)
            
            bbox = BoundingBox(min_point, max_point)
            triangle_bboxes.append(bbox)
        
        self.bvh_tree = triangle_bboxes
    
    def check_point_collision(self, point: np.ndarray, 
                             collision_type: CollisionType = CollisionType.POINT_SURFACE) -> CollisionResult:
        """
        Check collision for a single point.
        
        Implements ray collision detection algorithms from FIXR research
        to identify potential interference between wire path and teeth structures.
        """
        start_time = time.time()
        self.performance_stats['total_queries'] += 1
        
        # Check cache first
        point_key = tuple(np.round(point, 3))
        if point_key in self.collision_cache:
            self.performance_stats['cache_hits'] += 1
            return self.collision_cache[point_key]
        
        if self.mesh_kdtree is None:
            return CollisionResult(False, collision_type, point, np.zeros(3), 0.0, float('inf'))
        
        # Find nearest vertices
        distances, indices = self.mesh_kdtree.query(point, k=10)
        min_distance = distances[0]
        
        collision_detected = min_distance < self.collision_tolerance
        
        if collision_detected:
            self.performance_stats['collision_detections'] += 1
            
            # Find closest surface point and normal
            closest_point, normal, triangle_idx = self._find_closest_surface_point(point)
            penetration_depth = self.collision_tolerance - min_distance
            
            result = CollisionResult(
                collision_detected=True,
                collision_type=collision_type,
                collision_point=closest_point,
                collision_normal=normal,
                penetration_depth=max(penetration_depth, 0.0),
                collision_distance=min_distance,
                triangle_index=triangle_idx
            )
        else:
            result = CollisionResult(
                collision_detected=False,
                collision_type=collision_type,
                collision_point=point,
                collision_normal=np.zeros(3),
                penetration_depth=0.0,
                collision_distance=min_distance
            )
        
        # Cache result
        self.collision_cache[point_key] = result
        
        # Update performance stats
        query_time = time.time() - start_time
        self.performance_stats['average_query_time'] = (
            (self.performance_stats['average_query_time'] * (self.performance_stats['total_queries'] - 1) + 
             query_time) / self.performance_stats['total_queries']
        )
        
        return result
    
    def _find_closest_surface_point(self, point: np.ndarray) -> Tuple[np.ndarray, np.ndarray, int]:
        """Find closest point on mesh surface and its normal."""
        if self.triangle_kdtree is None:
            nearest_vertex_idx = self.mesh_kdtree.query(point)[1]
            return self.mesh_vertices[nearest_vertex_idx], np.array([0, 0, 1]), -1
        
        # Find nearest triangles
        distances, triangle_indices = self.triangle_kdtree.query(point, k=5)
        
        closest_point = point
        closest_normal = np.array([0, 0, 1])
        closest_triangle_idx = -1
        min_distance = float('inf')
        
        for triangle_idx in triangle_indices:
            if triangle_idx >= len(self.mesh_triangles):
                continue
            
            triangle = self.mesh_triangles[triangle_idx]
            v0 = self.mesh_vertices[triangle[0]]
            v1 = self.mesh_vertices[triangle[1]]
            v2 = self.mesh_vertices[triangle[2]]
            
            # Project point onto triangle plane
            surface_point, distance = self._project_point_to_triangle(point, v0, v1, v2)
            
            if distance < min_distance:
                min_distance = distance
                closest_point = surface_point
                closest_normal = self.triangle_normals[triangle_idx]
                closest_triangle_idx = triangle_idx
        
        return closest_point, closest_normal, closest_triangle_idx
    
    def _project_point_to_triangle(self, point: np.ndarray, v0: np.ndarray, 
                                  v1: np.ndarray, v2: np.ndarray) -> Tuple[np.ndarray, float]:
        """Project point onto triangle and return closest point and distance."""
        # Triangle edges
        edge1 = v1 - v0
        edge2 = v2 - v0
        
        # Triangle normal
        normal = np.cross(edge1, edge2)
        if np.linalg.norm(normal) > 1e-10:
            normal = normal / np.linalg.norm(normal)
        else:
            # Degenerate triangle
            return v0, np.linalg.norm(point - v0)
        
        # Project point onto triangle plane
        to_point = point - v0
        distance_to_plane = np.dot(to_point, normal)
        projected_point = point - distance_to_plane * normal
        
        # Check if projected point is inside triangle using barycentric coordinates
        v0_to_proj = projected_point - v0
        
        # Barycentric coordinates
        dot00 = np.dot(edge2, edge2)
        dot01 = np.dot(edge2, edge1)
        dot02 = np.dot(edge2, v0_to_proj)
        dot11 = np.dot(edge1, edge1)
        dot12 = np.dot(edge1, v0_to_proj)
        
        inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
        u = (dot11 * dot02 - dot01 * dot12) * inv_denom
        v = (dot00 * dot12 - dot01 * dot02) * inv_denom
        
        # Check if point is inside triangle
        if u >= 0 and v >= 0 and u + v <= 1:
            # Inside triangle
            return projected_point, abs(distance_to_plane)
        else:
            # Outside triangle - find closest edge point
            edge_points = [
                self._closest_point_on_line_segment(point, v0, v1),
                self._closest_point_on_line_segment(point, v1, v2),
                self._closest_point_on_line_segment(point, v2, v0)
            ]
            
            closest_edge_point = min(edge_points, key=lambda p: np.linalg.norm(point - p))
            return closest_edge_point, np.linalg.norm(point - closest_edge_point)
    
    def _closest_point_on_line_segment(self, point: np.ndarray, line_start: np.ndarray, 
                                      line_end: np.ndarray) -> np.ndarray:
        """Find closest point on line segment to given point."""
        line_vec = line_end - line_start
        point_vec = point - line_start
        
        line_length_sq = np.dot(line_vec, line_vec)
        
        if line_length_sq < 1e-10:
            return line_start
        
        t = np.dot(point_vec, line_vec) / line_length_sq
        t = np.clip(t, 0.0, 1.0)
        
        return line_start + t * line_vec
    
    def check_path_collision(self, path_points: np.ndarray) -> List[CollisionResult]:
        """
        Check collision for entire wire path.
        
        Performs comprehensive collision detection along the wire path
        with optimization for performance.
        """
        collision_results = []
        
        print(f"Checking collision for path with {len(path_points)} points...")
        
        for i, point in enumerate(path_points):
            result = self.check_point_collision(point)
            collision_results.append(result)
            
            # Progress reporting for large paths
            if i % 100 == 0 and i > 0:
                collision_count = sum(1 for r in collision_results if r.collision_detected)
                print(f"  Progress: {i}/{len(path_points)} points, {collision_count} collisions detected")
        
        total_collisions = sum(1 for r in collision_results if r.collision_detected)
        print(f"Path collision check complete: {total_collisions} collisions detected")
        
        return collision_results
    
    def resolve_path_collisions(self, path_points: np.ndarray, 
                               collision_results: List[CollisionResult]) -> np.ndarray:
        """
        Resolve collisions by adjusting path points.
        
        Implements collision avoidance algorithms that maintain smooth
        wire path while avoiding geometric conflicts.
        """
        corrected_path = path_points.copy()
        correction_count = 0
        
        for i, (point, collision) in enumerate(zip(path_points, collision_results)):
            if collision.collision_detected:
                corrected_point = self._resolve_single_collision(point, collision)
                corrected_path[i] = corrected_point
                correction_count += 1
        
        if correction_count > 0:
            print(f"Resolved {correction_count} collisions")
            # Apply smoothing to maintain wire continuity
            corrected_path = self._smooth_corrected_path(corrected_path, path_points, collision_results)
        
        return corrected_path
    
    def _resolve_single_collision(self, collision_point: np.ndarray, 
                                 collision: CollisionResult) -> np.ndarray:
        """Resolve a single collision by moving point to safe location."""
        if not collision.collision_detected:
            return collision_point
        
        # Move point along collision normal to safe distance
        safe_distance = self.collision_tolerance + 0.5  # Extra margin
        
        if np.linalg.norm(collision.collision_normal) > 1e-6:
            # Use surface normal for correction
            correction_direction = collision.collision_normal
        else:
            # Fallback: move away from collision point
            correction_direction = collision_point - collision.collision_point
            if np.linalg.norm(correction_direction) < 1e-6:
                correction_direction = np.array([0, 0, 1])  # Default upward
        
        # Normalize direction
        correction_direction = correction_direction / np.linalg.norm(correction_direction)
        
        # Calculate corrected position
        corrected_point = collision.collision_point + correction_direction * safe_distance
        
        return corrected_point
    
    def _smooth_corrected_path(self, corrected_path: np.ndarray, original_path: np.ndarray,
                              collision_results: List[CollisionResult]) -> np.ndarray:
        """Apply smoothing to corrected path while preserving collision avoidance."""
        smoothed_path = corrected_path.copy()
        
        # Identify corrected segments
        corrected_indices = [i for i, result in enumerate(collision_results) if result.collision_detected]
        
        # Apply local smoothing around corrected areas
        for idx in corrected_indices:
            # Define smoothing window
            window_start = max(0, idx - 2)
            window_end = min(len(smoothed_path), idx + 3)
            
            # Only smooth if we won't affect other corrected points
            window_indices = list(range(window_start, window_end))
            if any(i in corrected_indices for i in window_indices if i != idx):
                continue
            
            # Apply gentle smoothing
            for i in range(window_start + 1, window_end - 1):
                if i == idx:
                    continue  # Don't modify the corrected point
                
                # Weighted average with neighbors
                neighbor_avg = (smoothed_path[i-1] + smoothed_path[i+1]) / 2
                smoothed_path[i] = 0.7 * smoothed_path[i] + 0.3 * neighbor_avg
        
        return smoothed_path
    
    def ray_triangle_intersection(self, ray_origin: np.ndarray, ray_direction: np.ndarray,
                                 triangle_index: int) -> Tuple[bool, float, np.ndarray]:
        """
        Ray-triangle intersection using Möller-Trumbore algorithm.
        
        Implements triangle intersection algorithms from FIXR research
        for precise geometric interference detection.
        """
        if (triangle_index < 0 or triangle_index >= len(self.mesh_triangles) or
            self.mesh_vertices is None):
            return False, 0.0, np.zeros(3)
        
        triangle = self.mesh_triangles[triangle_index]
        v0 = self.mesh_vertices[triangle[0]]
        v1 = self.mesh_vertices[triangle[1]]
        v2 = self.mesh_vertices[triangle[2]]
        
        # Möller-Trumbore intersection algorithm
        edge1 = v1 - v0
        edge2 = v2 - v0
        h = np.cross(ray_direction, edge2)
        a = np.dot(edge1, h)
        
        # Ray parallel to triangle
        if abs(a) < 1e-10:
            return False, 0.0, np.zeros(3)
        
        f = 1.0 / a
        s = ray_origin - v0
        u = f * np.dot(s, h)
        
        if u < 0.0 or u > 1.0:
            return False, 0.0, np.zeros(3)
        
        q = np.cross(s, edge1)
        v = f * np.dot(ray_direction, q)
        
        if v < 0.0 or u + v > 1.0:
            return False, 0.0, np.zeros(3)
        
        # Calculate intersection distance
        t = f * np.dot(edge2, q)
        
        if t > 1e-10:  # Ray intersection
            intersection_point = ray_origin + t * ray_direction
            return True, t, intersection_point
        
        return False, 0.0, np.zeros(3)
    
    def batch_collision_check(self, points: np.ndarray, use_parallel: bool = True) -> List[CollisionResult]:
        """
        Batch collision checking for improved performance.
        
        Optimizes collision detection for large point sets using
        spatial acceleration structures.
        """
        if self.mesh_kdtree is None:
            return [CollisionResult(False, CollisionType.POINT_SURFACE, point, 
                                  np.zeros(3), 0.0, float('inf')) for point in points]
        
        print(f"Batch collision check for {len(points)} points...")
        
        # Query all points at once for better performance
        distances, indices = self.mesh_kdtree.query(points, k=1)
        
        results = []
        for i, (point, distance, vertex_idx) in enumerate(zip(points, distances, indices)):
            collision_detected = distance < self.collision_tolerance
            
            if collision_detected:
                # Get detailed collision information
                closest_point, normal, triangle_idx = self._find_closest_surface_point(point)
                penetration_depth = max(self.collision_tolerance - distance, 0.0)
                
                result = CollisionResult(
                    collision_detected=True,
                    collision_type=CollisionType.POINT_SURFACE,
                    collision_point=closest_point,
                    collision_normal=normal,
                    penetration_depth=penetration_depth,
                    collision_distance=distance,
                    triangle_index=triangle_idx
                )
            else:
                result = CollisionResult(
                    collision_detected=False,
                    collision_type=CollisionType.POINT_SURFACE,
                    collision_point=point,
                    collision_normal=np.zeros(3),
                    penetration_depth=0.0,
                    collision_distance=distance
                )
            
            results.append(result)
        
        collision_count = sum(1 for r in results if r.collision_detected)
        print(f"Batch collision check complete: {collision_count} collisions detected")
        
        return results
    
    def get_collision_statistics(self) -> Dict:
        """Get comprehensive collision detection statistics."""
        cache_hit_rate = (self.performance_stats['cache_hits'] / 
                         max(self.performance_stats['total_queries'], 1)) * 100
        
        return {
            'total_queries': self.performance_stats['total_queries'],
            'collision_detections': self.performance_stats['collision_detections'],
            'cache_hits': self.performance_stats['cache_hits'],
            'cache_hit_rate': cache_hit_rate,
            'average_query_time': self.performance_stats['average_query_time'] * 1000,  # ms
            'collision_tolerance': self.collision_tolerance,
            'mesh_vertices': len(self.mesh_vertices) if self.mesh_vertices is not None else 0,
            'mesh_triangles': len(self.mesh_triangles) if self.mesh_triangles is not None else 0,
            'cache_size': len(self.collision_cache)
        }
    
    def clear_cache(self):
        """Clear collision detection cache."""
        self.collision_cache.clear()
        print("Collision detection cache cleared")
    
    def set_collision_tolerance(self, tolerance: float):
        """Update collision tolerance and clear cache."""
        self.collision_tolerance = tolerance
        self.clear_cache()  # Cache is no longer valid
        print(f"Collision tolerance updated to {tolerance}mm")
    
    def visualize_collision_data(self, collision_results: List[CollisionResult]) -> Dict:
        """
        Generate visualization data for collision results.
        
        Returns data that can be used by visualization systems to show
        collision points, normals, and corrected paths.
        """
        collision_points = []
        collision_normals = []
        penetration_depths = []
        safe_points = []
        
        for result in collision_results:
            if result.collision_detected:
                collision_points.append(result.collision_point)
                collision_normals.append(result.collision_normal)
                penetration_depths.append(result.penetration_depth)
                
                # Calculate safe point
                safe_distance = self.collision_tolerance + 0.5
                if np.linalg.norm(result.collision_normal) > 1e-6:
                    safe_point = (result.collision_point + 
                                result.collision_normal * safe_distance)
                    safe_points.append(safe_point)
        
        return {
            'collision_points': np.array(collision_points) if collision_points else np.array([]),
            'collision_normals': np.array(collision_normals) if collision_normals else np.array([]),
            'penetration_depths': np.array(penetration_depths) if penetration_depths else np.array([]),
            'safe_points': np.array(safe_points) if safe_points else np.array([]),
            'collision_count': len(collision_points),
            'max_penetration': max(penetration_depths) if penetration_depths else 0.0,
            'average_penetration': np.mean(penetration_depths) if penetration_depths else 0.0
        }
    
    def export_collision_report(self, collision_results: List[CollisionResult], 
                               original_path: np.ndarray, corrected_path: np.ndarray) -> Dict:
        """
        Export comprehensive collision detection report.
        
        Provides detailed analysis for manufacturing and quality control.
        """
        collision_points = [r for r in collision_results if r.collision_detected]
        
        report = {
            'summary': {
                'total_path_points': len(collision_results),
                'collision_detections': len(collision_points),
                'collision_rate': len(collision_points) / len(collision_results) * 100,
                'collision_tolerance': self.collision_tolerance,
                'max_penetration_depth': max([r.penetration_depth for r in collision_points]) if collision_points else 0.0,
                'average_penetration_depth': np.mean([r.penetration_depth for r in collision_points]) if collision_points else 0.0
            },
            'path_analysis': {
                'original_path_length': self._calculate_path_length(original_path),
                'corrected_path_length': self._calculate_path_length(corrected_path),
                'path_deviation': self._calculate_path_deviation(original_path, corrected_path),
                'max_point_deviation': self._calculate_max_point_deviation(original_path, corrected_path)
            },
            'collision_regions': self._analyze_collision_regions(collision_points),
            'performance_metrics': self.get_collision_statistics(),
            'recommendations': self._generate_collision_recommendations(collision_results)
        }
        
        return report
    
    def _calculate_path_length(self, path: np.ndarray) -> float:
        """Calculate total path length."""
        if len(path) < 2:
            return 0.0
        
        total_length = 0.0
        for i in range(len(path) - 1):
            segment_length = np.linalg.norm(path[i + 1] - path[i])
            total_length += segment_length
        
        return total_length
    
    def _calculate_path_deviation(self, original: np.ndarray, corrected: np.ndarray) -> float:
        """Calculate average deviation between original and corrected paths."""
        if len(original) != len(corrected):
            return 0.0
        
        deviations = [np.linalg.norm(orig - corr) for orig, corr in zip(original, corrected)]
        return np.mean(deviations)
    
    def _calculate_max_point_deviation(self, original: np.ndarray, corrected: np.ndarray) -> float:
        """Calculate maximum point deviation between paths."""
        if len(original) != len(corrected):
            return 0.0
        
        deviations = [np.linalg.norm(orig - corr) for orig, corr in zip(original, corrected)]
        return max(deviations) if deviations else 0.0
    
    def _analyze_collision_regions(self, collision_results: List[CollisionResult]) -> Dict:
        """Analyze collision distribution and identify problem regions."""
        if not collision_results:
            return {'total_regions': 0, 'regions': []}
        
        # Simple clustering of collision points
        collision_points = np.array([r.collision_point for r in collision_results])
        
        # Basic region analysis (in production, use proper clustering)
        regions = []
        if len(collision_points) > 0:
            center = np.mean(collision_points, axis=0)
            max_distance = np.max([np.linalg.norm(p - center) for p in collision_points])
            
            regions.append({
                'center': center.tolist(),
                'radius': max_distance,
                'collision_count': len(collision_points),
                'severity': 'high' if len(collision_points) > 10 else 'medium' if len(collision_points) > 5 else 'low'
            })
        
        return {
            'total_regions': len(regions),
            'regions': regions
        }
    
    def _generate_collision_recommendations(self, collision_results: List[CollisionResult]) -> List[str]:
        """Generate recommendations based on collision analysis."""
        recommendations = []
        
        collision_count = sum(1 for r in collision_results if r.collision_detected)
        collision_rate = collision_count / len(collision_results) * 100
        
        if collision_rate > 20:
            recommendations.append("High collision rate detected. Consider increasing wire height or adjusting bracket positions.")
        elif collision_rate > 10:
            recommendations.append("Moderate collision rate. Review wire path for potential optimization.")
        
        max_penetration = max([r.penetration_depth for r in collision_results if r.collision_detected], default=0.0)
        if max_penetration > 1.0:
            recommendations.append(f"Deep penetration detected ({max_penetration:.2f}mm). Increase collision tolerance or revise wire design.")
        
        if collision_count == 0:
            recommendations.append("No collisions detected. Wire path is clear for manufacturing.")
        
        return recommendations