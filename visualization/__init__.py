
# ================================================================
# visualization/__init__.py
"""
3D visualization and interaction modules.

This package provides:
- Interactive 3D visualization
- Control point management
- Mesh factory for creating 3D objects
"""

from .visualizer_3d import Visualizer3D
from .control_point_manager import ControlPointManager
from .mesh_factory import MeshFactory

__all__ = [
    'Visualizer3D',
    'ControlPointManager',
    'MeshFactory'
]

__version__ = "1.0.0"

