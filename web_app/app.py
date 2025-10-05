#!/usr/bin/env python3
"""
web_app/app.py

Flask Web Application for Orthodontic Wire Generator
===================================================
Modern web-based UI replacing the desktop application.
Implements FIXR-inspired workflow with Three.js 3D visualization.
"""

import os
import sys
import json
import tempfile
import numpy as np
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import uuid

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wire.wire_generator import WireGenerator
from core.mesh_processor import MeshProcessor
import open3d as o3d

app = Flask(__name__)
app.secret_key = 'orthodontic_wire_generator_secret_key_2024'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Global storage for active sessions
active_sessions = {}

class WireGeneratorSession:
    """Manages a wire generation session for a user."""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.generator = None
        self.stl_path = None
        self.mesh_data = None
        self.wire_data = None
        self.control_points = []
        self.status = "initialized"
    
    def load_stl(self, stl_path, arch_type='upper', wire_size='0.018'):
        """Load STL file and initialize wire generator."""
        try:
            self.stl_path = stl_path
            self.generator = WireGenerator(stl_path, arch_type, wire_size)
            self.status = "stl_loaded"
            
            # Extract mesh data immediately after loading
            self._extract_mesh_data()
            
            return True
        except Exception as e:
            print(f"Error loading STL: {e}")
            return False
    
    def generate_wire(self):
        """Generate wire using FIXR-inspired approach."""
        try:
            if not self.generator:
                return False
            
            result = self.generator.generate_wire()
            if result:
                self.status = "wire_generated"
                self._extract_mesh_data()
                self._extract_wire_data()
                self._extract_control_points()
                return True
            return False
        except Exception as e:
            print(f"Error generating wire: {e}")
            return False
    
    def _extract_mesh_data(self):
        """Extract mesh data for Three.js rendering."""
        try:
            # Load mesh using the mesh processor
            if self.generator and self.generator.mesh_processor:
                mesh = self.generator.mesh_processor.load_stl(self.stl_path)
                if mesh:
                    # Clean the mesh
                    mesh = self.generator.mesh_processor.clean_mesh(mesh)
                    
                    vertices = np.asarray(mesh.vertices)
                    triangles = np.asarray(mesh.triangles)
                    
                    # Optimize mesh for web rendering - reduce complexity if too large
                    max_vertices = 20000  # Reasonable limit for web rendering
                    if len(vertices) > max_vertices:
                        print(f"Mesh too large ({len(vertices)} vertices), simplifying...")
                        
                        # Simplify mesh using Open3D
                        target_triangles = int(len(triangles) * (max_vertices / len(vertices)))
                        simplified_mesh = mesh.simplify_quadric_decimation(target_triangles)
                        
                        vertices = np.asarray(simplified_mesh.vertices)
                        triangles = np.asarray(simplified_mesh.triangles)
                        
                        print(f"Mesh simplified to {len(vertices)} vertices, {len(triangles)} faces")
                    
                    # Calculate center
                    center = vertices.mean(axis=0) if len(vertices) > 0 else [0, 0, 0]
                    
                    self.mesh_data = {
                        'vertices': vertices.tolist(),
                        'faces': triangles.tolist(),
                        'center': center.tolist()
                    }
                    
                    print(f"✓ Mesh data extracted: {len(vertices)} vertices, {len(triangles)} faces")
                else:
                    print("❌ Failed to load mesh")
                    self.mesh_data = None
            else:
                print("❌ No mesh processor available")
                self.mesh_data = None
        except Exception as e:
            print(f"Error extracting mesh data: {e}")
            import traceback
            traceback.print_exc()
            self.mesh_data = None
    
    def _extract_wire_data(self):
        """Extract wire data for Three.js rendering."""
        try:
            if self.generator and self.generator.wire_path is not None:
                wire_path = self.generator.wire_path
                
                self.wire_data = {
                    'path': wire_path.tolist(),
                    'radius': self.generator.wire_radius if hasattr(self.generator, 'wire_radius') else 0.25
                }
        except Exception as e:
            print(f"Error extracting wire data: {e}")
            self.wire_data = None
    
    def _extract_control_points(self):
        """Extract control points for interactive manipulation."""
        try:
            if self.generator and hasattr(self.generator, 'interactive_control_points'):
                control_points = self.generator.interactive_control_points
                
                self.control_points = []
                for i, cp in enumerate(control_points):
                    self.control_points.append({
                        'id': i,
                        'position': cp['position'].tolist(),
                        'type': cp['type'],
                        'surface_constrained': cp.get('surface_constrained', False)
                    })
        except Exception as e:
            print(f"Error extracting control points: {e}")
            self.control_points = []
    
    def update_control_point(self, point_id, new_position):
        """Update a control point position with surface constraint."""
        try:
            if not self.generator or point_id >= len(self.control_points):
                return False
            
            # Convert to numpy array
            new_pos = np.array(new_position)
            
            # Use the generator's surface constraint method
            self.generator._handle_interactive_update(point_id, new_pos)
            
            # Update our stored data
            self._extract_wire_data()
            self._extract_control_points()
            
            return True
        except Exception as e:
            print(f"Error updating control point: {e}")
            return False
    
    def adjust_wire_position(self, offset):
        """Adjust wire position."""
        try:
            if not self.generator:
                return False
            
            # Apply offset to wire path
            if self.generator.wire_path is not None:
                self.generator.wire_path += np.array(offset)
                
                # Rebuild wire mesh
                self.generator.wire_mesh = self.generator.wire_mesh_builder.build_wire_mesh(
                    self.generator.wire_path
                )
                
                # Update our stored data
                self._extract_wire_data()
                return True
            return False
        except Exception as e:
            print(f"Error adjusting wire position: {e}")
            return False
    
    def export_stl(self, output_path):
        """Export wire as STL file."""
        try:
            if not self.generator or not self.generator.wire_mesh:
                return False
            
            o3d.io.write_triangle_mesh(output_path, self.generator.wire_mesh)
            return True
        except Exception as e:
            print(f"Error exporting STL: {e}")
            return False

