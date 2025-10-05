#!/usr/bin/env python3
"""
Manual test for Flask endpoints
"""

import sys
import os
sys.path.append('web_app')
sys.path.append('.')

from web_app.app import app, WireGeneratorSession
import tempfile

def test_session_directly():
    """Test the session functionality directly."""
    
    print("🧪 Testing WireGeneratorSession directly")
    print("=" * 50)
    
    # Create a session
    session = WireGeneratorSession('test_session')
    
    # Test STL loading
    stl_path = 'STLfiles/assets/Amina Imam scan for retainers LowerJawScan.stl'
    
    print(f"Loading STL: {stl_path}")
    success = session.load_stl(stl_path, 'upper', '0.018')
    
    print(f"Load success: {success}")
    print(f"Session status: {session.status}")
    print(f"Mesh data available: {session.mesh_data is not None}")
    
    if session.mesh_data:
        print(f"Vertices: {len(session.mesh_data['vertices'])}")
        print(f"Faces: {len(session.mesh_data['faces'])}")
        print(f"Center: {session.mesh_data['center']}")
        print("✅ Mesh data extraction working!")
    else:
        print("❌ Mesh data extraction failed!")
        
        # Debug the issue
        print("\nDebugging...")
        print(f"Generator exists: {session.generator is not None}")
        if session.generator:
            print(f"Mesh processor exists: {session.generator.mesh_processor is not None}")
            print(f"STL path: {session.stl_path}")
            
            # Try manual extraction
            try:
                session._extract_mesh_data()
                print(f"Manual extraction result: {session.mesh_data is not None}")
            except Exception as e:
                print(f"Manual extraction error: {e}")
                import traceback
                traceback.print_exc()

def test_flask_app():
    """Test the Flask app endpoints."""
    
    print("\n🌐 Testing Flask App")
    print("=" * 50)
    
    with app.test_client() as client:
        # Test status endpoint
        response = client.get('/api/status')
        print(f"Status endpoint: {response.status_code}")
        print(f"Status data: {response.get_json()}")
        
        # Test file upload
        stl_path = 'STLfiles/assets/Amina Imam scan for retainers LowerJawScan.stl'
        
        if os.path.exists(stl_path):
            with open(stl_path, 'rb') as f:
                data = {
                    'file': (f, 'test.stl'),
                    'arch_type': 'upper',
                    'wire_size': '0.018'
                }
                response = client.post('/api/upload_mesh', data=data)
                
            print(f"Upload endpoint: {response.status_code}")
            print(f"Upload data: {response.get_json()}")
            
            # Test mesh data retrieval
            response = client.get('/api/get_mesh_data')
            print(f"Mesh data endpoint: {response.status_code}")
            print(f"Mesh data response: {response.get_json()}")
            
        else:
            print(f"STL file not found: {stl_path}")

if __name__ == "__main__":
    # Change to the correct directory
    os.chdir('/home/ubuntu/orthodontic_wire_generator_latest')
    
    # Test session directly
    test_session_directly()
    
    # Test Flask app
    test_flask_app()
