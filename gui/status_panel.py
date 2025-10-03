#!/usr/bin/env python3
# ================================================================
# gui/status_panel.py
"""Center status panel for generation status and 3D view."""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from typing import Optional

class StatusPanel:
    """Center status panel showing generation progress and information."""
    
    def __init__(self, parent_frame, wire_generator_gui):
        """Initialize status panel."""
        self.parent = parent_frame
        self.gui = wire_generator_gui
        
        # Main status frame
        self.status_frame = ttk.LabelFrame(parent_frame, text="Generation Status & Information", padding="10")
        self.status_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        self.status_frame.columnconfigure(0, weight=1)
        self.status_frame.rowconfigure(2, weight=1)
        
        # Setup all sections
        self.setup_status_indicators()
        self.setup_progress_section()
        self.setup_information_display()
        self.setup_action_buttons()
        
    def setup_status_indicators(self):
        """Setup status indicator section."""
        indicators_frame = ttk.Frame(self.status_frame)
        indicators_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        indicators_frame.columnconfigure(1, weight=1)
        indicators_frame.columnconfigure(3, weight=1)
        
        # Status indicators in grid layout
        row = 0
        
        # Main status
        ttk.Label(indicators_frame, text="Status:", font=("Arial", 9, "bold")).grid(row=row, column=0, sticky=tk.W)
        self.status_label = ttk.Label(indicators_frame, textvariable=self.gui.status, foreground="blue")
        self.status_label.grid(row=row, column=1, sticky=tk.W, padx=(5, 20))
        
        # Architecture info
        ttk.Label(indicators_frame, text="Architecture:", font=("Arial", 9, "bold")).grid(row=row, column=2, sticky=tk.W)
        arch_label = ttk.Label(indicators_frame, text="Modular Design", foreground="green")
        arch_label.grid(row=row, column=3, sticky=tk.W, padx=(5, 0))
        row += 1
        
        # Teeth count
        ttk.Label(indicators_frame, text="Teeth Detected:", font=("Arial", 9, "bold")).grid(row=row, column=0, sticky=tk.W)
        ttk.Label(indicators_frame, textvariable=self.gui.teeth_count).grid(row=row, column=1, sticky=tk.W, padx=(5, 20))
        
        # Brackets count
        ttk.Label(indicators_frame, text="Brackets:", font=("Arial", 9, "bold")).grid(row=row, column=2, sticky=tk.W)
        ttk.Label(indicators_frame, textvariable=self.gui.brackets_count).grid(row=row, column=3, sticky=tk.W, padx=(5, 0))
        row += 1
        
        # Wire length
        ttk.Label(indicators_frame, text="Wire Length:", font=("Arial", 9, "bold")).grid(row=row, column=0, sticky=tk.W)
        ttk.Label(indicators_frame, textvariable=self.gui.wire_length).grid(row=row, column=1, sticky=tk.W, padx=(5, 20))
        
        # Height offset
        ttk.Label(indicators_frame, text="Height Offset:", font=("Arial", 9, "bold")).grid(row=row, column=2, sticky=tk.W)
        height_offset_label = ttk.Label(indicators_frame, textvariable=self.gui.height_offset, foreground="red")
        height_offset_label.grid(row=row, column=3, sticky=tk.W, padx=(5, 0))
    
    def setup_progress_section(self):
        """Setup progress indication section."""
        progress_frame = ttk.Frame(self.status_frame)
        progress_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Progress status text
        self.progress_text = ttk.Label(progress_frame, text="Ready to generate wire", font=("Arial", 8))
        self.progress_text.grid(row=1, column=0, sticky=tk.W)
    
    def setup_information_display(self):
        """Setup main information display area."""
        info_frame = ttk.LabelFrame(self.status_frame, text="System Information", padding="5")
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)
        
        # Information text area with tabs
        self.info_notebook = ttk.Notebook(info_frame)
        self.info_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Architecture tab
        self.setup_architecture_tab()
        
        # Generation log tab
        self.setup_log_tab()
        
        # Component status tab
        self.setup_component_status_tab()
    
    def setup_architecture_tab(self):
        """Setup architecture information tab."""
        arch_frame = ttk.Frame(self.info_notebook)
        self.info_notebook.add(arch_frame, text="Architecture")
        
        arch_text = scrolledtext.ScrolledText(
            arch_frame, 
            height=15, 
            width=50, 
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        arch_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        architecture_info = """MODULAR ARCHITECTURE OVERVIEW

🎯 WIRE DRAWING COMPONENTS:
├── WirePathCreator (wire/wire_path_creator.py)
│   └── create_smooth_path() - Core drawing algorithm
│       ├── Spline interpolation
│       ├── Control point management
│       └── Height offset application
│
└── WireMeshBuilder (wire/wire_mesh_builder.py)
    └── build_wire_mesh() - 3D mesh creation
        ├── Cylindrical segments
        ├── Material properties
        └── Mesh optimization

🏗️ SUPPORTING COMPONENTS:
├── MeshProcessor - STL loading/cleaning
├── ToothDetector - Anatomical analysis
├── BracketPositioner - Clinical placement
└── HeightController - Height management

📤 EXPORT MODULES:
├── GCodeGenerator - CNC instructions
├── ESP32Generator - Arduino code
└── STLExporter - 3D model export

🔄 DATA FLOW:
STL → MeshProcessor → ToothDetector → BracketPositioner
→ WirePathCreator (ALGORITHM) → WireMeshBuilder (RENDERING)
→ HeightController → Visualization → Export

✅ BENEFITS:
• Separation of Concerns - Clear responsibilities
• Modularity - Independent development
• Testability - Isolated component testing
• Maintainability - Localized changes
• Extensibility - Easy feature addition"""
        
        arch_text.insert(1.0, architecture_info)
        arch_text.config(state=tk.DISABLED)
    
    def setup_log_tab(self):
        """Setup generation log tab."""
        log_frame = ttk.Frame(self.info_notebook)
        self.info_notebook.add(log_frame, text="Generation Log")
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            width=50,
            font=("Consolas", 8),
            bg="black",
            fg="lime"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add initial log entry
        self.add_log_entry("System initialized - Modular architecture ready")
    
    def setup_component_status_tab(self):
        """Setup component status tab."""
        status_frame = ttk.Frame(self.info_notebook)
        self.info_notebook.add(status_frame, text="Components")
        
        # Component status tree
        self.component_tree = ttk.Treeview(status_frame, columns=("status", "info"), show="tree headings")
        self.component_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure columns
        self.component_tree.heading("#0", text="Component")
        self.component_tree.heading("status", text="Status")
        self.component_tree.heading("info", text="Information")
        
        self.component_tree.column("#0", width=200)
        self.component_tree.column("status", width=100)
        self.component_tree.column("info", width=200)
        
        # Populate component tree
        self.populate_component_tree()
    
    def setup_action_buttons(self):
        """Setup action buttons section."""
        action_frame = ttk.Frame(self.status_frame)
        action_frame.grid(row=3, column=0, pady=(10, 0))
        
        # 3D Editor button
        ttk.Button(
            action_frame,
            text="Launch 3D Interactive Editor",
            command=self.gui.launch_3d_editor,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Quick actions
        ttk.Button(
            action_frame,
            text="Reset Parameters",
            command=self.reset_all_parameters
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            action_frame,
            text="Refresh Status",
            command=self.refresh_status
        ).pack(side=tk.LEFT)
    
    def populate_component_tree(self):
        """Populate the component status tree."""
        # Clear existing items
        for item in self.component_tree.get_children():
            self.component_tree.delete(item)
        
        # Core components
        core_node = self.component_tree.insert("", "end", text="Core Components", values=("Ready", ""))
        self.component_tree.insert(core_node, "end", text="MeshProcessor", values=("Ready", "STL loading/cleaning"))
        self.component_tree.insert(core_node, "end", text="ToothDetector", values=("Ready", "Anatomical analysis"))
        self.component_tree.insert(core_node, "end", text="BracketPositioner", values=("Ready", "Clinical positioning"))
        
        # Wire components
        wire_node = self.component_tree.insert("", "end", text="Wire Generation", values=("Ready", ""))
        self.component_tree.insert(wire_node, "end", text="WirePathCreator", values=("Ready", "Drawing algorithm"))
        self.component_tree.insert(wire_node, "end", text="WireMeshBuilder", values=("Ready", "3D rendering"))
        self.component_tree.insert(wire_node, "end", text="HeightController", values=("Ready", "Height management"))
        
        # Export components
        export_node = self.component_tree.insert("", "end", text="Export Systems", values=("Ready", ""))
        self.component_tree.insert(export_node, "end", text="GCodeGenerator", values=("Ready", "CNC instructions"))
        self.component_tree.insert(export_node, "end", text="ESP32Generator", values=("Ready", "Arduino code"))
        self.component_tree.insert(export_node, "end", text="STLExporter", values=("Ready", "3D model export"))
        
        # Expand all nodes
        for item in self.component_tree.get_children():
            self.component_tree.item(item, open=True)
    
    def update_component_status(self, component_name: str, status: str, info: str = ""):
        """Update status of a specific component."""
        for item in self.component_tree.get_children():
            for child in self.component_tree.get_children(item):
                if self.component_tree.item(child, "text") == component_name:
                    self.component_tree.item(child, values=(status, info))
                    break
    
    def add_log_entry(self, message: str, level: str = "INFO"):
        """Add entry to generation log."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)  # Scroll to bottom
        self.log_text.config(state=tk.DISABLED)
    
    def start_progress(self, message: str = "Processing..."):
        """Start progress indication."""
        self.progress.start()
        self.progress_text.config(text=message)
        self.add_log_entry(f"Started: {message}")
    
    def stop_progress(self, message: str = "Complete"):
        """Stop progress indication."""
        self.progress.stop()
        self.progress_text.config(text=message)
        self.add_log_entry(f"Completed: {message}")
    
    def update_status_display(self, generator=None):
        """Update all status displays with current generator state."""
        if generator:
            # Update component statuses
            if hasattr(generator, 'mesh') and generator.mesh:
                self.update_component_status("MeshProcessor", "Active", "Mesh loaded")
            
            if hasattr(generator, 'teeth') and generator.teeth:
                self.update_component_status("ToothDetector", "Complete", f"{len(generator.teeth)} teeth")
            
            if hasattr(generator, 'bracket_positions') and generator.bracket_positions:
                self.update_component_status("BracketPositioner", "Complete", f"{len(generator.bracket_positions)} brackets")
            
            if hasattr(generator, 'wire_path') and generator.wire_path is not None:
                self.update_component_status("WirePathCreator", "Complete", "Path generated")
                self.update_component_status("WireMeshBuilder", "Complete", "Mesh created")
        
        self.refresh_status()
    
    def reset_all_parameters(self):
        """Reset all parameters to defaults."""
        if hasattr(self.gui, 'reset_all_parameters'):
            self.gui.reset_all_parameters()
        self.add_log_entry("All parameters reset to defaults")
        
        # Reset component statuses
        self.populate_component_tree()
    
    def refresh_status(self):
        """Refresh all status displays."""
        # Force update of all tkinter variables
        self.gui.root.update_idletasks()
        self.add_log_entry("Status refreshed", "DEBUG")

