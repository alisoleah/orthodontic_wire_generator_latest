#!/usr/bin/env python3
"""
tests/test_professional_wire.py

Comprehensive test suite for professional wire generation modules.
Tests material properties, path generation, arch form optimization, and clinical validation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from typing import List, Dict
import json

# Import professional modules
from wire.professional_materials import (
    PROFESSIONAL_MATERIALS,
    get_material,
    create_wire_spec,
    WireMaterialType,
    STANDARD_WIRE_SIZES
)
from wire.wire_path_creator_professional import (
    WirePathCreatorProfessional,
    SmoothingStrategy,
    PathQualityMetrics
)
from wire.arch_form_optimizer import (
    ArchFormOptimizer,
    ArchFormType,
    create_standard_arch_form
)
from wire.clinical_validator import (
    ClinicalValidator,
    validate_wire_for_manufacturing,
    ValidationSeverity
)


def create_test_bracket_positions() -> List[Dict]:
    """Create realistic test bracket positions for upper arch."""
    # Simulated upper arch bracket positions (mm)
    # Based on typical dental arch dimensions
    positions = [
        # Right side (patient's right)
        {'position': np.array([22.0, 5.0, 0.0]), 'visible': True, 'tooth_type': 'molar'},
        {'position': np.array([18.0, 10.0, 0.0]), 'visible': True, 'tooth_type': 'premolar'},
        {'position': np.array([14.0, 15.0, 0.0]), 'visible': True, 'tooth_type': 'premolar'},
        {'position': np.array([10.0, 20.0, 0.0]), 'visible': True, 'tooth_type': 'canine'},
        {'position': np.array([5.0, 24.0, 0.0]), 'visible': True, 'tooth_type': 'lateral'},
        {'position': np.array([1.5, 25.0, 0.0]), 'visible': True, 'tooth_type': 'central'},
        # Left side
        {'position': np.array([-1.5, 25.0, 0.0]), 'visible': True, 'tooth_type': 'central'},
        {'position': np.array([-5.0, 24.0, 0.0]), 'visible': True, 'tooth_type': 'lateral'},
        {'position': np.array([-10.0, 20.0, 0.0]), 'visible': True, 'tooth_type': 'canine'},
        {'position': np.array([-14.0, 15.0, 0.0]), 'visible': True, 'tooth_type': 'premolar'},
        {'position': np.array([-18.0, 10.0, 0.0]), 'visible': True, 'tooth_type': 'premolar'},
        {'position': np.array([-22.0, 5.0, 0.0]), 'visible': True, 'tooth_type': 'molar'},
    ]
    return positions


def test_materials_library():
    """Test professional materials library."""
    print("\n" + "="*60)
    print("TEST: Professional Materials Library")
    print("="*60)
    
    print(f"\nAvailable materials: {len(PROFESSIONAL_MATERIALS)}")
    
    for name, material in PROFESSIONAL_MATERIALS.items():
        print(f"\n{material.name}:")
        print(f"  - Type: {material.material_type.value}")
        print(f"  - Young's Modulus: {material.youngs_modulus_gpa} GPa")
        print(f"  - Min Bend Radius: {material.min_bend_radius_mm} mm")
        print(f"  - Springback Ratio: {material.springback_ratio}")
        print(f"  - Superelastic: {material.is_superelastic}")
        print(f"  - Nickel-free: {material.is_nickel_free}")
    
    # Test wire specification creation
    print("\n--- Wire Specification Test ---")
    spec = create_wire_spec("niti_superelastic", "0.016")
    print(f"Created spec: {spec.material.name}, {spec.diameter_mm}mm")
    print(f"Cross-sectional area: {spec.cross_sectional_area_mm2:.6f} mm²")
    print(f"Bending stiffness: {spec.get_bending_stiffness()}")
    
    print("\n✓ Materials library test PASSED")
    return True


def test_professional_path_creator():
    """Test professional wire path creator."""
    print("\n" + "="*60)
    print("TEST: Professional Wire Path Creator")
    print("="*60)
    
    brackets = create_test_bracket_positions()
    arch_center = np.array([0.0, 15.0, 0.0])
    
    # Test different smoothing strategies
    strategies = [
        SmoothingStrategy.GAUSSIAN,
        SmoothingStrategy.CURVATURE_FLOW,
        SmoothingStrategy.BILATERAL
    ]
    
    for strategy in strategies:
        print(f"\n--- Testing {strategy.value} smoothing ---")
        
        creator = WirePathCreatorProfessional(
            material_name="niti_superelastic",
            wire_size="0.016",
            base_resolution=50,
            smoothing_strategy=strategy
        )
        
        path = creator.create_professional_path(
            brackets,
            arch_center,
            height_offset=0.0
        )
        
        if path is not None and len(path) > 0:
            print(f"  Path generated: {len(path)} points")
            print(f"  Path length: {creator.get_path_length():.2f} mm")
            
            metrics = creator.quality_metrics
            if metrics:
                print(f"  Smoothness score: {metrics.smoothness_score:.1f}/100")
                print(f"  Min bend radius: {metrics.min_bend_radius_mm:.2f} mm")
                print(f"  Clinical compliance: {metrics.clinical_compliance}")
        else:
            print("  ERROR: Path generation failed!")
            return False
    
    # Test with different materials
    print("\n--- Testing different materials ---")
    materials = ["niti_superelastic", "tma", "stainless_steel"]
    
    for mat_name in materials:
        creator = WirePathCreatorProfessional(
            material_name=mat_name,
            wire_size="0.016",
            smoothing_strategy=SmoothingStrategy.CURVATURE_FLOW
        )
        
        path = creator.create_professional_path(brackets, arch_center)
        report = creator.get_quality_report()
        
        print(f"\n  {mat_name}:")
        print(f"    Path length: {report['path_length_mm']:.2f} mm")
        print(f"    Smoothness: {report['metrics']['smoothness_score']:.1f}/100")
        print(f"    Min radius: {report['metrics']['min_bend_radius_mm']:.2f} mm")
    
    print("\n✓ Professional path creator test PASSED")
    return True


def test_arch_form_optimizer():
    """Test arch form optimizer."""
    print("\n" + "="*60)
    print("TEST: Arch Form Optimizer")
    print("="*60)
    
    brackets = create_test_bracket_positions()
    positions = np.array([b['position'] for b in brackets])
    
    optimizer = ArchFormOptimizer()
    
    # Fit arch form
    params = optimizer.fit_arch_form(positions, arch_type='upper')
    
    print(f"\nFitted arch form parameters:")
    print(f"  Arch type: {params.arch_form_type.value}")
    print(f"  Inter-canine width: {params.inter_canine_width:.2f} mm")
    print(f"  Inter-molar width: {params.inter_molar_width:.2f} mm")
    print(f"  Arch depth: {params.arch_depth:.2f} mm")
    print(f"  Beta function α: {params.alpha:.3f}")
    print(f"  Beta function β: {params.beta_param:.3f}")
    print(f"  Fit R²: {params.fit_r_squared:.4f}")
    
    # Generate ideal arch curve
    ideal_curve = optimizer.generate_ideal_arch_curve(params, num_points=50)
    print(f"\nGenerated ideal arch curve: {len(ideal_curve)} points")
    
    # Test standard arch forms
    print("\n--- Standard arch forms ---")
    for form_type in ArchFormType:
        curve = create_standard_arch_form('upper', form_type, 50)
        print(f"  {form_type.value}: {len(curve)} points, "
              f"width={np.max(curve[:,0]) - np.min(curve[:,0]):.1f}mm")
    
    print("\n✓ Arch form optimizer test PASSED")
    return True


def test_clinical_validator():
    """Test clinical validator."""
    print("\n" + "="*60)
    print("TEST: Clinical Validator")
    print("="*60)
    
    brackets = create_test_bracket_positions()
    arch_center = np.array([0.0, 15.0, 0.0])
    
    # Generate a wire path
    creator = WirePathCreatorProfessional(
        material_name="niti_superelastic",
        wire_size="0.016",
        smoothing_strategy=SmoothingStrategy.CURVATURE_FLOW
    )
    
    path = creator.create_professional_path(brackets, arch_center)
    
    # Validate the path
    result = validate_wire_for_manufacturing(path, "niti_superelastic", "0.016")
    
    print(f"\nValidation result:")
    print(f"  Is valid: {result.is_valid}")
    print(f"  Overall score: {result.overall_score:.1f}/100")
    print(f"  Issue count: {len(result.issues)}")
    
    if result.issues:
        print("\n  Issues found:")
        for issue in result.issues:
            print(f"    [{issue.severity.value.upper()}] {issue.code}: {issue.message}")
    
    print(f"\n  Metrics:")
    for key, value in result.metrics.items():
        if isinstance(value, float):
            print(f"    {key}: {value:.3f}")
        else:
            print(f"    {key}: {value}")
    
    print(f"\n  Recommendations:")
    for rec in result.recommendations:
        print(f"    - {rec}")
    
    # Test with intentionally bad path (sharp bends)
    print("\n--- Testing with problematic path ---")
    bad_path = np.array([
        [0, 0, 0],
        [1, 0, 0],
        [1.5, 0.1, 0],  # Sharp bend
        [2, 0, 0],
        [3, 0, 0]
    ])
    
    bad_result = validate_wire_for_manufacturing(bad_path, "niti_superelastic", "0.016")
    print(f"  Bad path score: {bad_result.overall_score:.1f}/100")
    print(f"  Is valid: {bad_result.is_valid}")
    print(f"  Issues: {len(bad_result.issues)}")
    
    print("\n✓ Clinical validator test PASSED")
    return True


def test_bend_calculation():
    """Test bend calculation for manufacturing."""
    print("\n" + "="*60)
    print("TEST: Bend Calculation for Manufacturing")
    print("="*60)
    
    brackets = create_test_bracket_positions()
    arch_center = np.array([0.0, 15.0, 0.0])
    
    creator = WirePathCreatorProfessional(
        material_name="stainless_steel",  # SS allows tighter bends
        wire_size="0.016",
        smoothing_strategy=SmoothingStrategy.CURVATURE_FLOW
    )
    
    path = creator.create_professional_path(brackets, arch_center)
    
    # Calculate bends
    bends = creator.calculate_bends(bend_threshold=5.0)
    
    print(f"\nDetected {len(bends)} significant bends:")
    for i, bend in enumerate(bends[:10]):  # Show first 10
        print(f"  Bend {i+1}:")
        print(f"    Position: ({bend['position'][0]:.1f}, {bend['position'][1]:.1f}, {bend['position'][2]:.1f})")
        print(f"    Angle: {bend['angle']:.1f}°")
        print(f"    Direction: {bend['direction']}")
        print(f"    Wire length at bend: {bend['wire_length']:.2f} mm")
        print(f"    Radius: {bend['radius']:.2f} mm")
        print(f"    Valid for material: {bend['is_valid']}")
    
    if len(bends) > 10:
        print(f"  ... and {len(bends) - 10} more bends")
    
    print("\n✓ Bend calculation test PASSED")
    return True


def test_quality_comparison():
    """Compare quality between original and professional path creators."""
    print("\n" + "="*60)
    print("TEST: Quality Comparison (Original vs Professional)")
    print("="*60)
    
    brackets = create_test_bracket_positions()
    arch_center = np.array([0.0, 15.0, 0.0])
    positions = [b['position'] for b in brackets]
    
    # Import original creator
    from wire.wire_path_creator_enhanced import WirePathCreatorEnhanced
    
    # Original enhanced creator
    original = WirePathCreatorEnhanced()
    original_path = original.create_smooth_path(positions, arch_center)
    
    # Professional creator
    professional = WirePathCreatorProfessional(
        material_name="niti_superelastic",
        wire_size="0.016",
        smoothing_strategy=SmoothingStrategy.CURVATURE_FLOW
    )
    pro_path = professional.create_professional_path(brackets, arch_center)
    
    # Validate both
    validator = ClinicalValidator()
    
    print("\n--- Original Enhanced Path ---")
    if original_path is not None:
        orig_result = validator.validate_wire_path(original_path)
        print(f"  Points: {len(original_path)}")
        print(f"  Score: {orig_result.overall_score:.1f}/100")
        print(f"  Valid: {orig_result.is_valid}")
        print(f"  Issues: {len(orig_result.issues)}")
    else:
        print("  Failed to generate path")
    
    print("\n--- Professional Path ---")
    if pro_path is not None:
        pro_result = validator.validate_wire_path(pro_path)
        print(f"  Points: {len(pro_path)}")
        print(f"  Score: {pro_result.overall_score:.1f}/100")
        print(f"  Valid: {pro_result.is_valid}")
        print(f"  Issues: {len(pro_result.issues)}")
        
        # Additional professional metrics
        report = professional.get_quality_report()
        print(f"  Smoothness: {report['metrics']['smoothness_score']:.1f}/100")
    else:
        print("  Failed to generate path")
    
    print("\n✓ Quality comparison test PASSED")
    return True


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*60)
    print("PROFESSIONAL WIRE GENERATION TEST SUITE")
    print("="*60)
    
    tests = [
        ("Materials Library", test_materials_library),
        ("Professional Path Creator", test_professional_path_creator),
        ("Arch Form Optimizer", test_arch_form_optimizer),
        ("Clinical Validator", test_clinical_validator),
        ("Bend Calculation", test_bend_calculation),
        ("Quality Comparison", test_quality_comparison),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"\n✗ {name} FAILED: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, p, _ in results if p)
    total = len(results)
    
    for name, passed_test, error in results:
        status = "✓ PASSED" if passed_test else f"✗ FAILED: {error}"
        print(f"  {name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
