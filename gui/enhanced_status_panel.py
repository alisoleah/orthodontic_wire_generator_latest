"""
Enhanced Status Panel for the Hybrid Orthodontic Wire Generator.

This module provides a PyQt5-based status panel that displays comprehensive
information about the current workflow, wire properties, and exported code.
"""

import numpy as np
from typing import Dict, Any

try:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QGroupBox, QLabel, QFrame
except ImportError:
    # This check is for environments where PyQt5 might not be installed.
    # The main application handles the fallback.
    class QWidget: pass
    PYQT5_AVAILABLE = False
else:
    PYQT5_AVAILABLE = True


class EnhancedStatusPanel(QWidget if PYQT5_AVAILABLE else object):
    """Enhanced status panel with comprehensive information display and code viewer."""

    def __init__(self, parent=None):
        if PYQT5_AVAILABLE:
            super().__init__(parent)
            self.init_ui()

    def init_ui(self):
        """Initialize status panel UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Status & Information")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title)

        # Workflow status
        workflow_group = QFrame()
        workflow_group.setFrameStyle(QFrame.StyledPanel)
        workflow_layout = QVBoxLayout()

        self.mode_status = QLabel("Mode: Automatic")
        self.active_arch_status = QLabel("Active Arch: Upper")
        self.arches_loaded_status = QLabel("Arches Loaded: 0/2")

        workflow_layout.addWidget(self.mode_status)
        workflow_layout.addWidget(self.active_arch_status)
        workflow_layout.addWidget(self.arches_loaded_status)

        workflow_group.setLayout(workflow_layout)
        layout.addWidget(workflow_group)

        # Wire information
        wire_group = QFrame()
        wire_group.setFrameStyle(QFrame.StyledPanel)
        wire_layout = QVBoxLayout()

        wire_title = QLabel("Wire Information")
        wire_title.setStyleSheet("font-weight: bold;")
        wire_layout.addWidget(wire_title)

        self.wire_length_status = QLabel("Length: Not calculated")
        self.control_points_status = QLabel("Control Points: 0")
        self.height_offset_status = QLabel("Height Offset: 0.0 mm")

        wire_layout.addWidget(self.wire_length_status)
        wire_layout.addWidget(self.control_points_status)
        wire_layout.addWidget(self.height_offset_status)

        wire_group.setLayout(wire_layout)
        layout.addWidget(wire_group)

        # Exported Code Viewer
        export_group = QGroupBox("Exported Code Viewer")
        export_layout = QVBoxLayout()
        self.code_viewer = QTextEdit()
        self.code_viewer.setReadOnly(True)
        self.code_viewer.setFontFamily("Courier")
        self.code_viewer.setLineWrapMode(QTextEdit.NoWrap)
        export_layout.addWidget(self.code_viewer)
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        # Add stretch to push content to top
        layout.addStretch()

        self.setLayout(layout)

    def update_workflow_mode(self, mode: str):
        """Update workflow mode display"""
        if PYQT5_AVAILABLE:
            self.mode_status.setText(f"Mode: {mode.capitalize()}")

    def update_active_arch(self, arch_type: str):
        """Update active arch display"""
        if PYQT5_AVAILABLE:
            self.active_arch_status.setText(f"Active Arch: {arch_type.capitalize()}")

    def update_arch_info(self, arch_type: str, file_path: str):
        """Update arch loading information"""
        # This can be expanded to show file names or other details.
        pass

    def update_wire_info(self, wire_path):
        """Update wire information"""
        if PYQT5_AVAILABLE and wire_path is not None:
            length = self.calculate_wire_length(wire_path)
            self.wire_length_status.setText(f"Length: {length:.2f} mm")

    def update_workflow_status(self, status: Dict[str, Any]):
        """Update comprehensive workflow status"""
        if PYQT5_AVAILABLE:
            upper_loaded = 1 if status.get('upper_loaded', False) else 0
            lower_loaded = 1 if status.get('lower_loaded', False) else 0
            total_loaded = upper_loaded + lower_loaded
            self.arches_loaded_status.setText(f"Arches Loaded: {total_loaded}/2")

            height_offset = status.get('height_offset', 0.0)
            self.height_offset_status.setText(f"Height Offset: {height_offset:.1f} mm")

    def calculate_wire_length(self, wire_path) -> float:
        """Calculate total wire length"""
        if len(wire_path) < 2:
            return 0.0

        return np.sum(np.linalg.norm(np.diff(wire_path, axis=0), axis=1))

    def reset_display(self):
        """Reset all status displays"""
        if PYQT5_AVAILABLE:
            self.wire_length_status.setText("Length: Not calculated")
            self.control_points_status.setText("Control Points: 0")
            self.height_offset_status.setText("Height Offset: 0.0 mm")
            self.arches_loaded_status.setText("Arches Loaded: 0/2")
            if hasattr(self, 'code_viewer'):
                self.code_viewer.clear()

    def display_exported_code(self, code: str):
        """Display the given code in the code viewer text edit."""
        if PYQT5_AVAILABLE and hasattr(self, 'code_viewer'):
            self.code_viewer.setText(code)