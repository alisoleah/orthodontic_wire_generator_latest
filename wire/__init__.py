
# ================================================================
# wire/__init__.py
"""
Wire generation modules.

This package contains the core wire generation components:
- Main coordinator class
- Drawing algorithm (mathematical path generation)
- 3D mesh builder (visual rendering)
- Height control system
"""

from .wire_generator import WireGenerator
from .wire_path_creator import WirePathCreator
from .wire_mesh_builder import WireMeshBuilder
from .height_controller import HeightController

__all__ = [
    'WireGenerator',
    'WirePathCreator',
    'WireMeshBuilder', 
    'HeightController'
]

__version__ = "1.0.0"
# Init