# Orthodontic Wire Generator - User Guide

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/alisoleah/orthodontic_wire_generator_latest.git
cd orthodontic_wire_generator_latest

# Install dependencies
pip install -r requirements.txt

# Run application
python3 run_app.py
```

### First Wire Generation (30 seconds)

1. **Load STL** → Click "Upper Arch (.stl)" → Select your STL file
2. **Generate** → Automatic detection runs → Wire appears
3. **Export** → Click "💾 Export G-Code" → Save file

---

## 📖 Complete Guide

### Interface Overview

The application has 3 main panels:

```
┌─────────────┬──────────────────┬─────────────┐
│   Control   │   3D Viewport    │   Status    │
│   Panel     │                  │   Panel     │
│  (Left)     │    (Center)      │   (Right)   │
└─────────────┴──────────────────┴─────────────┘
```

**Left Panel:** All controls (8 collapsible sections)  
**Center:** 3D visualization of dental arch and wire  
**Right:** Real-time statistics and quality metrics

---

## 🎮 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **F3** | Front (Anterior) view |
| **F4** | Side (Lateral) view |
| **F5** | Top (Occlusal) view |
| **F6** | 3D Oblique view |

---

## 📋 Step-by-Step Workflows

### Workflow 1: Automatic Mode (Recommended)

**Best for:** Normal anatomies, quick wire generation

1. **Section 1: DENTAL MODELS**
   - Click "⬆️ Upper Arch (.stl)"
   - Select your STL file
   - Card turns green when loaded ✓

2. **Section 2: WORKFLOW MODE**
   - Select "🤖 Automatic Detection" (default)

3. **Section 3: ACTIVE ARCH**
   - Select "Upper Arch" or "Lower Arch"
   - Check "Show Both Arches" to see both

4. **Section 4: DESIGN WORKFLOW**
   - Click "Re-run Automatic Detection" if needed
   - Wire generates automatically
   - Toggle "Show Detected Teeth" / "Show Bracket Positions"

5. **Section 5: WIRE PARAMETERS**
   - Adjust "Height Offset" slider (-10mm to +10mm)
   - Adjust "Forward/Backward" slider
   - Change "Wire Diameter" (0.3-2.0mm)
   - Adjust "Curve Smoothness" (10-1000 points)

6. **Section 7: EXPORT**
   - Click "💾 Export G-Code" → Save for CNC
   - Click "📟 Export ESP32 Code" → Save for wire bender
   - Click "🔷 Export STL" → Save wire as 3D model

---

### Workflow 2: Manual Mode (FIXR Style)

**Best for:** Complex cases, precise control

1. **Load STL** (Section 1)

2. **Select Manual Mode** (Section 2)
   - Choose "✏️ Manual Design (FIXR Style)"

3. **Define Wire Path** (Section 4)
   - Click "Define Wire Path (0/3)"
   - **Right-click** on mesh to place 3 control points:
     - Point 1: Posterior (back)
     - Point 2: Midpoint
     - Point 3: Anterior (front)
   - Wire follows teeth between points

4. **Generate Wire**
   - Click "Generate Wire"
   - Wire appears following tooth contours

5. **Adjust & Export**
   - Use sliders to fine-tune
   - Export when satisfied

---

### Workflow 3: Hybrid Mode

**Best for:** Start automatic, refine manually

1. **Load STL** → Automatic wire generates

2. **Select Hybrid Mode** (Section 2)
   - Choose "⚡ Hybrid (Auto + Manual Adjust)"

3. **Convert to Manual** (Section 4)
   - Click "Convert to Manual Mode"
   - Control points appear on wire

4. **Drag Points**
   - Click "Enable Point Dragging"
   - Drag yellow spheres to adjust wire path
   - Wire updates in real-time

5. **Export** when satisfied

---

## 📊 Understanding the Status Panel

### Section 1: WIRE STATISTICS

- **Wire Length:** Total wire length in mm
- **Control Points:** Number of points in wire path
- **Generation Time:** How long it took to generate

### Section 2: DETECTION INFO

- **Teeth Detected:** Count (e.g., "14/14" = all teeth found)
- **Confidence:** Detection confidence (0-100%)
- **Missing Teeth:** Number of missing teeth detected

### Section 3: QUALITY METRICS

- **Smoothness:** Wire smoothness score (0-100%)
  - >80% = Excellent
  - 60-80% = Good
  - <60% = May need adjustment

- **Max Curvature:** Maximum curvature (mm⁻¹)
  - Lower = smoother wire
  - Higher = sharper bends

- **Clinical Status:** Validation result
  - "✓ PASS" = Clinically acceptable
  - "✗ FAIL" = Needs adjustment

### Section 5: EXPORTED CODE

- View G-Code or ESP32 code after export
- Monospace font for readability
- Copy/paste ready

---

## 🔧 Advanced Features

### Wire Parameters Explained

**Height Offset:**
- Positive (+) = Wire higher (labial)
- Negative (-) = Wire lower (lingual)
- Range: -10mm to +10mm
- Use for: Adjusting vertical position

**Forward/Backward:**
- Positive (+) = Wire more anterior
- Negative (-) = Wire more posterior
- Range: -10mm to +10mm
- Use for: AP positioning

**Wire Diameter:**
- Range: 0.3mm to 2.0mm
- Common: 0.016" (0.4mm), 0.018" (0.46mm), 0.9mm
- Affects: Wire stiffness and force

**Curve Smoothness:**
- Range: 10 to 1000 points
- Lower = Faster, less smooth
- Higher = Slower, more smooth
- Recommended: 300-500 points

---

### Collision Detection

**Section 6: OCCLUSAL INTERFERENCE**

1. Load opposing arch (optional)
2. Click "Check for Collisions"
3. Results show:
   - "✓ No collisions detected" = Safe
   - "⚠️ Collision detected at X points" = Adjust height

---

### Jaw Simulation

**Section 8: JAW SIMULATION**

- Slider: 0° to 45° jaw opening
- Simulates: Lower jaw rotation
- Use for: Checking occlusion during opening

---

## 🧪 Clinical Validation (Advanced)

### Validating Against Reference Wires

**Requirements:**
- Reference wire STL (3D printed wire)
- Generated wire from same case

**Steps:**

1. Generate wire using automatic mode
2. Open validation panel (to be integrated)
3. Click "📂 Load Reference Wire (.stl)"
4. Select reference STL file
5. Click "▶️ Run Validation"

**Results:**
- **RMS Deviation:** <0.15mm = Acceptable
- **Max Deviation:** <0.30mm = Acceptable
- **Clinical Status:** PASS/FAIL

---

## 💡 Tips & Best Practices

### For Best Results

✅ **DO:**
- Use high-quality STL scans (clean, complete)
- Start with automatic mode
- Check smoothness score (aim for >80%)
- Validate against reference wires
- Export multiple formats (G-Code + STL)

❌ **DON'T:**
- Use incomplete or damaged STL files
- Set extreme parameter values
- Skip collision detection
- Ignore quality metrics

### Common Issues & Solutions

**Issue:** "Failed to detect teeth"
- **Solution:** Check STL quality, try manual mode

**Issue:** "Wire too high/low"
- **Solution:** Adjust height offset slider

**Issue:** "Wire not smooth"
- **Solution:** Increase smoothness points (500-1000)

**Issue:** "Collision detected"
- **Solution:** Adjust height offset, check opposing arch

---

## 📁 File Formats

### Input Files

- **STL Files:** Dental arch 3D scans
  - Format: Binary or ASCII STL
  - Units: Millimeters
  - Origin: Centered on arch

### Output Files

**G-Code (.gcode)**
- CNC machine instructions
- For wire bending machines
- Standard G-code format

**ESP32 Code (.cpp)**
- Arduino/ESP32 compatible
- For custom wire benders
- Includes servo commands

**STL (.stl)**
- 3D model of wire
- For visualization/printing
- Can be imported to CAD software

**JSON (.json)**
- Wire design data
- For saving/loading projects
- Contains all parameters

---

## 🎯 Example Cases

### Case 1: Normal Upper Arch

```
1. Load: upper_arch.stl
2. Mode: Automatic
3. Parameters: Default
4. Result: 14 teeth detected, 85% smoothness
5. Export: G-Code
```

### Case 2: Crowded Lower Arch

```
1. Load: lower_crowded.stl
2. Mode: Hybrid
3. Detect: 14 teeth (some overlapping)
4. Adjust: Manual refinement
5. Export: G-Code + STL
```

### Case 3: Missing Tooth

```
1. Load: upper_missing.stl
2. Mode: Automatic
3. Detect: 13/14 teeth (1 missing)
4. Wire: Automatically spans gap
5. Validate: Check smoothness
6. Export: G-Code
```

---

## 🔍 Troubleshooting

### Application Won't Start

```bash
# Check Python version (need 3.7+)
python3 --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for errors
python3 run_app.py
```

### STL Won't Load

- Check file format (must be STL)
- Check file size (<100MB recommended)
- Try opening in another 3D viewer first
- Ensure file is not corrupted

### Wire Generation Fails

- Check tooth detection results
- Try different workflow mode
- Adjust parameters
- Check console for error messages

---

## 📞 Support & Resources

### Documentation
- `PROJECT_DOCUMENTATION.md` - Technical details
- `ALGORITHM.md` - Algorithm explanations
- `README.md` - Project overview

### GitHub
- Repository: `alisoleah/orthodontic_wire_generator_latest`
- Branch: `feature/mac_smoothwire`
- Issues: Report bugs and request features

### Reference Files
- Test STLs: `STLfiles/stl/AyaKhairy/`
- Example outputs: `export/`

---

## 🎓 Learning Resources

### Understanding the Workflow

1. **Tooth Detection:** How teeth are identified
2. **Bracket Positioning:** Where brackets are placed
3. **Wire Generation:** How wire path is calculated
4. **Smoothing:** How curves are smoothed
5. **Validation:** How accuracy is measured

### Clinical Concepts

- **FA Point:** Facial Axis point for bracket placement
- **Arch Form:** Natural curve of dental arch
- **Occlusal Plane:** Biting surface reference
- **RMS Deviation:** Root mean square accuracy metric

---

## 🚀 Quick Reference

### Essential Shortcuts
- **F3-F6:** Camera views
- **Ctrl+N:** New project
- **Ctrl+O:** Open project
- **Ctrl+S:** Save project

### Key Sections
1. Load STL
2. Choose mode
3. Select arch
4. Generate wire
5. Adjust parameters
6. Check collisions
7. Export files

### Quality Checklist
- [ ] All teeth detected
- [ ] Smoothness >80%
- [ ] No collisions
- [ ] RMS <0.15mm (if validated)
- [ ] Wire looks natural

---

**Version:** 1.0  
**Last Updated:** January 10, 2026  
**Author:** Ali Soleah
