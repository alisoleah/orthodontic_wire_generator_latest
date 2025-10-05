/**
 * Three.js Setup and 3D Visualization
 * Handles 3D rendering of dental meshes and orthodontic wires
 */

class ThreeViewer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        
        // 3D Objects
        this.meshObject = null;
        this.wireObject = null;
        this.controlPointObjects = [];
        
        // Interaction
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.selectedControlPoint = null;
        this.isDragging = false;
        
        // Settings
        this.wireframeMode = false;
        
        this.init();
    }
    
    init() {
        this.setupScene();
        this.setupCamera();
        this.setupRenderer();
        this.setupControls();
        this.setupLighting();
        this.setupEventListeners();
        this.animate();
        
        console.log('✓ Three.js viewer initialized');
    }
    
    setupScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xf8f9fa);
        
        // Add fog for depth perception
        this.scene.fog = new THREE.Fog(0xf8f9fa, 100, 1000);
    }
    
    setupCamera() {
        const aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 2000);
        this.camera.position.set(0, 50, 100);
        this.camera.lookAt(0, 0, 0);
    }
    
    setupRenderer() {
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true 
        });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.outputEncoding = THREE.sRGBEncoding;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.2;
        
        this.container.appendChild(this.renderer.domElement);
    }
    
    setupControls() {
        // Handle different Three.js versions for OrbitControls
        if (typeof THREE.OrbitControls !== 'undefined') {
            this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        } else if (window.OrbitControls) {
            this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        } else {
            console.warn('OrbitControls not available');
            return;
        }
        
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.screenSpacePanning = false;
        this.controls.minDistance = 10;
        this.controls.maxDistance = 500;
        this.controls.maxPolarAngle = Math.PI;
    }
    
    setupLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
        this.scene.add(ambientLight);
        
        // Main directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(50, 100, 50);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 500;
        directionalLight.shadow.camera.left = -100;
        directionalLight.shadow.camera.right = 100;
        directionalLight.shadow.camera.top = 100;
        directionalLight.shadow.camera.bottom = -100;
        this.scene.add(directionalLight);
        
        // Fill light
        const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
        fillLight.position.set(-50, 50, -50);
        this.scene.add(fillLight);
        
        // Rim light
        const rimLight = new THREE.DirectionalLight(0xffffff, 0.2);
        rimLight.position.set(0, 50, -100);
        this.scene.add(rimLight);
    }
    
    setupEventListeners() {
        // Window resize
        window.addEventListener('resize', () => this.onWindowResize());
        
        // Mouse events for control point interaction
        this.renderer.domElement.addEventListener('mousedown', (event) => this.onMouseDown(event));
        this.renderer.domElement.addEventListener('mousemove', (event) => this.onMouseMove(event));
        this.renderer.domElement.addEventListener('mouseup', (event) => this.onMouseUp(event));
        
        // Prevent context menu on right click
        this.renderer.domElement.addEventListener('contextmenu', (event) => event.preventDefault());
    }
    
    onWindowResize() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }
    
    onMouseDown(event) {
        if (event.button !== 0) return; // Only left mouse button
        
        this.updateMousePosition(event);
        
        // Check for control point intersection
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.controlPointObjects);
        
        if (intersects.length > 0) {
            this.selectedControlPoint = intersects[0].object;
            this.isDragging = true;
            this.controls.enabled = false; // Disable orbit controls during drag
            
            // Highlight selected control point
            this.highlightControlPoint(this.selectedControlPoint);
            
            console.log('Control point selected:', this.selectedControlPoint.userData.pointId);
        }
    }
    
    onMouseMove(event) {
        this.updateMousePosition(event);
        
        if (this.isDragging && this.selectedControlPoint) {
            // Project mouse position to 3D space
            this.raycaster.setFromCamera(this.mouse, this.camera);
            
            // Create a plane at the control point's current position
            const plane = new THREE.Plane();
            const normal = new THREE.Vector3(0, 0, 1); // Use Z-axis as normal
            plane.setFromNormalAndCoplanarPoint(normal, this.selectedControlPoint.position);
            
            // Find intersection with the plane
            const intersection = new THREE.Vector3();
            this.raycaster.ray.intersectPlane(plane, intersection);
            
            if (intersection) {
                // Update control point position
                this.selectedControlPoint.position.copy(intersection);
                
                // Notify the backend about the position change
                this.notifyControlPointUpdate(
                    this.selectedControlPoint.userData.pointId,
                    [intersection.x, intersection.y, intersection.z]
                );
            }
        }
    }
    
    onMouseUp(event) {
        if (this.isDragging) {
            this.isDragging = false;
            this.controls.enabled = true; // Re-enable orbit controls
            
            // Remove highlight from control point
            this.unhighlightControlPoint(this.selectedControlPoint);
            this.selectedControlPoint = null;
        }
    }
    
    updateMousePosition(event) {
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    }
    
    highlightControlPoint(controlPoint) {
        if (controlPoint && controlPoint.material) {
            controlPoint.material.color.setHex(0xffff00); // Yellow highlight
            controlPoint.scale.set(1.5, 1.5, 1.5); // Make it bigger
        }
    }
    
    unhighlightControlPoint(controlPoint) {
        if (controlPoint && controlPoint.material) {
            controlPoint.material.color.setHex(0xff4444); // Red default
            controlPoint.scale.set(1, 1, 1); // Normal size
        }
    }
    
    notifyControlPointUpdate(pointId, position) {
        // This will be called by the API client
        if (window.apiClient) {
            window.apiClient.updateControlPoint(pointId, position);
        }
    }
    
    loadMesh(meshData) {
        try {
            // Remove existing mesh
            if (this.meshObject) {
                this.scene.remove(this.meshObject);
            }
            
            // Create geometry from mesh data
            const geometry = new THREE.BufferGeometry();
            
            // Convert vertices and faces
            const vertices = new Float32Array(meshData.vertices.flat());
            const indices = new Uint32Array(meshData.faces.flat());
            
            geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
            geometry.setIndex(new THREE.BufferAttribute(indices, 1));
            geometry.computeVertexNormals();
            
            // Create material
            const material = new THREE.MeshLambertMaterial({
                color: 0xe8e8e8,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.9
            });
            
            // Create mesh
            this.meshObject = new THREE.Mesh(geometry, material);
            this.meshObject.castShadow = true;
            this.meshObject.receiveShadow = true;
            this.scene.add(this.meshObject);
            
            // Center the camera on the mesh
            this.centerCameraOnMesh(meshData.center);
            
            console.log('✓ Mesh loaded successfully');
            return true;
        } catch (error) {
            console.error('Error loading mesh:', error);
            return false;
        }
    }
    
    loadWire(wireData, controlPoints) {
        try {
            // Remove existing wire and control points
            if (this.wireObject) {
                this.scene.remove(this.wireObject);
            }
            this.clearControlPoints();
            
            // Create wire geometry
            const wireGeometry = new THREE.BufferGeometry();
            const wireVertices = new Float32Array(wireData.path.flat());
            wireGeometry.setAttribute('position', new THREE.BufferAttribute(wireVertices, 3));
            
            // Create wire material
            const wireMaterial = new THREE.MeshPhongMaterial({
                color: 0xd4af37, // Gold color
                shininess: 100,
                transparent: true,
                opacity: 0.9
            });
            
            // Create wire as tube geometry for better visualization
            const curve = new THREE.CatmullRomCurve3(
                wireData.path.map(point => new THREE.Vector3(point[0], point[1], point[2]))
            );
            
            const tubeGeometry = new THREE.TubeGeometry(curve, 100, wireData.radius, 8, false);
            this.wireObject = new THREE.Mesh(tubeGeometry, wireMaterial);
            this.wireObject.castShadow = true;
            this.scene.add(this.wireObject);
            
            // Create control points
            this.createControlPoints(controlPoints);
            
            console.log('✓ Wire loaded successfully');
            return true;
        } catch (error) {
            console.error('Error loading wire:', error);
            return false;
        }
    }
    
    createControlPoints(controlPoints) {
        controlPoints.forEach((cp, index) => {
            const geometry = new THREE.SphereGeometry(2, 16, 16);
            const material = new THREE.MeshPhongMaterial({
                color: 0xff4444,
                transparent: true,
                opacity: 0.8
            });
            
            const sphere = new THREE.Mesh(geometry, material);
            sphere.position.set(cp.position[0], cp.position[1], cp.position[2]);
            sphere.userData = {
                pointId: cp.id,
                type: cp.type,
                surfaceConstrained: cp.surface_constrained
            };
            
            this.controlPointObjects.push(sphere);
            this.scene.add(sphere);
        });
        
        console.log(`✓ Created ${controlPoints.length} control points`);
    }
    
    clearControlPoints() {
        this.controlPointObjects.forEach(cp => {
            this.scene.remove(cp);
        });
        this.controlPointObjects = [];
    }
    
    centerCameraOnMesh(center) {
        if (center && center.length === 3) {
            const target = new THREE.Vector3(center[0], center[1], center[2]);
            this.controls.target.copy(target);
            
            // Position camera at a good viewing angle
            const distance = 100;
            this.camera.position.set(
                target.x + distance * 0.5,
                target.y + distance * 0.7,
                target.z + distance
            );
            
            this.controls.update();
        }
    }
    
    toggleWireframe() {
        this.wireframeMode = !this.wireframeMode;
        
        if (this.meshObject && this.meshObject.material) {
            this.meshObject.material.wireframe = this.wireframeMode;
        }
        
        return this.wireframeMode;
    }
    
    resetView() {
        if (this.meshObject) {
            // Reset camera position
            this.camera.position.set(0, 50, 100);
            this.controls.target.set(0, 0, 0);
            this.controls.update();
        }
    }
    
    showLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    }
    
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        if (this.controls) {
            this.controls.update();
        }
        
        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }
    
    dispose() {
        if (this.renderer) {
            this.renderer.dispose();
        }
        if (this.controls) {
            this.controls.dispose();
        }
    }
}

// Global viewer instance
window.threeViewer = null;
