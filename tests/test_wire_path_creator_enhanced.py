#!/usr/bin/env python3
"""
Unit tests for enhanced wire path creator.
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wire.wire_path_creator_enhanced import (
    WirePathCreatorEnhanced,
    ControlPoint,
    BracketPosition,
    WireMaterial,
    PathGenerationStrategy,
    Point3D,
    CubicSplineGenerator,
    BSplineGenerator,
    CatmullRomGenerator
)


class TestPoint3D:
    """Test Point3D dataclass."""

    def test_creation(self):
        point = Point3D(x=1.0, y=2.0, z=3.0)
        assert point.x == 1.0
        assert point.y == 2.0
        assert point.z == 3.0

    def test_to_array(self):
        point = Point3D(x=1.0, y=2.0, z=3.0)
        arr = point.to_array()
        assert np.array_equal(arr, np.array([1.0, 2.0, 3.0]))

    def test_from_array(self):
        arr = np.array([1.0, 2.0, 3.0])
        point = Point3D.from_array(arr)
        assert point.x == 1.0
        assert point.y == 2.0
        assert point.z == 3.0


class TestControlPoint:
    """Test ControlPoint dataclass."""

    def test_creation(self):
        cp = ControlPoint(
            position=np.array([0, 0, 0]),
            type='bracket',
            index=0,
            original_position=np.array([0, 0, 0])
        )
        assert cp.type == 'bracket'
        assert cp.index == 0
        assert cp.weight == 1.0
        assert not cp.locked

    def test_with_custom_weight(self):
        cp = ControlPoint(
            position=np.array([0, 0, 0]),
            type='intermediate',
            index=1,
            original_position=np.array([0, 0, 0]),
            weight=0.5
        )
        assert cp.weight == 0.5


class TestWireMaterial:
    """Test WireMaterial dataclass."""

    def test_niti_material(self):
        niti = WireMaterial(
            name="NiTi",
            youngs_modulus=83,
            yield_strength=1400,
            density=6.45,
            min_bend_radius=2.0,
            is_superelastic=True
        )
        assert niti.name == "NiTi"
        assert niti.is_superelastic

    def test_stainless_steel_material(self):
        ss = WireMaterial(
            name="Stainless Steel",
            youngs_modulus=200,
            yield_strength=800,
            density=7.9,
            min_bend_radius=3.0,
            is_superelastic=False
        )
        assert ss.name == "Stainless Steel"
        assert not ss.is_superelastic


class TestPathGenerators:
    """Test different path generation strategies."""

    @pytest.fixture
    def simple_control_points(self):
        """Create simple control points for testing."""
        return [
            ControlPoint(
                position=np.array([0.0, 0.0, 0.0]),
                type='bracket',
                index=0,
                original_position=np.array([0.0, 0.0, 0.0])
            ),
            ControlPoint(
                position=np.array([5.0, 0.0, 0.0]),
                type='bracket',
                index=1,
                original_position=np.array([5.0, 0.0, 0.0])
            ),
            ControlPoint(
                position=np.array([10.0, 5.0, 0.0]),
                type='bracket',
                index=2,
                original_position=np.array([10.0, 5.0, 0.0])
            ),
            ControlPoint(
                position=np.array([15.0, 0.0, 0.0]),
                type='bracket',
                index=3,
                original_position=np.array([15.0, 0.0, 0.0])
            )
        ]

    def test_cubic_spline_generator(self, simple_control_points):
        generator = CubicSplineGenerator(smoothing_factor=0.1)
        path = generator.generate_path(simple_control_points, resolution=10)

        assert len(path) > 0
        assert path.shape[1] == 3  # 3D points
        # Path should start near first control point
        assert np.linalg.norm(path[0] - simple_control_points[0].position) < 1.0

    def test_bspline_generator(self, simple_control_points):
        generator = BSplineGenerator(degree=3)
        path = generator.generate_path(simple_control_points, resolution=10)

        assert len(path) > 0
        assert path.shape[1] == 3

    def test_catmull_rom_generator(self, simple_control_points):
        generator = CatmullRomGenerator(alpha=0.5)
        path = generator.generate_path(simple_control_points, resolution=10)

        assert len(path) > 0
        assert path.shape[1] == 3


class TestWirePathCreatorEnhanced:
    """Test enhanced wire path creator."""

    @pytest.fixture
    def creator(self):
        """Create wire path creator instance."""
        return WirePathCreatorEnhanced(
            bend_radius=2.0,
            wire_tension=1.0,
            strategy=PathGenerationStrategy.CATMULL_ROM
        )

    @pytest.fixture
    def sample_brackets(self):
        """Create sample bracket positions."""
        return [
            {'position': np.array([10.0, 0.0, 5.0]), 'visible': True, 'tooth_type': 'incisor'},
            {'position': np.array([5.0, 8.0, 5.0]), 'visible': True, 'tooth_type': 'canine'},
            {'position': np.array([-5.0, 8.0, 5.0]), 'visible': True, 'tooth_type': 'canine'},
            {'position': np.array([-10.0, 0.0, 5.0]), 'visible': True, 'tooth_type': 'incisor'}
        ]

    def test_creation(self, creator):
        assert creator.bend_radius == 2.0
        assert creator.wire_tension == 1.0
        assert creator.strategy == PathGenerationStrategy.CATMULL_ROM

    def test_create_smooth_path(self, creator, sample_brackets):
        arch_center = np.array([0.0, 4.0, 0.0])
        path = creator.create_smooth_path(sample_brackets, arch_center, height_offset=0.0)

        assert path is not None
        assert len(path) > 0
        assert path.shape[1] == 3

    def test_path_length_calculation(self, creator, sample_brackets):
        arch_center = np.array([0.0, 4.0, 0.0])
        creator.create_smooth_path(sample_brackets, arch_center)

        length = creator.get_path_length()
        assert length > 0
        # Path should be reasonably long
        assert length > 20  # mm

    def test_adaptive_resolution(self, creator):
        # Straight line - should have low resolution
        straight_cp = [
            ControlPoint(np.array([0, 0, 0]), 'bracket', 0, np.array([0, 0, 0])),
            ControlPoint(np.array([10, 0, 0]), 'bracket', 1, np.array([10, 0, 0]))
        ]
        creator.control_points = straight_cp
        res_straight = creator._calculate_adaptive_resolution()

        # Curved line - should have higher resolution
        curved_cp = [
            ControlPoint(np.array([0, 0, 0]), 'bracket', 0, np.array([0, 0, 0])),
            ControlPoint(np.array([5, 5, 0]), 'bracket', 1, np.array([5, 5, 0])),
            ControlPoint(np.array([10, 0, 0]), 'bracket', 2, np.array([10, 0, 0]))
        ]
        creator.control_points = curved_cp
        res_curved = creator._calculate_adaptive_resolution()

        assert res_curved >= res_straight

    def test_minimum_bend_radius_enforcement(self, creator, sample_brackets):
        arch_center = np.array([0.0, 4.0, 0.0])
        creator.create_smooth_path(sample_brackets, arch_center)

        bends = creator.calculate_bends_enhanced(bend_threshold=1.0)

        # All bends should meet minimum radius requirement
        for bend in bends:
            if bend.is_valid:
                assert bend.radius >= creator.material.min_bend_radius

    def test_bend_calculation(self, creator, sample_brackets):
        arch_center = np.array([0.0, 4.0, 0.0])
        creator.create_smooth_path(sample_brackets, arch_center)

        bends = creator.calculate_bends_enhanced(bend_threshold=5.0)

        assert isinstance(bends, list)
        # Should have some bends for this arch
        assert len(bends) > 0

        for bend in bends:
            assert hasattr(bend, 'angle')
            assert hasattr(bend, 'radius')
            assert hasattr(bend, 'is_valid')
            assert hasattr(bend, 'stress_concentration')

    def test_path_statistics(self, creator, sample_brackets):
        arch_center = np.array([0.0, 4.0, 0.0])
        creator.create_smooth_path(sample_brackets, arch_center)

        stats = creator.get_path_statistics()

        assert stats['valid'] == True
        assert stats['length'] > 0
        assert stats['num_points'] > 0
        assert stats['num_control_points'] > 0
        assert 'strategy' in stats
        assert 'material' in stats

    def test_different_strategies(self, sample_brackets):
        arch_center = np.array([0.0, 4.0, 0.0])

        strategies = [
            PathGenerationStrategy.CUBIC_SPLINE,
            PathGenerationStrategy.BSPLINE,
            PathGenerationStrategy.CATMULL_ROM
        ]

        for strategy in strategies:
            creator = WirePathCreatorEnhanced(strategy=strategy)
            path = creator.create_smooth_path(sample_brackets, arch_center)

            assert path is not None
            assert len(path) > 0

    def test_height_offset(self, creator, sample_brackets):
        arch_center = np.array([0.0, 4.0, 0.0])
        height_offset = 2.0

        path = creator.create_smooth_path(sample_brackets, arch_center, height_offset)

        # Average Z coordinate should be offset
        avg_z = np.mean(path[:, 2])
        assert avg_z > 5.0  # Original ~5.0 + offset 2.0

    def test_wire_tension_effect(self, sample_brackets):
        arch_center = np.array([0.0, 4.0, 0.0])

        # Low tension
        creator_low = WirePathCreatorEnhanced(wire_tension=0.5)
        path_low = creator_low.create_smooth_path(sample_brackets, arch_center)

        # High tension
        creator_high = WirePathCreatorEnhanced(wire_tension=2.0)
        path_high = creator_high.create_smooth_path(sample_brackets, arch_center)

        # Paths should be different
        assert not np.array_equal(path_low, path_high)

    def test_material_properties(self):
        # Create with NiTi
        niti_material = WireMaterial(
            name="NiTi",
            youngs_modulus=83,
            yield_strength=1400,
            density=6.45,
            min_bend_radius=2.0,
            is_superelastic=True
        )
        creator_niti = WirePathCreatorEnhanced(wire_material=niti_material)

        assert creator_niti.material.name == "NiTi"
        assert creator_niti.material.min_bend_radius == 2.0

        # Create with SS
        ss_material = WireMaterial(
            name="SS",
            youngs_modulus=200,
            yield_strength=800,
            density=7.9,
            min_bend_radius=3.0,
            is_superelastic=False
        )
        creator_ss = WirePathCreatorEnhanced(wire_material=ss_material)

        assert creator_ss.material.name == "SS"
        assert creator_ss.material.min_bend_radius == 3.0


class TestBendRadiusCalculation:
    """Test bend radius calculations."""

    def test_straight_line_infinite_radius(self):
        creator = WirePathCreatorEnhanced()

        p1 = np.array([0, 0, 0])
        p2 = np.array([1, 0, 0])
        p3 = np.array([2, 0, 0])

        radius = creator._calculate_bend_radius(p1, p2, p3)
        assert radius == float('inf') or radius > 1000

    def test_right_angle_bend(self):
        creator = WirePathCreatorEnhanced()

        p1 = np.array([0, 0, 0])
        p2 = np.array([1, 0, 0])
        p3 = np.array([1, 1, 0])

        radius = creator._calculate_bend_radius(p1, p2, p3)
        assert radius > 0
        assert radius < 10  # Should be relatively small for 90-degree bend


class TestStressConcentration:
    """Test stress concentration calculations."""

    def test_stress_increases_with_sharper_bend(self):
        creator = WirePathCreatorEnhanced()

        # Gentle bend
        stress_gentle = creator._calculate_stress_concentration(radius=5.0, angle=30.0)

        # Sharp bend
        stress_sharp = creator._calculate_stress_concentration(radius=2.0, angle=90.0)

        assert stress_sharp > stress_gentle


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
