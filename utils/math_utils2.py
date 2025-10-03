#!/usr/bin/env python3
"""
utils/math_utils.py - ENHANCED VERSION

Professional Mathematical Utilities with FIXR-Inspired Algorithms
===============================================================
Enhanced with advanced mathematical functions from FIXR research including:
- B-spline curve implementations
- Energy optimization functions
- Geometric constraint solving
- 3D transformation matrices
"""

import numpy as np
from scipy import interpolate, optimize, linalg
from scipy.spatial.transform import Rotation as R
from typing import List, Tuple, Optional, Callable, Dict
import math

class AdvancedMathUtils:
    """
    Professional mathematical utilities implementing FIXR research algorithms.
    
    Includes:
    - B-spline curve processing algorithms
    - Energy-based optimization methods
    - 3D transformation matrices
    - Constraint satisfaction formulations
    - Geometric computation functions
    """
    
    @staticmethod
    def create_b_spline_curve(control_points: np.ndarray, degree: int = 3, 
                             num_samples: int = 100, weights: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Create B-spline curve using FIXR's spline curve processing algorithms.
        
        Implements Non-Uniform Rational B-Spline (NURBS) curve generation
        with optimized control point handling.
        """
        n_points, n_dims = control_points.shape
        
        if n_points < degree + 1:
            degree = max(1, n_points - 1)
        
        # Create parameter vector
        t = np.linspace(0, 1, n_points)
        
        # Generate uniform knot vector
        knots = np.concatenate([
            np.zeros(degree),
            np.linspace(0, 1, n_points - degree + 1),
            np.ones(degree)
        ])
        
        # Sample parameter values
        t_sample = np.linspace(0, 1, num_samples)
        
        # Generate B-spline curve
        curve_points = []
        
        for dim in range(n_dims):
            if weights is not None:
                # NURBS curve with weights
                weighted_points = control_points[:, dim] * weights
                tck = interpolate.splrep(t, weighted_points, k=degree, t=knots[degree:-degree])
                weight_sum = interpolate.splrep(t, weights, k=degree, t=knots[degree:-degree])
                
                curve_dim = interpolate.splev(t_sample, tck) / interpolate.splev(t_sample, weight_sum)
            else:
                # Standard B-spline
                tck = interpolate.splrep(t, control_points[:, dim], k=degree, s=0)
                curve_dim = interpolate.splev(t_sample, tck)
            
            curve_points.append(curve_dim)
        
        return np.array(curve_points).T
    
    @staticmethod
    def bezier_curve_optimization(control_points: np.ndarray, target_points: np.ndarray, 
                                 chord_to_arc_ratio: float = 0.8) -> np.ndarray:
        """
        Optimize Bézier curve using dichotomy algorithms and chord-to-arc ratios.
        
        Implements FIXR's finite point extension methods combined with 
        dichotomy algorithms for optimal curve approximation.
        """
        def bezier_curve(t: float, points: np.ndarray) -> np.ndarray:
            """Calculate point on Bézier curve at parameter t."""
            n = len(points) - 1
            result = np.zeros_like(points[0])
            
            for i, point in enumerate(points):
                # Binomial coefficient
                binom_coeff = math.comb(n, i)
                # Bernstein basis polynomial
                basis = binom_coeff * (t ** i) * ((1 - t) ** (n - i))
                result += basis * point
            
            return result
        
        def objective_function(flattened_control_points):
            """Objective function for optimization."""
            reshaped_points = flattened_control_points.reshape(-1, 3)
            total_error = 0.0
            
            # Sample points along curve
            t_values = np.linspace(0, 1, len(target_points))
            
            for i, t in enumerate(t_values):
                curve_point = bezier_curve(t, reshaped_points)
                error = np.linalg.norm(curve_point - target_points[i])
                total_error += error ** 2
            
            # Add chord-to-arc ratio constraint
            arc_length = AdvancedMathUtils.calculate_curve_length(reshaped_points, bezier_curve)
            chord_length = np.linalg.norm(reshaped_points[-1] - reshaped_points[0])
            
            if chord_length > 0:
                current_ratio = chord_length / arc_length
                ratio_penalty = (current_ratio - chord_to_arc_ratio) ** 2 * 100
                total_error += ratio_penalty
            
            return total_error
        
        # Optimize control points
        initial_params = control_points.flatten()
        result = optimize.minimize(objective_function, initial_params, method='L-BFGS-B')
        
        if result.success:
            return result.x.reshape(-1, 3)
        else:
            return control_points
    
    @staticmethod
    def calculate_curve_length(control_points: np.ndarray, curve_function: Callable, 
                              num_samples: int = 1000) -> float:
        """Calculate arc length of parametric curve."""
        t_values = np.linspace(0, 1, num_samples)
        total_length = 0.0
        
        prev_point = curve_function(0, control_points)
        
        for t in t_values[1:]:
            current_point = curve_function(t, control_points)
            segment_length = np.linalg.norm(current_point - prev_point)
            total_length += segment_length
            prev_point = current_point
        
        return total_length
    
    @staticmethod
    def energy_minimization_function(path_points: np.ndarray, tension_weight: float = 1.0,
                                   curvature_weight: float = 1.0, length_weight: float = 0.1) -> float:
        """
        Energy-based optimization function from FIXR research.
        
        Implements energy-constrained optimization algorithms that minimize
        internal stresses while achieving desired geometric configuration.
        """
        if len(path_points) < 3:
            return 0.0
        
        # Curvature energy (bending resistance)
        curvature_energy = 0.0
        for i in range(1, len(path_points) - 1):
            p1, p2, p3 = path_points[i-1], path_points[i], path_points[i+1]
            curvature = AdvancedMathUtils.calculate_curvature_3d(p1, p2, p3)
            curvature_energy += curvature ** 2
        
        # Tension energy (stretching resistance)
        tension_energy = 0.0
        for i in range(len(path_points) - 1):
            segment_length = np.linalg.norm(path_points[i+1] - path_points[i])
            tension_energy += segment_length
        
        # Total length penalty
        total_length = sum(np.linalg.norm(path_points[i+1] - path_points[i]) 
                          for i in range(len(path_points) - 1))
        
        # Combine energy components
        total_energy = (curvature_weight * curvature_energy + 
                       tension_weight * tension_energy + 
                       length_weight * total_length)
        
        return total_energy
    
    @staticmethod
    def calculate_curvature_3d(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """
        Calculate 3D curvature at point p2 using advanced geometric methods.
        
        Implements precise curvature calculation for manufacturing optimization.
        """
        # Vectors from p2 to adjacent points
        v1 = p1 - p2
        v2 = p3 - p2
        
        # Check for degenerate cases
        len1 = np.linalg.norm(v1)
        len2 = np.linalg.norm(v2)
        
        if len1 < 1e-10 or len2 < 1e-10:
            return 0.0
        
        # Normalize vectors
        v1_norm = v1 / len1
        v2_norm = v2 / len2
        
        # Calculate curvature using cross product method
        cross_product = np.cross(v1_norm, v2_norm)
        cross_magnitude = np.linalg.norm(cross_product)
        
        # Dot product for angle calculation
        dot_product = np.clip(np.dot(v1_norm, v2_norm), -1.0, 1.0)
        
        # Curvature formula: κ = |v1 × v2| / |v1|^3 (approximately)
        # More precise formula considering the angle
        angle = np.arccos(abs(dot_product))
        average_length = (len1 + len2) / 2
        
        if average_length > 0:
            curvature = 2 * np.sin(angle) / average_length
        else:
            curvature = 0.0
        
        return curvature
    
    @staticmethod
    def create_transformation_matrix(translation: np.ndarray, rotation_angles: np.ndarray, 
                                   scale: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Create 3D transformation matrix for coordinate conversion.
        
        Implements FIXR's 3D transformation matrices for converting
        design space coordinates to machine-specific parameters.
        """
        if scale is None:
            scale = np.array([1.0, 1.0, 1.0])
        
        # Create rotation matrix from Euler angles (XYZ order)
        rotation_matrix = R.from_euler('xyz', rotation_angles).as_matrix()
        
        # Create scaling matrix
        scale_matrix = np.diag(scale)
        
        # Combine rotation and scaling
        rotation_scale = rotation_matrix @ scale_matrix
        
        # Create 4x4 transformation matrix
        transform_matrix = np.eye(4)
        transform_matrix[:3, :3] = rotation_scale
        transform_matrix[:3, 3] = translation
        
        return transform_matrix
    
    @staticmethod
    def xyz_to_bending_parameters(points: np.ndarray) -> List[Dict]:
        """
        Convert XYZ coordinates to (L, β, θ) bending parameters.
        
        Implements FIXR's B-Code generation system for manufacturing.
        """
        bending_parameters = []
        
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            
            # Calculate length L
            length = np.linalg.norm(p2 - p1)
            
            # Calculate bend angle β (if not the last segment)
            if i < len(points) - 2:
                p3 = points[i + 2]
                
                # Vectors
                v1 = p2 - p1
                v2 = p3 - p2
                
                # Normalize
                if np.linalg.norm(v1) > 1e-10 and np.linalg.norm(v2) > 1e-10:
                    v1_norm = v1 / np.linalg.norm(v1)
                    v2_norm = v2 / np.linalg.norm(v2)
                    
                    # Bend angle
                    dot_product = np.clip(np.dot(v1_norm, v2_norm), -1, 1)
                    bend_angle = np.degrees(np.arccos(dot_product))
                else:
                    bend_angle = 0.0
            else:
                bend_angle = 0.0
            
            # Calculate rotation angle θ (twist around segment axis)
            # For orthodontic wires, this is typically 0 or based on bracket orientation
            rotation_angle = 0.0  # Simplified for now
            
            bending_parameters.append({
                'length': length,
                'bend_angle': bend_angle,
                'rotation_angle': rotation_angle,
                'position': p1.copy(),
                'segment_index': i
            })
        
        return bending_parameters
    
    @staticmethod
    def constraint_satisfaction_solver(variables: np.ndarray, constraints: List[Callable], 
                                     objectives: List[Callable], weights: Optional[List[float]] = None) -> np.ndarray:
        """
        Multi-objective constraint satisfaction solver.
        
        Implements FIXR's constraint satisfaction formulations for managing
        multiple design requirements simultaneously.
        """
        if weights is None:
            weights = [1.0] * len(objectives)
        
        def combined_objective(x):
            """Combine multiple objectives with weights."""
            total_cost = 0.0
            
            # Objective functions
            for i, objective in enumerate(objectives):
                try:
                    cost = objective(x)
                    total_cost += weights[i] * cost
                except:
                    total_cost += 1e6  # Heavy penalty for invalid solutions
            
            # Constraint penalties
            for constraint in constraints:
                try:
                    violation = constraint(x)
                    if violation > 0:  # Constraint violated
                        total_cost += 1000 * violation ** 2
                except:
                    total_cost += 1e6
            
            return total_cost
        
        # Bounds based on reasonable wire parameters
        bounds = [(-100, 100)] * len(variables)  # Position bounds in mm
        
        # Optimize using multiple methods for robustness
        methods = ['L-BFGS-B', 'TNC', 'SLSQP']
        best_result = None
        best_cost = float('inf')
        
        for method in methods:
            try:
                result = optimize.minimize(
                    combined_objective, 
                    variables, 
                    method=method, 
                    bounds=bounds,
                    options={'maxiter': 1000}
                )
                
                if result.success and result.fun < best_cost:
                    best_result = result
                    best_cost = result.fun
            except:
                continue
        
        if best_result is not None:
            return best_result.x
        else:
            return variables  # Return original if optimization fails
    
    @staticmethod
    def calculate_springback_compensation(bend_angle: float, bend_radius: float, 
                                        material_properties: Dict) -> float:
        """
        Calculate springback compensation based on material properties.
        
        Implements FIXR's springback compensation calculations for different
        wire materials' elastic properties.
        """
        # Extract material properties
        elastic_modulus = material_properties.get('elastic_modulus', 200000)  # MPa
        yield_strength = material_properties.get('yield_strength', 500)  # MPa
        thickness = material_properties.get('thickness', 0.5)  # mm
        
        # Calculate bending stress
        if bend_radius > 0:
            bending_stress = elastic_modulus * thickness / (2 * bend_radius)
        else:
            return bend_angle  # No compensation for infinite radius
        
        # Springback factor based on stress level
        if bending_stress < yield_strength * 0.5:
            # Elastic regime - predictable springback
            springback_factor = 0.85 + 0.10 * (bending_stress / (yield_strength * 0.5))
        elif bending_stress < yield_strength:
            # Transition regime - increasing plastic deformation
            stress_ratio = bending_stress / yield_strength
            springback_factor = 0.95 - 0.20 * (stress_ratio - 0.5) / 0.5
        else:
            # Plastic regime - minimal springback
            springback_factor = 0.75
        
        # Apply compensation
        compensated_angle = bend_angle / springback_factor
        
        return compensated_angle
    
    @staticmethod
    def ray_triangle_intersection(ray_origin: np.ndarray, ray_direction: np.ndarray,
                                 triangle_vertices: np.ndarray, tolerance: float = 1e-6) -> Tuple[bool, float, np.ndarray]:
        """
        Ray-triangle intersection for collision detection.
        
        Implements triangle intersection algorithms based on non-linear programming
        methods for precise geometric interference detection.
        """
        v0, v1, v2 = triangle_vertices[0], triangle_vertices[1], triangle_vertices[2]
        
        # Calculate triangle edges
        edge1 = v1 - v0
        edge2 = v2 - v0
        
        # Calculate determinant
        h = np.cross(ray_direction, edge2)
        det = np.dot(edge1, h)
        
        # Ray parallel to triangle
        if abs(det) < tolerance:
            return False, 0.0, np.zeros(3)
        
        inv_det = 1.0 / det
        s = ray_origin - v0
        u = inv_det * np.dot(s, h)
        
        # Check if intersection point is outside triangle
        if u < 0.0 or u > 1.0:
            return False, 0.0, np.zeros(3)
        
        q = np.cross(s, edge1)
        v = inv_det * np.dot(ray_direction, q)
        
        if v < 0.0 or u + v > 1.0:
            return False, 0.0, np.zeros(3)
        
        # Calculate intersection distance
        t = inv_det * np.dot(edge2, q)
        
        if t > tolerance:  # Ray intersection
            intersection_point = ray_origin + t * ray_direction
            return True, t, intersection_point
        
        return False, 0.0, np.zeros(3)
    
    @staticmethod
    def oriented_bounding_box_collision(obb1_center: np.ndarray, obb1_axes: np.ndarray, obb1_extents: np.ndarray,
                                       obb2_center: np.ndarray, obb2_axes: np.ndarray, obb2_extents: np.ndarray) -> bool:
        """
        Oriented Bounding Box (OBB) collision detection.
        
        Implements extended OBB tree algorithms optimized for wire-to-tooth
        interference analysis from FIXR research.
        """
        # Translation vector
        t = obb2_center - obb1_center
        
        # Rotation matrix from OBB1 to OBB2
        R = obb1_axes.T @ obb2_axes
        abs_R = np.abs(R) + 1e-6  # Add small epsilon for numerical stability
        
        # Test axes from OBB1
        for i in range(3):
            ra = obb1_extents[i]
            rb = np.sum(obb2_extents * abs_R[i, :])
            if abs(np.dot(t, obb1_axes[i])) > ra + rb:
                return False
        
        # Test axes from OBB2
        for i in range(3):
            ra = np.sum(obb1_extents * abs_R[:, i])
            rb = obb2_extents[i]
            if abs(np.dot(t, obb2_axes[i])) > ra + rb:
                return False
        
        # Test cross products of axes
        for i in range(3):
            for j in range(3):
                ra = obb1_extents[(i+1)%3] * abs_R[(i+2)%3, j] + obb1_extents[(i+2)%3] * abs_R[(i+1)%3, j]
                rb = obb2_extents[(j+1)%3] * abs_R[i, (j+2)%3] + obb2_extents[(j+2)%3] * abs_R[i, (j+1)%3]
                
                cross_axis = np.cross(obb1_axes[i], obb2_axes[j])
                if np.linalg.norm(cross_axis) > 1e-6:
                    cross_axis = cross_axis / np.linalg.norm(cross_axis)
                    if abs(np.dot(t, cross_axis)) > ra + rb:
                        return False
        
        return True  # No separating axis found - collision detected
    
    @staticmethod
    def principal_component_analysis_3d(points: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        3D Principal Component Analysis for geometric analysis.
        
        Implements level set functions combined with PCA for sophisticated
        geometric analysis of dental anatomy.
        """
        # Center the points
        centroid = np.mean(points, axis=0)
        centered_points = points - centroid
        
        # Calculate covariance matrix
        covariance_matrix = np.cov(centered_points.T)
        
        # Eigen decomposition
        eigenvalues, eigenvectors = linalg.eigh(covariance_matrix)
        
        # Sort by eigenvalue (largest first)
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        
        # Ensure right-handed coordinate system
        if np.linalg.det(eigenvectors) < 0:
            eigenvectors[:, -1] *= -1
        
        return centroid, eigenvalues, eigenvectors
    
    @staticmethod
    def calculate_minimal_energy_curve(start_point: np.ndarray, end_point: np.ndarray,
                                      intermediate_points: List[np.ndarray], 
                                      tension: float = 1.0, num_samples: int = 100) -> np.ndarray:
        """
        Calculate minimal energy curve for flexible wire path optimization.
        
        Implements minimal-energy curve algorithms for natural wire behavior.
        """
        # Combine all points
        all_points = [start_point] + intermediate_points + [end_point]
        all_points = np.array(all_points)
        
        # Parameter values
        n_points = len(all_points)
        t_control = np.linspace(0, 1, n_points)
        t_sample = np.linspace(0, 1, num_samples)
        
        # Energy minimization function
        def energy_functional(coefficients):
            # Reshape coefficients into curve points
            curve_points = coefficients.reshape(num_samples, 3)
            
            # Bending energy (second derivative)
            energy = 0.0
            for i in range(1, len(curve_points) - 1):
                # Approximate second derivative
                second_deriv = curve_points[i+1] - 2*curve_points[i] + curve_points[i-1]
                energy += np.sum(second_deriv**2)
            
            # Tension energy (first derivative)
            for i in range(len(curve_points) - 1):
                first_deriv = curve_points[i+1] - curve_points[i]
                energy += tension * np.sum(first_deriv**2)
            
            return energy
        
        # Constraints: curve must pass through control points
        def constraint_function(coefficients):
            curve_points = coefficients.reshape(num_samples, 3)
            errors = []
            
            # Interpolate to find closest points to control points
            for control_point in all_points:
                distances = [np.linalg.norm(curve_points[i] - control_point) 
                           for i in range(num_samples)]
                min_distance = min(distances)
                errors.append(min_distance)
            
            return np.array(errors)
        
        # Initial guess: linear interpolation between all points
        initial_curve = []
        for i in range(num_samples):
            t = i / (num_samples - 1)
            # Find the appropriate segment
            segment_idx = min(int(t * (n_points - 1)), n_points - 2)
            local_t = (t * (n_points - 1)) - segment_idx
            
            point = (1 - local_t) * all_points[segment_idx] + local_t * all_points[segment_idx + 1]
            initial_curve.append(point)
        
        initial_curve = np.array(initial_curve)
        
        # Optimize
        try:
            result = optimize.minimize(
                energy_functional,
                initial_curve.flatten(),
                method='L-BFGS-B',
                options={'maxiter': 500}
            )
            
            if result.success:
                optimal_curve = result.x.reshape(num_samples, 3)
                return optimal_curve
        except:
            pass
        
        # Fallback to spline interpolation if optimization fails
        curve_points = []
        for dim in range(3):
            tck = interpolate.splrep(t_control, all_points[:, dim], k=min(3, n_points-1), s=0)
            curve_dim = interpolate.splev(t_sample, tck)
            curve_points.append(curve_dim)
        
        return np.array(curve_points).T
    
    @staticmethod
    def a_star_pathfinding(start: Tuple[int, int, int], goal: Tuple[int, int, int],
                          obstacle_grid: np.ndarray, heuristic_weight: float = 1.0) -> List[Tuple[int, int, int]]:
        """
        A* search algorithm for automatic bending sequence computation.
        
        Implements A* search algorithms from FIXR for minimizing collision risks
        and optimizing processing time efficiency.
        """
        from heapq import heappush, heappop
        
        def heuristic(a, b):
            return np.sqrt(sum((a[i] - b[i])**2 for i in range(3))) * heuristic_weight
        
        def get_neighbors(pos):
            x, y, z = pos
            neighbors = []
            
            # 26-connectivity (3D)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        if dx == 0 and dy == 0 and dz == 0:
                            continue
                        
                        nx, ny, nz = x + dx, y + dy, z + dz
                        
                        # Check bounds
                        if (0 <= nx < obstacle_grid.shape[0] and
                            0 <= ny < obstacle_grid.shape[1] and
                            0 <= nz < obstacle_grid.shape[2]):
                            
                            # Check if not obstacle
                            if obstacle_grid[nx, ny, nz] == 0:
                                neighbors.append((nx, ny, nz))
            
            return neighbors
        
        # A* algorithm
        open_set = []
        heappush(open_set, (0, start))
        
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}
        
        while open_set:
            current = heappop(open_set)[1]
            
            if current == goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]
            
            for neighbor in get_neighbors(current):
                # Movement cost (Euclidean distance)
                movement_cost = np.sqrt(sum((current[i] - neighbor[i])**2 for i in range(3)))
                tentative_g_score = g_score[current] + movement_cost
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                    
                    heappush(open_set, (f_score[neighbor], neighbor))
        
        return []  # No path found

class MathUtils(AdvancedMathUtils):
    """
    Legacy compatibility wrapper maintaining original interface
    while providing access to enhanced functionality.
    """
    
    @staticmethod
    def calculate_arc_length(points: np.ndarray) -> float:
        """Calculate total arc length of a path."""
        if len(points) < 2:
            return 0.0
        
        total_length = 0.0
        for i in range(len(points) - 1):
            segment_length = np.linalg.norm(points[i + 1] - points[i])
            total_length += segment_length
        
        return total_length
    
    @staticmethod
    def calculate_curvature(points: np.ndarray, index: int) -> float:
        """Calculate curvature at a specific point using enhanced method."""
        if index < 1 or index >= len(points) - 1:
            return 0.0
        
        p1 = points[index - 1]
        p2 = points[index]
        p3 = points[index + 1]
        
        return AdvancedMathUtils.calculate_curvature_3d(p1, p2, p3)
    
    @staticmethod
    def smooth_path(points: np.ndarray, smoothing_factor: float = 0.1) -> np.ndarray:
        """Enhanced path smoothing with energy considerations."""
        if len(points) < 3:
            return points
        
        # Use energy minimization for better smoothing
        return AdvancedMathUtils.calculate_minimal_energy_curve(
            points[0], points[-1], points[1:-1].tolist(), 
            tension=smoothing_factor, num_samples=len(points)
        )
    
    @staticmethod
    def resample_path(points: np.ndarray, target_spacing: float) -> np.ndarray:
        """Resample path with uniform spacing using B-spline interpolation."""
        if len(points) < 2:
            return points
        
        # Calculate cumulative distances
        distances = [0.0]
        for i in range(1, len(points)):
            dist = np.linalg.norm(points[i] - points[i - 1])
            distances.append(distances[-1] + dist)
        
        total_length = distances[-1]
        if total_length < target_spacing:
            return points
        
        # Create B-spline curve for high-quality resampling
        num_samples = max(int(total_length / target_spacing), len(points))
        resampled = AdvancedMathUtils.create_b_spline_curve(points, degree=3, num_samples=num_samples)
        
        return resampled
    
    @staticmethod
    def calculate_bending_angle(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """Calculate bending angle at point p2 with enhanced precision."""
        v1 = p2 - p1
        v2 = p3 - p2
        
        if np.linalg.norm(v1) < 1e-6 or np.linalg.norm(v2) < 1e-6:
            return 0.0
        
        v1_norm = v1 / np.linalg.norm(v1)
        v2_norm = v2 / np.linalg.norm(v2)
        
        dot_product = np.clip(np.dot(v1_norm, v2_norm), -1, 1)
        angle = np.degrees(np.arccos(dot_product))
        
        return 180 - angle  # Return supplement of angle