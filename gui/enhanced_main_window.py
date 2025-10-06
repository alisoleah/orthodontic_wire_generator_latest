"""
Enhanced Main Window for Hybrid Automatic/Manual Orthodontic Wire Generator

This module provides the main application window that integrates:
- Enhanced control panel with hybrid workflow
- Dual-arch 3D visualizer
- Status panel with comprehensive information
- Professional layout and user experience
"""

import sys
import os
import numpy as np
from typing import Optional, Dict, Any

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
        QMenuBar, QStatusBar, QAction, QMessageBox, QApplication,
        QProgressBar, QLabel, QFrame
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal
    from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
    PYQT5_AVAILABLE = True
except ImportError:
    print("PyQt5 not available, falling back to tkinter implementation")
    PYQT5_AVAILABLE = False

from core.workflow_manager import WorkflowManager, WorkflowMode
from gui.enhanced_control_panel import EnhancedControlPanel
from visualization.dual_arch_visualizer import DualArchVisualizer
from gui.status_panel import StatusPanel


class EnhancedMainWindow(QMainWindow if PYQT5_AVAILABLE else object):
    """
    Main application window with hybrid workflow support
    """
    
    def __init__(self):
        if PYQT5_AVAILABLE:
            super().__init__()
        
        # Initialize workflow manager
        self.workflow_manager = WorkflowManager()
        
        # Initialize UI components
        self.control_panel = None
        self.visualizer = None
        self.status_panel = None
        
        # Status tracking
        self.current_status = "Ready"
        self.progress_bar = None
        
        if PYQT5_AVAILABLE:
            self.init_ui()
            self.setup_connections()
            self.setup_styling()
        else:
            self.init_fallback_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Orthodontic Wire Generator - Professional Hybrid Edition")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # LEFT PANEL - Enhanced Control Panel
        self.control_panel = EnhancedControlPanel(self.workflow_manager)
        self.control_panel.setMinimumWidth(350)
        self.control_panel.setMaximumWidth(450)
        splitter.addWidget(self.control_panel)
        
        # CENTER - 3D Visualization
        self.visualizer = DualArchVisualizer()
        self.visualizer.setMinimumWidth(800)
        splitter.addWidget(self.visualizer)
        
        # RIGHT PANEL - Status and Information
        self.status_panel = EnhancedStatusPanel()
        self.status_panel.setMinimumWidth(300)
        self.status_panel.setMaximumWidth(400)
        splitter.addWidget(self.status_panel)
        
        # Set splitter proportions
        splitter.setSizes([350, 900, 350])

        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.create_status_bar()
        
        # Set window icon (if available)
        try:
            self.setWindowIcon(QIcon('assets/icon.png'))
        except:
            pass
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # New project
        new_action = QAction('New Project', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        # Open project
        open_action = QAction('Open Project', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        # Save project
        save_action = QAction('Save Project', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        # Reset camera
        reset_camera_action = QAction('Reset Camera', self)
        reset_camera_action.setShortcut('R')
        reset_camera_action.triggered.connect(self.reset_camera)
        view_menu.addAction(reset_camera_action)
        
        # Toggle panels
        toggle_control_action = QAction('Toggle Control Panel', self)
        toggle_control_action.setShortcut('F1')
        toggle_control_action.triggered.connect(self.toggle_control_panel)
        view_menu.addAction(toggle_control_action)
        
        toggle_status_action = QAction('Toggle Status Panel', self)
        toggle_status_action.setShortcut('F2')
        toggle_status_action.triggered.connect(self.toggle_status_panel)
        view_menu.addAction(toggle_status_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        # Workflow mode shortcuts
        auto_mode_action = QAction('Automatic Mode', self)
        auto_mode_action.setShortcut('F3')
        auto_mode_action.triggered.connect(lambda: self.set_workflow_mode('automatic'))
        tools_menu.addAction(auto_mode_action)
        
        manual_mode_action = QAction('Manual Mode', self)
        manual_mode_action.setShortcut('F4')
        manual_mode_action.triggered.connect(lambda: self.set_workflow_mode('manual'))
        tools_menu.addAction(manual_mode_action)
        
        hybrid_mode_action = QAction('Hybrid Mode', self)
        hybrid_mode_action.setShortcut('F5')
        hybrid_mode_action.triggered.connect(lambda: self.set_workflow_mode('hybrid'))
        tools_menu.addAction(hybrid_mode_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        # About
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # User guide
        guide_action = QAction('User Guide', self)
        guide_action.triggered.connect(self.show_user_guide)
        help_menu.addAction(guide_action)
    
    def create_status_bar(self):
        """Create the application status bar"""
        status_bar = self.statusBar()
        
        # Status label
        self.status_label = QLabel("Ready - Hybrid Orthodontic Wire Generator")
        status_bar.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        status_bar.addPermanentWidget(self.progress_bar)
        
        # Mode indicator
        self.mode_label = QLabel("Mode: Automatic")
        self.mode_label.setStyleSheet("QLabel { background-color: #4CAF50; color: white; padding: 2px 8px; border-radius: 3px; }")
        status_bar.addPermanentWidget(self.mode_label)
    
    def setup_connections(self):
        """Setup signal-slot connections between components"""
        # Control panel signals
        self.control_panel.arch_loaded.connect(self.on_arch_loaded)
        self.control_panel.mode_changed.connect(self.on_mode_changed)
        self.control_panel.active_arch_changed.connect(self.on_active_arch_changed)
        self.control_panel.show_both_changed.connect(self.on_show_both_changed)
        self.control_panel.wire_generated.connect(self.on_wire_generated)
        self.control_panel.interaction_mode_requested.connect(self.on_interaction_mode_requested)
        self.control_panel.control_points_converted.connect(self.on_control_points_converted)
        self.control_panel.gcode_exported.connect(self.on_gcode_exported)
        self.control_panel.jaw_rotation_changed.connect(self.on_jaw_rotation_changed)
        
        # Visualizer signals
        self.visualizer.point_added.connect(self.on_point_added)
        self.visualizer.point_moved.connect(self.on_point_moved)
        self.visualizer.interaction_mode_changed.connect(self.on_interaction_mode_changed)
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_display)
        self.status_timer.start(1000)  # Update every second
    
    def setup_styling(self):
        """Setup application styling and theme"""
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                font-size: 12px;
                border-radius: 4px;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 10px;
                border-radius: 4px;
            }
            
            QSlider::sub-page:horizontal {
                background: #4CAF50;
                border: 1px solid #777;
                height: 10px;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #777;
                width: 18px;
                margin-top: -2px;
                margin-bottom: -2px;
                border-radius: 3px;
            }
            
            QRadioButton::indicator {
                width: 13px;
                height: 13px;
            }
            
            QRadioButton::indicator:unchecked {
                border: 2px solid #cccccc;
                border-radius: 7px;
                background-color: white;
            }
            
            QRadioButton::indicator:checked {
                border: 2px solid #4CAF50;
                border-radius: 7px;
                background-color: #4CAF50;
            }
        """)
    
    # ============================================
    # EVENT HANDLERS
    # ============================================
    
    def on_arch_loaded(self, arch_type: str, file_path: str):
        """Handle arch loading"""
        try:
            arch_data = self.workflow_manager.get_arch_data(arch_type)
            if arch_data:
                self.visualizer.load_arch(arch_data['mesh'], arch_type)
                self.status_panel.update_arch_info(arch_type, file_path)
                self.update_status(f"{arch_type.capitalize()} arch loaded successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load {arch_type} arch:\n{str(e)}")
    
    def on_mode_changed(self, mode: str):
        """Handle workflow mode change"""
        self.update_mode_display(mode)
        self.status_panel.update_workflow_mode(mode)
        self.update_status(f"Switched to {mode} mode")
    
    def on_active_arch_changed(self, arch_type: str):
        """Handle active arch change and synchronize the visualizer's state."""
        self.visualizer.set_active_arch(arch_type)
        self.status_panel.update_active_arch(arch_type)
        self.update_status(f"Active arch: {arch_type}")

        # Synchronize the visualizer with the data from the new active arch
        arch_data = self.workflow_manager.get_arch_data(arch_type)
        if arch_data:
            # If data exists for this arch, load it into the visualizer
            self.visualizer.control_points = arch_data.get('control_points', [])
            self.visualizer.wire_path = arch_data.get('wire_path', None)
            self.visualizer.detected_teeth = arch_data.get('teeth_detected', [])
            self.visualizer.bracket_positions = arch_data.get('bracket_positions', [])
        else:
            # If no data exists (e.g., arch not loaded yet), clear the visualizer
            self.visualizer.control_points = []
            self.visualizer.wire_path = None
            self.visualizer.detected_teeth = []
            self.visualizer.bracket_positions = []

        self.visualizer.update()
    
    def on_show_both_changed(self, show_both: bool):
        """Handle show both arches toggle"""
        self.visualizer.set_show_both_arches(show_both)
        status = "both arches" if show_both else "active arch only"
        self.update_status(f"Display mode: {status}")
    
    def on_wire_generated(self):
        """Handle wire generation completion"""
        arch_type = self.workflow_manager.get_active_arch()
        arch_data = self.workflow_manager.get_active_arch_data()
        
        if arch_data and arch_data['wire_path'] is not None:
            self.visualizer.display_wire_path(arch_data['wire_path'])
            self.status_panel.update_wire_info(arch_data['wire_path'])
            self.update_status("Wire generated successfully")
    
    def on_point_added(self, point: np.ndarray, point_type: str):
        """Handle point addition in visualizer and update workflow manager."""
        try:
            if point_type == 'plane':
                if len(self.workflow_manager.occlusal_plane_points) < 3:
                    self.workflow_manager.occlusal_plane_points.append(point)
                    count = len(self.workflow_manager.occlusal_plane_points)
                    self.update_status(f"Occlusal plane point {count}/3 added")

                    # Update the control panel button text
                    if hasattr(self.control_panel, 'start_plane_btn'):
                        self.control_panel.start_plane_btn.setText(f"Placing Points... ({count}/3)")

                    if count == 3:
                        self.workflow_manager.set_occlusal_plane_points(self.workflow_manager.occlusal_plane_points)
                        self.update_status("Occlusal plane defined. You can now place control points.")
                        if hasattr(self.control_panel, 'start_points_btn'):
                            self.control_panel.start_points_btn.setEnabled(True)  # Enable next step

            elif point_type == 'control':
                active_arch = self.workflow_manager.get_active_arch()
                self.workflow_manager.add_control_point(point, active_arch)

                arch_data = self.workflow_manager.get_active_arch_data()
                if arch_data:
                    count = len(arch_data['control_points'])
                    self.update_status(f"Control point {count} added")

                    # Update control panel button text
                    if hasattr(self.control_panel, 'start_points_btn'):
                        self.control_panel.start_points_btn.setText(f"Placing Points ({count})")
                    if hasattr(self.control_panel, 'generate_wire_btn') and count >= 2:
                        self.control_panel.generate_wire_btn.setEnabled(True)

        except Exception as e:
            self.update_status(f"Error adding point: {str(e)}")
    
    def on_point_moved(self, index: int, new_position):
        """Handle point movement in visualizer and regenerate the wire."""
        try:
            self.workflow_manager.update_control_point(index, new_position)
            self.update_status(f"Control point {index + 1} moved")

            # Regenerate the wire to reflect the change in real-time
            self.workflow_manager.generate_wire_from_control_points()
            self.on_wire_generated()

        except Exception as e:
            self.update_status(f"Error updating wire: {str(e)}")
    
    def on_interaction_mode_changed(self, mode: str):
        """Handle interaction mode change"""
        mode_descriptions = {
            'VIEW': 'View mode - rotate camera with right mouse',
            'DEFINE_PLANE': 'Click on 3 tooth tips to define occlusal plane',
            'PLACE_POINTS': 'Click on tooth surfaces to place control points',
            'DRAG_POINTS': 'Drag control points to adjust wire path',
            'EDIT_POINTS': 'Edit control points - click and drag to modify'
        }
        
        description = mode_descriptions.get(mode, f"Mode: {mode}")
        self.update_status(description)

    def on_interaction_mode_requested(self, mode: str):
        """Handle request to change interaction mode from control panel"""
        self.visualizer.set_interaction_mode(mode)
        self.update_status(f"Switched to {mode} mode")

    def on_control_points_converted(self, control_points: list):
        """Handle the conversion of an automatic wire to manual control points."""
        if self.visualizer:
            self.visualizer.display_editable_control_points(control_points)
        self.update_status(f"Converted to {len(control_points)} manual control points. Ready for editing.")

    def on_gcode_exported(self, gcode_content: str):
        """Display the generated G-code in the status panel's code viewer."""
        if self.status_panel:
            self.status_panel.display_exported_code(gcode_content)

    def on_jaw_rotation_changed(self, angle: int):
        """Handle the jaw rotation slider change and update the visualizer."""
        if self.visualizer:
            self.visualizer.set_jaw_rotation(angle)

    # ============================================
    # MENU ACTIONS
    # ============================================
    
    def new_project(self):
        """Create a new project"""
        reply = QMessageBox.question(
            self, 'New Project', 
            'Are you sure you want to start a new project? All unsaved changes will be lost.',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.workflow_manager.reset_workflow()
            self.visualizer.clear_control_points()
            self.visualizer.clear_plane()
            self.status_panel.reset_display()
            self.update_status("New project created")
    
    def open_project(self):
        """Open an existing project"""
        # This would implement project file loading
        QMessageBox.information(self, "Open Project", "Project loading not yet implemented")
    
    def save_project(self):
        """Save the current project"""
        # This would implement project file saving
        QMessageBox.information(self, "Save Project", "Project saving not yet implemented")
    
    def reset_camera(self):
        """Reset camera to default position"""
        if hasattr(self.visualizer, 'camera_rotation'):
            self.visualizer.camera_rotation = [0, 0]
            self.visualizer.camera_distance = 100
            self.visualizer.update()
        self.update_status("Camera reset to default position")
    
    def toggle_control_panel(self):
        """Toggle control panel visibility"""
        self.control_panel.setVisible(not self.control_panel.isVisible())
    
    def toggle_status_panel(self):
        """Toggle status panel visibility"""
        self.status_panel.setVisible(not self.status_panel.isVisible())
    
    def set_workflow_mode(self, mode: str):
        """Set workflow mode via menu"""
        mode_map = {
            'automatic': WorkflowMode.AUTOMATIC,
            'manual': WorkflowMode.MANUAL,
            'hybrid': WorkflowMode.HYBRID
        }
        
        if mode in mode_map:
            self.workflow_manager.set_mode(mode_map[mode])
            # Update control panel radio buttons
            if mode == 'automatic':
                self.control_panel.mode_automatic.setChecked(True)
            elif mode == 'manual':
                self.control_panel.mode_manual.setChecked(True)
            else:
                self.control_panel.mode_hybrid.setChecked(True)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, 
            "About Orthodontic Wire Generator",
            """
            <h3>Orthodontic Wire Generator</h3>
            <p><b>Professional Hybrid Edition</b></p>
            <p>Version 2.0</p>
            <p>A comprehensive tool for designing orthodontic wires with both automatic and manual workflows.</p>
            <p><b>Features:</b></p>
            <ul>
                <li>Automatic tooth detection and wire generation</li>
                <li>Manual control point placement (FixR style)</li>
                <li>Hybrid workflow combining both approaches</li>
                <li>Dual-arch support</li>
                <li>Collision detection</li>
                <li>Multiple export formats</li>
            </ul>
            <p>© 2024 Orthodontic Wire Generator Team</p>
            """
        )
    
    def show_user_guide(self):
        """Show user guide"""
        guide_text = """
        <h3>User Guide - Quick Start</h3>
        
        <h4>Automatic Mode:</h4>
        <ol>
            <li>Load upper or lower arch STL file</li>
            <li>Automatic detection runs immediately</li>
            <li>Review and adjust wire height if needed</li>
            <li>Export your design</li>
        </ol>
        
        <h4>Manual Mode:</h4>
        <ol>
            <li>Load arch STL file</li>
            <li>Define occlusal plane (3 points)</li>
            <li>Place control points on tooth surfaces</li>
            <li>Generate wire from control points</li>
            <li>Export your design</li>
        </ol>
        
        <h4>Hybrid Mode:</h4>
        <ol>
            <li>Load arch STL file</li>
            <li>Run automatic detection</li>
            <li>Convert to manual control points</li>
            <li>Drag points to refine the wire</li>
            <li>Export your design</li>
        </ol>
        
        <h4>Keyboard Shortcuts:</h4>
        <ul>
            <li>F3: Automatic Mode</li>
            <li>F4: Manual Mode</li>
            <li>F5: Hybrid Mode</li>
            <li>R: Reset Camera</li>
            <li>F1: Toggle Control Panel</li>
            <li>F2: Toggle Status Panel</li>
        </ul>
        """
        
        QMessageBox.information(self, "User Guide", guide_text)
    
    # ============================================
    # STATUS AND DISPLAY UPDATES
    # ============================================
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.current_status = message
        self.status_label.setText(message)
    
    def update_mode_display(self, mode: str):
        """Update mode indicator in status bar"""
        mode_colors = {
            'automatic': '#4CAF50',  # Green
            'manual': '#2196F3',     # Blue
            'hybrid': '#FF9800'      # Orange
        }
        
        color = mode_colors.get(mode, '#666666')
        self.mode_label.setText(f"Mode: {mode.capitalize()}")
        self.mode_label.setStyleSheet(
            f"QLabel {{ background-color: {color}; color: white; padding: 2px 8px; border-radius: 3px; }}"
        )
    
    def update_status_display(self):
        """Update status display periodically"""
        # Update workflow status in status panel
        status = self.workflow_manager.get_workflow_status()
        self.status_panel.update_workflow_status(status)
    
    def show_progress(self, message: str, maximum: int = 0):
        """Show progress bar with message"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(0)
        self.update_status(message)
    
    def update_progress(self, value: int):
        """Update progress bar value"""
        self.progress_bar.setValue(value)
    
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.setVisible(False)
    
    # ============================================
    # WINDOW EVENTS
    # ============================================
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self, 'Exit Application', 
            'Are you sure you want to exit? Any unsaved changes will be lost.',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
    
    def init_fallback_ui(self):
        """Initialize fallback UI for systems without PyQt5"""
        print("Enhanced Main Window - Fallback Mode")
        print("PyQt5 not available. Please install PyQt5 for full functionality.")


class EnhancedStatusPanel(QWidget if PYQT5_AVAILABLE else object):
    """Enhanced status panel with comprehensive information display and code viewer."""
    
    def __init__(self, parent=None):
        if PYQT5_AVAILABLE:
            super().__init__(parent)
            self.init_ui()
    
    def init_ui(self):
        """Initialize status panel UI"""
        from PyQt5.QtWidgets import QTextEdit, QGroupBox, QFrame
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
        # This would update the arches loaded count
        pass
    
    def update_wire_info(self, wire_path):
        """Update wire information"""
        if PYQT5_AVAILABLE and wire_path is not None:
            # Calculate wire length
            length = self.calculate_wire_length(wire_path)
            self.wire_length_status.setText(f"Length: {length:.2f} mm")
    
    def update_workflow_status(self, status: Dict[str, Any]):
        """Update comprehensive workflow status"""
        if PYQT5_AVAILABLE:
            # Update arches loaded count
            upper_loaded = 1 if status.get('upper_loaded', False) else 0
            lower_loaded = 1 if status.get('lower_loaded', False) else 0
            total_loaded = upper_loaded + lower_loaded
            self.arches_loaded_status.setText(f"Arches Loaded: {total_loaded}/2")
            
            # Update height offset
            height_offset = status.get('height_offset', 0.0)
            self.height_offset_status.setText(f"Height Offset: {height_offset:.1f} mm")
    
    def calculate_wire_length(self, wire_path) -> float:
        """Calculate total wire length"""
        if len(wire_path) < 2:
            return 0.0
        
        total_length = 0.0
        for i in range(1, len(wire_path)):
            segment_length = np.linalg.norm(wire_path[i] - wire_path[i-1])
            total_length += segment_length
        
        return total_length
    
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


# Main application entry point
def main():
    """Main application entry point"""
    if PYQT5_AVAILABLE:
        app = QApplication(sys.argv)
        app.setApplicationName("Orthodontic Wire Generator")
        app.setApplicationVersion("2.0")
        
        # Set application icon
        try:
            app.setWindowIcon(QIcon('assets/icon.png'))
        except:
            pass
        
        # Create and show main window
        window = EnhancedMainWindow()
        window.show()
        
        sys.exit(app.exec_())
    else:
        print("PyQt5 not available. Please install PyQt5 to run the enhanced GUI.")
        print("pip install PyQt5 PyOpenGL")


if __name__ == '__main__':
    main()
