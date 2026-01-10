#!/usr/bin/env python3
"""
wire/professional_materials.py

Professional Orthodontic Wire Materials Library
===============================================
Clinically-accurate material properties based on ISO 15841 and ANSI/ADA 32 standards.
Includes NiTi (superelastic and conventional), TMA (Beta-Titanium), and Stainless Steel.

References:
- ISO 15841:2014 - Dentistry — Wires for use in orthodontics
- ANSI/ADA Standard No. 32 - Orthodontic Wires
- Bellini et al. (2016) - J Mater Sci Mater Med, PMC5021743
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Tuple
import numpy as np


class WireMaterialType(Enum):
    """Enumeration of orthodontic wire material types."""
    NITI_SUPERELASTIC = "niti_superelastic"
    NITI_CONVENTIONAL = "niti_conventional"
    NITI_THERMALLY_ACTIVATED = "niti_thermal"
    TMA_BETA_TITANIUM = "tma"
    STAINLESS_STEEL = "stainless_steel"
    STAINLESS_STEEL_BRAIDED = "ss_braided"


class WireCrossSection(Enum):
    """Wire cross-section types."""
    ROUND = "round"
    RECTANGULAR = "rectangular"
    SQUARE = "square"


@dataclass(frozen=True)
class WireMaterialProperties:
    """
    Immutable dataclass containing clinically-validated wire material properties.
    
    All values are based on published research and ISO/ADA standards.
    """
    name: str
    material_type: WireMaterialType
    
    # Mechanical properties
    youngs_modulus_gpa: float  # Elastic modulus in GPa
    yield_strength_mpa: float  # Yield strength in MPa
    ultimate_tensile_strength_mpa: float  # UTS in MPa
    density_g_cm3: float  # Density in g/cm³
    
    # Clinical properties
    min_bend_radius_mm: float  # Minimum bend radius without permanent deformation
    springback_ratio: float  # Ratio of elastic recovery (0-1)
    formability: float  # Ease of bending (0-1, higher = easier)
    
    # Superelastic properties (for NiTi)
    is_superelastic: bool = False
    austenite_finish_temp_c: Optional[float] = None  # Af temperature
    plateau_force_n_per_mm: Optional[float] = None  # Force at superelastic plateau
    
    # Thermal properties
    is_thermally_activated: bool = False
    activation_temp_c: Optional[float] = None
    
    # Biocompatibility
    nickel_content_percent: float = 0.0
    is_nickel_free: bool = True
    
    # Manufacturing constraints
    max_bend_angle_degrees: float = 90.0
    min_segment_length_mm: float = 1.0
    
    def get_moment_of_inertia(self, diameter_mm: float) -> float:
        """Calculate moment of inertia for round wire."""
        radius = diameter_mm / 2.0
        return (np.pi * radius**4) / 4.0
    
    def get_bending_stiffness(self, diameter_mm: float) -> float:
        """Calculate bending stiffness EI in N·mm²."""
        e_n_mm2 = self.youngs_modulus_gpa * 1e6  # Convert GPa to N/mm²
        i_mm4 = self.get_moment_of_inertia(diameter_mm)
        return e_n_mm2 * i_mm4
    
    def calculate_force_at_deflection(self, 
                                       deflection_mm: float,
                                       span_mm: float = 10.0,
                                       diameter_mm: float = 0.4064) -> float:
        """
        Calculate force at given deflection using three-point bending formula.
        Based on ISO 15841 test method.
        
        Args:
            deflection_mm: Wire deflection in mm
            span_mm: Support span in mm (ISO standard = 10mm)
            diameter_mm: Wire diameter in mm
            
        Returns:
            Force in Newtons
        """
        ei = self.get_bending_stiffness(diameter_mm)
        
        if self.is_superelastic and deflection_mm > 1.0:
            # Superelastic plateau behavior
            base_force = (48 * ei * 1.0) / (span_mm**3)
            plateau_addition = (deflection_mm - 1.0) * (self.plateau_force_n_per_mm or 0.15)
            return base_force + plateau_addition
        else:
            # Linear elastic behavior
            return (48 * ei * deflection_mm) / (span_mm**3)


# ============================================================================
# Professional Materials Library
# ============================================================================

PROFESSIONAL_MATERIALS: Dict[str, WireMaterialProperties] = {
    # NiTi Superelastic (e.g., Damon Optimal Force, Sentalloy)
    "niti_superelastic": WireMaterialProperties(
        name="NiTi Superelastic",
        material_type=WireMaterialType.NITI_SUPERELASTIC,
        youngs_modulus_gpa=41.0,  # Austenite phase
        yield_strength_mpa=1400.0,
        ultimate_tensile_strength_mpa=1900.0,
        density_g_cm3=6.45,
        min_bend_radius_mm=2.0,
        springback_ratio=0.95,
        formability=0.3,  # Difficult to form permanently
        is_superelastic=True,
        austenite_finish_temp_c=27.0,
        plateau_force_n_per_mm=0.15,
        nickel_content_percent=55.0,
        is_nickel_free=False,
        max_bend_angle_degrees=45.0,
        min_segment_length_mm=2.0
    ),
    
    # NiTi Conventional (e.g., Nitinol Classic)
    "niti_conventional": WireMaterialProperties(
        name="NiTi Conventional",
        material_type=WireMaterialType.NITI_CONVENTIONAL,
        youngs_modulus_gpa=34.0,
        yield_strength_mpa=1100.0,
        ultimate_tensile_strength_mpa=1500.0,
        density_g_cm3=6.45,
        min_bend_radius_mm=2.5,
        springback_ratio=0.85,
        formability=0.4,
        is_superelastic=False,
        nickel_content_percent=55.0,
        is_nickel_free=False,
        max_bend_angle_degrees=60.0,
        min_segment_length_mm=1.5
    ),
    
    # NiTi Thermally Activated (e.g., Copper NiTi)
    "niti_thermal": WireMaterialProperties(
        name="NiTi Thermally Activated",
        material_type=WireMaterialType.NITI_THERMALLY_ACTIVATED,
        youngs_modulus_gpa=35.0,
        yield_strength_mpa=1200.0,
        ultimate_tensile_strength_mpa=1600.0,
        density_g_cm3=6.50,
        min_bend_radius_mm=2.0,
        springback_ratio=0.92,
        formability=0.35,
        is_superelastic=True,
        is_thermally_activated=True,
        austenite_finish_temp_c=35.0,
        activation_temp_c=35.0,
        plateau_force_n_per_mm=0.12,
        nickel_content_percent=52.0,
        is_nickel_free=False,
        max_bend_angle_degrees=45.0,
        min_segment_length_mm=2.0
    ),
    
    # TMA (Beta-Titanium) - e.g., TMA from Ormco
    "tma": WireMaterialProperties(
        name="TMA (Beta-Titanium)",
        material_type=WireMaterialType.TMA_BETA_TITANIUM,
        youngs_modulus_gpa=69.0,
        yield_strength_mpa=1000.0,
        ultimate_tensile_strength_mpa=1200.0,
        density_g_cm3=4.85,
        min_bend_radius_mm=1.5,
        springback_ratio=0.75,
        formability=0.7,  # Good formability
        is_superelastic=False,
        nickel_content_percent=0.0,
        is_nickel_free=True,
        max_bend_angle_degrees=90.0,
        min_segment_length_mm=1.0
    ),
    
    # Stainless Steel - Standard
    "stainless_steel": WireMaterialProperties(
        name="Stainless Steel",
        material_type=WireMaterialType.STAINLESS_STEEL,
        youngs_modulus_gpa=180.0,
        yield_strength_mpa=1500.0,
        ultimate_tensile_strength_mpa=2000.0,
        density_g_cm3=7.95,
        min_bend_radius_mm=1.0,
        springback_ratio=0.65,
        formability=0.85,  # Excellent formability
        is_superelastic=False,
        nickel_content_percent=8.0,
        is_nickel_free=False,
        max_bend_angle_degrees=90.0,
        min_segment_length_mm=0.5
    ),
    
    # Stainless Steel Braided
    "ss_braided": WireMaterialProperties(
        name="Stainless Steel Braided",
        material_type=WireMaterialType.STAINLESS_STEEL_BRAIDED,
        youngs_modulus_gpa=160.0,  # Lower due to braiding
        yield_strength_mpa=1200.0,
        ultimate_tensile_strength_mpa=1600.0,
        density_g_cm3=7.80,
        min_bend_radius_mm=1.5,
        springback_ratio=0.70,
        formability=0.80,
        is_superelastic=False,
        nickel_content_percent=8.0,
        is_nickel_free=False,
        max_bend_angle_degrees=75.0,
        min_segment_length_mm=1.0
    )
}


@dataclass
class WireSpecification:
    """
    Complete wire specification including material and dimensions.
    """
    material: WireMaterialProperties
    cross_section: WireCrossSection
    diameter_mm: float  # For round wire
    width_mm: Optional[float] = None  # For rectangular wire
    height_mm: Optional[float] = None  # For rectangular wire
    
    def __post_init__(self):
        """Validate wire specification."""
        if self.cross_section == WireCrossSection.RECTANGULAR:
            if self.width_mm is None or self.height_mm is None:
                raise ValueError("Rectangular wire requires width and height")
    
    @property
    def cross_sectional_area_mm2(self) -> float:
        """Calculate cross-sectional area."""
        if self.cross_section == WireCrossSection.ROUND:
            return np.pi * (self.diameter_mm / 2)**2
        elif self.cross_section == WireCrossSection.RECTANGULAR:
            return self.width_mm * self.height_mm
        elif self.cross_section == WireCrossSection.SQUARE:
            return self.diameter_mm**2
        return 0.0
    
    @property
    def moment_of_inertia_mm4(self) -> Tuple[float, float]:
        """
        Calculate moment of inertia (Ix, Iy).
        For round wire, Ix = Iy.
        """
        if self.cross_section == WireCrossSection.ROUND:
            i = (np.pi * (self.diameter_mm / 2)**4) / 4
            return (i, i)
        elif self.cross_section == WireCrossSection.RECTANGULAR:
            ix = (self.width_mm * self.height_mm**3) / 12
            iy = (self.height_mm * self.width_mm**3) / 12
            return (ix, iy)
        return (0.0, 0.0)
    
    def get_bending_stiffness(self) -> Tuple[float, float]:
        """Get bending stiffness EI in both directions (N·mm²)."""
        e = self.material.youngs_modulus_gpa * 1e6  # N/mm²
        ix, iy = self.moment_of_inertia_mm4
        return (e * ix, e * iy)


# ============================================================================
# Standard Wire Sizes (inches to mm conversion)
# ============================================================================

STANDARD_WIRE_SIZES: Dict[str, Dict] = {
    # Round wires
    "0.012": {"type": WireCrossSection.ROUND, "diameter_mm": 0.3048},
    "0.014": {"type": WireCrossSection.ROUND, "diameter_mm": 0.3556},
    "0.016": {"type": WireCrossSection.ROUND, "diameter_mm": 0.4064},
    "0.018": {"type": WireCrossSection.ROUND, "diameter_mm": 0.4572},
    "0.020": {"type": WireCrossSection.ROUND, "diameter_mm": 0.5080},
    
    # Rectangular wires
    "0.016x0.022": {
        "type": WireCrossSection.RECTANGULAR,
        "diameter_mm": 0.4064,
        "width_mm": 0.4064,
        "height_mm": 0.5588
    },
    "0.017x0.025": {
        "type": WireCrossSection.RECTANGULAR,
        "diameter_mm": 0.4318,
        "width_mm": 0.4318,
        "height_mm": 0.6350
    },
    "0.018x0.025": {
        "type": WireCrossSection.RECTANGULAR,
        "diameter_mm": 0.4572,
        "width_mm": 0.4572,
        "height_mm": 0.6350
    },
    "0.019x0.025": {
        "type": WireCrossSection.RECTANGULAR,
        "diameter_mm": 0.4826,
        "width_mm": 0.4826,
        "height_mm": 0.6350
    },
    "0.021x0.025": {
        "type": WireCrossSection.RECTANGULAR,
        "diameter_mm": 0.5334,
        "width_mm": 0.5334,
        "height_mm": 0.6350
    }
}


def get_material(material_name: str) -> WireMaterialProperties:
    """
    Get material properties by name.
    
    Args:
        material_name: Material identifier (e.g., 'niti_superelastic', 'tma')
        
    Returns:
        WireMaterialProperties for the specified material
        
    Raises:
        KeyError: If material not found
    """
    if material_name.lower() not in PROFESSIONAL_MATERIALS:
        available = ", ".join(PROFESSIONAL_MATERIALS.keys())
        raise KeyError(f"Unknown material '{material_name}'. Available: {available}")
    return PROFESSIONAL_MATERIALS[material_name.lower()]


def create_wire_spec(material_name: str, wire_size: str) -> WireSpecification:
    """
    Create a complete wire specification from material and size.
    
    Args:
        material_name: Material identifier
        wire_size: Standard wire size (e.g., '0.016', '0.018x0.025')
        
    Returns:
        Complete WireSpecification
    """
    material = get_material(material_name)
    
    if wire_size not in STANDARD_WIRE_SIZES:
        available = ", ".join(STANDARD_WIRE_SIZES.keys())
        raise KeyError(f"Unknown wire size '{wire_size}'. Available: {available}")
    
    size_spec = STANDARD_WIRE_SIZES[wire_size]
    
    return WireSpecification(
        material=material,
        cross_section=size_spec["type"],
        diameter_mm=size_spec["diameter_mm"],
        width_mm=size_spec.get("width_mm"),
        height_mm=size_spec.get("height_mm")
    )


# ============================================================================
# Clinical Force Guidelines
# ============================================================================

@dataclass(frozen=True)
class ClinicalForceGuidelines:
    """
    Optimal force ranges for different tooth movements.
    Based on clinical research and orthodontic literature.
    """
    # Forces in Newtons (N)
    INTRUSION_INCISORS: Tuple[float, float] = (0.10, 0.25)
    INTRUSION_MOLARS: Tuple[float, float] = (0.50, 1.00)
    EXTRUSION: Tuple[float, float] = (0.35, 0.60)
    TIPPING: Tuple[float, float] = (0.35, 0.60)
    BODILY_MOVEMENT: Tuple[float, float] = (0.70, 1.20)
    ROOT_TORQUE: Tuple[float, float] = (0.50, 1.00)
    ROTATION: Tuple[float, float] = (0.35, 0.60)
    
    # Optimal force for initial alignment
    ALIGNMENT_LIGHT: Tuple[float, float] = (0.25, 0.50)
    ALIGNMENT_MEDIUM: Tuple[float, float] = (0.50, 1.00)
    ALIGNMENT_HEAVY: Tuple[float, float] = (1.00, 2.00)


CLINICAL_FORCE_GUIDELINES = ClinicalForceGuidelines()
