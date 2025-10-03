#!/usr/bin/env python3
"""
GUI and Utility Components
=========================
Final components to complete the modular architecture.
"""

# ================================================================
# gui/main_window.py
"""Main GUI application using the modular architecture."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import time
from typing import Optional

from wire.wire_generator import WireGenerator
from core.constants import WIRE_SIZES

class WireGeneratorGUI:
    """Main GUI application using modular components."""
    
    def __init__(self):
        """Initialize the modular GUI application."""
        self.root = tk.Tk()
        self.root.title("Modular Orthodontic Wire Generator")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Core modular generator
        self.generator: Optional[WireGenerator] = None
        self.stl_path = None
        
        # GUI variables
        self.wire_size = tk.StringVar(value='0.018')
        self.arch_type = tk.StringVar(value='auto')
        self.bend_radius = tk.DoubleVar(value=2.0)
        self.wire_tension = tk.DoubleVar(value=1.0)
        self.height_offset = tk.DoubleVar(value=0.0)
        self.height_step = tk.DoubleVar(value=0.5)
        
        # Status variables
        self.status = tk.StringVar(value="Ready - Modular Architecture")
        self.teeth_count = tk.StringVar(value="0")
        self.brackets_count = tk.StringVar(value="0")
        self.wire_length = tk.StringVar(value="0.0")
        
        # Display content tracking
        self.displayed_code_type = None
        self.displayed_code_content = ""
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the main GUI interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Modular Orthodontic Wire Generator",
            font=("Arial", 16, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        subtitle_label = tk.Label(
            main_frame,
            text="Refactored Architecture • Separated Drawing Components • Modular Design",
            font=("Arial", 10, "italic"),
            bg='#f0f0f0',
            fg='#7f8c8d'
        )
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # Setup panels
        self.setup_control_panel(main_frame)
        self.setup_status_panel(main_frame)
        self.setup_output_panel(main_frame)
        self.setup_action_panel(main_frame)
    
    def setup_control_panel(self, parent):
        """Setup the left control panel."""
        control_frame = ttk.LabelFrame(parent, text="Generation Controls", padding="10")
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # STL File Section
        stl_frame = ttk.LabelFrame(control_frame, text="STL Input", padding="5")
        stl_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        stl_frame.columnconfigure(1, weight=1)
        
        ttk.Button(stl_frame, text="Load STL", command=self.load_stl_file).grid(row=0, column=0, padx=(0, 10))
        self.stl_label = ttk.Label(stl_frame, text="No file selected", foreground="gray")
        self.stl_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Wire Parameters
        params_frame = ttk.LabelFrame(control_frame, text="Wire Parameters", padding="5")
        params_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Parameter controls
        row = 0
        for label, var, values in [
            ("Wire Size:", self.wire_size, list(WIRE_SIZES.keys())),
            ("Arch Type:", self.arch_type, ["auto", "upper", "lower"])
        ]:
            ttk.Label(params_frame, text=label).grid(row=row, column=0, sticky=tk.W, pady=2)
            combo = ttk.Combobox(params_frame, textvariable=var, values=values, state="readonly", width=15)
            combo.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
            row += 1
        
        # Numeric parameters
        for label, var, range_vals in [
            ("Bend Radius (mm):", self.bend_radius, (0.5, 10.0, 0.1)),
            ("Wire Tension:", self.wire_tension, (0.1, 2.0, 0.1))
        ]:
            ttk.Label(params_frame, text=label).grid(row=row, column=0, sticky=tk.W, pady=2)
            spin = ttk.Spinbox(params_frame, from_=range_vals[0], to=range_vals[1], 
                             increment=range_vals[2], textvariable=var, width=15)
            spin.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
            row += 1
        
        # Height Control Section
        height_frame = ttk.LabelFrame(control_frame, text="Height Control (Modular)", padding="5")
        height_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(height_frame, text="Height Offset:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.height_display = ttk.Label(height_frame, textvariable=self.height_offset, foreground="blue")
        self.height_display.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        ttk.Label(height_frame, text="Height Step:").grid(row=1, column=0, sticky=tk.W, pady=2)
        height_step_spin = ttk.Spinbox(height_frame, from_=0.1, to=2.0, increment=0.1, 
                                     textvariable=self.height_step, width=15)
        height_step_spin.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Height control buttons
        btn_frame = ttk.Frame(height_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        
        ttk.Button(btn_frame, text="↑ UP", command=self.wire_up, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="↓ DOWN", command=self.wire_down, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Reset", command=self.reset_height, width=8).pack(side=tk.LEFT)
    
    def setup_status_panel(self, parent):
        """Setup the center status panel."""
        status_frame = ttk.LabelFrame(parent, text="Generation Status", padding="10")
        status_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(1, weight=1)
        
        # Status display
        info_frame = ttk.Frame(status_frame)
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        # Status indicators
        ttk.Label(info_frame, text="Status:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(info_frame, textvariable=self.status).grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(info_frame, text="Teeth:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W)
        ttk.Label(info_frame, textvariable=self.teeth_count).grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(info_frame, text="Wire Length:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky=tk.W)
        ttk.Label(info_frame, textvariable=self.wire_length).grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(info_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Architecture info display
        arch_frame = ttk.Frame(status_frame, relief="sunken", borderwidth=2)
        arch_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.arch_text = scrolledtext.ScrolledText(
            arch_frame, height=20, width=50, font=("Consolas", 9), wrap=tk.WORD
        )
        self.arch_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Display architecture info
        self.show_architecture_info()
        
        # 3D Editor button
        ttk.Button(
            status_frame,
            text="Launch 3D Interactive Editor",
            command=self.launch_3d_editor,
            style="Accent.TButton"
        ).grid(row=2, column=0, pady=(10, 0))
    
    def setup_output_panel(self, parent):
        """Setup the right output panel."""
        output_frame = ttk.LabelFrame(parent, text="Generated Output", padding="10")
        output_frame.grid(row=2, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(1, weight=1)
        
        # Output controls
        controls_frame = ttk.Frame(output_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(controls_frame, text="G-code", command=self.show_gcode).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="ESP32", command=self.show_esp32).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Export", command=self.export_code).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Clear", command=self.clear_output).pack(side=tk.LEFT)
        
        # Output display
        self.output_text = scrolledtext.ScrolledText(
            output_frame, width=50, height=30, font=("Consolas", 9),
            bg="black", fg="lime", insertbackground="lime", wrap=tk.NONE
        )
        self.output_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def setup_action_panel(self, parent):
        """Setup the bottom action panel."""
        action_frame = ttk.Frame(parent, padding="10")
        action_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Main actions
        ttk.Button(action_frame, text="Generate Wire", command=self.generate_wire, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Save Design", command=self.save_design).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Export STL", command=self.export_stl).pack(side=tk.LEFT, padx=(0, 10))
        
        # Info buttons
        ttk.Button(action_frame, text="Architecture Info", command=self.show_architecture_dialog).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(action_frame, text="Help", command=self.show_help).pack(side=tk.RIGHT, padx=(10, 0))
    
    def show_architecture_info(self):
        """Display architecture information in the status panel."""
        info_text = """MODULAR ARCHITECTURE OVERVIEW"""

# 🎯 WIRE DRAWING COMPONENTS:
# ├── WirePathCreator (wire/wire_path_creator.py)
# │   └── create_smooth_path() - Core drawing algorithm
# │       ├── Spline interpolation
# │       ├── Control point management
# │       └── Height offset application
# │
# └── WireMeshBuilder (wire/wire_mesh_builder.py)
#     └── build_wire_mesh() - 3D mesh creation
#         ├── Cylindrical segments
#         ├── Material properties
#         └── Mesh optimization

# 🏗️ CORE COMPONENTS:
# ├── MeshProcessor - STL loading/cleaning
# ├── ToothDetector - Anatomical analysis
# ├── BracketPositioner - Clinical placement
# └── HeightController - Height management

# 📤 EXPORT MODULES:
# ├── GCodeGenerator - CNC instructions
# ├── ESP32Generator - Arduino code
# └── STLExporter - 3D model export

# 🔄 DATA FLOW:
# STL → MeshProcessor → ToothDetector → BracketPositioner
# → WirePathCreator (ALGORITHM) → WireMeshBuilder (RENDERING)
# → HeightController → Visualization → Export

# ✅ BENEFITS:
# • Separation of Concerns
# • Modular Development
# • Independent Testing
# • Easy Maintenance
# • Clear Wire Drawing Logic"""
        
        self.arch_text.delete(1.0, tk.END)
        self.arch_text.insert(1.0, info_text)
        self.arch_text.config(state=tk.DISABLED)
    
    # Core functionality methods
    def load_stl_file(self):
        """Load STL file using modular architecture."""
        file_path = filedialog.askopenfilename(
            title="Select STL File",
            filetypes=[("STL files", "*.stl"), ("All files", "*.*")]
        )
        
        if file_path:
            self.stl_path = file_path
            filename = os.path.basename(file_path)
            self.stl_label.config(text=f"✓ {filename}", foreground="green")
            
            # Auto-detect arch type
            if 'lower' in filename.lower():
                self.arch_type.set('lower')
            elif 'upper' in filename.lower():
                self.arch_type.set('upper')
            
            self.status.set("STL loaded - Ready to generate")
    
    def generate_wire(self):
        """Generate wire using modular architecture."""
        if not self.stl_path:
            messagebox.showerror("Error", "Please load an STL file first!")
            return
        
        self.progress.start()
        self.status.set("Generating wire using modular components...")
        
        thread = threading.Thread(target=self._generate_wire_thread, daemon=True)
        thread.start()
    
    def _generate_wire_thread(self):
        """Wire generation thread using modular components."""
        try:
            # Create modular generator
            self.generator = WireGenerator(
                stl_path=self.stl_path,
                arch_type=self.arch_type.get(),
                wire_size=self.wire_size.get()
            )
            
            # Set parameters
            self.generator.wire_path_creator.bend_radius = self.bend_radius.get()
            self.generator.wire_path_creator.wire_tension = self.wire_tension.get()
            self.generator.height_controller.set_step_size(self.height_step.get())
            
            # Generate wire using modular pipeline
            results = self.generator.generate_wire()
            
            if results:
                self.root.after(0, self._update_generation_results)
            else:
                self.root.after(0, lambda: self._handle_error("Wire generation failed"))
                
        except Exception as e:
            error_message = str(e)  # Capture the error message
            self.root.after(0, lambda msg=error_message: self._handle_error(msg))
    
    def _update_generation_results(self):
        """Update GUI with generation results."""
        self.progress.stop()
        self.status.set("Wire generated successfully using modular architecture!")
        
        if self.generator:
            self.teeth_count.set(str(len(self.generator.teeth)))
            self.brackets_count.set(str(len(self.generator.bracket_positions)))
            
            wire_length = self.generator.wire_path_creator.get_path_length()
            self.wire_length.set(f"{wire_length:.1f}mm")
            
            self.height_offset.set(self.generator.get_wire_height_offset())
            
            messagebox.showinfo("Success", "Wire generated successfully!\nReady for height adjustment and export.")
    
    def _handle_error(self, error_msg):
        """Handle generation errors."""
        self.progress.stop()
        self.status.set("Generation failed")
        messagebox.showerror("Error", f"Generation failed:\n{error_msg}")
    
    # Height control methods
    def wire_up(self):
        """Move wire up using modular height controller."""
        if not self.generator:
            messagebox.showerror("Error", "Generate wire first!")
            return
        
        step = self.height_step.get()
        self.generator.adjust_wire_height(step)
        self.height_offset.set(self.generator.get_wire_height_offset())
    
    def wire_down(self):
        """Move wire down using modular height controller."""
        if not self.generator:
            messagebox.showerror("Error", "Generate wire first!")
            return
        
        step = self.height_step.get()
        self.generator.adjust_wire_height(-step)
        self.height_offset.set(self.generator.get_wire_height_offset())
    
    def reset_height(self):
        """Reset wire height using modular height controller."""
        if not self.generator:
            messagebox.showerror("Error", "Generate wire first!")
            return
        
        self.generator.reset_wire_height()
        self.height_offset.set(self.generator.get_wire_height_offset())
    
    # Output methods
    def show_gcode(self):
        """Display G-code using modular export system."""
        if not self.generator:
            messagebox.showerror("Error", "Generate wire first!")
            return
        
        # Generate G-code using modular GCodeGenerator
        gcode_content = self._generate_gcode_preview()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, gcode_content)
        self.displayed_code_type = 'gcode'
        self.displayed_code_content = gcode_content
    
    def show_esp32(self):
        """Display ESP32 code using modular export system."""
        if not self.generator:
            messagebox.showerror("Error", "Generate wire first!")
            return
        
        # Generate ESP32 code using modular ESP32Generator
        esp32_code = self.generator.generate_esp32_code()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, esp32_code)
        self.displayed_code_type = 'esp32'
        self.displayed_code_content = esp32_code
    
    def _generate_gcode_preview(self):
        """Generate G-code preview using modular components."""
        bends = self.generator.wire_path_creator.calculate_bends()
        wire_length = self.generator.wire_path_creator.get_path_length()
        height_offset = self.generator.get_wire_height_offset()
        
        lines = [
            "; Generated by Modular Wire Generator",
            f"; Date: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"; Architecture: Modular design with separated components",
            f"; Wire: {self.wire_size.get()} {self.arch_type.get()} arch",
            f"; Length: {wire_length:.2f}mm",
            f"; Height Offset: {height_offset:.2f}mm",
            f"; Bends: {len(bends)}",
            ";",
            "; Generated using:",
            ";   WirePathCreator - Mathematical path algorithm",
            ";   WireMeshBuilder - 3D mesh creation",
            ";   HeightController - Height management",
            ";   GCodeGenerator - Export processing",
            "",
            "G21 ; Millimeters",
            "G90 ; Absolute positioning", 
            "G28 ; Home axes",
            "M117 Modular Wire Bending Started",
            "",
        ]
        
        # Add sample bending operations
        for i, bend in enumerate(bends[:5]):  # Show first 5 bends
            lines.extend([
                f"; Bend {i+1}: {bend['angle']:.1f}° {bend['direction']}",
                f"G0 X{bend['position'][0]:.2f} Y{bend['position'][1]:.2f}",
                f"M5 A{bend['angle']:.1f} R{bend['radius']:.1f}",
                "",
            ])
        
        if len(bends) > 5:
            lines.append(f"; ... {len(bends) - 5} more bends ...")
        
        lines.extend([
            "",
            "M117 Bending Complete",
            "M30 ; End program"
        ])
        
        return '\n'.join(lines)
    
    def export_code(self):
        """Export displayed code using modular export system."""
        if not hasattr(self, 'displayed_code_content') or not self.displayed_code_content:
            messagebox.showerror("Error", "No code to export. Generate and display code first.")
            return
        
        if self.displayed_code_type == 'gcode':
            filetypes = [("G-code files", "*.gcode"), ("Text files", "*.txt")]
            default_ext = ".gcode"
        else:
            filetypes = [("Arduino files", "*.ino"), ("Text files", "*.txt")]
            default_ext = ".ino"
        
        file_path = filedialog.asksaveasfilename(
            title="Export Code",
            defaultextension=default_ext,
            filetypes=filetypes
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.displayed_code_content)
                messagebox.showinfo("Success", f"Code exported to:\n{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def clear_output(self):
        """Clear output display."""
        self.output_text.delete(1.0, tk.END)
        self.displayed_code_content = ""
    
    # Other methods
    def launch_3d_editor(self):
        """Launch 3D editor using modular visualization system."""
        if not self.generator:
            messagebox.showerror("Error", "Generate wire first!")
            return

        try:
            # IMPORTANT: On macOS, Open3D MUST run on main thread
            # Do NOT use threading for Open3D visualization
            print("\nLaunching 3D Interactive Editor...")
            print("Note: GUI will be unresponsive while 3D editor is open")
            print("Close the 3D window to return to the GUI\n")

            # Hide the main window temporarily
            self.root.withdraw()

            # Launch on main thread (required for macOS)
            self.generator.launch_interactive_mode()

            # Restore main window after 3D editor closes
            self.root.deiconify()

        except Exception as e:
            self.root.deiconify()  # Make sure to restore window on error
            messagebox.showerror("Error", f"Failed to launch 3D editor:\n{str(e)}")
    
    def save_design(self):
        """Save design using modular architecture."""
        if not self.generator:
            messagebox.showerror("Error", "No design to save!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Design",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file_path:
            saved_file = self.generator.save_design(file_path)
            if saved_file:
                messagebox.showinfo("Success", f"Design saved:\n{os.path.basename(saved_file)}")
    
    def export_stl(self):
        """Export STL using modular STL exporter."""
        if not self.generator or not self.generator.wire_mesh:
            messagebox.showerror("Error", "No wire mesh to export!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Wire STL",
            defaultextension=".stl",
            filetypes=[("STL files", "*.stl")]
        )
        
        if file_path:
            if self.generator.export_stl(file_path):
                messagebox.showinfo("Success", f"STL exported:\n{os.path.basename(file_path)}")
    
    def show_architecture_dialog(self):
        """Show detailed architecture dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Modular Architecture Details")
        dialog.geometry("800x600")
        
        text_widget = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, font=("Consolas", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        arch_details = """MODULAR ORTHODONTIC WIRE GENERATOR - DETAILED ARCHITECTURE

═══════════════════════════════════════════════════════════════════════

🎯 WIRE DRAWING COMPONENTS (Core Drawing Logic)

📁 wire/wire_path_creator.py - WirePathCreator
   🔸 create_smooth_path() - Main drawing algorithm
      ├── _cubic_spline_interpolation() - Smooth curve generation
      ├── _apply_wire_tension() - Physical behavior simulation
      ├── _validate_and_clean_path() - Path optimization
      └── calculate_bends() - Manufacturing analysis
   
   This is the CORE MATHEMATICAL ALGORITHM that defines how the wire
   path is calculated. It's pure mathematics with no graphics dependency.

📁 wire/wire_mesh_builder.py - WireMeshBuilder  
   🔸 build_wire_mesh() - 3D geometry creation
      ├── _create_wire_segments() - Cylindrical mesh generation
      ├── _orient_cylinder() - 3D rotation mathematics
      ├── _apply_wire_material() - Visual properties
      └── _optimize_mesh() - Performance optimization
   
   This handles the VISUAL RENDERING of the mathematical wire path
   into actual 3D geometry that can be displayed and exported.

═══════════════════════════════════════════════════════════════════════

🏗️ SUPPORTING ARCHITECTURE

📁 core/ - Fundamental Processing
   ├── mesh_processor.py - STL file handling
   ├── tooth_detector.py - Anatomical analysis  
   ├── bracket_positioner.py - Clinical positioning
   └── constants.py - Wire specifications

📁 wire/ - Wire Generation Coordination
   ├── wire_generator.py - Main coordinator class
   └── height_controller.py - Height management

📁 visualization/ - Interactive 3D System
   ├── visualizer_3d.py - 3D scene management
   ├── control_point_manager.py - Interactive editing
   └── mesh_factory.py - 3D object creation

📁 export/ - Output Generation  
   ├── gcode_generator.py - CNC manufacturing code
   ├── esp32_generator.py - Arduino microcontroller code
   └── stl_exporter.py - 3D model export

📁 gui/ - User Interface
   └── main_window.py - This modular GUI application

═══════════════════════════════════════════════════════════════════════

🔄 DATA FLOW ARCHITECTURE

Input Stage:     STL File → MeshProcessor → Clean 3D Model
Analysis Stage:  3D Model → ToothDetector → Classified Teeth
                 Classified Teeth → BracketPositioner → Bracket Positions
Drawing Stage:   Bracket Positions → WirePathCreator → Mathematical Path
                 Mathematical Path → WireMeshBuilder → 3D Wire Geometry
Control Stage:   User Input → HeightController → Path Adjustments
Output Stage:    Final Data → Export Components → Various Formats

═══════════════════════════════════════════════════════════════════════

✅ KEY ARCHITECTURAL BENEFITS

🔸 SEPARATION OF CONCERNS
   Each class has exactly one responsibility. The drawing algorithm
   doesn't know about 3D graphics, and the 3D renderer doesn't know
   about mathematical computation.

🔸 MODULARITY  
   Components can be developed, tested, and modified independently.
   You can improve the drawing algorithm without touching the GUI.

🔸 TESTABILITY
   Each component can be unit tested in isolation:
   - Test drawing algorithm with known mathematical inputs
   - Test 3D rendering with predefined paths
   - Test height control with mock data

🔸 MAINTAINABILITY
   Changes are localized:
   - Better spline algorithm? Only modify WirePathCreator
   - Improved 3D rendering? Only touch WireMeshBuilder  
   - New export format? Add new class in export/

🔸 EXTENSIBILITY
   New features are easy to add:
   - Additional wire materials? Extend WireMeshBuilder
   - Different interpolation methods? Extend WirePathCreator
   - New machine types? Add export classes

═══════════════════════════════════════════════════════════════════════

🎨 DRAWING ALGORITHM DETAILS

The wire drawing happens in two completely separate phases:

PHASE 1: Mathematical Computation (WirePathCreator)
- Input: Bracket positions, clinical parameters
- Process: Spline interpolation, control point generation, path smoothing
- Output: Array of 3D points representing the wire path
- No graphics involved - pure mathematical computation

PHASE 2: Visual Rendering (WireMeshBuilder)  
- Input: Mathematical wire path from Phase 1
- Process: Cylindrical mesh creation, material application, optimization
- Output: 3D mesh object ready for display/export
- Handles all graphics and visual aspects

This separation makes both phases easier to understand, test, and modify.
The algorithm can be changed without affecting the visualization, and
vice versa.

═══════════════════════════════════════════════════════════════════════

This modular architecture transforms a complex monolithic system into
a maintainable, extensible, and testable professional application."""
        
        text_widget.insert(1.0, arch_details)
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
    
    def show_help(self):
        """Show help dialog."""
        messagebox.showinfo("Help", 
            "Modular Orthodontic Wire Generator\n\n"
            "1. Load STL file\n"
            "2. Set wire parameters\n" 
            "3. Generate wire using modular pipeline\n"
            "4. Adjust height with modular controls\n"
            "5. Launch 3D editor for interactive editing\n"
            "6. Export G-code, ESP32 code, or STL\n\n"
            "Architecture: Separated drawing algorithm and rendering\n"
            "Click 'Architecture Info' for detailed technical information.")
    
    def run(self):
        """Start the modular GUI application."""
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Accent.TButton", background="#0078d4", foreground="white")
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (700)
        y = (self.root.winfo_screenheight() // 2) - (450)
        self.root.geometry(f"1400x900+{x}+{y}")
        
        print("Modular Orthodontic Wire Generator GUI Started")
        print("Architecture: Separated drawing algorithm and 3D rendering")
        print("Components: Modular, testable, maintainable")
        
        self.root.mainloop()


# ================================================================
# utils/math_utils.py
"""Mathematical utility functions for wire generation."""

import numpy as np
from typing import List, Tuple
from scipy import interpolate

class MathUtils:
    """Mathematical utilities for wire path calculations."""
    
    @staticmethod
    def calculate_arc_length(points: np.ndarray) -> float:
        """Calculate total arc length of a path."""
        if len(points) < 2:
            return 0.0
        
        total_length = 0.0
        for i in range(len(points) - 1):
            segment_length = np.linalg.norm(points[i + 1] - points[i])
            total_length += segment_length
        
        return total_length
    
    @staticmethod
    def calculate_curvature(points: np.ndarray, index: int) -> float:
        """Calculate curvature at a specific point."""
        if index < 1 or index >= len(points) - 1:
            return 0.0
        
        p1 = points[index - 1]
        p2 = points[index]
        p3 = points[index + 1]
        
        # Calculate vectors
        v1 = p2 - p1
        v2 = p3 - p2
        
        # Calculate curvature using the formula: |v1 × v2| / |v1|³
        cross_product = np.cross(v1, v2)
        v1_magnitude = np.linalg.norm(v1)
        
        if v1_magnitude < 1e-6:
            return 0.0
        
        if len(cross_product.shape) == 0:  # 2D case
            curvature = abs(cross_product) / (v1_magnitude ** 3)
        else:  # 3D case
            curvature = np.linalg.norm(cross_product) / (v1_magnitude ** 3)
        
        return curvature
    
    @staticmethod
    def smooth_path(points: np.ndarray, smoothing_factor: float = 0.1) -> np.ndarray:
        """Apply smoothing to a path using moving average."""
        if len(points) < 3:
            return points
        
        smoothed = points.copy()
        
        for i in range(1, len(points) - 1):
            # Simple moving average smoothing
            neighbor_avg = (points[i - 1] + points[i + 1]) / 2
            smoothed[i] = (1 - smoothing_factor) * points[i] + smoothing_factor * neighbor_avg
        
        return smoothed
    
    @staticmethod
    def resample_path(points: np.ndarray, target_spacing: float) -> np.ndarray:
        """Resample path to have uniform spacing between points."""
        if len(points) < 2:
            return points
        
        # Calculate cumulative distances
        distances = [0.0]
        for i in range(1, len(points)):
            dist = np.linalg.norm(points[i] - points[i - 1])
            distances.append(distances[-1] + dist)
        
        total_length = distances[-1]
        if total_length < target_spacing:
            return points
        
        # Create target distances
        num_points = int(total_length / target_spacing) + 1
        target_distances = np.linspace(0, total_length, num_points)
        
        # Interpolate points at target distances
        resampled_points = []
        for target_dist in target_distances:
            # Find the segment containing this distance
            for i in range(len(distances) - 1):
                if distances[i] <= target_dist <= distances[i + 1]:
                    # Interpolate within this segment
                    segment_progress = (target_dist - distances[i]) / (distances[i + 1] - distances[i])
                    interpolated_point = points[i] + segment_progress * (points[i + 1] - points[i])
                    resampled_points.append(interpolated_point)
                    break
        
        return np.array(resampled_points) if resampled_points else points


# ================================================================  
# utils/file_utils.py
"""File I/O utilities for the wire generator."""

import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

class FileUtils:
    """Utilities for file operations and data persistence."""
    
    @staticmethod
    def ensure_directory(filepath: str) -> str:
        """Ensure directory exists for the given filepath."""
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        return filepath
    
    @staticmethod
    def get_safe_filename(filename: str, max_length: int = 255) -> str:
        """Get a safe filename by removing invalid characters."""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Truncate if too long
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            filename = name[:max_length - len(ext)] + ext
        
        return filename
    
    @staticmethod
    def add_timestamp_to_filename(filename: str) -> str:
        """Add timestamp to filename to avoid conflicts."""
        path = Path(filename)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        new_name = f"{path.stem}_{timestamp}{path.suffix}"
        return str(path.parent / new_name)
    
    @staticmethod
    def save_json(data: Dict[Any, Any], filename: str) -> bool:
        """Save data to JSON file with error handling."""
        try:
            FileUtils.ensure_directory(filename)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving JSON: {e}")
            return False
    
    @staticmethod
    def load_json(filename: str) -> Optional[Dict[Any, Any]]:
        """Load data from JSON file with error handling."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return None
    
    @staticmethod
    def get_file_info(filepath: str) -> Dict[str, Any]:
        """Get detailed file information."""
        if not os.path.exists(filepath):
            return {'exists': False}
        
        stat = os.stat(filepath)
        return {
            'exists': True,
            'size_bytes': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'modified_time': time.ctime(stat.st_mtime),
            'created_time': time.ctime(stat.st_ctime),
            'extension': Path(filepath).suffix.lower(),
            'basename': os.path.basename(filepath)
        }


if __name__ == "__main__":
    # Example usage of the modular GUI
    app = WireGeneratorGUI()
    app.run()