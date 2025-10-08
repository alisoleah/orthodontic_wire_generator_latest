import sys
import os
import numpy as np
import pytest

# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.workflow_manager import WorkflowManager, WorkflowMode

# Path to the sample STL file
STL_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'STLfiles', 'HanaElfouly_LowerJaw.stl')

@pytest.fixture
def workflow_manager():
    """Fixture to create a WorkflowManager instance for testing."""
    return WorkflowManager()

def test_3_point_wire_definition_workflow(workflow_manager):
    """
    Tests the entire 3-point manual wire definition workflow, from loading a mesh
    to generating a wire path.
    """
    # 1. Ensure the STL file exists
    assert os.path.exists(STL_FILE_PATH), f"STL file not found at: {STL_FILE_PATH}"

    # 2. Load the lower jaw mesh
    arch_type = 'lower'
    mesh = workflow_manager.load_arch(STL_FILE_PATH, arch_type)
    assert mesh is not None, "Failed to load the arch mesh."

    arch_data = workflow_manager.get_arch_data(arch_type)
    assert arch_data is not None, "Arch data was not created after loading."

    # 3. Set the workflow mode to Manual
    workflow_manager.set_mode(WorkflowMode.MANUAL)
    assert workflow_manager.current_mode == WorkflowMode.MANUAL

    # 4. Simulate the selection of three control points
    # These points are chosen to be on the surface of a typical dental arch.
    control_points = [
        np.array([-20.0, -10.0, 5.0]),
        np.array([0.0, -15.0, 6.0]),
        np.array([20.0, -10.0, 5.0])
    ]

    workflow_manager.clear_control_points(arch_type)
    for point in control_points:
        workflow_manager.add_control_point(point, arch_type)

    assert len(arch_data['control_points']) == 3, "Control points were not added correctly."

    # 5. Generate the wire from the control points
    try:
        wire_path = workflow_manager.generate_wire_from_control_points(arch_type)
    except Exception as e:
        pytest.fail(f"Wire generation from control points failed with an exception: {e}")

    # 6. Validate the generated wire path
    assert wire_path is not None, "Wire path should not be None."
    assert isinstance(wire_path, np.ndarray), "Wire path should be a numpy array."
    assert wire_path.ndim == 2, "Wire path should be a 2D array."
    assert wire_path.shape[1] == 3, "Wire path should have 3 columns (x, y, z)."
    assert wire_path.shape[0] > len(control_points), "Wire path should have more points than control points due to smoothing."

    print(f"Successfully generated wire path with {wire_path.shape[0]} points.")

if __name__ == "__main__":
    pytest.main(['-v', __file__])