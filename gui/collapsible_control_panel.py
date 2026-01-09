"""
Modern Collapsible Control Panel for Orthodontic Wire Generator

This is a modernized version with collapsible sections while preserving
all functionality from the original enhanced_control_panel.py
"""

import sys
import os
from typing import Optional, List, Dict, Any

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
        QRadioButton, QCheckBox, QSlider, QDoubleSpinBox, QFormLayout,
        QFileDialog, QMessageBox, QProgressDialog, QApplication, QScrollArea,
        QButtonGroup
    )
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QFont
except ImportError:
    print("PyQt5 not available, falling back to tkinter implementation")

from core.workflow_manager import WorkflowManager, WorkflowMode
from gui.widgets.collapsible_section import CollapsibleSection
from gui.widgets.file_upload_card import FileUploadCard


class CollapsibleControlPanel(QWidget):
    """
    Modern control panel with collapsible sections
    Preserves all functionality from EnhancedControlPanel
    """
    
    # Signals for communication with main window (same as original)
    arch_loaded = pyqtSignal(str, str)  # arch_type, file_path
    mode_changed = pyqtSignal(str)  # mode
    active_arch_changed = pyqtSignal(str)  # arch_type
    show_both_changed = pyqtSignal(bool)  # show_both
    wire_generated = pyqtSignal()
    interaction_mode_requested = pyqtSignal(str)
    control_points_converted = pyqtSignal(list)
    gcode_exported = pyqtSignal(str)
    esp32_code_exported = pyqtSignal(str)
    jaw_rotation_changed = pyqtSignal(int)
    
    def __init__(self, workflow_manager: WorkflowManager, parent=None):
        super().__init__(parent)
        self.workflow_manager = workflow_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface with collapsible sections"""
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

        # Create content widget for scroll area
        content_widget = QWidget()
        scroll.setWidget(content_widget)

        # Layout for scrollable content
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        content_widget.setLayout(layout)
        
        # ============================================
        # SECTION 1: FILE LOADING (Collapsible)
        # ============================================
        section1 = CollapsibleSection("DENTAL MODELS", section_number=1)
        
        # Upper Arch File Card
        self.upper_card = FileUploadCard("Upper Arch (.stl)", "⬆️")
        self.upper_card.file_selected.connect(lambda path: self.load_arch_from_card('upper', path))
        section1.add_widget(self.upper_card)
        
        # Lower Arch File Card
        self.lower_card = FileUploadCard("Lower Arch (.stl)", "⬇️")
        self.lower_card.file_selected.connect(lambda path: self.load_arch_from_card('lower', path))
        section1.add_widget(self.lower_card)
        
        # Opposing Arch File Card
        self.opposing_card = FileUploadCard("Opposing Arch (Optional)", "↔️")
        self.opposing_card.file_selected.connect(self.load_opposing_arch_from_card)
        section1.add_widget(self.opposing_card)
        
        layout.addWidget(section1)
        
        # ============================================
        # SECTION 2: WORKFLOW MODE (Collapsible)
        # ============================================
        section2 = CollapsibleSection("WORKFLOW MODE", section_number=2)
        
        mode_desc = QLabel("Choose how you want to design the wire:")
        mode_desc.setObjectName("subheadingLabel")
        mode_desc.setWordWrap(True)
        section2.add_widget(mode_desc)
        
        # Radio buttons for mode selection
        self.mode_automatic = QRadioButton("🤖 Automatic Detection")
        self.mode_automatic.setChecked(True)
        self.mode_automatic.toggled.connect(self.on_mode_changed)
        section2.add_widget(self.mode_automatic)
        
        auto_desc = QLabel("AI detects teeth and generates wire automatically")
        auto_desc.setStyleSheet("color: #718096; font-size: 12px; margin-left: 24px;")
        auto_desc.setWordWrap(True)
        section2.add_widget(auto_desc)
        
        self.mode_manual = QRadioButton("✏️ Manual Design (FIXR Style)")
        self.mode_manual.toggled.connect(self.on_mode_changed)
        section2.add_widget(self.mode_manual)
        
        manual_desc = QLabel("Place control points manually on tooth surfaces")
        manual_desc.setStyleSheet("color: #718096; font-size: 12px; margin-left: 24px;")
        manual_desc.setWordWrap(True)
        section2.add_widget(manual_desc)
        
        self.mode_hybrid = QRadioButton("⚡ Hybrid (Auto + Manual Adjust)")
        self.mode_hybrid.toggled.connect(self.on_mode_changed)
        section2.add_widget(self.mode_hybrid)
        
        hybrid_desc = QLabel("Start with automatic, then manually refine")
        hybrid_desc.setStyleSheet("color: #718096; font-size: 12px; margin-left: 24px;")
        hybrid_desc.setWordWrap(True)
        section2.add_widget(hybrid_desc)
        
        layout.addWidget(section2)
        
        # ============================================
        # SECTION 3: ACTIVE ARCH SELECTION (Collapsible)
        # ============================================
        section3 = CollapsibleSection("ACTIVE ARCH", section_number=3)
        
        arch_desc = QLabel("Choose which arch to design wire for:")
        arch_desc.setObjectName("subheadingLabel")
        section3.add_widget(arch_desc)
        
        self.active_upper = QRadioButton("Upper Arch")
        self.active_upper.setChecked(True)
        self.active_upper.toggled.connect(self.on_active_arch_changed)
        section3.add_widget(self.active_upper)
        
        self.active_lower = QRadioButton("Lower Arch")
        self.active_lower.toggled.connect(self.on_active_arch_changed)
        section3.add_widget(self.active_lower)
        
        # Option to show both
        self.show_both_checkbox = QCheckBox("Show Both Arches")
        self.show_both_checkbox.setChecked(False)
        self.show_both_checkbox.stateChanged.connect(self.on_show_both_changed)
        section3.add_widget(self.show_both_checkbox)
        
        layout.addWidget(section3)
        
        # ============================================
        # SECTION 4: WORKFLOW STEPS (Dynamic, Collapsible)
        # ============================================
        self.workflow_section = CollapsibleSection("DESIGN WORKFLOW", section_number=4)
        layout.addWidget(self.workflow_section)
        
        # This section will change based on selected mode
        self.update_workflow_steps()
        
        # ============================================
        # SECTION 5: WIRE PARAMETERS (Collapsible)
        # ============================================
        section5 = CollapsibleSection("WIRE PARAMETERS", section_number=5)
        
        # Height adjustment
        height_label = QLabel("Height Offset")
        height_label.setObjectName("subheadingLabel")
        section5.add_widget(height_label)
        
        self.height_slider = QSlider(Qt.Horizontal)
        self.height_slider.setMinimum(-100)
        self.height_slider.setMaximum(100)
        self.height_slider.setValue(0)
        self.height_slider.valueChanged.connect(self.on_height_changed)
        section5.add_widget(self.height_slider)
        
        self.height_label = QLabel("0.0 mm")
        self.height_label.setAlignment(Qt.AlignRight)
        section5.add_widget(self.height_label)
        
        # AP offset
        ap_label = QLabel("Forward/Backward")
        ap_label.setObjectName("subheadingLabel")
        section5.add_widget(ap_label)
        
        self.ap_slider = QSlider(Qt.Horizontal)
        self.ap_slider.setMinimum(-100)
        self.ap_slider.setMaximum(100)
        self.ap_slider.setValue(0)
        self.ap_slider.valueChanged.connect(self.on_ap_offset_changed)
        section5.add_widget(self.ap_slider)
        
        self.ap_label = QLabel("0.0 mm")
        self.ap_label.setAlignment(Qt.AlignRight)
        section5.add_widget(self.ap_label)
        
        # Wire diameter
        diameter_layout = QHBoxLayout()
        diameter_layout.addWidget(QLabel("Wire Diameter:"))
        self.wire_diameter = QDoubleSpinBox()
        self.wire_diameter.setRange(0.3, 2.0)
        self.wire_diameter.setValue(0.9)
        self.wire_diameter.setSuffix(" mm")
        self.wire_diameter.setSingleStep(0.1)
        self.wire_diameter.valueChanged.connect(self.on_wire_diameter_changed)
        diameter_layout.addWidget(self.wire_diameter)
        section5.add_layout(diameter_layout)
        
        # Smoothness
        smooth_label = QLabel("Curve Smoothness")
        smooth_label.setObjectName("subheadingLabel")
        section5.add_widget(smooth_label)
        
        self.smoothness_slider = QSlider(Qt.Horizontal)
        self.smoothness_slider.setMinimum(10)
        self.smoothness_slider.setMaximum(1000)
        self.smoothness_slider.setValue(300)
        self.smoothness_slider.valueChanged.connect(self.on_smoothness_changed)
        section5.add_widget(self.smoothness_slider)
        
        self.smoothness_label = QLabel("300 points")
        self.smoothness_label.setAlignment(Qt.AlignRight)
        section5.add_widget(self.smoothness_label)
        
        layout.addWidget(section5)
        
        # ============================================
        # SECTION 6: COLLISION CHECK (Collapsible)
        # ============================================
        section6 = CollapsibleSection("OCCLUSAL INTERFERENCE", section_number=6)
        
        self.check_collision_btn = QPushButton("Check for Collisions")
        self.check_collision_btn.clicked.connect(self.check_collisions)
        section6.add_widget(self.check_collision_btn)
        
        self.collision_status = QLabel("No collision check performed")
        self.collision_status.setWordWrap(True)
        self.collision_status.setStyleSheet("color: #718096; font-size: 12px;")
        section6.add_widget(self.collision_status)
        
        layout.addWidget(section6)
        
        # ============================================
        # SECTION 7: EXPORT (Collapsible)
        # ============================================
        section7 = CollapsibleSection("EXPORT", section_number=7)
        
        self.export_gcode_btn = QPushButton("💾 Export G-Code")
        self.export_gcode_btn.clicked.connect(self.export_gcode)
        section7.add_widget(self.export_gcode_btn)
        
        self.export_esp32_btn = QPushButton("📟 Export ESP32 Code")
        self.export_esp32_btn.clicked.connect(self.export_esp32)
        section7.add_widget(self.export_esp32_btn)
        
        self.export_stl_btn = QPushButton("🔷 Export STL")
        self.export_stl_btn.clicked.connect(self.export_stl)
        section7.add_widget(self.export_stl_btn)
        
        layout.addWidget(section7)
        
        # ============================================
        # SECTION 8: JAW SIMULATION (Collapsible)
        # ============================================
        section8 = CollapsibleSection("JAW SIMULATION", section_number=8)
        
        jaw_label = QLabel("Lower Jaw Opening")
        jaw_label.setObjectName("subheadingLabel")
        section8.add_widget(jaw_label)
        
        self.jaw_rotation_slider = QSlider(Qt.Horizontal)
        self.jaw_rotation_slider.setMinimum(0)
        self.jaw_rotation_slider.setMaximum(45)
        self.jaw_rotation_slider.setValue(0)
        self.jaw_rotation_slider.valueChanged.connect(self.on_jaw_rotation_changed)
        section8.add_widget(self.jaw_rotation_slider)
        
        self.jaw_rotation_label = QLabel("0°")
        self.jaw_rotation_label.setAlignment(Qt.AlignRight)
        section8.add_widget(self.jaw_rotation_label)
        
        layout.addWidget(section8)
        
        # Add stretch to push everything to top
        layout.addStretch()
    
    # ============================================
    # FILE LOADING HANDLERS
    # ============================================
    
    def load_arch_from_card(self, arch_type: str, file_path: str):
        """Load arch from file upload card"""
        try:
            self.workflow_manager.load_arch(file_path, arch_type)

            # Auto-switch active arch to the one being loaded
            self.workflow_manager.set_active_arch(arch_type)
            if arch_type == 'upper':
                self.active_upper.setChecked(True)
            else:
                self.active_lower.setChecked(True)

            # Emit signal for main window to update visualizer
            self.arch_loaded.emit(arch_type, file_path)
            
            # Run automatic detection based on mode
            current_mode = self.workflow_manager.current_mode.value
            
            if current_mode == 'automatic':
                self.run_automatic_detection(arch_type)
                
            elif current_mode == 'hybrid':
                self.run_automatic_detection(arch_type)
                QMessageBox.information(
                    self,
                    "Hybrid Mode - Auto Wire Generated",
                    f"{arch_type.capitalize()} arch loaded with automatic wire.\n"
                    "Click 'Convert to Manual Mode' to refine the wire path."
                )
                
            elif current_mode == 'manual':
                QMessageBox.information(
                    self,
                    "Manual Mode Active",
                    f"{arch_type.capitalize()} arch loaded successfully!\n"
                    "Click 'Define Wire Path (0/3)' to place control points."
                )
                    
        except Exception as e:
            import traceback
            print("Error loading arch:")
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to load {arch_type} arch:\n{str(e)}")
    
    def load_opposing_arch_from_card(self, file_path: str):
        """Load opposing arch from file upload card"""
        try:
            self.workflow_manager.load_opposing_arch(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load opposing arch:\n{str(e)}")
    
    # ============================================
    # MODE AND ARCH SELECTION HANDLERS
    # ============================================
    
    def on_mode_changed(self):
        """Handle mode selection change"""
        if self.mode_automatic.isChecked():
            self.workflow_manager.set_mode(WorkflowMode.AUTOMATIC)
        elif self.mode_manual.isChecked():
            self.workflow_manager.set_mode(WorkflowMode.MANUAL)
        else:
            self.workflow_manager.set_mode(WorkflowMode.HYBRID)
        
        self.update_workflow_steps()
        self.mode_changed.emit(self.workflow_manager.current_mode.value)
    
    def on_active_arch_changed(self):
        """Handle active arch selection change"""
        if self.active_upper.isChecked():
            self.workflow_manager.set_active_arch('upper')
        else:
            self.workflow_manager.set_active_arch('lower')
        
        self.active_arch_changed.emit(self.workflow_manager.get_active_arch())
    
    def on_show_both_changed(self, state):
        """Toggle showing both arches"""
        show_both = (state == Qt.Checked)
        self.show_both_changed.emit(show_both)
    
    # ============================================
    # PARAMETER ADJUSTMENT HANDLERS
    # ============================================
    
    def on_height_changed(self, value):
        """Handle height slider change and regenerate wire"""
        height_mm = value / 10.0
        self.height_label.setText(f"{height_mm:.1f} mm")
        self.workflow_manager.set_global_height(height_mm)
        
        # Regenerate wire with new height
        active_arch = self.workflow_manager.get_active_arch()
        arch_data = self.workflow_manager.get_arch_data(active_arch)
        
        if arch_data and arch_data.get('bracket_positions'):
            try:
                wire_path = self.workflow_manager.generate_wire_from_brackets(active_arch)
                arch_data['wire_path'] = wire_path
                self.wire_generated.emit()
            except Exception as e:
                print(f"Error updating wire height: {e}")
    
    def on_ap_offset_changed(self, value):
        """Handle AP offset slider change and regenerate wire"""
        ap_mm = value / 10.0
        self.ap_label.setText(f"{ap_mm:.1f} mm")
        self.workflow_manager.set_global_ap_offset(ap_mm)

        # Regenerate wire with new AP offset
        active_arch = self.workflow_manager.get_active_arch()
        arch_data = self.workflow_manager.get_arch_data(active_arch)

        if arch_data and arch_data.get('bracket_positions'):
            try:
                wire_path = self.workflow_manager.generate_wire_from_brackets(active_arch)
                arch_data['wire_path'] = wire_path
                self.wire_generated.emit()
            except Exception as e:
                print(f"Error updating wire AP offset: {e}")

    def on_wire_diameter_changed(self, value):
        """Handle wire diameter change"""
        self.workflow_manager.set_wire_diameter(value)

    def on_smoothness_changed(self, value):
        """Handle smoothness slider change and regenerate wire"""
        self.smoothness_label.setText(f"{value} points")
        self.workflow_manager.set_wire_smoothness(value)

        # Regenerate wire with new smoothness
        active_arch = self.workflow_manager.get_active_arch()
        arch_data = self.workflow_manager.get_arch_data(active_arch)

        if arch_data and arch_data.get('bracket_positions'):
            try:
                wire_path = self.workflow_manager.generate_wire_from_brackets(active_arch)
                arch_data['wire_path'] = wire_path
                self.wire_generated.emit()
            except Exception as e:
                print(f"Error updating wire smoothness: {e}")

    def on_jaw_rotation_changed(self, value):
        """Handle jaw rotation slider change"""
        self.jaw_rotation_label.setText(f"{value}°")
        self.jaw_rotation_changed.emit(value)

    # ============================================
    # WORKFLOW STEPS (Dynamic based on mode)
    # ============================================
    
    def update_workflow_steps(self):
        """Update workflow steps based on selected mode"""
        # Clear existing steps
        while self.workflow_section.content_layout.count():
            child = self.workflow_section.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        current_mode = self.workflow_manager.current_mode
        
        if current_mode == WorkflowMode.AUTOMATIC:
            self.add_automatic_workflow_steps()
        elif current_mode == WorkflowMode.MANUAL:
            self.add_manual_workflow_steps()
        else:  # HYBRID
            self.add_hybrid_workflow_steps()
    
    def add_automatic_workflow_steps(self):
        """Add steps for automatic mode"""
        step1 = QLabel("Step 1: Load arch(es) → Automatic detection runs")
        self.workflow_section.add_widget(step1)
        
        step2 = QLabel("Step 2: Review detected teeth and wire")
        self.workflow_section.add_widget(step2)
        
        step3 = QLabel("Step 3: Adjust wire height if needed")
        self.workflow_section.add_widget(step3)
        
        self.run_detection_btn = QPushButton("Re-run Automatic Detection")
        self.run_detection_btn.clicked.connect(self.run_automatic_detection_manual)
        self.workflow_section.add_widget(self.run_detection_btn)
        
        # Display toggles
        self.show_teeth_checkbox = QCheckBox("Show Detected Teeth")
        self.show_teeth_checkbox.setChecked(True)
        self.show_teeth_checkbox.stateChanged.connect(self.toggle_teeth_display)
        self.workflow_section.add_widget(self.show_teeth_checkbox)
        
        self.show_brackets_checkbox = QCheckBox("Show Bracket Positions")
        self.show_brackets_checkbox.setChecked(True)
        self.show_brackets_checkbox.stateChanged.connect(self.toggle_brackets_display)
        self.workflow_section.add_widget(self.show_brackets_checkbox)
    
    def add_manual_workflow_steps(self):
        """Add steps for manual mode"""
        step1 = QLabel("Step 1: Define Wire Path (3 Points)")
        self.workflow_section.add_widget(step1)
        
        step1_desc = QLabel("Wire will follow teeth between selected points")
        step1_desc.setStyleSheet("color: #718096; font-size: 12px;")
        self.workflow_section.add_widget(step1_desc)
        
        path_layout = QHBoxLayout()
        self.define_path_btn = QPushButton("Define Wire Path (0/3)")
        self.define_path_btn.clicked.connect(self.define_wire_path_3_points)
        path_layout.addWidget(self.define_path_btn)
        
        self.reset_path_btn = QPushButton("Reset Path")
        self.reset_path_btn.clicked.connect(self.reset_wire_path)
        self.reset_path_btn.setEnabled(False)
        path_layout.addWidget(self.reset_path_btn)
        
        self.workflow_section.add_layout(path_layout)
        
        step2 = QLabel("Step 2: Generate Wire Along Teeth")
        self.workflow_section.add_widget(step2)
        
        self.generate_wire_btn = QPushButton("Generate Wire")
        self.generate_wire_btn.clicked.connect(self.generate_manual_wire)
        self.generate_wire_btn.setEnabled(False)
        self.workflow_section.add_widget(self.generate_wire_btn)
    
    def add_hybrid_workflow_steps(self):
        """Add steps for hybrid mode"""
        step1 = QLabel("Step 1: Load arch → Automatic wire generation")
        self.workflow_section.add_widget(step1)
        
        step1_desc = QLabel("Wire is automatically generated when you load the arch")
        step1_desc.setStyleSheet("color: #718096; font-size: 12px;")
        self.workflow_section.add_widget(step1_desc)
        
        self.run_auto_btn = QPushButton("Re-run Automatic Detection")
        self.run_auto_btn.clicked.connect(self.run_automatic_detection_manual)
        self.workflow_section.add_widget(self.run_auto_btn)
        
        step2 = QLabel("Step 2: Convert to manual control points")
        self.workflow_section.add_widget(step2)
        
        self.convert_to_manual_btn = QPushButton("Convert to Manual Mode")
        self.convert_to_manual_btn.clicked.connect(self.convert_auto_to_manual)
        self.convert_to_manual_btn.setEnabled(False)
        self.workflow_section.add_widget(self.convert_to_manual_btn)
        
        step3 = QLabel("Step 3: Manually adjust control points")
        self.workflow_section.add_widget(step3)
        
        adjust_desc = QLabel("Drag points or add/remove as needed")
        adjust_desc.setStyleSheet("color: #718096; font-size: 12px;")
        self.workflow_section.add_widget(adjust_desc)
        
        self.enable_drag_btn = QPushButton("Enable Point Dragging")
        self.enable_drag_btn.clicked.connect(self.enable_point_dragging)
        self.enable_drag_btn.setEnabled(False)
        self.workflow_section.add_widget(self.enable_drag_btn)
    
    # ============================================
    # AUTOMATIC MODE FUNCTIONS
    # ============================================
    
    def run_automatic_detection(self, arch_type: str = None):
        """Run automatic tooth detection and wire generation"""
        if arch_type is None:
            arch_type = 'upper' if self.active_upper.isChecked() else 'lower'
        
        arch_data = self.workflow_manager.get_arch_data(arch_type)
        if arch_data is None:
            QMessageBox.warning(self, "Error", f"Please load {arch_type} arch first")
            return
        
        # Show progress
        progress = QProgressDialog("Running automatic detection...", None, 0, 3, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        try:
            # Step 1: Detect teeth
            progress.setValue(1)
            progress.setLabelText("Detecting teeth...")
            QApplication.processEvents()
            
            # Step 2: Position brackets
            progress.setValue(2)
            progress.setLabelText("Positioning brackets...")
            QApplication.processEvents()
            
            # Step 3: Generate wire
            progress.setValue(3)
            progress.setLabelText("Generating wire...")
            QApplication.processEvents()
            
            detected_teeth, bracket_positions, wire_path = self.workflow_manager.run_automatic_detection(arch_type)
            
            progress.close()
            
            # Emit signal to update visualization
            self.wire_generated.emit()
            
            # Enable conversion button in hybrid mode
            if self.mode_hybrid.isChecked():
                self.convert_to_manual_btn.setEnabled(True)
                
            QMessageBox.information(
                self,
                "Detection Complete",
                f"Successfully detected {len(detected_teeth)} teeth and generated wire path."
            )
            
        except Exception as e:
            progress.close()
            import traceback
            print("Automatic detection error:")
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Automatic detection failed:\n{str(e)}")
    
    def run_automatic_detection_manual(self):
        """Manual trigger for automatic detection"""
        arch_type = 'upper' if self.active_upper.isChecked() else 'lower'
        self.run_automatic_detection(arch_type)
    
    def toggle_teeth_display(self, state):
        """Toggle display of detected teeth"""
        pass
    
    def toggle_brackets_display(self, state):
        """Toggle display of bracket positions"""
        pass
    
    # ============================================
    # MANUAL MODE FUNCTIONS
    # ============================================
    
    def define_wire_path_3_points(self):
        """Launch PyVista point selector with tooth detection"""
        active_arch = self.workflow_manager.get_active_arch()
        arch_data = self.workflow_manager.get_arch_data(active_arch)
        
        if not arch_data or arch_data.get('mesh') is None:
            QMessageBox.warning(self, "No Mesh", "Please load an arch before selecting points.")
            return
        
        # Run tooth detection first if not done yet
        if not arch_data.get('teeth_detected') or not arch_data.get('bracket_positions'):
            try:
                detected_teeth, bracket_positions, _ = self.workflow_manager.run_automatic_detection(active_arch)
                print(f"Detected {len(detected_teeth)} teeth for manual mode")
            except Exception as e:
                print(f"Warning: Could not detect teeth: {e}")
        
        # Get the main window's visualizer
        main_window = self.parent().parent().parent()
        visualizer = main_window.visualizer
        
        # Enable point picking
        visualizer.enable_point_picking(num_points=3)
        
        self.define_path_btn.setText("Selecting Points... (0/3)")
        self.define_path_btn.setEnabled(False)

    def reset_wire_path(self):
        """Reset the 3-point wire path"""
        self.workflow_manager.clear_control_points()
        self.define_path_btn.setText("Define Wire Path (0/3)")
        self.define_path_btn.setEnabled(True)
        self.reset_path_btn.setEnabled(False)
        self.generate_wire_btn.setEnabled(False)
    
    def generate_manual_wire(self):
        """Generate wire that follows teeth between 3 points"""
        try:
            wire_path = self.workflow_manager.generate_wire_from_control_points()
            self.wire_generated.emit()
            QMessageBox.information(self, "Success", "Wire generated following tooth contours!")
        except Exception as e:
            import traceback
            print("Error generating manual wire:")
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to generate wire:\n{str(e)}")
    
    # ============================================
    # HYBRID MODE FUNCTIONS
    # ============================================
    
    def convert_auto_to_manual(self):
        """Convert automatic wire to editable control points"""
        try:
            arch_type = 'upper' if self.active_upper.isChecked() else 'lower'
            arch_data = self.workflow_manager.get_arch_data(arch_type)
            
            if not arch_data:
                QMessageBox.warning(self, "No Data", f"No {arch_type} arch data available.")
                return
            
            if arch_data.get('wire_path') is None or len(arch_data.get('wire_path', [])) == 0:
                QMessageBox.warning(
                    self, 
                    "No Wire Path", 
                    "No automatic wire path found. Please run automatic detection first."
                )
                return
            
            # Extract control points from automatic wire
            control_points = self.workflow_manager.extract_control_points_from_auto(arch_type)
            
            if control_points and len(control_points) > 0:
                self.control_points_converted.emit(control_points)
                self.enable_drag_btn.setEnabled(True)

                QMessageBox.information(
                    self,
                    "Converted to Manual Mode",
                    f"Generated {len(control_points)} control points from the automatic wire.\n"
                    "You can now drag these points to refine the wire path."
                )
            else:
                QMessageBox.warning(
                    self, 
                    "Conversion Failed", 
                    "Could not extract control points from automatic wire path."
                )

        except Exception as e:
            import traceback
            print("Full error traceback:")
            traceback.print_exc()
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to convert to manual mode:\n{str(e)}"
            )
    
    def enable_point_dragging(self):
        """Enable dragging of control points"""
        main_window = self.parent().parent().parent()
        visualizer = main_window.visualizer
        visualizer.enable_control_point_dragging()
        self.enable_drag_btn.setText("Point Dragging Enabled ✓")
        self.enable_drag_btn.setEnabled(False)
    
    # ============================================
    # COLLISION AND EXPORT FUNCTIONS
    # ============================================
    
    def check_collisions(self):
        """Check for collisions with opposing arch"""
        try:
            active_arch = self.workflow_manager.get_active_arch()
            arch_data = self.workflow_manager.get_arch_data(active_arch)
            
            if not arch_data or arch_data.get('wire_path') is None:
                QMessageBox.warning(self, "No Wire", "Please generate a wire first.")
                return
            
            if not self.workflow_manager.opposing_arch_data:
                QMessageBox.warning(self, "No Opposing Arch", "Please load opposing arch first.")
                return
            
            # Check for collisions
            has_collision, collision_points = self.workflow_manager.check_wire_collision(active_arch)
            
            if has_collision:
                self.collision_status.setText(f"⚠️ Collision detected at {len(collision_points)} points")
                self.collision_status.setStyleSheet("color: #dc3545; font-weight: 600;")
            else:
                self.collision_status.setText("✓ No collisions detected")
                self.collision_status.setStyleSheet("color: #28a745; font-weight: 600;")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Collision check failed:\n{str(e)}")
    
    def export_gcode(self):
        """Generate G-code and display it"""
        try:
            active_arch = self.workflow_manager.get_active_arch()
            arch_data = self.workflow_manager.get_arch_data(active_arch)
            
            if not arch_data or arch_data.get('wire_path') is None:
                QMessageBox.warning(self, "No Wire", "Please generate a wire first.")
                return
            
            gcode = self.workflow_manager.export_gcode(active_arch)
            self.gcode_exported.emit(gcode)
            
            # Ask if user wants to save
            reply = QMessageBox.question(
                self, 
                "Export G-Code", 
                "G-Code generated! Would you like to save it to a file?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                file_path, _ = QFileDialog.getSaveFileName(
                    self, 
                    "Save G-Code", 
                    f"{active_arch}_wire.gcode", 
                    "G-Code Files (*.gcode);;All Files (*)"
                )
                
                if file_path:
                    with open(file_path, 'w') as f:
                        f.write(gcode)
                    QMessageBox.information(self, "Success", f"G-Code saved to {file_path}")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"G-Code export failed:\n{str(e)}")
    
    def export_esp32(self):
        """Generate ESP32 code and display it"""
        try:
            active_arch = self.workflow_manager.get_active_arch()
            arch_data = self.workflow_manager.get_arch_data(active_arch)
            
            if not arch_data or arch_data.get('wire_path') is None:
                QMessageBox.warning(self, "No Wire", "Please generate a wire first.")
                return
            
            esp32_code = self.workflow_manager.export_esp32(active_arch)
            self.esp32_code_exported.emit(esp32_code)
            
            reply = QMessageBox.question(
                self, 
                "Export ESP32 Code", 
                "ESP32 code generated! Would you like to save it to a file?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                file_path, _ = QFileDialog.getSaveFileName(
                    self, 
                    "Save ESP32 Code", 
                    f"{active_arch}_wire.ino", 
                    "Arduino Files (*.ino);;All Files (*)"
                )
                
                if file_path:
                    with open(file_path, 'w') as f:
                        f.write(esp32_code)
                    QMessageBox.information(self, "Success", f"ESP32 code saved to {file_path}")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"ESP32 export failed:\n{str(e)}")
    
    def export_stl(self):
        """Export wire as STL"""
        try:
            active_arch = self.workflow_manager.get_active_arch()
            arch_data = self.workflow_manager.get_arch_data(active_arch)
            
            if not arch_data or arch_data.get('wire_path') is None:
                QMessageBox.warning(self, "No Wire", "Please generate a wire first.")
                return
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Wire STL", 
                f"{active_arch}_wire.stl", 
                "STL Files (*.stl);;All Files (*)"
            )
            
            if file_path:
                self.workflow_manager.export_stl(active_arch, file_path)
                QMessageBox.information(self, "Success", f"Wire STL saved to {file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"STL export failed:\n{str(e)}")
