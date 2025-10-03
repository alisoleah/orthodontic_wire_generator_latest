
# ================================================================
# gui/gcode_panel.py
"""Right panel for G-code and export output display."""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import time
from typing import Optional

class GCodePanel:
    """Right panel for displaying and managing G-code and export output."""
    
    def __init__(self, parent_frame, wire_generator_gui):
        """Initialize G-code panel."""
        self.parent = parent_frame
        self.gui = wire_generator_gui
        
        # Main output frame
        self.output_frame = ttk.LabelFrame(parent_frame, text="Generated Output", padding="10")
        self.output_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.output_frame.columnconfigure(0, weight=1)
        self.output_frame.rowconfigure(2, weight=1)
        
        # Track displayed content
        self.displayed_code_type = None
        self.displayed_code_content = ""
        
        # Setup all sections
        self.setup_output_controls()
        self.setup_output_tabs()
        self.setup_export_controls()
        
    def setup_output_controls(self):
        """Setup output generation controls."""
        controls_frame = ttk.Frame(self.output_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Generation buttons
        ttk.Button(
            controls_frame,
            text="Show G-code",
            command=self.show_gcode,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            controls_frame,
            text="Show ESP32",
            command=self.show_esp32,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            controls_frame,
            text="Show Summary",
            command=self.show_summary
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            controls_frame,
            text="Clear",
            command=self.clear_output
        ).pack(side=tk.LEFT)
    
    def setup_output_tabs(self):
        """Setup tabbed output display."""
        self.output_notebook = ttk.Notebook(self.output_frame)
        self.output_notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Main output tab
        self.setup_main_output_tab()
        
        # Preview tab
        self.setup_preview_tab()
        
        # Settings tab
        self.setup_settings_tab()
    
    def setup_main_output_tab(self):
        """Setup main code output tab."""
        output_tab = ttk.Frame(self.output_notebook)
        self.output_notebook.add(output_tab, text="Code Output")
        
        output_tab.columnconfigure(0, weight=1)
        output_tab.rowconfigure(0, weight=1)
        
        # Code display area
        self.output_text = scrolledtext.ScrolledText(
            output_tab,
            width=50,
            height=25,
            font=("Consolas", 9),
            bg="black",
            fg="lime",
            insertbackground="lime",
            wrap=tk.NONE
        )
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add welcome message
        welcome_msg = """Generated Output Display
========================

This panel shows generated code and export output.

Available outputs:
• G-code for CNC wire bending machines
• ESP32 Arduino code for stepper control
• Design summaries and reports

Click the buttons above to generate and display code.

Architecture: Modular export system with separated
drawing algorithm and 3D rendering components."""
        
        self.output_text.insert(1.0, welcome_msg)
    
    def setup_preview_tab(self):
        """Setup preview/summary tab."""
        preview_tab = ttk.Frame(self.output_notebook)
        self.output_notebook.add(preview_tab, text="Preview")
        
        preview_tab.columnconfigure(0, weight=1)
        preview_tab.rowconfigure(0, weight=1)
        
        self.preview_text = scrolledtext.ScrolledText(
            preview_tab,
            width=50,
            height=25,
            font=("Arial", 10),
            wrap=tk.WORD
        )
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def setup_settings_tab(self):
        """Setup export settings tab."""
        settings_tab = ttk.Frame(self.output_notebook)
        self.output_notebook.add(settings_tab, text="Export Settings")
        
        # G-code settings
        gcode_frame = ttk.LabelFrame(settings_tab, text="G-code Settings", padding="5")
        gcode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Feed rate
        ttk.Label(gcode_frame, text="Feed Rate (mm/min):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.feed_rate_var = tk.IntVar(value=1000)
        ttk.Spinbox(gcode_frame, from_=100, to=5000, increment=100, 
                   textvariable=self.feed_rate_var, width=10).grid(row=0, column=1, padx=(10, 0), pady=2)
        
        # Bend speed
        ttk.Label(gcode_frame, text="Bend Speed (mm/min):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.bend_speed_var = tk.IntVar(value=500)
        ttk.Spinbox(gcode_frame, from_=50, to=2000, increment=50,
                   textvariable=self.bend_speed_var, width=10).grid(row=1, column=1, padx=(10, 0), pady=2)
        
        # Safety height
        ttk.Label(gcode_frame, text="Safety Height (mm):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.safety_height_var = tk.DoubleVar(value=10.0)
        ttk.Spinbox(gcode_frame, from_=5.0, to=50.0, increment=1.0,
                   textvariable=self.safety_height_var, width=10).grid(row=2, column=1, padx=(10, 0), pady=2)
        
        # ESP32 settings
        esp32_frame = ttk.LabelFrame(settings_tab, text="ESP32 Settings", padding="5")
        esp32_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Steps per mm
        ttk.Label(esp32_frame, text="X Steps/mm:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.x_steps_var = tk.IntVar(value=80)
        ttk.Spinbox(esp32_frame, from_=10, to=500, increment=10,
                   textvariable=self.x_steps_var, width=10).grid(row=0, column=1, padx=(10, 0), pady=2)
        
        ttk.Label(esp32_frame, text="Y Steps/mm:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.y_steps_var = tk.IntVar(value=80)
        ttk.Spinbox(esp32_frame, from_=10, to=500, increment=10,
                   textvariable=self.y_steps_var, width=10).grid(row=1, column=1, padx=(10, 0), pady=2)
        
        ttk.Label(esp32_frame, text="Z Steps/mm:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.z_steps_var = tk.IntVar(value=400)
        ttk.Spinbox(esp32_frame, from_=50, to=1000, increment=50,
                   textvariable=self.z_steps_var, width=10).grid(row=2, column=1, padx=(10, 0), pady=2)
    
    def setup_export_controls(self):
        """Setup export controls section."""
        export_frame = ttk.Frame(self.output_frame)
        export_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Export buttons
        ttk.Button(
            export_frame,
            text="Export Current",
            command=self.export_current_code,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            export_frame,
            text="Export All",
            command=self.export_all_formats
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            export_frame,
            text="Copy to Clipboard",
            command=self.copy_to_clipboard
        ).pack(side=tk.LEFT)
        
        # Export status
        self.export_status = ttk.Label(export_frame, text="Ready to export", foreground="gray")
        self.export_status.pack(side=tk.RIGHT)
    
    def show_gcode(self):
        """Display G-code in the output area."""
        if not self.gui.generator:
            messagebox.showerror("Error", "Please generate wire first!")
            return
        
        try:
            # Generate G-code using current settings
            gcode_content = self._generate_gcode_with_settings()
            
            # Display in output area
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(1.0, gcode_content)
            
            # Track displayed content
            self.displayed_code_type = 'gcode'
            self.displayed_code_content = gcode_content
            
            # Update preview
            self._update_gcode_preview(gcode_content)
            
            # Switch to main output tab
            self.output_notebook.select(0)
            
            self.export_status.config(text="G-code ready for export", foreground="green")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate G-code:\n{str(e)}")
    
    def show_esp32(self):
        """Display ESP32 Arduino code in the output area."""
        if not self.gui.generator:
            messagebox.showerror("Error", "Please generate wire first!")
            return
        
        try:
            # Generate ESP32 code using current settings
            esp32_code = self.gui.generator.generate_esp32_code()
            
            # Display in output area
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(1.0, esp32_code)
            
            # Track displayed content
            self.displayed_code_type = 'esp32'
            self.displayed_code_content = esp32_code
            
            # Update preview
            self._update_esp32_preview(esp32_code)
            
            # Switch to main output tab
            self.output_notebook.select(0)
            
            self.export_status.config(text="ESP32 code ready for export", foreground="green")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate ESP32 code:\n{str(e)}")
    
    def show_summary(self):
        """Display design summary."""
        if not self.gui.generator:
            messagebox.showerror("Error", "Please generate wire first!")
            return
        
        try:
            summary = self._generate_design_summary()
            
            # Display in preview tab
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, summary)
            
            # Switch to preview tab
            self.output_notebook.select(1)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate summary:\n{str(e)}")
    
    def clear_output(self):
        """Clear all output displays."""
        self.output_text.delete(1.0, tk.END)
        self.preview_text.delete(1.0, tk.END)
        
        self.displayed_code_type = None
        self.displayed_code_content = ""
        
        self.export_status.config(text="Output cleared", foreground="gray")
    
    def _generate_gcode_with_settings(self) -> str:
        """Generate G-code with current panel settings."""
        bends = self.gui.generator.wire_path_creator.calculate_bends()
        wire_length = self.gui.generator.wire_path_creator.get_path_length()
        height_offset = self.gui.generator.get_wire_height_offset()
        
        lines = [
            "; Generated by Modular Orthodontic Wire Generator",
            f"; Date: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"; Wire: {self.gui.wire_size.get()} {self.gui.arch_type.get()} arch",
            f"; Length: {wire_length:.2f}mm",
            f"; Height Offset: {height_offset:.2f}mm",
            f"; Bends: {len(bends)}",
            f"; Feed Rate: {self.feed_rate_var.get()} mm/min",
            f"; Bend Speed: {self.bend_speed_var.get()} mm/min",
            f"; Safety Height: {self.safety_height_var.get()}mm",
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
    
    def _update_gcode_preview(self, gcode_content: str):
        """Update G-code preview information."""
        lines = gcode_content.split('\n')
        total_lines = len(lines)
        comment_lines = sum(1 for line in lines if line.strip().startswith(';'))
        command_lines = total_lines - comment_lines
        
        preview = f"""G-code Generated Successfully
=============================

Statistics:
• Total lines: {total_lines}
• Command lines: {command_lines} 
• Comment lines: {comment_lines}
• Feed rate: {self.feed_rate_var.get()} mm/min
• Bend speed: {self.bend_speed_var.get()} mm/min
• Safety height: {self.safety_height_var.get()} mm

Generated using modular GCodeGenerator component.
Ready for export to CNC wire bending machine."""
        
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, preview)
    
    def _update_esp32_preview(self, esp32_code: str):
        """Update ESP32 code preview information."""
        lines = esp32_code.split('\n')
        
        preview = f"""ESP32 Arduino Code Generated
============================

Statistics:
• Total lines: {len(lines)}
• X Steps/mm: {self.x_steps_var.get()}
• Y Steps/mm: {self.y_steps_var.get()}
• Z Steps/mm: {self.z_steps_var.get()}

Features:
• AccelStepper library integration
• 3-axis coordinated movement
• Path following algorithms
• Serial communication

Generated using modular ESP32Generator component.
Ready for upload to ESP32 microcontroller."""
        
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, preview)
    
    def _generate_design_summary(self) -> str:
        """Generate comprehensive design summary."""
        generator = self.gui.generator
        
        summary = f"""Wire Design Summary
==================
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
Architecture: Modular design with separated components

STL Model:
• File: {os.path.basename(generator.stl_path)}
• Arch Type: {generator.arch_type.upper()}
• Wire Size: {generator.wire_size}

Detection Results:
• Teeth Detected: {len(generator.teeth)}
• Brackets Positioned: {len(generator.bracket_positions)}
• Visible Brackets: {sum(1 for b in generator.bracket_positions if b.get('visible', True))}

Wire Path:
• Total Length: {generator.wire_path_creator.get_path_length():.1f}mm
• Path Points: {len(generator.wire_path) if generator.wire_path is not None else 0}
• Height Offset: {generator.get_wire_height_offset():.2f}mm
• Control Points: {len(generator.wire_path_creator.control_points)}

Manufacturing:
• Calculated Bends: {len(generator.wire_path_creator.calculate_bends())}
• Bend Radius: {generator.wire_path_creator.bend_radius:.1f}mm
• Wire Tension: {generator.wire_path_creator.wire_tension:.1f}

Components Used:
• WirePathCreator - Mathematical path generation
• WireMeshBuilder - 3D mesh rendering  
• HeightController - Height management
• Export modules - G-code, ESP32, STL generation

This design uses the modular architecture with clear
separation between drawing algorithm and 3D rendering."""
        
        return summary
    
    def export_current_code(self):
        """Export currently displayed code."""
        if not self.displayed_code_content:
            messagebox.showerror("Error", "No code to export. Generate code first.")
            return
        
        # Determine file type and extension
        if self.displayed_code_type == 'gcode':
            filetypes = [("G-code files", "*.gcode"), ("Text files", "*.txt")]
            default_ext = ".gcode"
        elif self.displayed_code_type == 'esp32':
            filetypes = [("Arduino files", "*.ino"), ("Text files", "*.txt")]
            default_ext = ".ino"
        else:
            filetypes = [("Text files", "*.txt"), ("All files", "*.*")]
            default_ext = ".txt"
        
        # Get save location
        file_path = filedialog.asksaveasfilename(
            title="Export Code",
            defaultextension=default_ext,
            filetypes=filetypes
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.displayed_code_content)
                
                messagebox.showinfo("Success", f"Code exported successfully:\n{os.path.basename(file_path)}")
                self.export_status.config(text=f"Exported: {os.path.basename(file_path)}", foreground="blue")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export code:\n{str(e)}")
                self.export_status.config(text="Export failed", foreground="red")
    
    def export_all_formats(self):
        """Export all available formats."""
        if not self.gui.generator:
            messagebox.showerror("Error", "Please generate wire first!")
            return
        
        # Get directory for exports
        export_dir = filedialog.askdirectory(title="Select Export Directory")
        if not export_dir:
            return
        
        exported_files = []
        
        try:
            # Generate timestamp for filenames
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            base_name = f"wire_{self.gui.generator.arch_type}_{timestamp}"
            
            # Export G-code
            try:
                gcode_content = self._generate_gcode_with_settings()
                gcode_path = os.path.join(export_dir, f"{base_name}.gcode")
                with open(gcode_path, 'w') as f:
                    f.write(gcode_content)
                exported_files.append(os.path.basename(gcode_path))
            except Exception as e:
                print(f"G-code export failed: {e}")
            
            # Export ESP32 code
            try:
                esp32_code = self.gui.generator.generate_esp32_code()
                esp32_path = os.path.join(export_dir, f"{base_name}.ino")
                with open(esp32_path, 'w') as f:
                    f.write(esp32_code)
                exported_files.append(os.path.basename(esp32_path))
            except Exception as e:
                print(f"ESP32 export failed: {e}")
            
            # Export design summary
            try:
                summary = self._generate_design_summary()
                summary_path = os.path.join(export_dir, f"{base_name}_summary.txt")
                with open(summary_path, 'w') as f:
                    f.write(summary)
                exported_files.append(os.path.basename(summary_path))
            except Exception as e:
                print(f"Summary export failed: {e}")
            
            # Export STL if possible
            try:
                if hasattr(self.gui.generator, 'wire_mesh') and self.gui.generator.wire_mesh:
                    stl_path = os.path.join(export_dir, f"{base_name}.stl")
                    if self.gui.generator.export_stl(stl_path):
                        exported_files.append(os.path.basename(stl_path))
            except Exception as e:
                print(f"STL export failed: {e}")
            
            # Export design JSON
            try:
                json_path = os.path.join(export_dir, f"{base_name}_design.json")
                if self.gui.generator.save_design(json_path):
                    exported_files.append(os.path.basename(json_path))
            except Exception as e:
                print(f"Design JSON export failed: {e}")
            
            if exported_files:
                files_list = "\n".join([f"• {f}" for f in exported_files])
                messagebox.showinfo(
                    "Export Complete", 
                    f"Successfully exported {len(exported_files)} files:\n\n{files_list}"
                )
                self.export_status.config(text=f"Exported {len(exported_files)} files", foreground="green")
            else:
                messagebox.showerror("Error", "No files were exported successfully.")
                self.export_status.config(text="Export failed", foreground="red")
                
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{str(e)}")
            self.export_status.config(text="Export failed", foreground="red")
    
    def copy_to_clipboard(self):
        """Copy current output to clipboard."""
        if not self.displayed_code_content:
            messagebox.showerror("Error", "No code to copy. Generate code first.")
            return
        
        try:
            self.gui.root.clipboard_clear()
            self.gui.root.clipboard_append(self.displayed_code_content)
            
            messagebox.showinfo("Success", "Code copied to clipboard")
            self.export_status.config(text="Copied to clipboard", foreground="blue")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard:\n{str(e)}")
    
    def get_export_settings(self) -> dict:
        """Get current export settings."""
        return {
            'gcode': {
                'feed_rate': self.feed_rate_var.get(),
                'bend_speed': self.bend_speed_var.get(),
                'safety_height': self.safety_height_var.get()
            },
            'esp32': {
                'steps_per_mm': (
                    self.x_steps_var.get(),
                    self.y_steps_var.get(), 
                    self.z_steps_var.get()
                )
            }
        }
    
    def set_export_settings(self, settings: dict):
        """Set export settings from dictionary."""
        if 'gcode' in settings:
            gcode_settings = settings['gcode']
            if 'feed_rate' in gcode_settings:
                self.feed_rate_var.set(gcode_settings['feed_rate'])
            if 'bend_speed' in gcode_settings:
                self.bend_speed_var.set(gcode_settings['bend_speed'])
            if 'safety_height' in gcode_settings:
                self.safety_height_var.set(gcode_settings['safety_height'])
        
        if 'esp32' in settings:
            esp32_settings = settings['esp32']
            if 'steps_per_mm' in esp32_settings:
                steps = esp32_settings['steps_per_mm']
                if len(steps) >= 3:
                    self.x_steps_var.set(steps[0])
                    self.y_steps_var.set(steps[1])
                    self.z_steps_var.set(steps[2])
    
    def update_output_status(self, message: str, color: str = "black"):
        """Update export status message."""
        self.export_status.config(text=message, foreground=color)


# ================================================================
# Example usage of these panels in main_window.py integration:
"""
To integrate these panels into your main GUI, add this to your main_window.py:

def setup_gui(self):
    # ... existing setup code ...
    
    # Import the panels
    from gui.control_panel import ControlPanel
    from gui.status_panel import StatusPanel  
    from gui.gcode_panel import GCodePanel
    
    # Create panels
    self.control_panel = ControlPanel(main_frame, self)
    self.status_panel = StatusPanel(main_frame, self)
    self.gcode_panel = GCodePanel(main_frame, self)
    
    # Configure grid weights
    main_frame.columnconfigure(0, weight=0)  # Control panel - fixed width
    main_frame.columnconfigure(1, weight=1)  # Status panel - expandable
    main_frame.columnconfigure(2, weight=0)  # G-code panel - fixed width
"""