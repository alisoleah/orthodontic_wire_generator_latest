"""
Enhanced Control Panel for Hybrid Automatic/Manual Orthodontic Wire Generator

FIXED ISSUES:
- Hybrid mode now auto-generates wire on load
- Lower jaw wire generation working
- Wire updates with height controls
- Manual mode follows teeth (not just arcs)
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
        QFileDialog, QMessageBox, QProgressDialog, QApplication, QScrollArea
    )
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QFont
except ImportError:
    print("PyQt5 not available, falling back to tkinter implementation")

from core.workflow_manager import WorkflowManager, WorkflowMode


class EnhancedControlPanel(QWidget):
    """
    Control panel with mode selection and dual-arch support
    """
    
    # Signals for communication with main window
    arch_loaded = pyqtSignal(str, str)  # arch_type, file_path
    mode_changed = pyqtSignal(str)  # mode
    active_arch_changed = pyqtSignal(str)  # arch_type
    show_both_changed = pyqtSignal(bool)  # show_both
    wire_generated = pyqtSignal()
    interaction_mode_requested = pyqtSignal(str)  # mode (DEFINE_PLANE, PLACE_POINTS, etc.)
    control_points_converted = pyqtSignal(list) # list of control points
    gcode_exported = pyqtSignal(str) # The generated G-code content
    esp32_code_exported = pyqtSignal(str) # The generated ESP32 code content
    jaw_rotation_changed = pyqtSignal(int) # The new rotation angle
    
    def __init__(self, workflow_manager: WorkflowManager, parent=None):
        super().__init__(parent)
        self.workflow_manager = workflow_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        # Main layout for this widget
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_layout.addWidget(scroll)

        # Create content widget for scroll area
        content_widget = QWidget()
        scroll.setWidget(content_widget)

        # Layout for scrollable content
        layout = QVBoxLayout()
        content_widget.setLayout(layout)

        # Set font for better readability
        font = QFont()
        font.setPointSize(9)
        content_widget.setFont(font)
        
        # ============================================
        # SECTION 1: FILE LOADING
        # ============================================
        file_group = QGroupBox("1. Load Dental Models")
        file_layout = QVBoxLayout()
        
        # Upper Arch
        upper_layout = QHBoxLayout()
        self.load_upper_btn = QPushButton("Load Upper Arch (.stl)")
        self.load_upper_btn.clicked.connect(lambda: self.load_arch('upper'))
        self.upper_status = QLabel("Not loaded")
        self.upper_status.setStyleSheet("color: gray;")
        upper_layout.addWidget(self.load_upper_btn)
        upper_layout.addWidget(self.upper_status)
        file_layout.addLayout(upper_layout)
        
        # Lower Arch
        lower_layout = QHBoxLayout()
        self.load_lower_btn = QPushButton("Load Lower Arch (.stl)")
        self.load_lower_btn.clicked.connect(lambda: self.load_arch('lower'))
        self.lower_status = QLabel("Not loaded")
        self.lower_status.setStyleSheet("color: gray;")
        lower_layout.addWidget(self.load_lower_btn)
        lower_layout.addWidget(self.lower_status)
        file_layout.addLayout(lower_layout)
        
        # Optional: Opposing arch for collision
        opposing_layout = QHBoxLayout()
        self.load_opposing_btn = QPushButton("Load Opposing Arch (Optional)")
        self.load_opposing_btn.clicked.connect(self.load_opposing_arch)
        self.opposing_status = QLabel("Not loaded")
        self.opposing_status.setStyleSheet("color: gray;")
        opposing_layout.addWidget(self.load_opposing_btn)
        opposing_layout.addWidget(self.opposing_status)
        file_layout.addLayout(opposing_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # ============================================
        # SECTION 2: WORKFLOW MODE SELECTION
        # ============================================
        mode_group = QGroupBox("2. Select Workflow Mode")
        mode_layout = QVBoxLayout()
        
        # Mode description
        mode_desc = QLabel("Choose how you want to design the wire:")
        mode_desc.setWordWrap(True)
        mode_layout.addWidget(mode_desc)
        
        # Radio buttons for mode selection
        self.mode_automatic = QRadioButton("Automatic Detection")
        self.mode_automatic.setChecked(True)
        self.mode_automatic.toggled.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_automatic)
        
        auto_desc = QLabel("   • AI detects teeth and generates wire automatically")
        auto_desc.setStyleSheet("color: gray; font-size: 10px;")
        mode_layout.addWidget(auto_desc)
        
        self.mode_manual = QRadioButton("Manual Design (FixR Style)")
        self.mode_manual.toggled.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_manual)
        
        manual_desc = QLabel("   • Place control points manually on tooth surfaces")
        manual_desc.setStyleSheet("color: gray; font-size: 10px;")
        mode_layout.addWidget(manual_desc)
        
        self.mode_hybrid = QRadioButton("Hybrid (Auto + Manual Adjust)")
        self.mode_hybrid.toggled.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_hybrid)
        
        hybrid_desc = QLabel("   • Start with automatic, then manually refine")
        hybrid_desc.setStyleSheet("color: gray; font-size: 10px;")
        mode_layout.addWidget(hybrid_desc)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # ============================================
        # SECTION 3: ACTIVE ARCH SELECTION
        # ============================================
        arch_group = QGroupBox("3. Select Active Arch for Design")
        arch_layout = QVBoxLayout()
        
        arch_desc = QLabel("Choose which arch to design wire for:")
        arch_layout.addWidget(arch_desc)
        
        self.active_upper = QRadioButton("Upper Arch")
        self.active_upper.setChecked(True)
        self.active_upper.toggled.connect(self.on_active_arch_changed)
        arch_layout.addWidget(self.active_upper)
        
        self.active_lower = QRadioButton("Lower Arch")
        self.active_lower.toggled.connect(self.on_active_arch_changed)
        arch_layout.addWidget(self.active_lower)
        
        # Option to show both
        self.show_both_checkbox = QCheckBox("Show Both Arches")
        self.show_both_checkbox.setChecked(False)
        self.show_both_checkbox.stateChanged.connect(self.on_show_both_changed)
        arch_layout.addWidget(self.show_both_checkbox)
        
        arch_group.setLayout(arch_layout)
        layout.addWidget(arch_group)
        
        # ============================================
        # SECTION 4: WORKFLOW STEPS (Dynamic)
        # ============================================
        self.workflow_steps_group = QGroupBox("4. Design Workflow")
        self.workflow_steps_layout = QVBoxLayout()
        self.workflow_steps_group.setLayout(self.workflow_steps_layout)
        layout.addWidget(self.workflow_steps_group)
        
        # This section will change based on selected mode
        self.update_workflow_steps()
        
        # ============================================
        # SECTION 5: WIRE PARAMETERS
        # ============================================
        params_group = QGroupBox("5. Wire Parameters")
        params_layout = QFormLayout()
        
        # Height adjustment slider
        self.height_slider = QSlider(Qt.Horizontal)
        self.height_slider.setMinimum(-100)  # -10.0mm
        self.height_slider.setMaximum(100)   # +10.0mm
        self.height_slider.setValue(0)
        self.height_slider.setTickPosition(QSlider.TicksBelow)
        self.height_slider.setTickInterval(20)
        self.height_slider.valueChanged.connect(self.on_height_changed)
        
        self.height_label = QLabel("0.0 mm")
        height_layout = QHBoxLayout()
        height_layout.addWidget(self.height_slider)
        height_layout.addWidget(self.height_label)
        
        params_layout.addRow("Wire Height Offset:", height_layout)

        # Anterior/Posterior adjustment slider (forward/backward)
        self.ap_slider = QSlider(Qt.Horizontal)
        self.ap_slider.setMinimum(-100)  # -10.0mm
        self.ap_slider.setMaximum(100)   # +10.0mm
        self.ap_slider.setValue(0)
        self.ap_slider.setTickPosition(QSlider.TicksBelow)
        self.ap_slider.setTickInterval(20)
        self.ap_slider.valueChanged.connect(self.on_ap_offset_changed)

        self.ap_label = QLabel("0.0 mm")
        ap_layout = QHBoxLayout()
        ap_layout.addWidget(self.ap_slider)
        ap_layout.addWidget(self.ap_label)

        params_layout.addRow("Forward/Backward:", ap_layout)

        # Wire diameter
        self.wire_diameter = QDoubleSpinBox()
        self.wire_diameter.setRange(0.3, 2.0)
        self.wire_diameter.setValue(0.9)
        self.wire_diameter.setSuffix(" mm")
        self.wire_diameter.setSingleStep(0.1)
        self.wire_diameter.valueChanged.connect(self.on_wire_diameter_changed)
        params_layout.addRow("Wire Diameter:", self.wire_diameter)
        
        # Smoothness (for spline)
        self.smoothness_slider = QSlider(Qt.Horizontal)
        self.smoothness_slider.setMinimum(10)
        self.smoothness_slider.setMaximum(1000)
        self.smoothness_slider.setValue(300)
        self.smoothness_slider.valueChanged.connect(self.on_smoothness_changed)
        self.smoothness_label = QLabel("300 points")
        smoothness_layout = QHBoxLayout()
        smoothness_layout.addWidget(self.smoothness_slider)
        smoothness_layout.addWidget(self.smoothness_label)
        params_layout.addRow("Curve Smoothness:", smoothness_layout)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # ============================================
        # SECTION 6: COLLISION CHECK
        # ============================================
        collision_group = QGroupBox("6. Occlusal Interference Check")
        collision_layout = QVBoxLayout()
        
        self.check_collision_btn = QPushButton("Check for Collisions")
        self.check_collision_btn.clicked.connect(self.check_collisions)
        collision_layout.addWidget(self.check_collision_btn)
        
        self.collision_status = QLabel("No collision check performed")
        self.collision_status.setWordWrap(True)
        collision_layout.addWidget(self.collision_status)
        
        collision_group.setLayout(collision_layout)
        layout.addWidget(collision_group)
        
        # ============================================
        # SECTION 7: EXPORT
        # ============================================
        export_group = QGroupBox("7. Export Wire Design")
        export_layout = QVBoxLayout()
        
        self.export_gcode_btn = QPushButton("Export G-Code")
        self.export_gcode_btn.clicked.connect(self.export_gcode)
        export_layout.addWidget(self.export_gcode_btn)
        
        self.export_esp32_btn = QPushButton("Export ESP32 Code")
        self.export_esp32_btn.clicked.connect(self.export_esp32)
        export_layout.addWidget(self.export_esp32_btn)
        
        self.export_stl_btn = QPushButton("Export STL")
        self.export_stl_btn.clicked.connect(self.export_stl)
        export_layout.addWidget(self.export_stl_btn)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        # ============================================
        # SECTION 8: JAW SIMULATION
        # ============================================
        simulation_group = QGroupBox("8. Jaw Simulation")
        simulation_layout = QFormLayout()

        self.jaw_rotation_slider = QSlider(Qt.Horizontal)
        self.jaw_rotation_slider.setMinimum(0)
        self.jaw_rotation_slider.setMaximum(45)
        self.jaw_rotation_slider.setValue(0)
        self.jaw_rotation_slider.setTickPosition(QSlider.TicksBelow)
        self.jaw_rotation_slider.setTickInterval(5)
        self.jaw_rotation_slider.valueChanged.connect(self.on_jaw_rotation_changed)

        self.jaw_rotation_label = QLabel("0°")
        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(self.jaw_rotation_slider)
        rotation_layout.addWidget(self.jaw_rotation_label)

        simulation_layout.addRow("Lower Jaw Opening:", rotation_layout)
        simulation_group.setLayout(simulation_layout)
        layout.addWidget(simulation_group)

        # Add stretch to push everything to top
        layout.addStretch()
    
    # ============================================
    # EVENT HANDLERS
    # ============================================
    
    def load_arch(self, arch_type: str):
        """Load upper or lower arch"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            f"Select {arch_type.capitalize()} Arch STL", 
            "", 
            "STL Files (*.stl)"
        )
        
        if file_path:
            try:
                self.workflow_manager.load_arch(file_path, arch_type)

                # Auto-switch active arch to the one being loaded
                self.workflow_manager.set_active_arch(arch_type)
                if arch_type == 'upper':
                    self.active_upper.setChecked(True)
                    self.upper_status.setText("✓ Loaded")
                    self.upper_status.setStyleSheet("color: green;")
                else:
                    self.active_lower.setChecked(True)
                    self.lower_status.setText("✓ Loaded")
                    self.lower_status.setStyleSheet("color: green;")

                # Emit signal for main window to update visualizer
                self.arch_loaded.emit(arch_type, file_path)
                
                # ✅ FIX: Run automatic detection in BOTH automatic AND hybrid modes
                current_mode = self.workflow_manager.current_mode.value
                
                if current_mode == 'automatic':
                    # Automatic mode: Full detection
                    self.run_automatic_detection(arch_type)
                    
                elif current_mode == 'hybrid':
                    # ✅ FIX: Hybrid mode should ALSO run automatic detection!
                    self.run_automatic_detection(arch_type)
                    QMessageBox.information(
                        self,
                        "Hybrid Mode - Auto Wire Generated",
                        f"{arch_type.capitalize()} arch loaded with automatic wire.\n"
                        "Click 'Convert to Manual Mode' to refine the wire path."
                    )
                    
                elif current_mode == 'manual':
                    # Manual mode: Wait for user input
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
    
    def load_opposing_arch(self):
        """Load opposing arch for collision detection"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Opposing Arch STL", 
            "", 
            "STL Files (*.stl)"
        )
        
        if file_path:
            try:
                self.workflow_manager.load_opposing_arch(file_path)
                self.opposing_status.setText("✓ Loaded")
                self.opposing_status.setStyleSheet("color: green;")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load opposing arch:\n{str(e)}")
    
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
    
    def on_height_changed(self, value):
        """✅ FIX: Handle height slider change and regenerate wire"""
        height_mm = value / 10.0
        self.height_label.setText(f"{height_mm:.1f} mm")
        self.workflow_manager.set_global_height(height_mm)
        
        # ✅ FIX: Regenerate wire with new height
        active_arch = self.workflow_manager.get_active_arch()
        arch_data = self.workflow_manager.get_arch_data(active_arch)
        
        if arch_data and arch_data.get('bracket_positions'):
            # Regenerate wire path with new height
            try:
                wire_path = self.workflow_manager.generate_wire_from_brackets(active_arch)
                # Store the updated wire path
                arch_data['wire_path'] = wire_path
                # Emit signal to update visualization
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
            # Regenerate wire path with new offset
            try:
                wire_path = self.workflow_manager.generate_wire_from_brackets(active_arch)
                # Store the updated wire path
                arch_data['wire_path'] = wire_path
                # Emit signal to update visualization
                self.wire_generated.emit()
            except Exception as e:
                print(f"Error updating wire AP offset: {e}")

    def on_wire_diameter_changed(self, value):
        """Handle wire diameter change"""
        self.workflow_manager.set_wire_diameter(value)
        # Wire diameter is mainly for export, but we store it

    def on_smoothness_changed(self, value):
        """Handle smoothness slider change and regenerate wire"""
        self.smoothness_label.setText(f"{value} points")
        self.workflow_manager.set_wire_smoothness(value)

        # Regenerate wire with new smoothness
        active_arch = self.workflow_manager.get_active_arch()
        arch_data = self.workflow_manager.get_arch_data(active_arch)

        if arch_data and arch_data.get('bracket_positions'):
            # Regenerate wire path with new smoothness
            try:
                wire_path = self.workflow_manager.generate_wire_from_brackets(active_arch)
                # Store the updated wire path
                arch_data['wire_path'] = wire_path
                # Emit signal to update visualization
                self.wire_generated.emit()
            except Exception as e:
                print(f"Error updating wire smoothness: {e}")

    def on_jaw_rotation_changed(self, value):
        """Handle jaw rotation slider change."""
        self.jaw_rotation_label.setText(f"{value}°")
        self.jaw_rotation_changed.emit(value)

    def update_workflow_steps(self):
        """Update workflow steps based on selected mode"""
        # Clear existing steps
        while self.workflow_steps_layout.count():
            child = self.workflow_steps_layout.takeAt(0)
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
        self.workflow_steps_layout.addWidget(step1)
        
        step2 = QLabel("Step 2: Review detected teeth and wire")
        self.workflow_steps_layout.addWidget(step2)
        
        step3 = QLabel("Step 3: Adjust wire height if needed")
        self.workflow_steps_layout.addWidget(step3)
        
        self.run_detection_btn = QPushButton("Re-run Automatic Detection")
        self.run_detection_btn.clicked.connect(self.run_automatic_detection_manual)
        self.workflow_steps_layout.addWidget(self.run_detection_btn)
        
        # Display toggles
        self.show_teeth_checkbox = QCheckBox("Show Detected Teeth")
        self.show_teeth_checkbox.setChecked(True)
        self.show_teeth_checkbox.stateChanged.connect(self.toggle_teeth_display)
        self.workflow_steps_layout.addWidget(self.show_teeth_checkbox)
        
        self.show_brackets_checkbox = QCheckBox("Show Bracket Positions")
        self.show_brackets_checkbox.setChecked(True)
        self.show_brackets_checkbox.stateChanged.connect(self.toggle_brackets_display)
        self.workflow_steps_layout.addWidget(self.show_brackets_checkbox)
    
    def add_manual_workflow_steps(self):
        """✅ FIX: Add steps for manual mode - will use bracket positions"""
        step1 = QLabel("Step 1: Define Wire Path (3 Points)")
        self.workflow_steps_layout.addWidget(step1)
        
        step1_desc = QLabel("Wire will follow teeth between selected points")
        step1_desc.setStyleSheet("color: gray; font-size: 10px;")
        self.workflow_steps_layout.addWidget(step1_desc)
        
        path_layout = QHBoxLayout()
        self.define_path_btn = QPushButton("Define Wire Path (0/3)")
        self.define_path_btn.clicked.connect(self.define_wire_path_3_points)
        path_layout.addWidget(self.define_path_btn)
        
        self.reset_path_btn = QPushButton("Reset Path")
        self.reset_path_btn.clicked.connect(self.reset_wire_path)
        self.reset_path_btn.setEnabled(False)
        path_layout.addWidget(self.reset_path_btn)
        
        path_widget = QWidget()
        path_widget.setLayout(path_layout)
        self.workflow_steps_layout.addWidget(path_widget)
        
        step2 = QLabel("Step 2: Generate Wire Along Teeth")
        self.workflow_steps_layout.addWidget(step2)
        
        self.generate_wire_btn = QPushButton("Generate Wire")
        self.generate_wire_btn.clicked.connect(self.generate_manual_wire)
        self.generate_wire_btn.setEnabled(False)
        self.workflow_steps_layout.addWidget(self.generate_wire_btn)
    
    def add_hybrid_workflow_steps(self):
        """✅ FIX: Add steps for hybrid mode with better descriptions"""
        step1 = QLabel("Step 1: Load arch → Automatic wire generation")
        self.workflow_steps_layout.addWidget(step1)
        
        step1_desc = QLabel("Wire is automatically generated when you load the arch")
        step1_desc.setStyleSheet("color: gray; font-size: 10px;")
        self.workflow_steps_layout.addWidget(step1_desc)
        
        self.run_auto_btn = QPushButton("Re-run Automatic Detection")
        self.run_auto_btn.clicked.connect(self.run_automatic_detection_manual)
        self.workflow_steps_layout.addWidget(self.run_auto_btn)
        
        step2 = QLabel("Step 2: Convert to manual control points")
        self.workflow_steps_layout.addWidget(step2)
        
        self.convert_to_manual_btn = QPushButton("Convert to Manual Mode")
        self.convert_to_manual_btn.clicked.connect(self.convert_auto_to_manual)
        self.convert_to_manual_btn.setEnabled(False)
        self.workflow_steps_layout.addWidget(self.convert_to_manual_btn)
        
        step3 = QLabel("Step 3: Manually adjust control points")
        self.workflow_steps_layout.addWidget(step3)
        
        adjust_desc = QLabel("Drag points or add/remove as needed")
        adjust_desc.setStyleSheet("color: gray; font-size: 10px;")
        self.workflow_steps_layout.addWidget(adjust_desc)
        
        self.enable_drag_btn = QPushButton("Enable Point Dragging")
        self.enable_drag_btn.clicked.connect(self.enable_point_dragging)
        self.enable_drag_btn.setEnabled(False)
        self.workflow_steps_layout.addWidget(self.enable_drag_btn)
    
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
            
            # ✅ FIX: Enable conversion button in hybrid mode
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
        # This would be connected to the visualizer
        pass
    
    def toggle_brackets_display(self, state):
        """Toggle display of bracket positions"""
        # This would be connected to the visualizer
        pass
    
    # ============================================
    # MANUAL MODE FUNCTIONS
    # ============================================
    
    def define_wire_path_3_points(self):
        """✅ FIX: Launch PyVista point selector with tooth detection"""
        active_arch = self.workflow_manager.get_active_arch()
        arch_data = self.workflow_manager.get_arch_data(active_arch)
        
        if not arch_data or arch_data.get('mesh') is None:
            QMessageBox.warning(self, "No Mesh", "Please load an arch before selecting points.")
            return
        
        # ✅ FIX: Run tooth detection first if not done yet
        if not arch_data.get('teeth_detected') or not arch_data.get('bracket_positions'):
            try:
                # Run detection silently
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
        """Reset the 3-point wire path."""
        self.workflow_manager.clear_control_points()
        self.define_path_btn.setText("Define Wire Path (0/3)")
        self.define_path_btn.setEnabled(True)
        self.reset_path_btn.setEnabled(False)
        self.generate_wire_btn.setEnabled(False)
    
    def generate_manual_wire(self):
        """✅ FIX: Generate wire that follows teeth between 3 points"""
        try:
            # Generate wire using bracket positions (follows teeth)
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
            
            # Check if wire path exists
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
                    "Could not extract control points from automatic wire path.\n"
                    "The wire path may be empty or invalid."
                )

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print("Full error traceback:")
            print(error_details)
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to convert to manual mode:\n{str(e)}\n\nSee console for details."
            )
    
    def enable_point_dragging(self):
        """Enable dragging of control points"""
        # This would set the visualizer to drag mode
        self.enable_drag_btn.setText("Point Dragging Enabled ✓")
        self.enable_drag_btn.setStyleSheet("background-color: #90EE90;")
    
    # ============================================
    # COLLISION AND EXPORT
    # ============================================
    
    def check_collisions(self):
        """Check for collisions with opposing arch"""
        if not self.workflow_manager.has_opposing_arch():
            QMessageBox.warning(
                self,
                "No Opposing Arch",
                "Please load an opposing arch first to check for collisions."
            )
            return
        
        try:
            collisions = self.workflow_manager.detect_collisions()
            
            if len(collisions) > 0:
                self.collision_status.setText(
                    f"⚠️ WARNING: {len(collisions)} collision points detected!\n"
                    f"Wire will interfere with opposing teeth."
                )
                self.collision_status.setStyleSheet("color: red; font-weight: bold;")
            else:
                self.collision_status.setText("✓ No collisions detected. Wire is clear.")
                self.collision_status.setStyleSheet("color: green; font-weight: bold;")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Collision detection failed:\n{str(e)}")
    
    def export_gcode(self):
        """Generate G-code and display it in the GUI, with an option to save."""
        try:
            wire_diameter = self.wire_diameter.value()
            gcode_content = self.workflow_manager.export_gcode(wire_size=wire_diameter)

            if gcode_content:
                self.gcode_exported.emit(gcode_content)
                QMessageBox.information(self, "G-Code Generated", "G-Code is now displayed in the Exported Code Viewer.")

                reply = QMessageBox.question(self, 'Save G-Code', 'Do you want to save the G-Code to a file?',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                if reply == QMessageBox.Yes:
                    file_path, _ = QFileDialog.getSaveFileName(
                        self, "Save G-Code", "", "G-Code Files (*.gcode)"
                    )
                    if file_path:
                        with open(file_path, 'w') as f:
                            f.write(gcode_content)
                        QMessageBox.information(self, "Success", f"G-Code saved to {file_path}")
            else:
                QMessageBox.warning(self, "Export Failed", "Could not generate G-Code. Ensure a wire path exists.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")
    
    def export_esp32(self):
        """Generate ESP32 code and display it in the GUI, with an option to save."""
        try:
            wire_diameter = self.wire_diameter.value()
            esp32_code = self.workflow_manager.export_esp32(wire_size=wire_diameter)

            if esp32_code:
                self.esp32_code_exported.emit(esp32_code)
                QMessageBox.information(self, "ESP32 Code Generated", "ESP32 code is now displayed in the Exported Code Viewer.")

                reply = QMessageBox.question(self, 'Save ESP32 Code', 'Do you want to save the ESP32 code to a file?',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                if reply == QMessageBox.Yes:
                    file_path, _ = QFileDialog.getSaveFileName(
                        self, "Save ESP32 Code", "", "Arduino Files (*.ino)"
                    )
                    if file_path:
                        with open(file_path, 'w') as f:
                            f.write(esp32_code)
                        QMessageBox.information(self, "Success", f"ESP32 code saved to {file_path}")
            else:
                QMessageBox.warning(self, "Export Failed", "Could not generate ESP32 code. Ensure a wire path exists.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")
    
    def export_stl(self):
        """Export STL"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save STL", "", "STL Files (*.stl)"
        )
        if file_path:
            try:
                self.workflow_manager.export_stl(file_path)
                QMessageBox.information(self, "Success", "STL exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")