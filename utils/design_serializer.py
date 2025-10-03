
# ================================================================
# utils/design_serializer.py
"""Design serialization and deserialization for save/load functionality."""

import json
import numpy as np
import time
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

class DesignSerializer:
    """Handles saving and loading of complete wire designs."""
    
    def __init__(self):
        """Initialize design serializer."""
        self.current_version = "3.0.0"
        self.supported_versions = ["1.0.0", "2.0.0", "3.0.0"]
        
    def serialize_design(self, generator, filename: Optional[str] = None) -> str:
        """
        Serialize a complete wire design to JSON format.
        
        Args:
            generator: WireGenerator instance with generated data
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"wire_design_{generator.arch_type}_{timestamp}.json"
        
        # Collect all design data
        design_data = {
            'metadata': self._create_metadata(generator),
            'mesh_info': self._serialize_mesh_info(generator),
            'teeth': self._serialize_teeth(generator.teeth),
            'brackets': self._serialize_brackets(generator.bracket_positions),
            'control_points': self._serialize_control_points(generator.wire_path_creator.control_points),
            'wire_path': self._serialize_wire_path(generator.wire_path),
            'height_settings': self._serialize_height_settings(generator),
            'generation_settings': self._serialize_generation_settings(generator),
            'calculated_data': self._serialize_calculated_data(generator),
            'export_settings': self._serialize_export_settings(generator)
        }
        
        # Save to file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(design_data, f, indent=2, default=self._json_serializer)
            
            print(f"Design serialized successfully: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error serializing design: {e}")
            raise
    
    def deserialize_design(self, filename: str) -> Dict[str, Any]:
        """
        Deserialize a wire design from JSON format.
        
        Args:
            filename: Path to JSON design file
            
        Returns:
            Dictionary containing design data
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                design_data = json.load(f)
            
            # Check version compatibility
            version = design_data.get('metadata', {}).get('version', '1.0.0')
            if version not in self.supported_versions:
                print(f"Warning: Design version {version} may not be fully compatible")
            
            # Convert arrays back to numpy
            design_data = self._deserialize_arrays(design_data)
            
            print(f"Design deserialized successfully: {filename}")
            return design_data
            
        except Exception as e:
            print(f"Error deserializing design: {e}")
            raise
    
    def _create_metadata(self, generator) -> Dict[str, Any]:
        """Create metadata for the design."""
        return {
            'version': self.current_version,
            'arch_type': generator.arch_type,
            'wire_size': generator.wire_size,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'stl_file': os.path.basename(generator.stl_path),
            'generator_type': 'modular_architecture',
            'serializer_version': self.current_version
        }
    
    def _serialize_mesh_info(self, generator) -> Dict[str, Any]:
        """Serialize mesh information."""
        if generator.mesh is None:
            return {}
        
        stats = generator.mesh_processor.get_mesh_statistics(generator.mesh)
        return {
            'vertex_count': stats.get('vertex_count', 0),
            'triangle_count': stats.get('triangle_count', 0),
            'bounding_box': stats.get('bounding_box', {}),
            'surface_area': stats.get('surface_area', 0.0),
            'volume': stats.get('volume', 0.0),
            'arch_center': generator.arch_center.tolist() if generator.arch_center is not None else None
        }
    
    def _serialize_teeth(self, teeth: List[Dict]) -> List[Dict]:
        """Serialize teeth data."""
        serialized_teeth = []
        for tooth in teeth:
            serialized_tooth = {
                'center': tooth['center'].tolist(),
                'angle': tooth['angle'],
                'ap_position': tooth['ap_position'],
                'lr_position': tooth['lr_position'],
                'index': tooth['index'],
                'type': tooth['type'],
                'vertex_count': len(tooth['vertices'])
            }
            serialized_teeth.append(serialized_tooth)
        return serialized_teeth
    
    def _serialize_brackets(self, brackets: List[Dict]) -> List[Dict]:
        """Serialize bracket positions."""
        serialized_brackets = []
        for bracket in brackets:
            serialized_bracket = {
                'position': bracket['position'].tolist(),
                'original_position': bracket['original_position'].tolist(),
                'tooth_type': bracket['tooth_type'],
                'tooth_index': bracket['tooth_index'],
                'tooth_center': bracket['tooth_center'].tolist(),
                'normal': bracket['normal'].tolist(),
                'height': bracket['height'],
                'surface': bracket['surface'],
                'visible': bracket['visible']
            }
            serialized_brackets.append(serialized_bracket)
        return serialized_brackets
    
    def _serialize_control_points(self, control_points: List[Dict]) -> List[Dict]:
        """Serialize control points."""
        serialized_cps = []
        for cp in control_points:
            serialized_cp = {
                'position': cp['position'].tolist(),
                'original_position': cp['original_position'].tolist(),
                'type': cp['type'],
                'index': cp['index'],
                'bend_angle': cp['bend_angle'],
                'vertical_offset': cp['vertical_offset']
            }
            serialized_cps.append(serialized_cp)
        return serialized_cps
    
    def _serialize_wire_path(self, wire_path) -> List[List[float]]:
        """Serialize wire path."""
        if wire_path is None:
            return []
        return wire_path.tolist()
    
    def _serialize_height_settings(self, generator) -> Dict[str, Any]:
        """Serialize height control settings."""
        return {
            'current_offset': generator.height_controller.get_height_offset(),
            'step_size': generator.height_controller.get_step_size(),
            'history': generator.height_controller.get_history()
        }
    
    def _serialize_generation_settings(self, generator) -> Dict[str, Any]:
        """Serialize generation parameters."""
        return {
            'bend_radius': generator.wire_path_creator.bend_radius,
            'wire_tension': generator.wire_path_creator.wire_tension,
            'path_resolution': generator.wire_path_creator.path_resolution,
            'smoothing_factor': generator.wire_path_creator.smoothing_factor,
            'minimum_segment_length': generator.wire_path_creator.minimum_segment_length,
            'wire_radius': generator.wire_mesh_builder.wire_radius,
            'mesh_resolution': generator.wire_mesh_builder.mesh_resolution
        }
    
    def _serialize_calculated_data(self, generator) -> Dict[str, Any]:
        """Serialize calculated results."""
        bends = generator.wire_path_creator.calculate_bends()
        wire_length = generator.wire_path_creator.get_path_length()
        
        return {
            'wire_length': wire_length,
            'bend_count': len(bends),
            'bends': [
                {
                    'position': bend['position'].tolist(),
                    'angle': bend['angle'],
                    'direction': bend['direction'],
                    'wire_length': bend['wire_length'],
                    'radius': bend['radius']
                }
                for bend in bends
            ]
        }
    
    def _serialize_export_settings(self, generator) -> Dict[str, Any]:
        """Serialize export settings."""
        return {
            'gcode_settings': generator.gcode_generator.settings if hasattr(generator, 'gcode_generator') else {},
            'esp32_settings': generator.esp32_generator.default_settings if hasattr(generator, 'esp32_generator') else {},
            'stl_settings': generator.stl_exporter.export_settings if hasattr(generator, 'stl_exporter') else {}
        }
    
    def _deserialize_arrays(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert list data back to numpy arrays where appropriate."""
        # Convert wire path
        if 'wire_path' in data and data['wire_path']:
            data['wire_path'] = np.array(data['wire_path'])
        
        # Convert teeth centers
        if 'teeth' in data:
            for tooth in data['teeth']:
                if 'center' in tooth:
                    tooth['center'] = np.array(tooth['center'])
        
        # Convert bracket positions
        if 'brackets' in data:
            for bracket in data['brackets']:
                for key in ['position', 'original_position', 'tooth_center', 'normal']:
                    if key in bracket:
                        bracket[key] = np.array(bracket[key])
        
        # Convert control points
        if 'control_points' in data:
            for cp in data['control_points']:
                for key in ['position', 'original_position']:
                    if key in cp:
                        cp[key] = np.array(cp[key])
        
        # Convert bend positions
        if 'calculated_data' in data and 'bends' in data['calculated_data']:
            for bend in data['calculated_data']['bends']:
                if 'position' in bend:
                    bend['position'] = np.array(bend['position'])
        
        return data
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for numpy arrays and other objects."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif hasattr(obj, 'tolist'):
            return obj.tolist()
        else:
            return str(obj)
    
    def create_design_summary(self, design_data: Dict[str, Any]) -> str:
        """Create a human-readable summary of the design."""
        metadata = design_data.get('metadata', {})
        calculated = design_data.get('calculated_data', {})
        height = design_data.get('height_settings', {})
        
        summary = f"""
Design Summary
==============
File: {metadata.get('stl_file', 'Unknown')}
Version: {metadata.get('version', 'Unknown')}
Created: {metadata.get('timestamp', 'Unknown')}

Wire Specifications:
- Arch Type: {metadata.get('arch_type', 'Unknown').upper()}
- Wire Size: {metadata.get('wire_size', 'Unknown')}
- Length: {calculated.get('wire_length', 0):.1f}mm
- Height Offset: {height.get('current_offset', 0):.2f}mm

Teeth & Brackets:
- Teeth Detected: {len(design_data.get('teeth', []))}
- Brackets Positioned: {len(design_data.get('brackets', []))}
- Control Points: {len(design_data.get('control_points', []))}

Manufacturing:
- Bends Required: {calculated.get('bend_count', 0)}
- Wire Path Points: {len(design_data.get('wire_path', []))}

Architecture: Modular Design with Separated Drawing Components
"""
        return summary.strip()



