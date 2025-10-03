# Quick Start Guide

## 🚀 Running the Application

### **IMPORTANT: Mac Users (You!)**

On macOS, Open3D visualization **MUST** run on the main thread. The app has been fixed to handle this correctly.

### **Method 1: Recommended - Use the Launcher**

```bash
cd "/Users/galala/STL con/Orthdontic inside jaw code (simplified)/latest/orthodontic_wire_generator_latest"

# Launch GUI (default)
python3 run_app.py

# Or explicitly
python3 run_app.py --gui
```

### **Method 2: Direct GUI Launch**

```bash
python3 gui_launcher.py
```

### **Method 3: Using main.py**

```bash
python3 main.py          # Launches GUI by default
python3 main.py --gui    # Explicit GUI mode
python3 main.py --cli    # Command line demo
```

---

## 📋 Prerequisites Check

Before running, ensure you have all dependencies:

```bash
# Test Open3D specifically (important for Mac)
python3 test_open3d.py

# Install missing packages
pip3 install -r requirements.txt
```

---

## 🔧 Troubleshooting the 3D Viewer

### **Problem: System Info Dump / Crash When Launching 3D**

This happens when Open3D tries to run on a background thread on macOS.

**✅ Solution Applied:**
- The code has been fixed to run Open3D on the main thread
- The GUI will hide temporarily when 3D viewer opens
- Close the 3D window to return to the GUI

### **What Happens Now:**

1. Click "Launch 3D Interactive Editor"
2. Main GUI window will **hide** temporarily
3. 3D viewer opens (only dental mesh and wire visible)
4. Close the 3D window
5. Main GUI returns

### **Controls in 3D Viewer:**

```
WIRE HEIGHT:
  Up Arrow      - Move wire up
  Down Arrow    - Move wire down
  R             - Reset wire height

CONTROL POINTS:
  1-9           - Select control point
  Left/Right    - Move selected point horizontally
  Page Up/Down  - Move selected point vertically

VIEW:
  Mouse Drag    - Rotate view
  Mouse Scroll  - Zoom
  Mouse Right   - Pan view

OTHER:
  H             - Show help
  Q             - Quit editor
```

---

## 📁 Which Version to Use?

### ✅ **USE THESE (Modular Architecture):**
- `run_app.py` - **Recommended launcher**
- `main.py` - Main entry point
- `gui_launcher.py` - GUI only
- All files in `core/`, `wire/`, `gui/`, `visualization/`, `export/` folders

### ❌ **DON'T USE:**
- `fullappv4.py` - Old monolithic version (100KB, has threading issues on Mac)

---

## 🎯 Quick Workflow

1. **Launch the app:**
   ```bash
   python3 run_app.py
   ```

2. **In the GUI:**
   - Click "Browse" to select your STL file
   - Choose arch type (upper/lower) or leave as "auto"
   - Select wire size (default: 0.018")
   - Click "Generate Wire"

3. **View Results:**
   - Status panel shows teeth/brackets detected
   - Wire length calculated
   - G-code preview available

4. **Interactive Editing:**
   - Click "Launch 3D Interactive Editor"
   - **Important:** Main GUI will hide - this is normal!
   - Edit wire in 3D viewer
   - Close 3D window to return to GUI

5. **Export:**
   - Click "Generate G-code" for manufacturing instructions
   - Click "Export Wire STL" for 3D model
   - Click "Save Design" to save complete project

---

## 🐛 Common Issues

### Issue 1: "Module not found"
**Solution:**
```bash
pip3 install numpy scipy open3d scikit-learn matplotlib
```

### Issue 2: 3D Viewer Crashes / System Info Dump
**Solution:** Already fixed! Make sure you're using `run_app.py` or `main.py`, NOT `fullappv4.py`

### Issue 3: "No STL file found"
**Solution:** Make sure you have STL files in your directory or browse to select one

### Issue 4: tkinter not found (Linux only)
**Solution:**
```bash
sudo apt-get install python3-tk
```

---

## 📊 Understanding the Architecture

### Modular Components:

```
core/           - STL loading, tooth detection, bracket positioning
wire/           - Wire path algorithm, mesh building, height control
visualization/  - 3D viewer, interactive controls
gui/            - User interface panels
export/         - G-code, STL, ESP32 code generation
```

### Where the Wire is Drawn:

1. **Algorithm:** `wire/wire_path_creator.py` - Math calculations
2. **Rendering:** `wire/wire_mesh_builder.py` - 3D geometry creation

---

## ✅ Verification Checklist

Before implementing improvements, verify:

- [ ] App launches without errors: `python3 run_app.py`
- [ ] Open3D works: `python3 test_open3d.py`
- [ ] Can load STL file
- [ ] Wire generation completes
- [ ] 3D viewer opens (without crash)
- [ ] Can export G-code and STL

---

## 🚀 Next Steps

Once everything works:

1. Review the professionalization plan in the main analysis
2. Install development tools: `pip3 install pytest black pylint`
3. Start with Phase 1 improvements (type hints, better splines)
4. Run tests after each change

---

## 📞 Support

If issues persist:
1. Check console output for error messages
2. Verify all dependencies: `pip3 list | grep -E "numpy|scipy|open3d"`
3. Test Open3D separately: `python3 test_open3d.py`
4. Use the modular files, not `fullappv4.py`
