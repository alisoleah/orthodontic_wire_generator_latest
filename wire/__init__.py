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

Usage
-----
The `WirePathCreator` and `WirePathCreatorEnhanced` classes can be used to generate
a wire path from a series of 3D points (e.g., bracket positions or manual control points).

Example:
    from wire import WirePathCreatorEnhanced

    control_points = [...]  # List of 3D points
    wire_creator = WirePathCreatorEnhanced()
    wire_path = wire_creator.create_smooth_path(control_points)
"""

# Export the main classes for easy access from other modules
from .wire_path_creator import WirePathCreator
from .wire_path_creator_enhanced import WirePathCreatorEnhanced

__all__ = [
    'WirePathCreator',
    'WirePathCreatorEnhanced'
]