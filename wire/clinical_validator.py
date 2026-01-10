#!/usr/bin/env python3
"""
wire/clinical_validator.py

Clinical Wire Validation Module
===============================
Validates generated wire paths against clinical orthodontic standards
and provides detailed quality assessment reports.

Based on:
- ISO 15841:2014 - Dentistry — Wires for use in orthodontics
- ANSI/ADA Standard No. 32 - Orthodontic Wires
- Clinical orthodontic best practices
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    from wire.professional_materials import (
        WireMaterialProperties,
        WireSpecification,
        CLINICAL_FORCE_GUIDELINES,
        get_material
    )
except ImportError:
    from professional_materials import (
        WireMaterialProperties,
        WireSpecification,
        CLINICAL_FORCE_GUIDELINES,
        get_material
    )


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    severity: ValidationSeverity
    code: str
    message: str
    location: Optional[int] = None  # Path index where issue occurs
    value: Optional[float] = None  # Actual value that caused issue
    threshold: Optional[float] = None  # Threshold that was violated
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'severity': self.severity.value,
            'code': self.code,
            'message': self.message,
            'location': self.location,
            'value': self.value,
            'threshold': self.threshold
        }


@dataclass
class ValidationResult:
    """Complete validation result."""
    is_valid: bool = True
    overall_score: float = 100.0  # 0-100
    issues: List[ValidationIssue] = field(default_factory=list)
    metrics: Dict = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    def add_issue(self, issue: ValidationIssue):
        """Add a validation issue."""
        self.issues.append(issue)
        
        # Update validity based on severity
        if issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
            self.is_valid = False
        
        # Reduce score based on severity
        severity_penalties = {
            ValidationSeverity.INFO: 1,
            ValidationSeverity.WARNING: 5,
            ValidationSeverity.ERROR: 15,
            ValidationSeverity.CRITICAL: 30
        }
        self.overall_score -= severity_penalties.get(issue.severity, 0)
        self.overall_score = max(0, self.overall_score)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'is_valid': self.is_valid,
            'overall_score': round(self.overall_score, 1),
            'issue_count': len(self.issues),
            'issues': [issue.to_dict() for issue in self.issues],
            'metrics': self.metrics,
            'recommendations': self.recommendations
        }


class ClinicalValidator:
    """
    Validates wire paths against clinical orthodontic standards.
    """
    
    def __init__(
        self,
        material: Optional[WireMaterialProperties] = None,
        wire_diameter_mm: float = 0.4064
    ):
        """
        Initialize clinical validator.
        
        Args:
            material: Wire material properties
            wire_diameter_mm: Wire diameter in mm
        """
        self.material = material or get_material("niti_superelastic")
        self.wire_diameter = wire_diameter_mm
        
        # Validation thresholds
        self.thresholds = {
            'min_bend_radius_mm': self.material.min_bend_radius_mm,
            'max_curvature': 1.0 / self.material.min_bend_radius_mm,
            'min_segment_length_mm': self.material.min_segment_length_mm,
            'max_segment_length_mm': 5.0,
            'max_bend_angle_degrees': self.material.max_bend_angle_degrees,
            'min_path_length_mm': 50.0,
            'max_path_length_mm': 200.0,
            'smoothness_threshold': 0.1,  # Max curvature change rate
            'max_height_variation_mm': 3.0,
            'max_consecutive_sharp_bends': 2
        }
    
    def validate_wire_path(
        self,
        wire_path: np.ndarray,
        bracket_positions: Optional[np.ndarray] = None
    ) -> ValidationResult:
        """
        Perform comprehensive validation of wire path.
        
        Args:
            wire_path: Nx3 array of wire path points
            bracket_positions: Optional bracket positions for deviation check
            
        Returns:
            Complete validation result
        """
        result = ValidationResult()
        
        if wire_path is None or len(wire_path) < 2:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                code="EMPTY_PATH",
                message="Wire path is empty or has insufficient points"
            ))
            return result
        
        # Run all validation checks
        self._validate_path_length(wire_path, result)
        self._validate_bend_radii(wire_path, result)
        self._validate_segment_lengths(wire_path, result)
        self._validate_smoothness(wire_path, result)
        self._validate_height_consistency(wire_path, result)
        self._validate_endpoint_positions(wire_path, result)
        
        if bracket_positions is not None:
            self._validate_bracket_proximity(wire_path, bracket_positions, result)
        
        # Calculate overall metrics
        result.metrics = self._calculate_metrics(wire_path)
        
        # Generate recommendations
        result.recommendations = self._generate_recommendations(result)
        
        return result
    
    def _validate_path_length(
        self,
        wire_path: np.ndarray,
        result: ValidationResult
    ):
        """Validate total path length."""
        lengths = np.linalg.norm(np.diff(wire_path, axis=0), axis=1)
        total_length = np.sum(lengths)
        
        if total_length < self.thresholds['min_path_length_mm']:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="PATH_TOO_SHORT",
                message=f"Path length {total_length:.1f}mm is below minimum {self.thresholds['min_path_length_mm']}mm",
                value=total_length,
                threshold=self.thresholds['min_path_length_mm']
            ))
        
        if total_length > self.thresholds['max_path_length_mm']:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="PATH_TOO_LONG",
                message=f"Path length {total_length:.1f}mm exceeds maximum {self.thresholds['max_path_length_mm']}mm",
                value=total_length,
                threshold=self.thresholds['max_path_length_mm']
            ))
    
    def _validate_bend_radii(
        self,
        wire_path: np.ndarray,
        result: ValidationResult
    ):
        """Validate bend radii throughout path."""
        min_radius = self.thresholds['min_bend_radius_mm']
        violations = []
        consecutive_sharp = 0
        
        for i in range(1, len(wire_path) - 1):
            radius = self._calculate_bend_radius(
                wire_path[i-1], wire_path[i], wire_path[i+1]
            )
            
            if radius < min_radius:
                violations.append((i, radius))
                consecutive_sharp += 1
                
                if consecutive_sharp > self.thresholds['max_consecutive_sharp_bends']:
                    result.add_issue(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        code="CONSECUTIVE_SHARP_BENDS",
                        message=f"Multiple consecutive sharp bends detected at index {i}",
                        location=i,
                        value=radius,
                        threshold=min_radius
                    ))
            else:
                consecutive_sharp = 0
        
        if violations:
            worst_violation = min(violations, key=lambda x: x[1])
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="BEND_RADIUS_VIOLATION",
                message=f"Bend radius {worst_violation[1]:.2f}mm below minimum {min_radius}mm at {len(violations)} locations",
                location=worst_violation[0],
                value=worst_violation[1],
                threshold=min_radius
            ))
    
    def _validate_segment_lengths(
        self,
        wire_path: np.ndarray,
        result: ValidationResult
    ):
        """Validate individual segment lengths."""
        lengths = np.linalg.norm(np.diff(wire_path, axis=0), axis=1)
        
        # Check for too-short segments
        short_segments = np.where(lengths < self.thresholds['min_segment_length_mm'])[0]
        if len(short_segments) > 0:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="SHORT_SEGMENTS",
                message=f"{len(short_segments)} segments shorter than {self.thresholds['min_segment_length_mm']}mm",
                value=float(np.min(lengths)),
                threshold=self.thresholds['min_segment_length_mm']
            ))
        
        # Check for too-long segments
        long_segments = np.where(lengths > self.thresholds['max_segment_length_mm'])[0]
        if len(long_segments) > 0:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.INFO,
                code="LONG_SEGMENTS",
                message=f"{len(long_segments)} segments longer than {self.thresholds['max_segment_length_mm']}mm",
                value=float(np.max(lengths)),
                threshold=self.thresholds['max_segment_length_mm']
            ))
    
    def _validate_smoothness(
        self,
        wire_path: np.ndarray,
        result: ValidationResult
    ):
        """Validate path smoothness using curvature analysis."""
        curvatures = []
        
        for i in range(1, len(wire_path) - 1):
            radius = self._calculate_bend_radius(
                wire_path[i-1], wire_path[i], wire_path[i+1]
            )
            if radius > 0 and radius < float('inf'):
                curvatures.append(1.0 / radius)
            else:
                curvatures.append(0.0)
        
        if len(curvatures) > 1:
            # Calculate curvature change rate
            curvature_changes = np.abs(np.diff(curvatures))
            max_change = np.max(curvature_changes)
            
            if max_change > self.thresholds['smoothness_threshold']:
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="SMOOTHNESS_ISSUE",
                    message=f"Curvature changes abruptly (max change: {max_change:.3f})",
                    value=max_change,
                    threshold=self.thresholds['smoothness_threshold']
                ))
    
    def _validate_height_consistency(
        self,
        wire_path: np.ndarray,
        result: ValidationResult
    ):
        """Validate height (Z) consistency."""
        heights = wire_path[:, 2]
        height_range = np.max(heights) - np.min(heights)
        
        if height_range > self.thresholds['max_height_variation_mm']:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="HEIGHT_VARIATION",
                message=f"Height varies by {height_range:.2f}mm (max allowed: {self.thresholds['max_height_variation_mm']}mm)",
                value=height_range,
                threshold=self.thresholds['max_height_variation_mm']
            ))
    
    def _validate_endpoint_positions(
        self,
        wire_path: np.ndarray,
        result: ValidationResult
    ):
        """Validate endpoint positions are reasonable."""
        start = wire_path[0]
        end = wire_path[-1]
        
        # Check if endpoints are at similar heights
        height_diff = abs(start[2] - end[2])
        if height_diff > 2.0:
            result.add_issue(ValidationIssue(
                severity=ValidationSeverity.INFO,
                code="ENDPOINT_HEIGHT_MISMATCH",
                message=f"Endpoint heights differ by {height_diff:.2f}mm",
                value=height_diff
            ))
    
    def _validate_bracket_proximity(
        self,
        wire_path: np.ndarray,
        bracket_positions: np.ndarray,
        result: ValidationResult
    ):
        """Validate wire passes near all brackets."""
        max_allowed_distance = 3.0  # mm
        
        for i, bracket in enumerate(bracket_positions):
            # Find minimum distance from wire to bracket
            distances = np.linalg.norm(wire_path - bracket, axis=1)
            min_distance = np.min(distances)
            
            if min_distance > max_allowed_distance:
                result.add_issue(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="BRACKET_DISTANCE",
                    message=f"Wire is {min_distance:.2f}mm from bracket {i} (max: {max_allowed_distance}mm)",
                    location=i,
                    value=min_distance,
                    threshold=max_allowed_distance
                ))
    
    def _calculate_bend_radius(
        self,
        p1: np.ndarray,
        p2: np.ndarray,
        p3: np.ndarray
    ) -> float:
        """Calculate bend radius using Menger curvature."""
        v1 = p2 - p1
        v2 = p3 - p2
        
        v1_norm = np.linalg.norm(v1)
        v2_norm = np.linalg.norm(v2)
        
        if v1_norm < 1e-6 or v2_norm < 1e-6:
            return float('inf')
        
        cross = np.cross(v1, v2)
        cross_norm = np.linalg.norm(cross)
        
        if cross_norm < 1e-6:
            return float('inf')
        
        area = cross_norm / 2
        chord = np.linalg.norm(p3 - p1)
        
        if chord < 1e-6:
            return float('inf')
        
        return (v1_norm * v2_norm * chord) / (4 * area)
    
    def _calculate_metrics(self, wire_path: np.ndarray) -> Dict:
        """Calculate comprehensive path metrics."""
        lengths = np.linalg.norm(np.diff(wire_path, axis=0), axis=1)
        
        # Curvature statistics
        curvatures = []
        bend_radii = []
        
        for i in range(1, len(wire_path) - 1):
            radius = self._calculate_bend_radius(
                wire_path[i-1], wire_path[i], wire_path[i+1]
            )
            if radius < float('inf'):
                bend_radii.append(radius)
                curvatures.append(1.0 / radius if radius > 0 else 0)
        
        return {
            'total_length_mm': float(np.sum(lengths)),
            'point_count': len(wire_path),
            'segment_count': len(lengths),
            'min_segment_length_mm': float(np.min(lengths)),
            'max_segment_length_mm': float(np.max(lengths)),
            'avg_segment_length_mm': float(np.mean(lengths)),
            'min_bend_radius_mm': float(min(bend_radii)) if bend_radii else float('inf'),
            'max_curvature': float(max(curvatures)) if curvatures else 0,
            'avg_curvature': float(np.mean(curvatures)) if curvatures else 0,
            'height_range_mm': float(np.max(wire_path[:, 2]) - np.min(wire_path[:, 2])),
            'width_mm': float(np.max(wire_path[:, 0]) - np.min(wire_path[:, 0])),
            'depth_mm': float(np.max(wire_path[:, 1]) - np.min(wire_path[:, 1]))
        }
    
    def _generate_recommendations(self, result: ValidationResult) -> List[str]:
        """Generate improvement recommendations based on issues."""
        recommendations = []
        
        issue_codes = [issue.code for issue in result.issues]
        
        if "BEND_RADIUS_VIOLATION" in issue_codes:
            recommendations.append(
                f"Increase smoothing or use a material with lower minimum bend radius "
                f"(current: {self.material.min_bend_radius_mm}mm)"
            )
        
        if "SMOOTHNESS_ISSUE" in issue_codes:
            recommendations.append(
                "Apply additional smoothing passes or use curvature-flow smoothing"
            )
        
        if "SHORT_SEGMENTS" in issue_codes:
            recommendations.append(
                "Reduce path resolution or increase minimum segment length threshold"
            )
        
        if "HEIGHT_VARIATION" in issue_codes:
            recommendations.append(
                "Check bracket height consistency or apply height normalization"
            )
        
        if "BRACKET_DISTANCE" in issue_codes:
            recommendations.append(
                "Adjust wire path to pass closer to bracket positions"
            )
        
        if result.overall_score >= 90:
            recommendations.append("Wire path meets professional quality standards")
        elif result.overall_score >= 70:
            recommendations.append("Wire path is acceptable but could be improved")
        else:
            recommendations.append("Wire path requires significant improvements before clinical use")
        
        return recommendations


def validate_wire_for_manufacturing(
    wire_path: np.ndarray,
    material_name: str = "niti_superelastic",
    wire_size: str = "0.016"
) -> ValidationResult:
    """
    Convenience function to validate wire path for manufacturing.
    
    Args:
        wire_path: Wire path to validate
        material_name: Material identifier
        wire_size: Wire size
        
    Returns:
        Validation result
    """
    from wire.professional_materials import STANDARD_WIRE_SIZES
    
    material = get_material(material_name)
    diameter = STANDARD_WIRE_SIZES.get(wire_size, {}).get('diameter_mm', 0.4064)
    
    validator = ClinicalValidator(material, diameter)
    return validator.validate_wire_path(wire_path)
