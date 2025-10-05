/**
 * Main Application JavaScript
 * Initializes the web application and coordinates all components
 */

class OrthodonticWireApp {
    constructor() {
        this.initialized = false;
        this.init();
    }
    
    async init() {
        try {
            console.log('🚀 Initializing Orthodontic Wire Generator Web App');
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.initializeComponents());
            } else {
                this.initializeComponents();
            }
            
        } catch (error) {
            console.error('App initialization error:', error);
            this.showError('Failed to initialize application');
        }
    }
    
    initializeComponents() {
        try {
            // Initialize Three.js viewer
            this.initializeThreeViewer();
            
            // Initialize API client (already done globally)
            console.log('✓ API Client initialized');
            
            // Initialize UI controller (already done globally)
            console.log('✓ UI Controller initialized');
            
            // Update initial button states
            this.updateInitialState();
            
            // Show welcome message
            this.showWelcomeMessage();
            
            this.initialized = true;
            console.log('✅ Application initialized successfully');
            
        } catch (error) {
            console.error('Component initialization error:', error);
            this.showError('Failed to initialize application components');
        }
    }
    
    initializeThreeViewer() {
        try {
            // Initialize Three.js viewer
            window.threeViewer = new ThreeViewer('three-container');
            console.log('✓ Three.js Viewer initialized');
            
            // Hide loading overlay initially
            window.threeViewer.hideLoading();
            
        } catch (error) {
            console.error('Three.js viewer initialization error:', error);
            throw new Error('Failed to initialize 3D viewer');
        }
    }
    
    async updateInitialState() {
        try {
            // Update button states based on current session
            if (window.apiClient) {
                await window.apiClient.updateButtonStates();
            }
            
            // Check if there's existing data to load
            await this.checkExistingData();
            
        } catch (error) {
            console.error('Initial state update error:', error);
        }
    }
    
    async checkExistingData() {
        try {
            const status = await window.apiClient.getStatus();
            
            // Load existing mesh if available
            if (status.has_mesh) {
                console.log('Loading existing mesh data...');
                const meshData = await window.apiClient.getMeshData();
                if (window.threeViewer) {
                    window.threeViewer.loadMesh(meshData);
                }
            }
            
            // Load existing wire if available
            if (status.has_wire) {
                console.log('Loading existing wire data...');
                const wireData = await window.apiClient.getWireData();
                if (window.threeViewer) {
                    window.threeViewer.loadWire(wireData.wire, wireData.controlPoints);
                }
                
                // Show generation info
                const generationInfo = document.getElementById('generation-info');
                if (generationInfo) {
                    generationInfo.style.display = 'block';
                }
            }
            
        } catch (error) {
            console.log('No existing data to load');
        }
    }
    
    showWelcomeMessage() {
        if (window.uiController) {
            window.uiController.showNotification(
                'Welcome to the FIXR-inspired Orthodontic Wire Generator!', 
                'success'
            );
        }
    }
    
    showError(message) {
        if (window.uiController) {
            window.uiController.showNotification(message, 'error');
        } else {
            alert(message);
        }
    }
    
    // Utility methods for external access
    getViewer() {
        return window.threeViewer;
    }
    
    getAPIClient() {
        return window.apiClient;
    }
    
    getUIController() {
        return window.uiController;
    }
    
    isInitialized() {
        return this.initialized;
    }
}

// Global app instance
window.orthodonticApp = new OrthodonticWireApp();

// Expose useful functions globally for debugging
window.debugApp = {
    viewer: () => window.threeViewer,
    api: () => window.apiClient,
    ui: () => window.uiController,
    app: () => window.orthodonticApp,
    
    // Debug functions
    loadTestMesh: async () => {
        console.log('Loading test mesh...');
        // This would load a test mesh for development
    },
    
    logStatus: async () => {
        try {
            const status = await window.apiClient.getStatus();
            console.log('Current status:', status);
        } catch (error) {
            console.error('Status error:', error);
        }
    },
    
    resetApp: () => {
        location.reload();
    }
};

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (window.threeViewer) {
        window.threeViewer.dispose();
    }
});

// Handle errors globally
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    if (window.uiController) {
        window.uiController.showNotification(
            'An unexpected error occurred. Please refresh the page.', 
            'error'
        );
    }
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    if (window.uiController) {
        window.uiController.showNotification(
            'A network or processing error occurred.', 
            'error'
        );
    }
});

console.log('📐 Orthodontic Wire Generator - FIXR-Inspired Technology');
console.log('🌐 Web Application Loaded');
console.log('🔧 Debug tools available at window.debugApp');
