/**
 * API Client for Backend Communication
 * Handles all HTTP requests to the Flask backend
 */

class APIClient {
    constructor() {
        this.baseURL = '';
        this.isProcessing = false;
    }
    
    async uploadMesh(file, archType = 'upper', wireSize = '0.018') {
        try {
            this.setProcessing(true);
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('arch_type', archType);
            formData.append('wire_size', wireSize);
            
            const response = await fetch('/api/upload_mesh', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Upload failed');
            }
            
            console.log('✓ STL uploaded successfully:', result);
            return result;
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        } finally {
            this.setProcessing(false);
        }
    }
    
    async generateWire() {
        try {
            this.setProcessing(true);
            
            const response = await fetch('/api/generate_wire', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Wire generation failed');
            }
            
            console.log('✓ Wire generated successfully:', result);
            return result;
        } catch (error) {
            console.error('Wire generation error:', error);
            throw error;
        } finally {
            this.setProcessing(false);
        }
    }
    
    async getMeshData() {
        try {
            const response = await fetch('/api/get_mesh_data');
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Failed to get mesh data');
            }
            
            return result.mesh;
        } catch (error) {
            console.error('Get mesh data error:', error);
            throw error;
        }
    }
    
    async getWireData() {
        try {
            const response = await fetch('/api/get_wire_data');
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Failed to get wire data');
            }
            
            return {
                wire: result.wire,
                controlPoints: result.control_points
            };
        } catch (error) {
            console.error('Get wire data error:', error);
            throw error;
        }
    }
    
    async updateControlPoint(pointId, position) {
        try {
            const response = await fetch('/api/update_control_point', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    point_id: pointId,
                    position: position
                })
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Failed to update control point');
            }
            
            console.log('✓ Control point updated:', pointId);
            
            // Update the 3D visualization with new wire data
            if (window.threeViewer && result.wire) {
                window.threeViewer.loadWire(result.wire, result.control_points);
            }
            
            return result;
        } catch (error) {
            console.error('Update control point error:', error);
            throw error;
        }
    }
    
    async adjustWirePosition(offset) {
        try {
            const response = await fetch('/api/adjust_wire_position', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    offset: offset
                })
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Failed to adjust wire position');
            }
            
            console.log('✓ Wire position adjusted');
            
            // Update the 3D visualization
            if (window.threeViewer && result.wire) {
                // Get current control points
                const wireData = await this.getWireData();
                window.threeViewer.loadWire(result.wire, wireData.controlPoints);
            }
            
            return result;
        } catch (error) {
            console.error('Adjust wire position error:', error);
            throw error;
        }
    }
    
    async exportSTL() {
        try {
            const response = await fetch('/api/export_stl');
            
            if (!response.ok) {
                const result = await response.json();
                throw new Error(result.error || 'Export failed');
            }
            
            // Create download link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'orthodontic_wire.stl';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            console.log('✓ STL exported successfully');
            return true;
        } catch (error) {
            console.error('Export error:', error);
            throw error;
        }
    }
    
    async getStatus() {
        try {
            const response = await fetch('/api/status');
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Failed to get status');
            }
            
            return result;
        } catch (error) {
            console.error('Get status error:', error);
            throw error;
        }
    }
    
    setProcessing(processing) {
        this.isProcessing = processing;
        
        // Update UI to show processing state
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        if (processing) {
            statusDot.className = 'status-dot status-processing';
            statusText.textContent = 'Processing...';
        } else {
            statusDot.className = 'status-dot status-ready';
            statusText.textContent = 'Ready';
        }
        
        // Disable/enable buttons during processing
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(btn => {
            if (processing) {
                btn.disabled = true;
            } else {
                // Re-enable based on current state
                this.updateButtonStates();
            }
        });
    }
    
    async updateButtonStates() {
        try {
            const status = await this.getStatus();
            
            const generateBtn = document.getElementById('generate-wire-btn');
            const exportBtn = document.getElementById('export-stl-btn');
            
            // Enable generate button if STL is loaded
            if (generateBtn) {
                generateBtn.disabled = !status.has_mesh;
            }
            
            // Enable export button if wire is generated
            if (exportBtn) {
                exportBtn.disabled = !status.has_wire;
            }
            
            // Update info display
            const generationInfo = document.getElementById('generation-info');
            const faPointsCount = document.getElementById('fa-points-count');
            const controlPointsCount = document.getElementById('control-points-count');
            
            if (status.has_wire && generationInfo) {
                generationInfo.style.display = 'block';
                if (faPointsCount) faPointsCount.textContent = status.fa_points_count || 0;
                if (controlPointsCount) controlPointsCount.textContent = status.control_points_count || 0;
            }
            
        } catch (error) {
            console.error('Error updating button states:', error);
        }
    }
}

// Global API client instance
window.apiClient = new APIClient();
