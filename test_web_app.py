#!/usr/bin/env python3
"""
Test script for the web application functionality
"""

import requests
import json
import os
import time

def test_web_app(original_dir):
    """Test the web application endpoints."""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Orthodontic Wire Generator Web Application")
    print("=" * 60)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        print("✓ Server is running")
        print(f"  Status: {response.json()}")
    except Exception as e:
        print(f"❌ Server not running: {e}")
        return False
    
    # Test 2: Upload STL file
    stl_path = os.path.join(original_dir, "STLfiles/assets/Amina Imam scan for retainers LowerJawScan.stl")
    if os.path.exists(stl_path):
        try:
            with open(stl_path, 'rb') as f:
                files = {'file': f}
                data = {'arch_type': 'upper', 'wire_size': '0.018'}
                response = requests.post(f"{base_url}/api/upload_mesh", files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                print("✓ STL file uploaded successfully")
                print(f"  Response: {response.json()}")
            else:
                print(f"❌ STL upload failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ STL upload error: {e}")
            return False
    else:
        print(f"❌ STL file not found: {stl_path}")
        return False
    
    # Test 3: Get mesh data
    try:
        response = requests.get(f"{base_url}/api/get_mesh_data", timeout=10)
        if response.status_code == 200:
            mesh_data = response.json()
            print("✓ Mesh data retrieved successfully")
            print(f"  Vertices: {len(mesh_data['mesh']['vertices'])}")
            print(f"  Faces: {len(mesh_data['mesh']['faces'])}")
            print(f"  Center: {mesh_data['mesh']['center']}")
        else:
            print(f"❌ Mesh data retrieval failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Mesh data error: {e}")
        return False
    
    # Test 4: Generate wire
    try:
        response = requests.post(f"{base_url}/api/generate_wire", timeout=60)
        if response.status_code == 200:
            wire_result = response.json()
            print("✓ Wire generated successfully")
            print(f"  FA Points: {wire_result.get('fa_points_count', 0)}")
            print(f"  Control Points: {wire_result.get('control_points_count', 0)}")
        else:
            print(f"❌ Wire generation failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Wire generation error: {e}")
        return False
    
    # Test 5: Get wire data
    try:
        response = requests.get(f"{base_url}/api/get_wire_data", timeout=10)
        if response.status_code == 200:
            wire_data = response.json()
            print("✓ Wire data retrieved successfully")
            print(f"  Wire path points: {len(wire_data['wire']['path'])}")
            print(f"  Control points: {len(wire_data['control_points'])}")
        else:
            print(f"❌ Wire data retrieval failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Wire data error: {e}")
        return False
    
    # Test 6: Update control point
    try:
        update_data = {
            'point_id': 0,
            'position': [0, 0, 0]
        }
        response = requests.post(f"{base_url}/api/update_control_point", 
                               json=update_data, timeout=10)
        if response.status_code == 200:
            print("✓ Control point updated successfully")
        else:
            print(f"❌ Control point update failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Control point update error: {e}")
        return False
    
    # Test 7: Adjust wire position
    try:
        adjust_data = {
            'offset': [0, 1, 0]
        }
        response = requests.post(f"{base_url}/api/adjust_wire_position", 
                               json=adjust_data, timeout=10)
        if response.status_code == 200:
            print("✓ Wire position adjusted successfully")
        else:
            print(f"❌ Wire position adjustment failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Wire position adjustment error: {e}")
        return False
    
    print("=" * 60)
    print("🎉 All tests passed! Web application is working correctly.")
    return True

if __name__ == "__main__":
    # Start the Flask app in background
    import subprocess
    import signal
    import sys
    
    print("Starting Flask application...")
    
    # Save current directory
    original_dir = os.getcwd()
    
    # Change to web_app directory for Flask app
    os.chdir("web_app")
    
    # Start Flask app
    flask_process = subprocess.Popen([sys.executable, "app.py"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Run tests
        success = test_web_app(original_dir)
        
        if success:
            print("\n✅ Web application is fully functional!")
        else:
            print("\n❌ Some tests failed. Check the output above.")
            
    finally:
        # Stop Flask app
        flask_process.terminate()
        flask_process.wait()
        print("\nFlask application stopped.")
