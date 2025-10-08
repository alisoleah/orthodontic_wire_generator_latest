"""
This file provides the WireGenerator class, which serves as a compatibility
layer between the older application structure and the new WorkflowManager.
It wraps the WorkflowManager to provide a familiar interface for components
that have not been fully migrated.
"""

from core.workflow_manager import WorkflowManager

class WireGenerator:
    """
    A wrapper class to maintain compatibility with older components that
    expect a WireGenerator class. All logic is delegated to the modern
    WorkflowManager.
    """
    def __init__(self, stl_path=None, arch_type='lower', wire_size='0.018'):
        self._workflow_manager = WorkflowManager()
        if stl_path:
            try:
                self._workflow_manager.load_arch(stl_path, arch_type)
            except Exception as e:
                print(f"Error loading STL file in WireGenerator: {e}")

    def generate_wire(self):
        """
        Triggers the automatic wire generation workflow. This is a simplified
        mapping for compatibility.
        """
        arch_type = self._workflow_manager.get_active_arch()
        try:
            # The results are stored within the manager, return success status
            self._workflow_manager.run_automatic_detection(arch_type)
            arch_data = self._workflow_manager.get_active_arch_data()
            return arch_data.get('wire_path') is not None
        except Exception as e:
            print(f"Error during automatic wire generation: {e}")
            return None

    def adjust_wire_height(self, height):
        """Adjusts the global wire height and regenerates the wire."""
        self._workflow_manager.set_global_height(height)

        # Re-generate wire to apply the new height
        arch_type = self._workflow_manager.get_active_arch()
        arch_data = self._workflow_manager.get_active_arch_data()
        if arch_data and arch_data.get('wire_path') is not None:
             if arch_data.get('control_points'):
                 self._workflow_manager.generate_wire_from_control_points(arch_type)
             elif arch_data.get('bracket_positions'):
                 self._workflow_manager.run_automatic_detection(arch_type)

    def launch_interactive_mode(self):
        """
        Placeholder for launching interactive mode. The new architecture
        handles this in run_hybrid_app.py.
        """
        print("Compatibility Warning: Interactive mode should be launched via 'run_hybrid_app.py'.")
        pass

    def print_summary(self):
        """Prints a summary of the generated wire path."""
        arch_data = self._workflow_manager.get_active_arch_data()
        if arch_data and arch_data.get('wire_path') is not None:
            print("\n--- Wire Generation Summary ---")
            print(f"  - Wire path generated with {len(arch_data['wire_path'])} points.")
            print(f"  - Active arch: {self._workflow_manager.get_active_arch()}")
            print(f"  - Height offset: {self._workflow_manager.global_height_offset} mm")
            print("-----------------------------\n")
        else:
            print("No wire path has been generated to summarize.")