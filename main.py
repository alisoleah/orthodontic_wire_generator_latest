import os
import shutil
from typing import List, Optional
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from wire.wire_generator import WireGenerator

app = FastAPI(
    title="Orthodontic Wire Generator API",
    description="A web API for generating, visualizing, and exporting orthodontic wires.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory storage for the wire generator instance.
# This is a simple approach for this specific problem. For a real-world application,
# you would want to manage state more robustly (e.g., sessions, databases).
generator_instance: Optional[WireGenerator] = None

# --- Helper Functions ---

def get_generator():
    """FastAPI dependency to get the generator instance and handle errors."""
    if generator_instance is None:
        raise HTTPException(status_code=400, detail="STL file not uploaded. Please upload a file first.")
    return generator_instance

def mesh_to_json(mesh):
    """Converts an Open3D mesh to a JSON-serializable format (vertices and faces)."""
    if not mesh:
        return None
    try:
        vertices = np.asarray(mesh.vertices).tolist()
        faces = np.asarray(mesh.triangles).tolist()
        return {"vertices": vertices, "faces": faces}
    except Exception:
        return None

# --- Pydantic Models for Request Bodies ---

class AdjustWirePayload(BaseModel):
    control_point_index: int
    new_coordinates: List[float]

# --- API Endpoints ---

@app.post("/api/upload", summary="Upload STL file")
async def upload_stl(file: UploadFile = File(...)):
    """
    Accepts an .stl file, saves it, and initializes the `WireGenerator`.
    This is the first step in the process.
    """
    global generator_instance
    upload_dir = "STLfiles"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Initialize the generator with the new file
    try:
        generator_instance = WireGenerator(stl_path=file_path)
        return {"filename": file.filename, "message": "File uploaded and wire generator initialized."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize wire generator: {e}")


@app.post("/api/generate-wire", summary="Generate Wire")
async def generate_wire():
    """
    Runs the main wire generation algorithm on the uploaded mesh.
    Returns the 3D data for both the jaw and the generated wire.
    """
    generator = get_generator()
    try:
        results = generator.generate_wire()
        if not results:
            raise HTTPException(status_code=500, detail="Wire generation failed for an unknown reason.")

        jaw_mesh_json = mesh_to_json(results.get('mesh'))
        wire_mesh_json = mesh_to_json(results.get('wire_mesh'))

        if not jaw_mesh_json:
            raise HTTPException(status_code=500, detail="Failed to process jaw mesh.")

        return {
            "jaw_mesh": jaw_mesh_json,
            "wire_mesh": wire_mesh_json,
            "message": "Wire generated successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during wire generation: {e}")


@app.post("/api/adjust-wire", summary="Adjust Wire Control Point")
async def adjust_wire(payload: AdjustWirePayload):
    """
    Accepts new coordinates for a single control point and returns the
    updated wire geometry.
    """
    generator = get_generator()
    wpc = generator.wire_path_creator

    if not hasattr(wpc, 'control_points') or not wpc.control_points:
        raise HTTPException(status_code=400, detail="Control points not available. Please generate the wire first.")

    index = payload.control_point_index
    if not 0 <= index < len(wpc.control_points):
        raise HTTPException(status_code=404, detail="Control point index out of bounds.")

    cp = wpc.control_points[index]
    cp_type = cp.type if hasattr(cp, 'type') else cp.get('type')

    if cp_type == 'bracket':
        raise HTTPException(status_code=400, detail="Cannot move a 'bracket' type control point directly.")

    # Update the position of the control point
    new_pos = np.array(payload.new_coordinates)
    if hasattr(cp, 'position'):
        cp.position = new_pos
    else:
        cp['position'] = new_pos

    # Regenerate the wire path and mesh with the updated control point
    try:
        height_offset = generator.height_controller.get_height_offset()
        new_wire_path = wpc.create_smooth_path(
            generator.bracket_positions,
            generator.arch_center,
            height_offset
        )
        generator.wire_path = new_wire_path

        new_wire_mesh = generator.wire_mesh_builder.build_wire_mesh(new_wire_path)
        if new_wire_mesh is None:
            raise HTTPException(status_code=500, detail="Failed to rebuild wire mesh after adjustment.")

        generator.wire_mesh = new_wire_mesh

        return {
            "wire_mesh": mesh_to_json(new_wire_mesh),
            "message": "Wire adjusted successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to adjust wire: {e}")


@app.get("/api/export-gcode", summary="Export G-code")
async def export_gcode():
    """
    Generates G-code for the current wire and returns it as a downloadable file.
    """
    generator = get_generator()
    if generator.wire_path is None:
        raise HTTPException(status_code=400, detail="Wire has not been generated yet.")

    try:
        gcode_content = generator.generate_gcode()
        return Response(
            content=gcode_content,
            media_type="text/plain",
            headers={"Content-Disposition": "attachment; filename=wire.gcode"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate G-code: {e}")


@app.get("/api/export-esp32", summary="Export ESP32 Code")
async def export_esp32():
    """
    Generates ESP32 Arduino code for the current wire and returns it as a
    downloadable file.
    """
    generator = get_generator()
    if generator.wire_path is None:
        raise HTTPException(status_code=400, detail="Wire has not been generated yet.")

    try:
        esp32_code = generator.generate_esp32_code()
        return Response(
            content=esp32_code,
            media_type="text/x-arduino",
            headers={"Content-Disposition": "attachment; filename=wire_esp32.ino"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate ESP32 code: {e}")


@app.get("/", include_in_schema=False)
async def read_index():
    """Serves the main HTML page."""
    return FileResponse('templates/index.html')