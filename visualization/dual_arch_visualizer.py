"""
Dual-Arch 3D Visualizer for Hybrid Automatic/Manual Orthodontic Wire Generator

This module provides a 3D visualizer that can display both upper and lower arches
with support for:
- Dual-arch visualization
- Interactive control point placement and editing
- Occlusal plane definition
- Wire path visualization
- Collision point display
"""

import sys
import os
import numpy as np
from typing import Optional, List, Dict, Any, Tuple

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from PyQt5.QtOpenGL import QOpenGLWidget
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtCore import Qt, pyqtSignal, QPoint
    from PyQt5.QtGui import QMouseEvent
    
    try:
        from OpenGL.GL import *
        from OpenGL.GLU import *
        OPENGL_AVAILABLE = True
    except ImportError:
        print("OpenGL not available, using fallback visualization")
        OPENGL_AVAILABLE = False
        
except ImportError:
    print("PyQt5 not available, using fallback visualization")
    OPENGL_AVAILABLE = False


class DualArchVisualizer(QOpenGLWidget if OPENGL_AVAILABLE else QWidget):
    """
    3D visualizer that can display both upper and lower arches
    """
    
    # Signals for interaction
    point_added = pyqtSignal(np.ndarray, str)  # point, type ('plane' or 'control')
    point_moved = pyqtSignal(int, np.ndarray)  # index, new_position
    interaction_mode_changed = pyqtSignal(str)  # mode
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Mesh data
        self.upper_arch_mesh = None
        self.lower_arch_mesh = None
        self.opposing_arch_mesh = None
        
        # Display settings
        self.active_arch = 'upper'
        self.show_both = False
        self.show_teeth = True
        self.show_brackets = True
        
        # Interaction mode
        self.interaction_mode = 'VIEW'  # VIEW, DEFINE_PLANE, PLACE_POINTS, DRAG_POINTS, EDIT_POINTS
        
        # Visualization data
        self.occlusal_plane_points = []
        self.control_points = []
        self.wire_path = None
        self.collision_points = []
        self.detected_teeth = []
        self.bracket_positions = []
        
        # Camera control
        self.camera_rotation = [0, 0]
        self.camera_distance = 100
        self.camera_center = [0, 0, 0]
        
        # Mouse interaction
        self.last_mouse_pos = QPoint()
        self.dragging_point_index = -1
        
        # Colors
        self.colors = {
            'upper_arch': (0.9, 0.9, 0.9, 1.0),
            'lower_arch': (0.85, 0.85, 0.85, 1.0),
            'opposing_arch': (0.7, 0.7, 0.9, 0.3),
            'wire': (0.2, 0.6, 1.0, 1.0),
            'control_points': (0, 1, 0, 1.0),
            'occlusal_plane': (1, 1, 0, 0.8),
            'collision_points': (1, 0, 0, 1.0),
            'teeth': (0.8, 0.8, 1.0, 0.7),
            'brackets': (1, 0.5, 0, 1.0)
        }
        
        if OPENGL_AVAILABLE:
            self.setMinimumSize(800, 600)
    
    def load_arch(self, mesh_data: Any, arch_type: str):
        """Load and display an arch"""
        if arch_type == 'upper':
            self.upper_arch_mesh = mesh_data
        elif arch_type == 'lower':
            self.lower_arch_mesh = mesh_data
        elif arch_type == 'opposing':
            self.opposing_arch_mesh = mesh_data
        
        if OPENGL_AVAILABLE:
            self.update()
    
    def set_active_arch(self, arch_type: str):
        """Set which arch is being designed"""
        self.active_arch = arch_type
        if OPENGL_AVAILABLE:
            self.update()
    
    def set_show_both_arches(self, show_both: bool):
        """Toggle showing both arches"""
        self.show_both = show_both
        if OPENGL_AVAILABLE:
            self.update()
    
    def set_show_teeth(self, show_teeth: bool):
        """Toggle display of detected teeth"""
        self.show_teeth = show_teeth
        if OPENGL_AVAILABLE:
            self.update()
    
    def set_show_brackets(self, show_brackets: bool):
        """Toggle display of bracket positions"""
        self.show_brackets = show_brackets
        if OPENGL_AVAILABLE:
            self.update()
    
    def set_interaction_mode(self, mode: str):
        """Set interaction mode for mouse clicks"""
        self.interaction_mode = mode
        
        if mode == 'DEFINE_PLANE':
            self.setCursor(Qt.CrossCursor)
        elif mode in ['PLACE_POINTS', 'DRAG_POINTS', 'EDIT_POINTS']:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        
        self.interaction_mode_changed.emit(mode)
    
    def display_automatic_results(self, detected_teeth: List, bracket_positions: List, 
                                wire_path: np.ndarray, arch_type: str):
        """Display results from automatic detection"""
        self.detected_teeth = detected_teeth
        self.bracket_positions = bracket_positions
        self.wire_path = wire_path
        
        if OPENGL_AVAILABLE:
            self.update()
    
    def display_editable_control_points(self, control_points: List[np.ndarray]):
        """Display control points that can be edited"""
        self.control_points = control_points
        self.set_interaction_mode('EDIT_POINTS')
        
        if OPENGL_AVAILABLE:
            self.update()
    
    def display_wire_path(self, wire_path: np.ndarray):
        """Display wire path"""
        self.wire_path = wire_path
        
        if OPENGL_AVAILABLE:
            self.update()
    
    def display_collision_points(self, collision_points: List[np.ndarray]):
        """Display collision points"""
        self.collision_points = collision_points
        
        if OPENGL_AVAILABLE:
            self.update()
    
    def clear_plane(self):
        """Clear occlusal plane"""
        self.occlusal_plane_points = []
        if OPENGL_AVAILABLE:
            self.update()
    
    def clear_control_points(self):
        """Clear all control points"""
        self.control_points = []
        if OPENGL_AVAILABLE:
            self.update()
    
    def update_control_points(self):
        """Update control points display"""
        if OPENGL_AVAILABLE:
            self.update()
    
    def update_wire_display(self):
        """Update wire display"""
        if OPENGL_AVAILABLE:
            self.update()
    
    # ============================================
    # OPENGL RENDERING (if available)
    # ============================================
    
    if OPENGL_AVAILABLE:
        def initializeGL(self):
            """Initialize OpenGL"""
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glClearColor(0.2, 0.2, 0.2, 1.0)
            
            # Setup lighting
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            
            light_pos = [10.0, 10.0, 10.0, 1.0]
            light_ambient = [0.3, 0.3, 0.3, 1.0]
            light_diffuse = [0.8, 0.8, 0.8, 1.0]
            
            glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
            glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
            glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        
        def resizeGL(self, width: int, height: int):
            """Handle window resize"""
            glViewport(0, 0, width, height)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45.0, width / height, 0.1, 1000.0)
            glMatrixMode(GL_MODELVIEW)
        
        def paintGL(self):
            """Render the 3D scene"""
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            # Setup camera
            self.setup_camera()
            
            # Draw upper arch
            if self.upper_arch_mesh is not None:
                if self.show_both or self.active_arch == 'upper':
                    self.draw_mesh(self.upper_arch_mesh, self.colors['upper_arch'])
            
            # Draw lower arch
            if self.lower_arch_mesh is not None:
                if self.show_both or self.active_arch == 'lower':
                    self.draw_mesh(self.lower_arch_mesh, self.colors['lower_arch'])
            
            # Draw opposing arch (if loaded, semi-transparent)
            if self.opposing_arch_mesh is not None:
                self.draw_mesh(self.opposing_arch_mesh, self.colors['opposing_arch'])
            
            # Draw detected teeth
            if self.show_teeth and len(self.detected_teeth) > 0:
                for tooth in self.detected_teeth:
                    self.draw_tooth_outline(tooth, self.colors['teeth'])
            
            # Draw bracket positions
            if self.show_brackets and len(self.bracket_positions) > 0:
                for i, bracket_pos in enumerate(self.bracket_positions):
                    self.draw_sphere(bracket_pos, radius=0.8, color=self.colors['brackets'])
                    self.draw_text_3d(bracket_pos, f"B{i+1}")
            
            # Draw occlusal plane
            if len(self.occlusal_plane_points) > 0:
                self.draw_occlusal_plane()
            
            # Draw control points
            for i, point in enumerate(self.control_points):
                color = self.colors['control_points']
                if self.interaction_mode == 'DRAG_POINTS' and i == self.dragging_point_index:
                    color = (1, 1, 0, 1)  # Highlight dragged point
                
                self.draw_sphere(point, radius=1.0, color=color)
                self.draw_text_3d(point, f"P{i+1}")
            
            # Draw wire path
            if self.wire_path is not None:
                self.draw_wire_path(self.wire_path)
            
            # Draw collision points
            for point in self.collision_points:
                self.draw_sphere(point, radius=0.5, color=self.colors['collision_points'])
        
        def setup_camera(self):
            """Setup camera position and orientation"""
            glTranslatef(0, 0, -self.camera_distance)
            glRotatef(self.camera_rotation[0], 1, 0, 0)
            glRotatef(self.camera_rotation[1], 0, 1, 0)
            glTranslatef(-self.camera_center[0], -self.camera_center[1], -self.camera_center[2])
        
        def draw_mesh(self, mesh_data: Any, color: Tuple[float, float, float, float]):
            """Draw a mesh with the specified color"""
            # This is a simplified mesh drawing - in practice, you'd use the actual mesh data
            glColor4f(*color)
            
            # Enable material properties
            glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color)
            
            # Draw mesh triangles (simplified - actual implementation would use mesh vertices/faces)
            # For now, just draw a placeholder
            self.draw_placeholder_arch()
        
        def draw_placeholder_arch(self):
            """Draw a placeholder arch shape"""
            glBegin(GL_TRIANGLES)
            # Simple arch-like shape
            for i in range(20):
                angle1 = i * np.pi / 20
                angle2 = (i + 1) * np.pi / 20
                
                x1, z1 = 20 * np.cos(angle1), 20 * np.sin(angle1)
                x2, z2 = 20 * np.cos(angle2), 20 * np.sin(angle2)
                
                # Create triangles for arch
                glVertex3f(x1, 0, z1)
                glVertex3f(x2, 0, z2)
                glVertex3f(x1, 5, z1)
                
                glVertex3f(x2, 0, z2)
                glVertex3f(x2, 5, z2)
                glVertex3f(x1, 5, z1)
            glEnd()
        
        def draw_sphere(self, center: np.ndarray, radius: float, color: Tuple[float, float, float, float]):
            """Draw a sphere at the specified position"""
            glPushMatrix()
            glTranslatef(center[0], center[1], center[2])
            glColor4f(*color)
            glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color)
            
            # Draw sphere using GLU
            from OpenGL.GLU import gluSphere, gluNewQuadric
            quadric = gluNewQuadric()
            gluSphere(quadric, radius, 16, 16)
            
            glPopMatrix()
        
        def draw_wire_path(self, wire_path: np.ndarray):
            """Draw the wire path as a smooth curve"""
            if len(wire_path) < 2:
                return
            
            glDisable(GL_LIGHTING)
            glColor4f(*self.colors['wire'])
            glLineWidth(3.0)
            
            glBegin(GL_LINE_STRIP)
            for point in wire_path:
                glVertex3f(point[0], point[1], point[2])
            glEnd()
            
            glEnable(GL_LIGHTING)
            glLineWidth(1.0)
        
        def draw_occlusal_plane(self):
            """Draw the occlusal plane"""
            # Draw the 3 points
            for i, point in enumerate(self.occlusal_plane_points):
                self.draw_sphere(point, radius=1.2, color=self.colors['occlusal_plane'])
                self.draw_text_3d(point, f"OP{i+1}")
            
            # If 3 points, draw the plane
            if len(self.occlusal_plane_points) == 3:
                center = np.mean(self.occlusal_plane_points, axis=0)
                normal = self.calculate_plane_normal(self.occlusal_plane_points)
                
                # Draw plane grid
                self.draw_plane_grid(center, normal, size=50, color=self.colors['occlusal_plane'])
        
        def draw_plane_grid(self, center: np.ndarray, normal: np.ndarray, 
                          size: float, color: Tuple[float, float, float, float]):
            """Draw a grid representing the occlusal plane"""
            # Create two perpendicular vectors in the plane
            if abs(normal[2]) < 0.9:
                v1 = np.cross(normal, [0, 0, 1])
            else:
                v1 = np.cross(normal, [1, 0, 0])
            
            v1 = v1 / np.linalg.norm(v1)
            v2 = np.cross(normal, v1)
            v2 = v2 / np.linalg.norm(v2)
            
            glDisable(GL_LIGHTING)
            glColor4f(*color)
            glLineWidth(1.0)
            
            # Draw grid lines
            glBegin(GL_LINES)
            for i in range(-5, 6):
                t = i * size / 10
                
                # Lines in v1 direction
                p1 = center + t * v1 - size/2 * v2
                p2 = center + t * v1 + size/2 * v2
                glVertex3f(p1[0], p1[1], p1[2])
                glVertex3f(p2[0], p2[1], p2[2])
                
                # Lines in v2 direction
                p1 = center + t * v2 - size/2 * v1
                p2 = center + t * v2 + size/2 * v1
                glVertex3f(p1[0], p1[1], p1[2])
                glVertex3f(p2[0], p2[1], p2[2])
            glEnd()
            
            glEnable(GL_LIGHTING)
        
        def draw_tooth_outline(self, tooth_data: Any, color: Tuple[float, float, float, float]):
            """Draw outline of detected tooth"""
            # Simplified tooth outline drawing
            glDisable(GL_LIGHTING)
            glColor4f(*color)
            glLineWidth(2.0)
            
            # Draw a simple tooth outline (placeholder)
            # In practice, this would use the actual tooth boundary data
            glBegin(GL_LINE_LOOP)
            for i in range(8):
                angle = i * 2 * np.pi / 8
                x = 3 * np.cos(angle)
                z = 2 * np.sin(angle)
                glVertex3f(x, 0, z)
            glEnd()
            
            glEnable(GL_LIGHTING)
            glLineWidth(1.0)
        
        def draw_text_3d(self, position: np.ndarray, text: str):
            """Draw 3D text at the specified position"""
            # Simplified text drawing - in practice, you'd use a proper text rendering system
            pass
        
        def calculate_plane_normal(self, points: List[np.ndarray]) -> np.ndarray:
            """Calculate normal vector from 3 points"""
            if len(points) < 3:
                return np.array([0, 1, 0])
            
            v1 = points[1] - points[0]
            v2 = points[2] - points[0]
            normal = np.cross(v1, v2)
            
            if np.linalg.norm(normal) > 0:
                return normal / np.linalg.norm(normal)
            else:
                return np.array([0, 1, 0])
    
    # ============================================
    # MOUSE INTERACTION
    # ============================================
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse clicks based on interaction mode"""
        if event.button() == Qt.LeftButton:
            if self.interaction_mode == 'DEFINE_PLANE':
                self.add_occlusal_plane_point(event.pos())
            elif self.interaction_mode == 'PLACE_POINTS':
                self.add_control_point(event.pos())
            elif self.interaction_mode in ['DRAG_POINTS', 'EDIT_POINTS']:
                self.start_dragging_point(event.pos())
        elif event.button() == Qt.RightButton:
            # Right click for camera rotation
            self.last_mouse_pos = event.pos()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse movement"""
        if event.buttons() & Qt.RightButton:
            # Camera rotation
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()
            
            self.camera_rotation[1] += dx * 0.5
            self.camera_rotation[0] += dy * 0.5
            
            self.last_mouse_pos = event.pos()
            
            if OPENGL_AVAILABLE:
                self.update()
        
        elif event.buttons() & Qt.LeftButton and self.dragging_point_index >= 0:
            # Drag control point
            new_position = self.screen_to_world(event.pos())
            if new_position is not None:
                self.control_points[self.dragging_point_index] = new_position
                self.point_moved.emit(self.dragging_point_index, new_position)
                
                if OPENGL_AVAILABLE:
                    self.update()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.dragging_point_index = -1
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        delta = event.angleDelta().y()
        zoom_factor = 1.1 if delta > 0 else 0.9
        self.camera_distance *= zoom_factor
        self.camera_distance = max(10, min(500, self.camera_distance))
        
        if OPENGL_AVAILABLE:
            self.update()
    
    def add_occlusal_plane_point(self, screen_pos: QPoint):
        """Add a point for occlusal plane definition"""
        world_pos = self.screen_to_world(screen_pos)
        if world_pos is not None and len(self.occlusal_plane_points) < 3:
            self.occlusal_plane_points.append(world_pos)
            self.point_added.emit(world_pos, 'plane')
            
            if OPENGL_AVAILABLE:
                self.update()
    
    def add_control_point(self, screen_pos: QPoint):
        """Add a control point"""
        world_pos = self.screen_to_world(screen_pos)
        if world_pos is not None:
            self.control_points.append(world_pos)
            self.point_added.emit(world_pos, 'control')
            
            if OPENGL_AVAILABLE:
                self.update()
    
    def start_dragging_point(self, screen_pos: QPoint):
        """Start dragging the nearest control point"""
        world_pos = self.screen_to_world(screen_pos)
        if world_pos is None:
            return
        
        # Find nearest control point
        min_distance = float('inf')
        nearest_index = -1
        
        for i, point in enumerate(self.control_points):
            distance = np.linalg.norm(world_pos - point)
            if distance < min_distance and distance < 5.0:  # 5.0 is selection threshold
                min_distance = distance
                nearest_index = i
        
        self.dragging_point_index = nearest_index
    
    def screen_to_world(self, screen_pos: QPoint) -> Optional[np.ndarray]:
        """Convert screen coordinates to world coordinates"""
        # This is a simplified implementation
        # In practice, you'd use proper OpenGL coordinate transformation
        
        # For now, return a placeholder position
        # This would need proper implementation using gluUnProject
        return np.array([
            (screen_pos.x() - self.width()/2) * 0.1,
            -(screen_pos.y() - self.height()/2) * 0.1,
            0.0
        ])


