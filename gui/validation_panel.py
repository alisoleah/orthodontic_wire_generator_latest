"""
Validation Panel - UI for Clinical Wire Validation

Provides interface for:
- Loading reference wire STL
- Running validation against generated wire
- Displaying validation results
- Generating validation reports
"""

import numpy as np
from typing import Optional

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog,
        QMessageBox, QProgressDialog
    )
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    PYQT5_AVAILABLE = True
except ImportError:
    class QWidget: pass
    PYQT5_AVAILABLE = False

from gui.widgets.collapsible_section import CollapsibleSection
from gui.widgets.info_card import InfoCard
from validation.wire_extractor import WireExtractor
from validation.clinical_accuracy_validator import ClinicalAccuracyValidator


class ValidationPanel(QWidget if PYQT5_AVAILABLE else object):
    """
    Panel for clinical wire validation against reference wires.
    """
    
    def __init__(self, parent=None):
        if PYQT5_AVAILABLE:
            super().__init__(parent)
            self.reference_wire = None
            self.generated_wire = None
            self.validation_results = None
            self.init_ui()
    
    def init_ui(self):
        """Initialize the validation panel UI"""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        self.setLayout(layout)
        
        # Title
        title = QLabel("📊 CLINICAL VALIDATION")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # ============================================
        # SECTION 1: Reference Wire Loading
        # ============================================
        ref_section = CollapsibleSection("REFERENCE WIRE", section_number=1)
        
        # Load button
        self.load_ref_btn = QPushButton("📂 Load Reference Wire (.stl)")
        self.load_ref_btn.clicked.connect(self.load_reference_wire)
        ref_section.add_widget(self.load_ref_btn)
        
        # Status label
        self.ref_status = QLabel("No reference wire loaded")
        self.ref_status.setStyleSheet("color: #718096; font-style: italic;")
        ref_section.add_widget(self.ref_status)
        
        layout.addWidget(ref_section)
        
        # ============================================
        # SECTION 2: Validation Controls
        # ============================================
        control_section = CollapsibleSection("VALIDATION", section_number=2)
        
        # Run validation button
        self.validate_btn = QPushButton("▶️ Run Validation")
        self.validate_btn.clicked.connect(self.run_validation)
        self.validate_btn.setEnabled(False)
        control_section.add_widget(self.validate_btn)
        
        layout.addWidget(control_section)
        
        # ============================================
        # SECTION 3: Results Display
        # ============================================
        results_section = CollapsibleSection("RESULTS", section_number=3)
        
        # RMS Deviation Card
        self.rms_card = InfoCard("RMS Deviation", "N/A", "📏", color="blue")
        results_section.add_widget(self.rms_card)
        
        # Max Deviation Card
        self.max_card = InfoCard("Max Deviation", "N/A", "⚠️", color="purple")
        results_section.add_widget(self.max_card)
        
        # Mean Deviation Card
        self.mean_card = InfoCard("Mean Deviation", "N/A", "📊", color="orange")
        results_section.add_widget(self.mean_card)
        
        # Clinical Status
        self.status_label = QLabel("Status: Not Tested")
        self.status_label.setStyleSheet(
            "font-size: 16px; font-weight: 700; padding: 12px; "
            "background: #f7fafc; border-radius: 8px; text-align: center;"
        )
        self.status_label.setAlignment(Qt.AlignCenter)
        results_section.add_widget(self.status_label)
        
        layout.addWidget(results_section)
        
        # Add stretch
        layout.addStretch()
    
    def load_reference_wire(self):
        """Load reference wire STL file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Reference Wire STL",
            "",
            "STL Files (*.stl);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Show progress
            progress = QProgressDialog("Extracting wire centerline...", None, 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Extract wire using wire extractor
            extractor = WireExtractor()
            self.reference_wire = extractor.extract_from_stl(file_path, num_points=500)
            
            progress.close()
            
            # Update UI
            import os
            filename = os.path.basename(file_path)
            self.ref_status.setText(f"✓ Loaded: {filename}")
            self.ref_status.setStyleSheet("color: #48bb78; font-weight: 600;")
            
            # Enable validation if we have generated wire
            if self.generated_wire is not None:
                self.validate_btn.setEnabled(True)
            
            QMessageBox.information(
                self,
                "Reference Wire Loaded",
                f"Successfully extracted centerline from {filename}\\n"
                f"Points: {len(self.reference_wire)}"
            )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load reference wire:\\n{str(e)}"
            )
    
    def set_generated_wire(self, wire_path: np.ndarray):
        """
        Set the generated wire to validate.
        Called by main window when wire is generated.
        """
        self.generated_wire = wire_path
        
        # Enable validation if we have reference wire
        if self.reference_wire is not None:
            self.validate_btn.setEnabled(True)
    
    def run_validation(self):
        """Run validation of generated wire against reference"""
        if self.reference_wire is None:
            QMessageBox.warning(self, "No Reference", "Please load a reference wire first.")
            return
        
        if self.generated_wire is None:
            QMessageBox.warning(self, "No Generated Wire", "Please generate a wire first.")
            return
        
        try:
            # Show progress
            progress = QProgressDialog("Running validation...", None, 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            # Run validation
            validator = ClinicalAccuracyValidator()
            self.validation_results = validator.validate(
                self.generated_wire,
                self.reference_wire
            )
            
            progress.close()
            
            # Update UI with results
            self.display_results(self.validation_results)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Validation Error",
                f"Failed to run validation:\\n{str(e)}"
            )
    
    def display_results(self, results: dict):
        """Display validation results in UI"""
        # Update cards
        rms = results['rms_deviation_mm']
        max_dev = results['max_deviation_mm']
        mean_dev = results['mean_deviation_mm']
        acceptable = results['acceptable']
        
        # RMS Deviation
        rms_text = f"{rms:.3f} mm"
        if rms < 0.15:
            rms_text += " ✓"
        self.rms_card.set_value(rms_text)
        
        # Max Deviation
        max_text = f"{max_dev:.3f} mm"
        if max_dev < 0.30:
            max_text += " ✓"
        self.max_card.set_value(max_text)
        
        # Mean Deviation
        self.mean_card.set_value(f"{mean_dev:.3f} mm")
        
        # Clinical Status
        if acceptable:
            self.status_label.setText("✓ CLINICALLY ACCEPTABLE")
            self.status_label.setStyleSheet(
                "font-size: 16px; font-weight: 700; padding: 12px; "
                "background: #c6f6d5; border-radius: 8px; color: #22543d;"
            )
        else:
            self.status_label.setText("✗ NOT ACCEPTABLE")
            self.status_label.setStyleSheet(
                "font-size: 16px; font-weight: 700; padding: 12px; "
                "background: #fed7d7; border-radius: 8px; color: #742a2a;"
            )
        
        # Show results message
        QMessageBox.information(
            self,
            "Validation Complete",
            f"Validation Results:\\n\\n"
            f"RMS Deviation: {rms:.3f} mm\\n"
            f"Max Deviation: {max_dev:.3f} mm\\n"
            f"Mean Deviation: {mean_dev:.3f} mm\\n\\n"
            f"Status: {'✓ ACCEPTABLE' if acceptable else '✗ NOT ACCEPTABLE'}"
        )
