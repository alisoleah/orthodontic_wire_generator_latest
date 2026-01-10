"""
Wire Package
============

This package contains modules for creating and manipulating the orthodontic wire path.

Modules
-------
- wire_path_creator:
  Original implementation for creating a smooth wire path from bracket positions.

- wire_path_creator_enhanced:
  An enhanced version with more advanced algorithms for wire path generation,
  including better handling of complex dental arch geometries and improved smoothing.

- wire_path_creator_professional:
  Professional-grade wire path generation with G2-continuous splines,
  material-specific constraints, and clinical validation.

- professional_materials:
  Clinically-accurate wire material properties based on ISO 15841 standards.

- arch_form_optimizer:
  Beta-function based arch form fitting for anatomically accurate curves.

- clinical_validator:
  Validation against clinical orthodontic standards with detailed reports.

Usage
-----
The `WirePathCreator`, `WirePathCreatorEnhanced`, and `WirePathCreatorProfessional` 
classes can be used to generate wire paths from bracket positions.

Example:
    from wire import WirePathCreatorProfessional, SmoothingStrategy

    # Create professional wire path creator
    wire_creator = WirePathCreatorProfessional(
        material_name="niti_superelastic",
        wire_size="0.016",
        smoothing_strategy=SmoothingStrategy.CURVATURE_FLOW
    )
    
    # Generate wire path
    wire_path = wire_creator.create_professional_path(
        bracket_positions,
        arch_center,
        height_offset=0.0
    )
    
    # Get quality report
    report = wire_creator.get_quality_report()
"""

# Export the main classes for easy access from other modules
from .wire_path_creator import WirePathCreator
from .wire_path_creator_enhanced import WirePathCreatorEnhanced
try:
    from .wire_mesh_builder import WireMeshBuilder
except ImportError:
    WireMeshBuilder = None

# Professional modules
try:
    from .wire_path_creator_professional import (
        WirePathCreatorProfessional,
        SmoothingStrategy,
        ProfessionalControlPoint,
        PathQualityMetrics
    )
    from .professional_materials import (
        WireMaterialProperties,
        WireSpecification,
        WireMaterialType,
        WireCrossSection,
        PROFESSIONAL_MATERIALS,
        STANDARD_WIRE_SIZES,
        get_material,
        create_wire_spec,
        CLINICAL_FORCE_GUIDELINES
    )
    from .arch_form_optimizer import (
        ArchFormOptimizer,
        ArchFormType,
        ArchFormParameters,
        create_standard_arch_form
    )
    from .clinical_validator import (
        ClinicalValidator,
        ValidationResult,
        ValidationIssue,
        ValidationSeverity,
        validate_wire_for_manufacturing
    )
    
    _PROFESSIONAL_AVAILABLE = True
except ImportError as e:
    _PROFESSIONAL_AVAILABLE = False
    import warnings
    warnings.warn(f"Professional wire modules not available: {e}")

__all__ = [
    # Original classes
    'WirePathCreator',
    'WirePathCreatorEnhanced',
    'WireMeshBuilder',
    
    # Professional classes
    'WirePathCreatorProfessional',
    'SmoothingStrategy',
    'ProfessionalControlPoint',
    'PathQualityMetrics',
    
    # Materials
    'WireMaterialProperties',
    'WireSpecification',
    'WireMaterialType',
    'WireCrossSection',
    'PROFESSIONAL_MATERIALS',
    'STANDARD_WIRE_SIZES',
    'get_material',
    'create_wire_spec',
    'CLINICAL_FORCE_GUIDELINES',
    
    # Arch form
    'ArchFormOptimizer',
    'ArchFormType',
    'ArchFormParameters',
    'create_standard_arch_form',
    
    # Validation
    'ClinicalValidator',
    'ValidationResult',
    'ValidationIssue',
    'ValidationSeverity',
    'validate_wire_for_manufacturing'
]