# Fallback implementation for systems without OpenGL
class DualArchVisualizerFallback(QWidget):
    """Fallback visualizer for systems without OpenGL support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: #333; color: white;")
        
        # Add a label indicating fallback mode
        from PyQt5.QtWidgets import QVBoxLayout, QLabel
        layout = QVBoxLayout()
        label = QLabel("3D Visualization (Fallback Mode)\nOpenGL not available")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)
    
    # Implement stub methods for compatibility
    def load_arch(self, mesh_data, arch_type): pass
    def set_active_arch(self, arch_type): pass
    def set_show_both_arches(self, show_both): pass
    def set_show_teeth(self, show_teeth): pass
    def set_show_brackets(self, show_brackets): pass
    def set_interaction_mode(self, mode): pass
    def display_automatic_results(self, detected_teeth, bracket_positions, wire_path, arch_type): pass
    def display_editable_control_points(self, control_points): pass
    def display_wire_path(self, wire_path): pass
    def display_collision_points(self, collision_points): pass
    def clear_plane(self): pass
    def clear_control_points(self): pass
    def update_control_points(self): pass
    def update_wire_display(self): pass


# Use fallback if OpenGL is not available
if not OPENGL_AVAILABLE:
    DualArchVisualizer = DualArchVisualizerFallback
