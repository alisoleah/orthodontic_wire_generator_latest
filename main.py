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
    version="1.1.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory storage for the wire generator instance.
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

class IncrementalAdjustPayload(BaseModel):
    y_offset: float = 0.0
    z_offset: float = 0.0

# --- API Endpoints ---

@app.post("/api/upload", summary="Upload STL file")
async def upload_stl(file: UploadFile = File(...)):
    """
    Accepts an .stl file, saves it, and initializes the `WireGenerator`.
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
            raise HTTPException(status_code=500, detail="Wire generation failed.")

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


@app.post("/api/adjust-wire-position", summary="Adjust Wire Position Incrementally")
async def adjust_wire_position(payload: IncrementalAdjustPayload):
    """
    Adjusts the wire position up/down (Y) or forward/backward (Z)
    and returns the updated wire geometry.
    """
    generator = get_generator()
    try:
        generator.adjust_wire_position(y_offset=payload.y_offset, z_offset=payload.z_offset)

        updated_wire_mesh = generator.wire_mesh
        if updated_wire_mesh is None:
            raise HTTPException(status_code=500, detail="Failed to get updated wire mesh after adjustment.")

        return {
            "wire_mesh": mesh_to_json(updated_wire_mesh),
            "message": "Wire position adjusted successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to adjust wire position: {e}")


@app.get("/api/export-gcode", summary="Get G-code")
async def get_gcode():
    """
    Generates G-code for the current wire and returns it as a JSON object.
    """
    generator = get_generator()
    if generator.wire_path is None:
        raise HTTPException(status_code=400, detail="Wire has not been generated yet.")

    try:
        gcode_content = generator.generate_gcode()
        return {"filename": "wire.gcode", "content": gcode_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate G-code: {e}")


@app.get("/api/export-esp32", summary="Get ESP32 Code")
async def get_esp32_code():
    """
    Generates ESP32 Arduino code for the current wire and returns it as a JSON object.
    """
    generator = get_generator()
    if generator.wire_path is None:
        raise HTTPException(status_code=400, detail="Wire has not been generated yet.")

    try:
        esp32_code = generator.generate_esp32_code()
        return {"filename": "wire_esp32.ino", "content": esp32_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate ESP32 code: {e}")


@app.get("/", include_in_schema=False)
async def read_index():
    """Serves the main HTML page."""
    return FileResponse('templates/index.html')