#!/usr/bin/env python3
# ================================================================
# core/__init__.py
"""
Core processing modules for the orthodontic wire generator.

This package contains fundamental components for:
- STL mesh loading and preprocessing
- Tooth detection and classification 
- Bracket positioning algorithms
- Wire specifications and constants
"""

from .constants import WIRE_SIZES, BRACKET_HEIGHTS, CLINICAL_OFFSETS
from .mesh_processor import MeshProcessor
from .tooth_detector import ToothDetector
from .bracket_positioner import BracketPositioner

__all__ = [
    'WIRE_SIZES',
    'BRACKET_HEIGHTS', 
    'CLINICAL_OFFSETS',
    'MeshProcessor',
    'ToothDetector',
    'BracketPositioner'
]

__version__ = "1.0.0"


