
# ================================================================
# gui/control_panel.py
"""Left control panel for wire generation parameters."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Callable, Optional

class ControlPanel:
    """Left control panel for wire generation parameters and controls."""
    
    def __init__(self, parent_frame, wire_generator_gui):
        """Initialize control panel."""
        self.parent = parent_frame
        self.gui = wire_generator_gui
        
        # Main control frame
        self.control_frame = ttk.LabelFrame(parent_frame, text="Generation Controls", padding="10")
        self.control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Setup all control sections
        self.setup_stl_section()
        self.setup_wire_parameters()
        self.setup_height_controls()
        self.setup_advanced_settings()
        
    def setup_stl_section(self):
        """Setup STL file loading section."""
        stl_frame = ttk.LabelFrame(self.control_frame, text="STL Input", padding="5")
        stl_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        stl_frame.columnconfigure(1, weight=1)
        
        # Load STL button
        ttk.Button(
            stl_frame, 
            text="Load STL File", 
            command=self.load_stl_file,
            style="Accent.TButton"
        ).grid(row=0, column=0, padx=(0, 10))
        
        # STL file status label
        self.stl_label = ttk.Label(stl_frame, text="No file selected", foreground="gray")
        self.stl_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # STL info display
        self.stl_info_text = tk.Text(stl_frame, height=3, width=40, font=("Consolas", 8))
        self.stl_info_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        self.stl_info_text.insert(1.0, "Load an STL file to see mesh information")
        self.stl_info_text.config(state=tk.DISABLED)
    
    def setup_wire_parameters(self):
        """Setup wire parameter controls."""
        params_frame = ttk.LabelFrame(self.control_frame, text="Wire Parameters", padding="5")
        params_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        params_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Wire Size
        ttk.Label(params_frame, text="Wire Size:").grid(row=row, column=0, sticky=tk.W, pady=2)
        wire_combo = ttk.Combobox(
            params_frame,
            textvariable=self.gui.wire_size,
            values=list(self.gui.WIRE_SIZES.keys()) if hasattr(self.gui, 'WIRE_SIZES') else 
                   ['0.012', '0.014', '0.016', '0.018', '0.020'],
            state="readonly",
            width=15
        )
        wire_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        row += 1
        
        # Arch Type
        ttk.Label(params_frame, text="Arch Type:").grid(row=row, column=0, sticky=tk.W, pady=2)
        arch_combo = ttk.Combobox(
            params_frame,
            textvariable=self.gui.arch_type,
            values=["auto", "upper", "lower"],
            state="readonly",
            width=15
        )
        arch_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        row += 1
        
        # Bend Radius
        ttk.Label(params_frame, text="Bend Radius (mm):").grid(row=row, column=0, sticky=tk.W, pady=2)
        bend_spin = ttk.Spinbox(
            params_frame,
            from_=0.5,
            to=10.0,
            increment=0.1,
            textvariable=self.gui.bend_radius,
            width=15
        )
        bend_spin.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        row += 1
        
        # Wire Tension
        ttk.Label(params_frame, text="Wire Tension:").grid(row=row, column=0, sticky=tk.W, pady=2)
        tension_spin = ttk.Spinbox(
            params_frame,
            from_=0.1,
            to=2.0,
            increment=0.1,
            textvariable=self.gui.wire_tension,
            width=15
        )
        tension_spin.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
    
    def setup_height_controls(self):
        """Setup height control section."""
        height_frame = ttk.LabelFrame(self.control_frame, text="Height Control", padding="5")
        height_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        height_frame.columnconfigure(1, weight=1)
        
        # Current height offset display
        ttk.Label(height_frame, text="Height Offset (mm):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.height_display = ttk.Label(
            height_frame, 
            textvariable=self.gui.height_offset, 
            foreground="blue",
            font=("Arial", 10, "bold")
        )
        self.height_display.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Height step size
        ttk.Label(height_frame, text="Height Step (mm):").grid(row=1, column=0, sticky=tk.W, pady=2)
        height_step_spin = ttk.Spinbox(
            height_frame,
            from_=0.1,
            to=2.0,
            increment=0.1,
            textvariable=self.gui.height_step,
            width=15
        )
        height_step_spin.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Height control buttons
        btn_frame = ttk.Frame(height_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(
            btn_frame, 
            text="↑ UP", 
            command=self.gui.wire_up,
            width=8
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            btn_frame, 
            text="↓ DOWN", 
            command=self.gui.wire_down,
            width=8
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            btn_frame, 
            text="Reset", 
            command=self.gui.reset_height,
            width=8
        ).pack(side=tk.LEFT)
        
        # Height history display
        history_frame = ttk.Frame(height_frame)
        history_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(history_frame, text="Height History:", font=("Arial", 8)).pack(anchor=tk.W)
        
        self.height_history = tk.Listbox(history_frame, height=3, font=("Consolas", 8))
        self.height_history.pack(fill=tk.X, pady=(2, 0))
        
        # Populate with initial value
        self.height_history.insert(tk.END, f"0.00mm (initial)")
    
    def setup_advanced_settings(self):
        """Setup advanced/expert settings."""
        advanced_frame = ttk.LabelFrame(self.control_frame, text="Advanced Settings", padding="5")
        advanced_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Collapsible advanced settings
        self.advanced_visible = tk.BooleanVar(value=False)
        
        # Toggle button
        self.advanced_toggle = ttk.Checkbutton(
            advanced_frame,
            text="Show Advanced Settings",
            variable=self.advanced_visible,
            command=self.toggle_advanced_settings
        )
        self.advanced_toggle.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # Advanced settings container (initially hidden)
        self.advanced_container = ttk.Frame(advanced_frame)
        # Will be gridded when advanced settings are shown
        
        # Advanced parameter controls
        self.setup_advanced_parameters()
    
    def setup_advanced_parameters(self):
        """Setup advanced parameter controls."""
        # Smoothing factor
        ttk.Label(self.advanced_container, text="Smoothing Factor:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.smoothing_var = tk.DoubleVar(value=0.1)
        smoothing_spin = ttk.Spinbox(
            self.advanced_container,
            from_=0.0,
            to=1.0,
            increment=0.05,
            textvariable=self.smoothing_var,
            width=10
        )
        smoothing_spin.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Path resolution
        ttk.Label(self.advanced_container, text="Path Resolution:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.resolution_var = tk.IntVar(value=100)
        resolution_spin = ttk.Spinbox(
            self.advanced_container,
            from_=20,
            to=500,
            increment=10,
            textvariable=self.resolution_var,
            width=10
        )
        resolution_spin.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Mesh quality
        ttk.Label(self.advanced_container, text="Mesh Quality:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.mesh_quality_var = tk.StringVar(value="normal")
        quality_combo = ttk.Combobox(
            self.advanced_container,
            textvariable=self.mesh_quality_var,
            values=["low", "normal", "high", "ultra"],
            state="readonly",
            width=10
        )
        quality_combo.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
    
    def toggle_advanced_settings(self):
        """Toggle visibility of advanced settings."""
        if self.advanced_visible.get():
            self.advanced_container.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        else:
            self.advanced_container.grid_remove()
    
    def load_stl_file(self):
        """Handle STL file loading."""
        file_path = filedialog.askopenfilename(
            title="Select STL File",
            filetypes=[
                ("STL files", "*.stl"),
                ("All files", "*.*")
            ],
            initialdir=os.getcwd()
        )
        
        if file_path:
            self.gui.stl_path = file_path
            filename = os.path.basename(file_path)
            
            # Update display
            self.stl_label.config(text=f"✓ {filename}", foreground="green")
            
            # Auto-detect arch type from filename
            if 'lower' in filename.lower():
                self.gui.arch_type.set('lower')
            elif 'upper' in filename.lower():
                self.gui.arch_type.set('upper')
            else:
                self.gui.arch_type.set('auto')
            
            # Update info display
            self.update_stl_info(file_path)
            
            # Update main GUI status
            self.gui.status.set("STL file loaded - Ready to generate")
    
    def update_stl_info(self, file_path: str):
        """Update STL file information display."""
        try:
            # Get file info
            stat = os.stat(file_path)
            file_size_mb = stat.st_size / (1024 * 1024)
            
            info_text = f"File: {os.path.basename(file_path)}\n"
            info_text += f"Size: {file_size_mb:.1f} MB\n"
            info_text += f"Type: {self.gui.arch_type.get().upper()} arch (auto-detected)"
            
            self.stl_info_text.config(state=tk.NORMAL)
            self.stl_info_text.delete(1.0, tk.END)
            self.stl_info_text.insert(1.0, info_text)
            self.stl_info_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.stl_info_text.config(state=tk.NORMAL)
            self.stl_info_text.delete(1.0, tk.END)
            self.stl_info_text.insert(1.0, f"Error reading file info: {e}")
            self.stl_info_text.config(state=tk.DISABLED)
    
    def update_height_history(self, new_height: float, action: str = "adjustment"):
        """Update height adjustment history."""
        self.height_history.insert(tk.END, f"{new_height:+.2f}mm ({action})")
        self.height_history.see(tk.END)  # Scroll to bottom
        
        # Limit history length
        if self.height_history.size() > 10:
            self.height_history.delete(0)
    
    def get_advanced_settings(self) -> dict:
        """Get current advanced settings."""
        return {
            'smoothing_factor': self.smoothing_var.get(),
            'path_resolution': self.resolution_var.get(),
            'mesh_quality': self.mesh_quality_var.get()
        }
    
    def reset_all_parameters(self):
        """Reset all parameters to defaults."""
        self.gui.wire_size.set('0.018')
        self.gui.arch_type.set('auto')
        self.gui.bend_radius.set(2.0)
        self.gui.wire_tension.set(1.0)
        self.gui.height_offset.set(0.0)
        self.gui.height_step.set(0.5)
        
        # Advanced settings
        self.smoothing_var.set(0.1)
        self.resolution_var.set(100)
        self.mesh_quality_var.set('normal')
        
        # Clear height history
        self.height_history.delete(0, tk.END)
        self.height_history.insert(tk.END, "0.00mm (reset)")
