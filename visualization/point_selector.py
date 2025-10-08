import pyvista as pv
import numpy as np
import open3d as o3d
from typing import Optional, List

class DentalPointSelector:
    def __init__(self, o3d_mesh, parent_window=None, n_points=3):
        self.o3d_mesh = o3d_mesh
        self.parent = parent_window
        self.n_points = n_points
        self.selected_points = []
        self.selected_indices = []

    def show(self) -> Optional[List[np.ndarray]]:
        """Launch modal selection dialog"""
        if self.parent:
            self.parent.wm_attributes("-disabled", True)

        try:
            # Convert mesh
            from .mesh_converter import open3d_to_pyvista
            pv_mesh = open3d_to_pyvista(self.o3d_mesh)

            # Setup plotter
            self.plotter = pv.Plotter()
            self.plotter.add_mesh(
                pv_mesh,
                color='tan',
                show_edges=True,
                pickable=True
            )

            # Enable point picking
            self.plotter.enable_point_picking(
                callback=self._on_point_picked,
                use_picker=True,
                pickable_window=False,
                show_message=f"Right-click to select {self.n_points} points"
            )

            # Add instructions
            self.plotter.add_text(
                f"Select {self.n_points} points on the dental arch\n"
                f"Selected: 0/{self.n_points}",
                position='upper_left',
                font_size=12,
                name='instructions'
            )

            self.plotter.show()

        finally:
            if self.parent:
                self.parent.wm_attributes("-disabled", False)

        return self.selected_points if len(self.selected_points) == self.n_points else None

    def _on_point_picked(self, point, picker):
        """Callback for each point selection"""
        if len(self.selected_points) >= self.n_points:
            return

        point_idx = picker.GetPointId()
        if point_idx in self.selected_indices:
            return  # Prevent duplicate selections

        self.selected_indices.append(point_idx)
        self.selected_points.append(point)

        # Add visual marker
        colors = ['red', 'green', 'blue']
        idx = len(self.selected_points) - 1
        sphere = pv.Sphere(radius=0.5, center=point)
        self.plotter.add_mesh(
            sphere,
            color=colors[idx % 3],
            name=f'point_{idx+1}'
        )

        # Add label
        self.plotter.add_point_labels(
            [point],
            [f"P{idx+1}"],
            point_size=20,
            font_size=24,
            name=f'label_{idx+1}'
        )

        # Update instructions
        self.plotter.add_text(
            f"Select {self.n_points} points on the dental arch\n"
            f"Selected: {len(self.selected_points)}/{self.n_points}",
            position='upper_left',
            font_size=12,
            name='instructions'
        )

        # Show completion message or update count
        if self.n_points > 0 and len(self.selected_points) >= self.n_points:
            self.plotter.add_text(
                "Selection complete! Close window to continue.",
                position='lower_center',
                font_size=16,
                color='green',
                name='complete'
            )
            if self.n_points == 3:
                self._validate_plane()
        elif self.n_points <= 0: # For open-ended selection
             self.plotter.add_text(
                "Press 'q' to close the window when you are finished.",
                position='lower_center',
                font_size=12,
                color='yellow',
                name='finish_hint'
            )

    def _validate_plane(self):
        """Check if points are non-colinear"""
        p1, p2, p3 = self.selected_points
        v1 = np.array(p2) - np.array(p1)
        v2 = np.array(p3) - np.array(p1)
        cross = np.cross(v1, v2)

        if np.linalg.norm(cross) < 1e-6:
            self.plotter.add_text(
                "WARNING: Points are nearly colinear!",
                position='lower_left',
                font_size=14,
                color='red',
                name='warning'
            )