#!/usr/bin/env python3
"""
core/fa_point.py

FAPoint - Facial Axis Point Data Structure
==========================================
Represents a clinically significant Facial Axis (FA) point on a tooth's clinical crown.
This is used for the new FIXR-inspired upper tooth surface adaptation algorithm.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class FAPoint:
    """
    Represents a Facial Axis (FA) point on a tooth's clinical crown.
    
    The FA point is the clinically relevant landmark used for orthodontic
    wire design, located on the buccal (cheek-facing) surface of each tooth.
    """
    tooth_number: int
    position: np.ndarray
    normal: np.ndarray
    is_upper: bool
    tooth_type: str = "unknown"  # 'incisor', 'canine', 'premolar', 'molar'
    confidence: float = 1.0  # Detection confidence (0.0 to 1.0)
    
    def __post_init__(self):
        """Ensure arrays are numpy arrays."""
        if not isinstance(self.position, np.ndarray):
            self.position = np.array(self.position)
        if not isinstance(self.normal, np.ndarray):
            self.normal = np.array(self.normal)
    
    def to_dict(self) -> dict:
        """Convert to dictionary format for compatibility."""
        return {
            'tooth_number': self.tooth_number,
            'position': self.position,
            'normal': self.normal,
            'is_upper': self.is_upper,
            'tooth_type': self.tooth_type,
            'confidence': self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FAPoint':
        """Create FAPoint from dictionary."""
        return cls(
            tooth_number=data['tooth_number'],
            position=np.array(data['position']),
            normal=np.array(data['normal']),
            is_upper=data['is_upper'],
            tooth_type=data.get('tooth_type', 'unknown'),
            confidence=data.get('confidence', 1.0)
        )
    
    def distance_to(self, other: 'FAPoint') -> float:
        """Calculate distance to another FA point."""
        return np.linalg.norm(self.position - other.position)
    
    def get_surface_point(self, offset: float = 0.0) -> np.ndarray:
        """
        Get a point on the tooth surface with optional offset.
        
        Args:
            offset: Distance to offset from surface along normal (positive = outward)
        
        Returns:
            3D point on or offset from the tooth surface
        """
        return self.position + (self.normal * offset)
