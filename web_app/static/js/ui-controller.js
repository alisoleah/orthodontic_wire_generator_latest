/**
 * UI Controller
 * Handles user interface interactions and notifications
 */

class UIController {
    constructor() {
        this.notifications = [];
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // File upload
        this.setupFileUpload();
        
        // Button clicks
        this.setupButtonHandlers();
        
        // Keyboard shortcuts
        this.setupKeyboardShortcuts();
    }
    
    setupFileUpload() {
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-input');
        
        // Click to browse
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        // File selection
        fileInput.addEventListener('change', (event) => {
            const file = event.target.files[0];
            if (file) {
                this.handleFileUpload(file);
            }
        });
        
        // Drag and drop
        uploadArea.addEventListener('dragover', (event) => {
            event.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (event) => {
            event.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = event.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0]);
            }
        });
    }
    
    setupButtonHandlers() {
        // Generate wire button
        const generateBtn = document.getElementById('generate-wire-btn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.handleGenerateWire());
        }
        
        // Export STL button
        const exportBtn = document.getElementById('export-stl-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.handleExportSTL());
        }
        
        // Wire position adjustment buttons
        const moveButtons = document.querySelectorAll('[data-action]');
        moveButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.getAttribute('data-action');
                this.handleWireMovement(action);
            });
        });
        
        // Reset wire button
        const resetBtn = document.getElementById('reset-wire-btn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.handleResetWire());
        }
        
        // View control buttons
        const resetViewBtn = document.getElementById('reset-view-btn');
        if (resetViewBtn) {
            resetViewBtn.addEventListener('click', () => {
                if (window.threeViewer) {
                    window.threeViewer.resetView();
                }
            });
        }
        
        const wireframeBtn = document.getElementById('toggle-wireframe-btn');
        if (wireframeBtn) {
            wireframeBtn.addEventListener('click', () => {
                if (window.threeViewer) {
                    const isWireframe = window.threeViewer.toggleWireframe();
                    wireframeBtn.textContent = isWireframe ? 'Solid' : 'Wireframe';
                }
            });
        }
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (event) => {
            // Prevent shortcuts when typing in inputs
            if (event.target.tagName === 'INPUT' || event.target.tagName === 'SELECT') {
                return;
            }
            
            switch (event.key.toLowerCase()) {
                case 'w':
                    event.preventDefault();
                    this.handleWireMovement('move-forward');
                    break;
                case 's':
                    event.preventDefault();
                    this.handleWireMovement('move-backward');
                    break;
                case 'arrowup':
                    event.preventDefault();
                    this.handleWireMovement('move-up');
                    break;
                case 'arrowdown':
                    event.preventDefault();
                    this.handleWireMovement('move-down');
                    break;
                case 'r':
                    if (event.ctrlKey || event.metaKey) {
                        event.preventDefault();
                        this.handleResetWire();
                    }
                    break;
                case 'g':
                    if (event.ctrlKey || event.metaKey) {
                        event.preventDefault();
                        this.handleGenerateWire();
                    }
                    break;
                case 'e':
                    if (event.ctrlKey || event.metaKey) {
                        event.preventDefault();
                        this.handleExportSTL();
                    }
                    break;
            }
        });
    }
    
    async handleFileUpload(file) {
        try {
            if (!file.name.toLowerCase().endsWith('.stl')) {
                this.showNotification('Please select an STL file', 'error');
                return;
            }
            
            this.showProgress('Uploading STL file...', 0);
            
            const archType = document.getElementById('arch-type').value;
            const wireSize = document.getElementById('wire-size').value;
            
            const result = await window.apiClient.uploadMesh(file, archType, wireSize);
            
            this.showProgress('Loading 3D model...', 50);
            
            // Load mesh data into 3D viewer
            const meshData = await window.apiClient.getMeshData();
            if (window.threeViewer) {
                window.threeViewer.showLoading();
                const success = window.threeViewer.loadMesh(meshData);
                window.threeViewer.hideLoading();
                
                if (success) {
                    this.showProgress('STL loaded successfully!', 100);
                    this.showNotification(`STL file "${file.name}" loaded successfully`, 'success');
                } else {
                    throw new Error('Failed to load mesh in 3D viewer');
                }
            }
            
            this.hideProgress();
            
        } catch (error) {
            this.hideProgress();
            this.showNotification(`Upload failed: ${error.message}`, 'error');
            console.error('File upload error:', error);
        }
    }
    
    async handleGenerateWire() {
        try {
            this.showProgress('Generating FIXR-inspired wire...', 0);
            
            const result = await window.apiClient.generateWire();
            
            this.showProgress('Loading wire visualization...', 50);
            
            // Load wire data into 3D viewer
            const wireData = await window.apiClient.getWireData();
            if (window.threeViewer) {
                window.threeViewer.showLoading();
                const success = window.threeViewer.loadWire(wireData.wire, wireData.controlPoints);
                window.threeViewer.hideLoading();
                
                if (success) {
                    this.showProgress('Wire generated successfully!', 100);
                    this.showNotification('FIXR-inspired wire generated successfully!', 'success');
                    
                    // Update info display
                    const faPointsCount = document.getElementById('fa-points-count');
                    const controlPointsCount = document.getElementById('control-points-count');
                    
                    if (faPointsCount) faPointsCount.textContent = result.fa_points_count || 0;
                    if (controlPointsCount) controlPointsCount.textContent = result.control_points_count || 0;
                    
                    const generationInfo = document.getElementById('generation-info');
                    if (generationInfo) generationInfo.style.display = 'block';
                } else {
                    throw new Error('Failed to load wire in 3D viewer');
                }
            }
            
            this.hideProgress();
            
        } catch (error) {
            this.hideProgress();
            this.showNotification(`Wire generation failed: ${error.message}`, 'error');
            console.error('Wire generation error:', error);
        }
    }
    
    async handleWireMovement(action) {
        try {
            let offset = [0, 0, 0];
            const step = 1.0; // 1mm step
            
            switch (action) {
                case 'move-up':
                    offset = [0, step, 0];
                    break;
                case 'move-down':
                    offset = [0, -step, 0];
                    break;
                case 'move-forward':
                    offset = [0, 0, step];
                    break;
                case 'move-backward':
                    offset = [0, 0, -step];
                    break;
                default:
                    return;
            }
            
            await window.apiClient.adjustWirePosition(offset);
            this.showNotification(`Wire moved ${action.replace('move-', '')}`, 'success');
            
        } catch (error) {
            this.showNotification(`Wire movement failed: ${error.message}`, 'error');
            console.error('Wire movement error:', error);
        }
    }
    
    async handleResetWire() {
        try {
            // Reset to original position (offset of [0,0,0])
            await window.apiClient.adjustWirePosition([0, 0, 0]);
            this.showNotification('Wire position reset', 'success');
            
        } catch (error) {
            this.showNotification(`Reset failed: ${error.message}`, 'error');
            console.error('Wire reset error:', error);
        }
    }
    
    async handleExportSTL() {
        try {
            this.showProgress('Exporting STL file...', 0);
            
            await window.apiClient.exportSTL();
            
            this.showProgress('Export complete!', 100);
            this.showNotification('STL file exported successfully', 'success');
            this.hideProgress();
            
        } catch (error) {
            this.hideProgress();
            this.showNotification(`Export failed: ${error.message}`, 'error');
            console.error('Export error:', error);
        }
    }
    
    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
        
        // Store reference
        this.notifications.push(notification);
    }
    
    showProgress(text, percentage) {
        const container = document.getElementById('progress-container');
        const fill = document.getElementById('progress-fill');
        const textElement = document.getElementById('progress-text');
        
        if (container) container.style.display = 'block';
        if (fill) fill.style.width = `${percentage}%`;
        if (textElement) textElement.textContent = text;
    }
    
    hideProgress() {
        const container = document.getElementById('progress-container');
        if (container) {
            setTimeout(() => {
                container.style.display = 'none';
            }, 1000);
        }
    }
    
    updateStatus(status, message) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        if (statusDot) {
            statusDot.className = `status-dot status-${status}`;
        }
        
        if (statusText) {
            statusText.textContent = message;
        }
    }
}

// Global UI controller instance
window.uiController = new UIController();
