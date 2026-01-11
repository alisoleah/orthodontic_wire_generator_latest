"""
Enhanced Status Panel V2 for Orthodontic Wire Generator

Modern status panel with InfoCards, collapsible sections, and real-time metrics
"""

import numpy as np
from typing import Dict, Any, Optional

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
    )
    from PyQt5.QtCore import Qt
    PYQT5_AVAILABLE = True
except ImportError:
    class QWidget: pass
    PYQT5_AVAILABLE = False

from gui.widgets.collapsible_section import CollapsibleSection
from gui.widgets.info_card import InfoCard


class EnhancedStatusPanelV2(QWidget if PYQT5_AVAILABLE else object):
    """
    Modern status panel with real-time wire statistics and quality metrics
    """
    
    def __init__(self, parent=None):
        if PYQT5_AVAILABLE:
            super().__init__(parent)
            self.init_ui()
            
    def init_ui(self):
        """Initialize the modern status panel UI"""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        main_layout.addWidget(scroll)
        
        # Content widget
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        
        # Content layout
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        content_widget.setLayout(layout)
        
        # ============================================
        # SECTION 1: WIRE STATISTICS (Always visible)
        # ============================================
        stats_section = CollapsibleSection("WIRE STATISTICS", section_number=1)
        
        # Wire Length Card
        self.length_card = InfoCard("Wire Length", "0.0 mm", "📏", color="blue")
        stats_section.add_widget(self.length_card)
        
        # Control Points Card
        self.points_card = InfoCard("Control Points", "0", "⚓", color="purple")
        stats_section.add_widget(self.points_card)
        
        # Generation Time Card
        self.time_card = InfoCard("Generation Time", "0.0s", "⏱️", color="orange")
        stats_section.add_widget(self.time_card)
        
        layout.addWidget(stats_section)
        
        # ============================================
        # SECTION 2: DETECTION INFO
        # ============================================
        detection_section = CollapsibleSection("DETECTION INFO", section_number=2)
        
        # Teeth Detected Card
        self.teeth_card = InfoCard("Teeth Detected", "0/14", "🦷", color="blue")
        detection_section.add_widget(self.teeth_card)
        
        # Confidence Score Card
        self.confidence_card = InfoCard("Confidence", "0%", "✓", color="purple")
        detection_section.add_widget(self.confidence_card)
        
        # Missing Teeth Card
        self.missing_card = InfoCard("Missing Teeth", "0", "⚠️", color="orange")
        detection_section.add_widget(self.missing_card)
        
        layout.addWidget(detection_section)
        
        # ============================================
        # SECTION 3: QUALITY METRICS
        # ============================================
        quality_section = CollapsibleSection("QUALITY METRICS", section_number=3)
        
        # Smoothness Score
        self.smoothness_card = InfoCard("Smoothness", "0%", "〰️", color="blue")
        quality_section.add_widget(self.smoothness_card)
        
        # Curvature Analysis
        self.curvature_card = InfoCard("Max Curvature", "0.0 mm⁻¹", "↻", color="purple")
        quality_section.add_widget(self.curvature_card)
        
        # Clinical Acceptability
        self.clinical_card = InfoCard("Clinical Status", "Not Tested", "✓", color="orange")
        quality_section.add_widget(self.clinical_card)
        
        layout.addWidget(quality_section)
        
        # ============================================
        # SECTION 4: WORKFLOW STATUS
        # ============================================
        workflow_section = CollapsibleSection("WORKFLOW STATUS", section_number=4)
        
        # Mode
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet("font-weight: 600; color: #2d3748;")
        self.mode_value = QLabel("Automatic")
        self.mode_value.setStyleSheet("color: #718096;")
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_value)
        mode_layout.addStretch()
        workflow_section.add_layout(mode_layout)
        
        # Active Arch
        arch_layout = QHBoxLayout()
        arch_label = QLabel("Active Arch:")
        arch_label.setStyleSheet("font-weight: 600; color: #2d3748;")
        self.arch_value = QLabel("Upper")
        self.arch_value.setStyleSheet("color: #718096;")
        arch_layout.addWidget(arch_label)
        arch_layout.addWidget(self.arch_value)
        arch_layout.addStretch()
        workflow_section.add_layout(arch_layout)
        
        # Arches Loaded
        loaded_layout = QHBoxLayout()
        loaded_label = QLabel("Arches Loaded:")
        loaded_label.setStyleSheet("font-weight: 600; color: #2d3748;")
        self.loaded_value = QLabel("0/2")
        self.loaded_value.setStyleSheet("color: #718096;")
        loaded_layout.addWidget(loaded_label)
        loaded_layout.addWidget(self.loaded_value)
        loaded_layout.addStretch()
        workflow_section.add_layout(loaded_layout)
        
        layout.addWidget(workflow_section)
        
        # ============================================
        # SECTION 5: EXPORTED CODE VIEWER
        # ============================================
        export_section = CollapsibleSection("EXPORTED CODE", section_number=5)
        
        from PyQt5.QtWidgets import QTextEdit
        self.code_viewer = QTextEdit()
        self.code_viewer.setReadOnly(True)
        self.code_viewer.setFontFamily("Courier")
        self.code_viewer.setLineWrapMode(QTextEdit.NoWrap)
        self.code_viewer.setMinimumHeight(200)
        self.code_viewer.setPlaceholderText("G-Code or ESP32 code will appear here after export...")
        export_section.add_widget(self.code_viewer)
        
        layout.addWidget(export_section)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
    # ============================================
    # UPDATE METHODS
    # ============================================
    
    def update_arch_info(self, arch_type: str, file_path: str):
        """Update arch loading information (compatibility method)"""
        # This method is called by main window when arch is loaded
        # We can use it to update workflow status
        pass
    
    def display_exported_code(self, code: str):
        """Display the given code in the code viewer"""
        if hasattr(self, 'code_viewer'):
            self.code_viewer.setText(code)
        
    # ============================================
    # UPDATE METHODS
    # ============================================
    
    def update_wire_info(self, wire_path: Optional[np.ndarray], generation_time: float = 0.0):
        """Update wire statistics"""
        if wire_path is not None and len(wire_path) > 0:
            # Calculate length
            length = self.calculate_wire_length(wire_path)
            self.length_card.set_value(f"{length:.2f} mm")
            
            # Update points
            self.points_card.set_value(str(len(wire_path)))
            
            # Update time
            self.time_card.set_value(f"{generation_time:.2f}s")
            
            # Calculate smoothness
            smoothness = self.calculate_smoothness(wire_path)
            self.smoothness_card.set_value(f"{smoothness:.0f}%")
            
            # Calculate curvature
            max_curvature = self.calculate_max_curvature(wire_path)
            self.curvature_card.set_value(f"{max_curvature:.3f} mm⁻¹")
        else:
            self.reset_wire_stats()
    
    def update_detection_info(self, teeth_detected: int, total_teeth: int = 14, 
                             confidence: float = 0.0, missing_teeth: int = 0):
        """Update detection information"""
        self.teeth_card.set_value(f"{teeth_detected}/{total_teeth}")
        self.confidence_card.set_value(f"{confidence:.0f}%")
        self.missing_card.set_value(str(missing_teeth))
    
    def update_workflow_mode(self, mode: str):
        """Update workflow mode display"""
        self.mode_value.setText(mode.capitalize())
    
    def update_active_arch(self, arch_type: str):
        """Update active arch display"""
        self.arch_value.setText(arch_type.capitalize())
    
    def update_workflow_status(self, status: Dict[str, Any]):
        """Update comprehensive workflow status"""
        upper_loaded = 1 if status.get('upper_loaded', False) else 0
        lower_loaded = 1 if status.get('lower_loaded', False) else 0
        total_loaded = upper_loaded + lower_loaded
        self.loaded_value.setText(f"{total_loaded}/2")
    
    def update_clinical_status(self, acceptable: bool, rms_deviation: float = 0.0):
        """Update clinical acceptability status"""
        if acceptable:
            self.clinical_card.set_value("✓ PASS")
            self.clinical_card.label.setStyleSheet("color: #48bb78; font-weight: 600;")
        else:
            self.clinical_card.set_value(f"✗ FAIL ({rms_deviation:.2f}mm)")
            self.clinical_card.label.setStyleSheet("color: #dc3545; font-weight: 600;")
    
    # ============================================
    # CALCULATION METHODS
    # ============================================
    
    def calculate_wire_length(self, wire_path: np.ndarray) -> float:
        """Calculate total wire length in mm"""
        if len(wire_path) < 2:
            return 0.0
        return float(np.sum(np.linalg.norm(np.diff(wire_path, axis=0), axis=1)))
    
    def calculate_smoothness(self, wire_path: np.ndarray) -> float:
        """
        Calculate smoothness score (0-100%)
        Based on curvature variation - lower variation = smoother
        """
        if len(wire_path) < 3:
            return 0.0
        
        # Calculate second derivatives (acceleration)
        second_deriv = np.diff(wire_path, n=2, axis=0)
        acceleration = np.linalg.norm(second_deriv, axis=1)
        
        # Smoothness is inverse of acceleration variance
        # Normalize to 0-100 scale
        variance = np.var(acceleration)
        smoothness = 100.0 / (1.0 + variance * 10)  # Scale factor for reasonable range
        
        return min(100.0, max(0.0, smoothness))
    
    def calculate_max_curvature(self, wire_path: np.ndarray) -> float:
        """
        Calculate maximum curvature along the wire path
        Curvature = |dT/ds| where T is unit tangent vector
        """
        if len(wire_path) < 3:
            return 0.0
        
        # Calculate tangent vectors
        tangents = np.diff(wire_path, axis=0)
        tangent_lengths = np.linalg.norm(tangents, axis=1, keepdims=True)
        tangent_lengths[tangent_lengths == 0] = 1.0  # Avoid division by zero
        unit_tangents = tangents / tangent_lengths
        
        # Calculate change in tangent direction
        dtangent = np.diff(unit_tangents, axis=0)
        ds = tangent_lengths[:-1].flatten()
        ds[ds == 0] = 1.0  # Avoid division by zero
        
        # Curvature magnitude
        curvatures = np.linalg.norm(dtangent, axis=1) / ds
        
        return float(np.max(curvatures)) if len(curvatures) > 0 else 0.0
    
    def reset_wire_stats(self):
        """Reset wire statistics to default values"""
        self.length_card.set_value("0.0 mm")
        self.points_card.set_value("0")
        self.time_card.set_value("0.0s")
        self.smoothness_card.set_value("0%")
        self.curvature_card.set_value("0.0 mm⁻¹")
    
    def reset_detection_stats(self):
        """Reset detection statistics"""
        self.teeth_card.set_value("0/14")
        self.confidence_card.set_value("0%")
        self.missing_card.set_value("0")
    
    def reset_display(self):
        """Reset all displays"""
        self.reset_wire_stats()
        self.reset_detection_stats()
        self.clinical_card.set_value("Not Tested")
        self.loaded_value.setText("0/2")
