import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

document.addEventListener('DOMContentLoaded', () => {
    // --- Element Selectors ---
    const uploadBtn = document.getElementById('upload-btn');
    const fileInput = document.getElementById('file-input');
    const generateBtn = document.getElementById('generate-btn');
    const exportGcodeBtn = document.getElementById('export-gcode-btn');
    const exportEsp32Btn = document.getElementById('export-esp32-btn');
    const statusDiv = document.getElementById('status');
    const viewerDiv = document.getElementById('viewer');
    const codeModal = document.getElementById('code-modal');
    const modalCloseBtn = document.querySelector('.modal-close-btn');
    const codeTitle = document.getElementById('code-title');
    const codeDisplay = document.getElementById('code-display');
    const copyCodeBtn = document.getElementById('copy-code-btn');

    let scene, camera, renderer, controls;
    let jawMesh, wireMesh;

    // --- 3D Viewer Initialization ---
    function initViewer() {
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x2c3e50);
        camera = new THREE.PerspectiveCamera(75, viewerDiv.clientWidth / viewerDiv.clientHeight, 0.1, 1000);
        camera.position.set(0, 0, 80);
        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(viewerDiv.clientWidth, viewerDiv.clientHeight);
        viewerDiv.appendChild(renderer.domElement);
        controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.1;
        // We let OrbitControls listen to keys by default, and we will programmatically
        // enable/disable its panning to avoid conflicts with our custom key-bindings.
        controls.listenToKeyEvents(window);
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(50, 50, 50);
        scene.add(directionalLight);
        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }
        animate();
        window.addEventListener('resize', () => {
            camera.aspect = viewerDiv.clientWidth / viewerDiv.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(viewerDiv.clientWidth, viewerDiv.clientHeight);
        });
    }

    // --- Status & State Management ---
    function updateStatus(message, isError = false) {
        statusDiv.textContent = message;
        statusDiv.style.color = isError ? 'red' : 'black';
    }

    function setButtonsState(isUploading, isGenerated) {
        uploadBtn.disabled = isUploading;
        generateBtn.disabled = isUploading || isGenerated;
        exportGcodeBtn.disabled = isUploading || !isGenerated;
        exportEsp32Btn.disabled = isUploading || !isGenerated;
    }

    // --- Mesh & Scene Management ---
    function createMeshFromJson(meshData, color) {
        if (!meshData || !meshData.vertices || !meshData.faces) return null;
        const geometry = new THREE.BufferGeometry();
        const vertices = new Float32Array(meshData.vertices.flat());
        const indices = new Uint32Array(meshData.faces.flat());
        geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
        geometry.setIndex(new THREE.BufferAttribute(indices, 1));
        geometry.computeVertexNormals();
        const material = new THREE.MeshStandardMaterial({ color, metalness: 0.3, roughness: 0.6 });
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

    function updateWireMesh(meshData) {
        if (wireMesh) {
            scene.remove(wireMesh);
            wireMesh.geometry.dispose();
            wireMesh.material.dispose();
        }
        wireMesh = createMeshFromJson(meshData, 0xffd700);
        if (wireMesh) scene.add(wireMesh);
    }

    // --- Code Modal Logic ---
    function showCodeModal(title, code) {
        codeTitle.textContent = title;
        codeDisplay.textContent = code;
        codeModal.classList.remove('modal-hidden');
        codeModal.classList.add('modal-visible');
    }

    function hideCodeModal() {
        codeModal.classList.remove('modal-visible');
        codeModal.classList.add('modal-hidden');
    }

    modalCloseBtn.addEventListener('click', hideCodeModal);
    codeModal.addEventListener('click', (event) => {
        if (event.target === codeModal) hideCodeModal();
    });

    copyCodeBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(codeDisplay.textContent).then(() => {
            updateStatus('Code copied to clipboard!');
            setTimeout(() => updateStatus(''), 2000);
        }).catch(err => {
            updateStatus(`Error copying code: ${err}`, true);
        });
    });

    // --- API Interactions ---
    uploadBtn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (!file) return;
        updateStatus('Uploading STL file...');
        setButtonsState(true, false);
        clearScene();
        controls.enablePan = true; // Re-enable camera panning
        const formData = new FormData();
        formData.append('file', file);
        try {
            const response = await fetch('/api/upload', { method: 'POST', body: formData });
            if (!response.ok) throw new Error((await response.json()).detail || 'Upload failed');
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
            const response = await fetch('/api/generate-wire', { method: 'POST' });
            if (!response.ok) throw new Error((await response.json()).detail || 'Generation failed');
            const result = await response.json();

            jawMesh = createMeshFromJson(result.jaw_mesh, 0xe0e0e0);
            if (jawMesh) scene.add(jawMesh);
            updateWireMesh(result.wire_mesh);
            const box = new THREE.Box3().setFromObject(jawMesh || wireMesh);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            const maxDim = Math.max(size.x, size.y, size.z);
            const fov = camera.fov * (Math.PI / 180);
            const cameraZ = Math.abs(maxDim / 2 * Math.tan(fov * 2)) * 1.5;
            camera.position.set(center.x, center.y, center.z + cameraZ);
            controls.target.copy(center);
            controls.update();

            setButtonsState(false, true);
            controls.enablePan = false; // Disable camera panning to enable wire adjustment
            updateStatus("Wire generated. Use arrow keys to adjust position.");

        } catch (error) {
            updateStatus(`Error: ${error.message}`, true);
            setButtonsState(false, false);
            generateBtn.disabled = false;
            controls.enablePan = true; // Re-enable pan on error
        }
    });

    async function handleWireAdjustment(y_offset = 0, z_offset = 0) {
        if (!wireMesh) return;
        updateStatus('Adjusting wire position...');
        try {
            const response = await fetch('/api/adjust-wire-position', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ y_offset, z_offset }),
            });
            if (!response.ok) throw new Error((await response.json()).detail || 'Adjustment failed');
            const result = await response.json();
            updateWireMesh(result.wire_mesh);
            updateStatus('Wire position adjusted.');
        } catch (error) {
            updateStatus(`Error: ${error.message}`, true);
        }
    }

    window.addEventListener('keydown', (event) => {
        // If a wire exists and camera panning is disabled, use arrow keys for adjustment.
        if (!wireMesh || controls.enablePan) return;

        const keyMap = {
            'ArrowUp': { y: 0.2, z: 0 },
            'ArrowDown': { y: -0.2, z: 0 },
            'ArrowLeft': { y: 0, z: -0.2 },
            'ArrowRight': { y: 0, z: 0.2 },
        };

        if (keyMap[event.key]) {
            event.preventDefault(); // Prevent scrolling
            const { y, z } = keyMap[event.key];
            handleWireAdjustment(y, z);
        }
    });

    async function fetchAndShowCode(url, title) {
        updateStatus(`Fetching ${title}...`);
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error((await response.json()).detail || 'Failed to fetch code');
            const data = await response.json();
            showCodeModal(data.filename, data.content);
            updateStatus(`${title} loaded.`);
        } catch (error) {
            updateStatus(`Error: ${error.message}`, true);
        }
    }

    exportGcodeBtn.addEventListener('click', () => fetchAndShowCode('/api/export-gcode', 'G-code'));
    exportEsp32Btn.addEventListener('click', () => fetchAndShowCode('/api/export-esp32', 'ESP32 Code'));

    // --- Initial State ---
    initViewer();
    updateStatus('Ready. Please upload an STL file.');
    setButtonsState(false, false);
    generateBtn.disabled = true;
});