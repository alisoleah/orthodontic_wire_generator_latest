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

Note: Modules are not auto-imported to prevent circular dependencies and
      to support a more modular, app-driven architecture.
"""

__all__ = [
    'constants',
    'mesh_processor',
    'tooth_detector',
    'bracket_positioner',
    'workflow_manager'
]

__version__ = "1.1.0"