def get_session():
    """Get or create a session for the current user."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    session_id = session['session_id']
    if session_id not in active_sessions:
        active_sessions[session_id] = WireGeneratorSession(session_id)
    
    return active_sessions[session_id]

@app.route('/')
def index():
    """Main application page."""
    return render_template('index.html')

@app.route('/api/upload_mesh', methods=['POST'])
def upload_mesh():
    """Upload STL mesh file."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.stl'):
            return jsonify({'error': 'Only STL files are supported'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        stl_path = os.path.join(temp_dir, filename)
        file.save(stl_path)
        
        # Get session and load STL
        user_session = get_session()
        arch_type = request.form.get('arch_type', 'upper')
        wire_size = request.form.get('wire_size', '0.018')
        
        if user_session.load_stl(stl_path, arch_type, wire_size):
            return jsonify({
                'success': True,
                'message': 'STL file uploaded successfully',
                'filename': filename,
                'arch_type': arch_type,
                'wire_size': wire_size
            })
        else:
            return jsonify({'error': 'Failed to load STL file'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/generate_wire', methods=['POST'])
def generate_wire():
    """Generate wire using FIXR-inspired approach."""
    try:
        user_session = get_session()
        
        if user_session.status != "stl_loaded":
            return jsonify({'error': 'No STL file loaded'}), 400
        
        if user_session.generate_wire():
            return jsonify({
                'success': True,
                'message': 'Wire generated successfully using FIXR-inspired approach',
                'status': user_session.status,
                'fa_points_count': len(user_session.generator.fa_points) if hasattr(user_session.generator, 'fa_points') else 0,
                'control_points_count': len(user_session.control_points)
            })
        else:
            return jsonify({'error': 'Failed to generate wire'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Wire generation failed: {str(e)}'}), 500

@app.route('/api/get_mesh_data')
def get_mesh_data():
    """Get mesh data for Three.js rendering."""
    try:
        user_session = get_session()
        
        print(f"Debug - Session status: {user_session.status}")
        print(f"Debug - Mesh data available: {user_session.mesh_data is not None}")
        print(f"Debug - Generator available: {user_session.generator is not None}")
        
        if not user_session.mesh_data:
            # Try to extract mesh data if we have a generator but no mesh data
            if user_session.generator and user_session.stl_path:
                print("Debug - Attempting to re-extract mesh data")
                user_session._extract_mesh_data()
                
                if user_session.mesh_data:
                    print("Debug - Mesh data re-extracted successfully")
                else:
                    print("Debug - Failed to re-extract mesh data")
                    return jsonify({'error': 'Failed to extract mesh data'}), 500
            else:
                return jsonify({'error': 'No mesh data available'}), 404
        
        return jsonify({
            'success': True,
            'mesh': user_session.mesh_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get mesh data: {str(e)}'}), 500

@app.route('/api/get_wire_data')
def get_wire_data():
    """Get wire data for Three.js rendering."""
    try:
        user_session = get_session()
        
        if not user_session.wire_data:
            return jsonify({'error': 'No wire data available'}), 404
        
        return jsonify({
            'success': True,
            'wire': user_session.wire_data,
            'control_points': user_session.control_points
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get wire data: {str(e)}'}), 500

@app.route('/api/update_control_point', methods=['POST'])
def update_control_point():
    """Update control point position with FIXR-style surface constraint."""
    try:
        data = request.get_json()
        point_id = data.get('point_id')
        new_position = data.get('position')
        
        if point_id is None or new_position is None:
            return jsonify({'error': 'Missing point_id or position'}), 400
        
        user_session = get_session()
        
        if user_session.update_control_point(point_id, new_position):
            return jsonify({
                'success': True,
                'message': 'Control point updated with surface constraint',
                'wire': user_session.wire_data,
                'control_points': user_session.control_points
            })
        else:
            return jsonify({'error': 'Failed to update control point'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Control point update failed: {str(e)}'}), 500

@app.route('/api/adjust_wire_position', methods=['POST'])
def adjust_wire_position():
    """Adjust wire position."""
    try:
        data = request.get_json()
        offset = data.get('offset', [0, 0, 0])
        
        user_session = get_session()
        
        if user_session.adjust_wire_position(offset):
            return jsonify({
                'success': True,
                'message': 'Wire position adjusted',
                'wire': user_session.wire_data
            })
        else:
            return jsonify({'error': 'Failed to adjust wire position'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Wire adjustment failed: {str(e)}'}), 500

@app.route('/api/export_stl')
def export_stl():
    """Export wire as STL file."""
    try:
        user_session = get_session()
        
        if user_session.status != "wire_generated":
            return jsonify({'error': 'No wire to export'}), 400
        
        # Create temporary file for export
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, 'orthodontic_wire.stl')
        
        if user_session.export_stl(output_path):
            return send_file(
                output_path,
                as_attachment=True,
                download_name='orthodontic_wire.stl',
                mimetype='application/octet-stream'
            )
        else:
            return jsonify({'error': 'Failed to export STL'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@app.route('/api/status')
def get_status():
    """Get current session status."""
    try:
        user_session = get_session()
        
        return jsonify({
            'success': True,
            'status': user_session.status,
            'has_mesh': user_session.mesh_data is not None,
            'has_wire': user_session.wire_data is not None,
            'control_points_count': len(user_session.control_points)
        })
        
    except Exception as e:
        return jsonify({'error': f'Status check failed: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting Orthodontic Wire Generator Web Application")
    print("📐 FIXR-inspired surface adaptation enabled")
    print("🌐 Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
