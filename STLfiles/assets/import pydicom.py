import pydicom
import numpy as np

# Replace with your DICOM file path  Amina Imam scan for retainers UpperJawScan.stl
file_path = "/Users/galala/STL con/assets/Amina Imam scan LowerJawScan.dcm"

try:
    ds = pydicom.dcmread(file_path, force=True)
    print(f"✓ DICOM loaded: {ds.get('Modality', 'Unknown')}")
    
    if hasattr(ds, 'pixel_array'):
        pa = ds.pixel_array
        print(f"✓ Pixel data: {pa.shape}, {pa.dtype}")
        print(f"Range: {pa.min()} to {pa.max()}")
    else:
        print("✗ No pixel data found")
        
except Exception as e:
    print(f"✗ Error: {e}")