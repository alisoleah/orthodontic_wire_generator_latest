import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

document.addEventListener('DOMContentLoaded', () => {
    const uploadBtn = document.getElementById('upload-btn');
    const fileInput = document.getElementById('file-input');
    const generateBtn = document.getElementById('generate-btn');
    const exportGcodeBtn = document.getElementById('export-gcode-btn');
    const exportEsp32Btn = document.getElementById('export-esp32-btn');
    const statusDiv = document.getElementById('status');
    const viewerDiv = document.getElementById('viewer');

    let scene, camera, renderer, controls;
    let jawMesh, wireMesh;

    // --- 3D Viewer Initialization ---
    function initViewer() {
        // Scene
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x2c3e50);

        // Camera
        camera = new THREE.PerspectiveCamera(75, viewerDiv.clientWidth / viewerDiv.clientHeight, 0.1, 1000);
        camera.position.set(0, 0, 80);

        // Renderer
        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(viewerDiv.clientWidth, viewerDiv.clientHeight);
        viewerDiv.appendChild(renderer.domElement);

        // Controls
        controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.1;

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(50, 50, 50);
        scene.add(directionalLight);

        // Animation loop
        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }
        animate();

        // Handle window resize
        window.addEventListener('resize', () => {
            camera.aspect = viewerDiv.clientWidth / viewerDiv.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(viewerDiv.clientWidth, viewerDiv.clientHeight);
        });
    }

    // --- Status Update Function ---
    function updateStatus(message, isError = false) {
        statusDiv.textContent = message;
        statusDiv.style.color = isError ? 'red' : 'black';
    }

    // --- Button State Management ---
    function setButtonsState(isUploading, isGenerated) {
        uploadBtn.disabled = isUploading;
        generateBtn.disabled = isUploading || isGenerated;
        exportGcodeBtn.disabled = isUploading || !isGenerated;
        exportEsp32Btn.disabled = isUploading || !isGenerated;
    }

    // --- Mesh Creation ---
    function createMeshFromJson(meshData, color) {
        if (!meshData || !meshData.vertices || !meshData.faces) return null;

        const geometry = new THREE.BufferGeometry();
        const vertices = new Float32Array(meshData.vertices.flat());
        const indices = new Uint32Array(meshData.faces.flat());

        geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
        geometry.setIndex(new THREE.BufferAttribute(indices, 1));
        geometry.computeVertexNormals();

        const material = new THREE.MeshStandardMaterial({
            color: color,
            metalness: 0.3,
            roughness: 0.6,
        });

        return new THREE.Mesh(geometry, material);
    }

    function clearScene() {
        if (jawMesh) {
            scene.remove(jawMesh);
            jawMesh.geometry.dispose();
            jawMesh.material.dispose();
            jawMesh = undefined;
        }
        if (wireMesh) {
            scene.remove(wireMesh);
            wireMesh.geometry.dispose();
            wireMesh.material.dispose();
            wireMesh = undefined;
        }
    }

    // --- Event Listeners ---
    uploadBtn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        updateStatus('Uploading STL file...');
        setButtonsState(true, false);
        clearScene();

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Upload failed');
            }

            const result = await response.json();
            updateStatus(result.message);
            setButtonsState(false, false);
            generateBtn.disabled = false;
        } catch (error) {
            updateStatus(`Error: ${error.message}`, true);
            setButtonsState(false, false);
        }
    });

    generateBtn.addEventListener('click', async () => {
        updateStatus('Generating wire...');
        setButtonsState(true, false);
        clearScene();

        try {
            const response = await fetch('/api/generate-wire', {
                method: 'POST',
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Generation failed');
            }

            const result = await response.json();
            updateStatus(result.message);

            // Create and add jaw mesh
            jawMesh = createMeshFromJson(result.jaw_mesh, 0xe0e0e0);
            if (jawMesh) {
                scene.add(jawMesh);
            }

            // Create and add wire mesh
            wireMesh = createMeshFromJson(result.wire_mesh, 0xffd700); // Gold color
            if (wireMesh) {
                scene.add(wireMesh);
            }

            // Fit camera to the new objects
            const box = new THREE.Box3().setFromObject(jawMesh || wireMesh);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            const maxDim = Math.max(size.x, size.y, size.z);
            const fov = camera.fov * (Math.PI / 180);
            let cameraZ = Math.abs(maxDim / 2 * Math.tan(fov * 2));
            cameraZ *= 1.5; // Zoom out a bit

            camera.position.set(center.x, center.y, center.z + cameraZ);
            controls.target.copy(center);
            controls.update();

            setButtonsState(false, true);

        } catch (error) {
            updateStatus(`Error: ${error.message}`, true);
            setButtonsState(false, false);
            generateBtn.disabled = false;
        }
    });

    async function handleExport(url, filename) {
        updateStatus(`Exporting ${filename}...`);
        try {
            const response = await fetch(url);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Export failed');
            }
            const blob = await response.blob();
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            updateStatus(`${filename} exported successfully.`);
        } catch (error) {
            updateStatus(`Error: ${error.message}`, true);
        }
    }

    exportGcodeBtn.addEventListener('click', () => {
        handleExport('/api/export-gcode', 'wire.gcode');
    });

    exportEsp32Btn.addEventListener('click', () => {
        handleExport('/api/export-esp32', 'wire_esp32.ino');
    });

    // --- Initial State ---
    initViewer();
    updateStatus('Ready. Please upload an STL file.');
    setButtonsState(false, false);
    generateBtn.disabled = true;
});