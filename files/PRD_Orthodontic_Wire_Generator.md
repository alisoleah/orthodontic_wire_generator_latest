# Product Requirements Document (PRD)
## Orthodontic Wire Generator - Professional Edition

**Document Version:** 1.0  
**Date:** January 9, 2026  
**Product Version Target:** 1.0.0  
**Repository:** [feature/smoothwire branch](https://github.com/alisoleah/orthodontic_wire_generator_latest/tree/feature/smoothwire)  
**Product Owner:** Aly Soleah

---

## Table of Contents

1. [Product Overview](#product-overview)
2. [User Personas](#user-personas)
3. [User Stories & Use Cases](#user-stories--use-cases)
4. [Functional Requirements](#functional-requirements)
5. [Non-Functional Requirements](#non-functional-requirements)
6. [UI/UX Requirements](#uiux-requirements)
7. [Technical Architecture](#technical-architecture)
8. [Data Requirements](#data-requirements)
9. [Integration Requirements](#integration-requirements)
10. [Testing & Quality Assurance](#testing--quality-assurance)
11. [Release Criteria](#release-criteria)

---

## Product Overview

### Product Vision

Create the world's most accessible, professional-grade orthodontic wire generator that democratizes custom archwire design through AI-powered automation, FIXR-compatible workflows, and an intuitive futuristic interface.

### Value Proposition

**For Orthodontists:**
> "Design clinically accurate custom archwires in 2 minutes instead of 30, with professional-grade tools at a fraction of commercial software costs."

**For Dental Laboratories:**
> "Scale your custom wire fabrication with AI-powered automation and consistent quality that rivals manual expert work."

**For Dental Educators:**
> "Teach modern digital orthodontic workflows with accessible software that visualizes biomechanical principles in real-time."

### Product Positioning

| Dimension | Commercial Solutions (FIXR, SureSmile) | This Product |
|-----------|---------------------------------------|--------------|
| **Cost** | $10K-$50K + subscriptions | Free (open-source) |
| **Workflow** | Proprietary, locked ecosystems | FIXR-compatible, flexible |
| **Speed** | 5-10 minutes | 2-5 minutes |
| **Customization** | Limited to vendor parameters | Full algorithm access |
| **Manufacturing** | Vendor-specific hardware | Universal (G-code, Arduino, STL) |
| **Learning Curve** | Moderate | Low (FIXR-like interface) |

### Success Metrics

| Metric | Baseline | Target (6 mo) | Target (12 mo) |
|--------|----------|---------------|----------------|
| Active Users | 0 | 50 | 200 |
| Wire Designs Created | 0 | 500 | 3,000 |
| Average Design Time | N/A | < 5 min | < 3 min |
| Clinical Accuracy | N/A | ±0.15mm | ±0.10mm |
| User Satisfaction (NPS) | N/A | 40+ | 60+ |
| GitHub Stars | 0 | 100 | 500 |

---

## User Personas

### Persona 1: Dr. Sarah Chen - Private Practice Orthodontist

**Demographics:**
- Age: 38
- Experience: 12 years in orthodontics
- Practice: Solo practice with 2 hygienists
- Location: Regional city (population 200K)

**Goals:**
- Provide personalized treatment for complex cases
- Reduce lab turnaround time for custom wires
- Maintain competitive edge with modern technology
- Minimize overhead costs

**Pain Points:**
- Can't justify $25K for commercial CAD/CAM system
- Current lab takes 2 weeks for custom wires
- Manual wire bending is time-consuming and inconsistent
- Limited customization with pre-fabricated wires

**Technical Profile:**
- Comfortable with dental software (Dolphin, practice management)
- Uses intraoral scanner regularly
- Basic computer skills (not a "power user")

**User Story:**
> "As a private practice orthodontist, I want to design custom archwires from my intraoral scans so that I can provide personalized treatment without expensive commercial software."

### Persona 2: Mike Rodriguez - Dental Laboratory Technician

**Demographics:**
- Age: 29
- Experience: 7 years in dental lab
- Workplace: Mid-size lab (15 employees)
- Location: Urban area with multiple orthodontic clients

**Goals:**
- Increase custom wire production volume
- Maintain consistent quality across technicians
- Reduce manual labor and repetitive strain
- Learn digital workflow skills

**Pain Points:**
- Manual wire bending is physically demanding
- Quality varies between technicians
- Hard to find skilled wire benders (aging workforce)
- Clients demand faster turnaround

**Technical Profile:**
- Expert with traditional dental lab equipment
- Familiar with CAD/CAM concepts (crown design software)
- Comfortable learning new software tools
- Interested in automation and CNC equipment

**User Story:**
> "As a dental lab technician, I want to automate wire design and manufacturing so that I can produce more consistent wires faster and reduce physical strain."

### Persona 3: Dr. James Okafor - Academic Orthodontist

**Demographics:**
- Age: 52
- Experience: 25 years, including 15 in academia
- Workplace: Dental school residency program
- Location: Major university medical center

**Goals:**
- Teach residents modern digital orthodontic workflows
- Provide hands-on experience with CAD/CAM tools
- Publish research on digital orthodontics
- Prepare students for modern practice

**Pain Points:**
- University can't afford commercial licenses for all students
- Limited access to modern training equipment
- Need tools that teach principles, not just button-pushing
- Want to expose students to open-source alternatives

**Technical Profile:**
- Strong understanding of biomechanics and algorithms
- Comfortable with Python and data analysis
- Interested in research and clinical validation
- Early adopter of new technology

**User Story:**
> "As an academic orthodontist, I want transparent, educational wire design software so that I can teach residents the principles behind digital orthodontics and modern CAD/CAM workflows."

---

## User Stories & Use Cases

### Epic 1: 3D Scan Import & Visualization

#### US-1.1: Import STL File
**As a** user  
**I want to** import STL files from my intraoral scanner  
**So that** I can start designing a custom archwire

**Acceptance Criteria:**
- [ ] Support .stl file format (ASCII and binary)
- [ ] Handle mesh sizes from 50K to 1M vertices
- [ ] Display file size and vertex count on import
- [ ] Validate mesh integrity (closed surface, no holes)
- [ ] Show import progress bar for large files (>500K vertices)
- [ ] Provide clear error messages for corrupted files

**Priority:** P0 (Must-Have)  
**Effort:** Small (already implemented)

#### US-1.2: Interactive 3D Visualization
**As a** user  
**I want to** rotate, pan, and zoom the 3D dental arch  
**So that** I can examine the anatomy from all angles

**Acceptance Criteria:**
- [ ] Left-click drag to rotate
- [ ] Middle-click drag (or Shift+drag) to pan
- [ ] Scroll to zoom
- [ ] Preset views: Front, Left, Right, Occlusal, Oblique
- [ ] Reset camera to default view (keyboard shortcut: 'R')
- [ ] Smooth camera transitions (no jarring jumps)

**Priority:** P0 (Must-Have)  
**Effort:** Small (already implemented)

### Epic 2: Automatic Wire Generation

#### US-2.1: AI-Powered Tooth Detection
**As a** user  
**I want to** automatically detect tooth positions from the STL  
**So that** I can quickly generate a wire without manual input

**Acceptance Criteria:**
- [ ] Detect 14-16 teeth per arch (standard anatomy)
- [ ] Handle upper and lower arches independently
- [ ] Display detected tooth boundaries with visual overlay
- [ ] Show confidence scores for each detected tooth
- [ ] Allow user to accept/reject detection results
- [ ] Complete detection in < 10 seconds for 200K vertex mesh

**Priority:** P0 (Must-Have)  
**Effort:** Medium (core algorithm already implemented)

#### US-2.2: Smooth Wire Path Generation
**As a** user  
**I want to** generate an ultra-smooth wire path through detected bracket positions  
**So that** the wire is clinically appropriate and manufacturing-ready

**Acceptance Criteria:**
- [ ] Wire passes through all bracket positions (±0.1mm tolerance)
- [ ] No sharp corners or discontinuities
- [ ] Smooth curvature (G2 continuity preferred)
- [ ] Adjustable wire height offset (0-5mm from tooth surface)
- [ ] Adjustable wire depth (labial-lingual positioning)
- [ ] Real-time preview of wire path in 3D view

**Priority:** P0 (Must-Have)  
**Effort:** Medium (core algorithm already implemented, tuning needed)

### Epic 3: Manual Control Point Workflow (FIXR-Like)

#### US-3.1: Place Control Points with Right-Click
**As a** user  
**I want to** right-click on the tooth surface to place control points  
**So that** I can manually define the wire path (FIXR workflow)

**Acceptance Criteria:**
- [ ] Right-click places control point at cursor position
- [ ] Minimum 3 control points required to generate wire
- [ ] Visual feedback: sphere marker appears at each point
- [ ] Points are numbered sequentially (1, 2, 3, ...)
- [ ] Hover over point shows coordinates (X, Y, Z in mm)
- [ ] Points snap to nearest tooth surface (within 2mm)

**Priority:** P0 (Must-Have)  
**Effort:** Small (already implemented)

#### US-3.2: Edit and Delete Control Points
**As a** user  
**I want to** modify or remove control points after placement  
**So that** I can refine the wire path without starting over

**Acceptance Criteria:**
- [ ] Left-click + drag to move control point
- [ ] Delete key removes selected point
- [ ] Ctrl+Z to undo last point placement
- [ ] Ctrl+Y to redo
- [ ] Right-click on point shows context menu (Edit, Delete, Insert Before/After)
- [ ] Wire updates in real-time as points move

**Priority:** P1 (Should-Have)  
**Effort:** Medium

### Epic 4: Hybrid Mode (Auto + Manual Refinement)

#### US-4.1: Convert Auto-Detected Points to Editable
**As a** user  
**I want to** convert automatically detected bracket positions to editable control points  
**So that** I can fine-tune the AI-generated wire path

**Acceptance Criteria:**
- [ ] One-click conversion from Auto → Hybrid mode
- [ ] Each detected bracket becomes a draggable sphere widget
- [ ] Preserve original wire path during conversion
- [ ] Visual distinction between locked and editable points
- [ ] Ability to lock/unlock individual points

**Priority:** P0 (Must-Have)  
**Effort:** Small (already implemented)

#### US-4.2: Real-Time Wire Updates During Dragging
**As a** user  
**I want to** see the wire path update immediately as I drag control points  
**So that** I can visually assess the impact of my adjustments

**Acceptance Criteria:**
- [ ] Wire regenerates within 200ms of releasing drag
- [ ] Smooth animation (no flickering)
- [ ] All 14 teeth remain editable
- [ ] Dragging one point doesn't affect neighboring points' positions
- [ ] Undo/redo works for drag operations

**Priority:** P1 (Should-Have)  
**Effort:** Medium (already implemented, may need optimization)

### Epic 5: Futuristic Modern UI/UX

#### US-5.1: Modern Gradient Interface
**As a** user  
**I want to** work in a visually appealing, modern interface with gradient accents  
**So that** the software feels professional and futuristic

**Acceptance Criteria:**
- [ ] Dark theme with gradient accents (blue/purple/teal preferred)
- [ ] Smooth transitions and hover effects
- [ ] Glass-morphism or neumorphic design elements
- [ ] High-contrast text for readability
- [ ] Consistent color palette across all UI elements
- [ ] Support for 4K/Retina displays (proper DPI scaling)

**Priority:** P1 (Should-Have)  
**Effort:** Large

**Design Mockup Requirements:**
```
Color Palette:
- Primary: Linear gradient(135deg, #667eea 0%, #764ba2 100%)
- Secondary: Linear gradient(135deg, #f093fb 0%, #f5576c 100%)
- Accent: Linear gradient(135deg, #4facfe 0%, #00f2fe 100%)
- Background: #1a1a2e (dark navy)
- Surface: rgba(255, 255, 255, 0.05) (glass effect)
- Text Primary: #e0e0e0
- Text Secondary: #a0a0a0
```

#### US-5.2: Intuitive Control Panel Layout
**As a** user  
**I want to** access all key functions from a clean, organized control panel  
**So that** I can work efficiently without cluttered UI

**Acceptance Criteria:**
- [ ] Collapsible sections for related controls
- [ ] Tooltips on hover (context-sensitive help)
- [ ] Logical grouping: File Operations, Detection, Adjustment, Export
- [ ] Keyboard shortcuts displayed next to buttons
- [ ] Status bar shows current mode, progress, and tips

**Priority:** P1 (Should-Have)  
**Effort:** Medium

### Epic 6: Manufacturing Export

#### US-6.1: Export to G-Code (CNC Wire Bender)
**As a** user  
**I want to** export the wire path as G-code  
**So that** I can manufacture the wire on a CNC bending machine

**Acceptance Criteria:**
- [ ] Support Marlin and Grbl G-code flavors
- [ ] Configurable feed rates (F parameter)
- [ ] Safety height moves (Z-hop between segments)
- [ ] Homing sequence at start (G28)
- [ ] End-of-program commands (M30)
- [ ] Time estimation displayed before export
- [ ] File preview with line-by-line visualization

**Priority:** P0 (Must-Have)  
**Effort:** Small (already implemented)

#### US-6.2: Export to Arduino/ESP32 Code
**As a** user  
**I want to** export the wire path as Arduino/ESP32 code  
**So that** I can control a DIY wire bending robot

**Acceptance Criteria:**
- [ ] AccelStepper library integration
- [ ] Coordinated XYZ stepper movement
- [ ] Serial command interface for manual control
- [ ] Emergency stop function
- [ ] Calibration routine included
- [ ] Comments explaining each code section

**Priority:** P1 (Should-Have)  
**Effort:** Small (already implemented)

#### US-6.3: Export to STL Mesh
**As a** user  
**I want to** export the wire path as an STL mesh  
**So that** I can 3D print verification models or import to CAD software

**Acceptance Criteria:**
- [ ] Adjustable wire diameter (0.3-0.6mm typical)
- [ ] High-resolution mesh (smooth curves)
- [ ] Binary STL format (smaller file size)
- [ ] Compatible with major CAD tools (Fusion 360, SolidWorks)

**Priority:** P2 (Nice-to-Have)  
**Effort:** Small (already implemented)

### Epic 7: Precision Adjustment & Fine-Tuning

#### US-7.1: Keyboard Shortcuts for Precision Control
**As a** user  
**I want to** use keyboard shortcuts to make precise wire adjustments  
**So that** I can work faster than mouse-only workflows

**Acceptance Criteria:**
- [ ] I/K: Increase/decrease wire height (0.1mm increments)
- [ ] J/L: Move wire forward/backward
- [ ] F3/F4/F5: Switch between Auto/Manual/Hybrid modes
- [ ] Ctrl+S: Quick save current design
- [ ] Ctrl+E: Quick export to last-used format
- [ ] R: Reset camera view
- [ ] All shortcuts displayed in Help menu

**Priority:** P1 (Should-Have)  
**Effort:** Small (already implemented)

#### US-7.2: Numeric Input for Exact Values
**As a** user  
**I want to** type exact numeric values for wire parameters  
**So that** I can achieve precise clinical specifications

**Acceptance Criteria:**
- [ ] Click on slider value to enter number directly
- [ ] Validate input range (prevent out-of-bounds values)
- [ ] Unit displayed (mm) next to input field
- [ ] Enter key applies value, Escape cancels

**Priority:** P2 (Nice-to-Have)  
**Effort:** Small

### Epic 8: Multi-Arch & Dual-Arch Support

#### US-8.1: Load Upper and Lower Arches Simultaneously
**As a** user  
**I want to** load both upper and lower arch STL files  
**So that** I can design wires with proper occlusal clearance

**Acceptance Criteria:**
- [ ] Separate file browsers for upper and lower
- [ ] Automatic alignment based on occlusal plane
- [ ] Toggle visibility of each arch independently
- [ ] Collision detection: warn if wires intersect
- [ ] Independent wire generation for each arch

**Priority:** P1 (Should-Have)  
**Effort:** Medium (already partially implemented)

---

## Functional Requirements

### FR-1: File Import & Management

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-1.1 | Import STL files (ASCII and binary formats) | P0 | ✅ Done |
| FR-1.2 | Support mesh sizes up to 1M vertices | P0 | ✅ Done |
| FR-1.3 | Validate mesh integrity (closed surface, manifold) | P1 | ✅ Done |
| FR-1.4 | Display file metadata (size, vertices, triangles) | P2 | ⏳ Pending |
| FR-1.5 | Recent files list (last 10 opened) | P2 | ⏳ Pending |
| FR-1.6 | Save/load project files (wire + settings) | P1 | ⏳ Pending |

### FR-2: Tooth Detection & Segmentation

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-2.1 | Angular segmentation algorithm for tooth detection | P0 | ✅ Done |
| FR-2.2 | Detect 14-16 teeth per arch (configurable) | P0 | ✅ Done |
| FR-2.3 | Handle upper and lower arches independently | P0 | ✅ Done |
| FR-2.4 | Visual overlay of detected tooth boundaries | P1 | ⏳ Pending |
| FR-2.5 | Confidence scores for each detected tooth | P1 | ⏳ Pending |
| FR-2.6 | Manual override for failed detections | P1 | ⏳ Pending |
| FR-2.7 | Handle missing teeth (gaps in arch) | P1 | ⏳ Pending |

### FR-3: Wire Path Generation

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-3.1 | Catmull-Rom spline interpolation | P0 | ✅ Done |
| FR-3.2 | Multi-stage Gaussian smoothing (σ=12.0, 5 passes) | P0 | ✅ Done |
| FR-3.3 | High-resolution path (300 points/segment) | P0 | ✅ Done |
| FR-3.4 | Adjustable wire height offset (0-5mm) | P0 | ✅ Done |
| FR-3.5 | Adjustable wire depth (labial-lingual) | P0 | ✅ Done |
| FR-3.6 | Real-time wire regeneration (< 200ms) | P1 | ✅ Done |
| FR-3.7 | Collision detection (dual-arch) | P1 | ✅ Done |
| FR-3.8 | Wire tension/spring-back compensation | P2 | ⏳ Future |

### FR-4: Interactive 3D Visualization

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-4.1 | PyVista-based 3D rendering | P0 | ✅ Done |
| FR-4.2 | Mouse controls (rotate, pan, zoom) | P0 | ✅ Done |
| FR-4.3 | Draggable control point spheres | P0 | ✅ Done |
| FR-4.4 | Preset camera views (Front, Side, Occlusal) | P1 | ⏳ Pending |
| FR-4.5 | Measurement tools (distance, angle) | P2 | ⏳ Future |
| FR-4.6 | Lighting controls (ambient, directional) | P2 | ⏳ Pending |
| FR-4.7 | Wireframe/solid/transparent display modes | P2 | ⏳ Pending |

### FR-5: Workflow Modes

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-5.1 | Automatic Mode (AI-powered, no user input) | P0 | ✅ Done |
| FR-5.2 | Manual Mode (FIXR-like control point placement) | P0 | ✅ Done |
| FR-5.3 | Hybrid Mode (Auto + manual refinement) | P0 | ✅ Done |
| FR-5.4 | One-click mode switching (F3/F4/F5) | P0 | ✅ Done |
| FR-5.5 | Preserve work when switching modes | P1 | ✅ Done |

### FR-6: Manufacturing Exports

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-6.1 | G-code export (Marlin flavor) | P0 | ✅ Done |
| FR-6.2 | G-code export (Grbl flavor) | P1 | ✅ Done |
| FR-6.3 | Arduino/ESP32 code export | P1 | ✅ Done |
| FR-6.4 | STL mesh export | P1 | ✅ Done |
| FR-6.5 | CSV point cloud export | P2 | ⏳ Pending |
| FR-6.6 | JSON export (coordinates + metadata) | P2 | ⏳ Pending |
| FR-6.7 | PDF report generation (for clinical records) | P2 | ⏳ Future |

### FR-7: User Assistance & Documentation

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-7.1 | Keyboard shortcuts displayed in UI | P0 | ✅ Done |
| FR-7.2 | Tooltips on all controls | P1 | ⏳ Pending |
| FR-7.3 | Interactive tutorial (first-time users) | P1 | ⏳ Future |
| FR-7.4 | Built-in help documentation | P1 | ⏳ Pending |
| FR-7.5 | Video tutorial links | P2 | ⏳ Future |
| FR-7.6 | Sample STL files bundled with app | P2 | ⏳ Pending |

---

## Non-Functional Requirements

### NFR-1: Performance

| ID | Requirement | Target | Priority |
|----|-------------|--------|----------|
| NFR-1.1 | STL file import time | < 3 seconds for 200K vertices | P0 |
| NFR-1.2 | Tooth detection time | < 10 seconds per arch | P0 |
| NFR-1.3 | Wire path generation time | < 2 seconds | P0 |
| NFR-1.4 | Real-time wire update (dragging) | < 200ms | P1 |
| NFR-1.5 | 3D rendering frame rate | 30 FPS minimum (60 FPS target) | P1 |
| NFR-1.6 | Application startup time | < 5 seconds | P2 |
| NFR-1.7 | Memory footprint | < 2GB RAM for typical use | P1 |

**Benchmarking Plan:**
- Test on low-end hardware: Core i5, 8GB RAM, integrated GPU
- Optimize bottlenecks identified through profiling (cProfile)
- Consider C++ extensions for critical algorithms if needed

### NFR-2: Usability

| ID | Requirement | Measurement | Priority |
|----|-------------|-------------|----------|
| NFR-2.1 | First-time user can generate wire | < 10 minutes without tutorial | P0 |
| NFR-2.2 | Expert user workflow time | < 3 minutes per wire (Hybrid mode) | P1 |
| NFR-2.3 | System Usability Scale (SUS) score | > 75 (Good usability) | P1 |
| NFR-2.4 | Error message clarity | Users understand issue & solution > 90% | P0 |
| NFR-2.5 | Keyboard shortcut discoverability | Users find shortcuts > 60% | P2 |

**Usability Testing Plan:**
- Conduct 5 usability sessions with target users (orthodontists, techs)
- Measure task completion time and errors
- Gather qualitative feedback via post-session interview

### NFR-3: Reliability & Stability

| ID | Requirement | Target | Priority |
|----|-------------|--------|----------|
| NFR-3.1 | Application crash rate | < 1% of sessions | P0 |
| NFR-3.2 | Successful wire generation rate | > 95% for standard anatomies | P0 |
| NFR-3.3 | Data loss prevention | Auto-save every 5 minutes | P1 |
| NFR-3.4 | Graceful error handling | No unhandled exceptions in production | P0 |
| NFR-3.5 | Recovery from errors | User can continue work after error | P1 |

**Testing Strategy:**
- Automated crash detection and reporting (Sentry or similar)
- Fuzz testing with varied/corrupted STL files
- Edge case testing (extreme anatomies, huge files)

### NFR-4: Compatibility

| ID | Requirement | Target | Priority |
|----|-------------|--------|----------|
| NFR-4.1 | Windows support | Windows 10, 11 (64-bit) | P0 |
| NFR-4.2 | macOS support | macOS 12 Monterey+ (Intel & Apple Silicon) | P0 |
| NFR-4.3 | Linux support | Ubuntu 20.04+, Fedora 35+ | P1 |
| NFR-4.4 | Python version | Python 3.7 - 3.11 | P0 |
| NFR-4.5 | Display resolution | 1920x1080 minimum, 4K/5K optimized | P1 |
| NFR-4.6 | GPU requirements | OpenGL 3.3+, no dedicated GPU required | P1 |

**Platform-Specific Considerations:**
- **macOS:** Test on both Intel and Apple Silicon (M1/M2/M3)
- **Linux:** Package as AppImage or Flatpak for broad compatibility
- **Windows:** Test on various GPU vendors (NVIDIA, AMD, Intel)

### NFR-5: Maintainability

| ID | Requirement | Measurement | Priority |
|----|-------------|-------------|----------|
| NFR-5.1 | Code documentation coverage | > 80% of functions have docstrings | P1 |
| NFR-5.2 | Inline comments for complex logic | All algorithms > 50 lines explained | P1 |
| NFR-5.3 | Modular architecture | Each component < 500 lines of code | P1 |
| NFR-5.4 | Dependency management | requirements.txt + virtual environment | P0 |
| NFR-5.5 | Version control | Git with semantic versioning (semver) | P0 |

**Code Quality Tools:**
- Linting: Pylint or Flake8
- Type checking: mypy (gradual adoption)
- Code formatter: Black (auto-format on commit)

### NFR-6: Accessibility

| ID | Requirement | Target | Priority |
|----|-------------|--------|----------|
| NFR-6.1 | Keyboard-only navigation | All functions accessible via keyboard | P1 |
| NFR-6.2 | High-contrast mode | Support for high-contrast themes | P2 |
| NFR-6.3 | Font scaling | UI scales with system font size settings | P2 |
| NFR-6.4 | Screen reader compatibility | Basic support for screen readers | P3 |
| NFR-6.5 | Colorblind-friendly palette | Avoid red-green only distinctions | P2 |

---

## UI/UX Requirements

### Design Philosophy

**Core Principles:**
1. **Futuristic Aesthetic** - Gradient accents, glass-morphism, smooth animations
2. **Professional Credibility** - Clean, uncluttered, inspired by medical software
3. **Efficient Workflow** - Minimize clicks, provide keyboard shortcuts
4. **Visual Feedback** - Immediate response to user actions
5. **Forgiving Design** - Easy undo/redo, non-destructive editing

### UI-1: Main Window Layout

**Requirements:**

```
┌─────────────────────────────────────────────────────────────┐
│ ▶ Ortho Wire Generator v1.0     [_] [□] [×]      Help  ℹ   │  ← Title Bar (Gradient)
├─────────────────────────────────────────────────────────────┤
│ File  Edit  View  Export  Tools  Help                       │  ← Menu Bar
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│  Control     │          3D Visualization Area              │
│  Panel       │                                              │
│  ┌────────┐  │          ┌───────────────────┐              │
│  │ Load   │  │          │                   │              │
│  │ STL    │  │          │   🦷 Dental Mesh   │              │
│  └────────┘  │          │                   │              │
│              │          │   📐 Wire Path     │              │
│  ┌────────┐  │          │                   │              │
│  │ Mode:  │  │          └───────────────────┘              │
│  │ [Auto▾]│  │                                              │
│  └────────┘  │          Mouse: Rotate | Pan | Zoom          │
│              │          Keyboard: I/K/J/L for adjustments   │
│  Wire Params │                                              │
│  Height: ●━━━│──────────────────────────────────────────────│
│  Depth:  ●━━━│  Status: Wire generated (4,200 points) | Ready │
│              │                                              │
│  [Generate]  │                                              │
│  [Export]    │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

**Specifications:**
- **Title Bar:** Gradient background (blue-purple), app icon + version
- **Control Panel Width:** 280px fixed (left sidebar)
- **3D Viewport:** Flexible, minimum 800x600px
- **Status Bar Height:** 32px (bottom)
- **Padding/Margins:** 8px consistent spacing

### UI-2: Color Scheme (Futuristic Dark Theme)

**Primary Palette:**

```css
/* Background Colors */
--background-primary: #1a1a2e;     /* Dark navy */
--background-secondary: #16213e;   /* Slightly lighter navy */
--surface: rgba(255, 255, 255, 0.05);  /* Glass effect */

/* Gradient Accents */
--gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--gradient-secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
--gradient-accent: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
--gradient-success: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);

/* Text Colors */
--text-primary: #e0e0e0;
--text-secondary: #a0a0a0;
--text-disabled: #606060;
--text-link: #4facfe;

/* UI Element Colors */
--border: rgba(255, 255, 255, 0.1);
--hover: rgba(255, 255, 255, 0.08);
--active: rgba(255, 255, 255, 0.12);
--focus: #4facfe;

/* Semantic Colors */
--success: #38ef7d;
--warning: #f5576c;
--error: #ff6b6b;
--info: #4facfe;
```

**Example Button Styles:**

```css
/* Primary Button (Gradient) */
.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    transition: all 0.3s ease;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* Glass-Morphism Panel */
.panel {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 20px;
}
```

### UI-3: Typography

**Font Stack:**

```css
--font-primary: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
```

**Type Scale:**

| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 (Title) | 28px | 700 | 1.2 |
| H2 (Section) | 22px | 600 | 1.3 |
| H3 (Subsection) | 18px | 600 | 1.4 |
| Body | 14px | 400 | 1.5 |
| Small | 12px | 400 | 1.4 |
| Code | 13px | 400 | 1.6 |

### UI-4: Interactive Elements

#### Buttons

**States:**
- **Default:** Gradient or solid color
- **Hover:** Lift effect (translateY(-2px)) + enhanced shadow
- **Active:** Slight scale down (scale(0.98))
- **Disabled:** 50% opacity, no hover effect
- **Loading:** Spinner icon, "Processing..." text

**Button Hierarchy:**

1. **Primary (Gradient):** Generate Wire, Export, Save
2. **Secondary (Outline):** Load STL, Reset, Cancel
3. **Tertiary (Text Only):** Help, About, Advanced Settings

#### Sliders

**Design:**
- Track: 4px height, rounded ends
- Thumb: 16px circle with gradient
- Active track: Gradient fill from start to thumb
- Inactive track: Semi-transparent white

**Behavior:**
- Smooth dragging (no jitter)
- Display value next to thumb while dragging
- Snap to increments (optional, e.g., 0.1mm steps)

#### Input Fields

**Design:**
- Background: rgba(255, 255, 255, 0.05)
- Border: 1px solid rgba(255, 255, 255, 0.1)
- Border on focus: 2px solid #4facfe
- Padding: 8px 12px
- Border radius: 6px

**Validation:**
- ✅ Valid: Green border, checkmark icon
- ⚠️ Warning: Yellow border, warning icon
- ❌ Error: Red border, error message below

### UI-5: 3D Viewport Enhancements

**Overlay Elements:**

```
┌─────────────────────────────────────────────┐
│  📹 View: Front ▾    🔦 Lighting ▾          │  ← Top-right corner
│                                             │
│                                       ┌────┐│
│                                       │ X  ││  ← Coordinate axes
│           🦷 Mesh                     │ Y Z││
│                                       └────┘│
│                                             │
│  📐 Mode: Hybrid                           │  ← Bottom-left
│  📊 Points: 4,200 | ⏱️ 0.8s                │
└─────────────────────────────────────────────┘
```

**Interactive Features:**
- **Hover highlights:** Tooth surfaces glow on mouse-over
- **Selection indicators:** Selected control points pulse slightly
- **Ghost preview:** Show old wire path in semi-transparent when editing
- **Grid overlay:** Optional reference grid (toggled with 'G' key)

### UI-6: Animations & Transitions

**Principles:**
- **Duration:** 200-300ms for most transitions (no longer)
- **Easing:** ease-out for exits, ease-in-out for position changes
- **Purposeful:** Animations guide user attention, not just decoration

**Key Animations:**

1. **Wire Generation:**
   - Progress bar fills with gradient (0 → 100%)
   - Wire path "draws" along mesh (animated line)
   - Completion: Pulse effect + success message

2. **Mode Switching:**
   - Fade out old controls (150ms)
   - Fade in new controls (150ms, after 50ms delay)
   - Smooth transition (not jarring)

3. **Hover Effects:**
   - Buttons lift 2px with shadow increase
   - Control points scale to 1.1× size
   - Tooth surfaces brighten slightly

### UI-7: Responsive Layout

**Minimum Window Size:** 1280x720px

**Responsive Breakpoints:**

| Screen Size | Layout Adjustments |
|-------------|-------------------|
| 1280-1600px | Default layout |
| 1600-2560px | Wider control panel (320px), larger fonts |
| 2560px+ (4K) | Scale UI 1.5×, high-res textures |
| < 1280px | Warn user: "For best experience, use 1280x720 or larger" |

**Control Panel Behavior:**
- Collapsible sections (accordion style)
- Scroll within panel if content exceeds viewport height
- Pinned "Generate" and "Export" buttons at bottom

---

## Technical Architecture

### System Architecture Diagram

```
┌────────────────────────────────────────────────────────────┐
│                    Application Layer                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Enhanced Main Window (PyQt5)                 │  │
│  │  ┌────────────────┐  ┌────────────────────────────┐  │  │
│  │  │ Control Panel  │  │  PyVista 3D Visualizer     │  │  │
│  │  │ - Mode Select  │  │  - Mesh Rendering          │  │  │
│  │  │ - Sliders      │  │  - Wire Overlay            │  │  │
│  │  │ - Buttons      │  │  - Interactive Spheres     │  │  │
│  │  └────────────────┘  └────────────────────────────┘  │  │
│  └──────────────┬───────────────────┬────────────────────┘  │
└─────────────────┼───────────────────┼───────────────────────┘
                  │                   │
                  ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  Business Logic Layer                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Workflow Manager (Orchestrator)             │  │
│  │  • Coordinates all operations                        │  │
│  │  • Manages state transitions                         │  │
│  │  • Handles mode switching                            │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                            │
│   ┌─────────────┼──────────────┬────────────────┐           │
│   ▼             ▼              ▼                ▼           │
│ ┌─────────┐ ┌─────────┐ ┌──────────────┐ ┌──────────────┐  │
│ │  Tooth  │ │ Bracket │ │ Wire Path    │ │  Collision   │  │
│ │Detector │ │Position.│ │  Creator ⭐   │ │  Detector    │  │
│ └─────────┘ └─────────┘ └──────────────┘ └──────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Access Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ STL Importer │  │ Mesh Processor│  │ Export Manager  │  │
│  │ (Open3D)     │  │ (trimesh)     │  │ - G-code        │  │
│  └──────────────┘  └──────────────┘  │ - Arduino       │  │
│                                       │ - STL           │  │
│                                       └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 External Dependencies                       │
│  [NumPy] [SciPy] [VTK] [PyVista] [Open3D] [trimesh]        │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. Enhanced Main Window (PyQt5)

**File:** `gui/enhanced_main_window.py`

**Responsibilities:**
- Main application window and layout
- User event handling (button clicks, slider changes)
- Communication between UI and business logic
- Status updates and progress bars

**Key Methods:**
```python
class EnhancedMainWindow(QMainWindow):
    def __init__(self):
        """Initialize UI components and connections"""
        
    def load_stl_file(self, file_path: str):
        """Import STL file and display in 3D viewer"""
        
    def generate_wire(self):
        """Trigger wire generation based on current mode"""
        
    def export_gcode(self, export_path: str):
        """Export wire path to G-code format"""
        
    def update_visualization(self):
        """Refresh 3D viewport with latest wire path"""
```

#### 2. Workflow Manager

**File:** `core/workflow_manager.py`

**Responsibilities:**
- Central orchestrator for all operations
- Mode management (Auto, Manual, Hybrid)
- Coordinate calls to detection, positioning, wire creation
- Maintain application state

**Key Methods:**
```python
class WorkflowManager:
    def __init__(self):
        self.tooth_detector = ToothDetector()
        self.bracket_positioner = BracketPositioner()
        self.wire_creator = WirePathCreator()
        self.mode = WorkflowMode.AUTOMATIC
        
    def process_automatic_mode(self, mesh):
        """Execute automatic workflow: detect → position → generate"""
        
    def process_manual_mode(self, mesh, control_points):
        """Execute manual workflow: use user points → generate"""
        
    def process_hybrid_mode(self, mesh):
        """Execute hybrid workflow: auto-detect → convert to editable"""
        
    def switch_mode(self, new_mode: WorkflowMode):
        """Handle mode transitions and state preservation"""
```

#### 3. Wire Path Creator ⭐ (Core Algorithm)

**File:** `wire/wire_path_creator.py`

**Responsibilities:**
- Multi-stage smooth path generation
- Catmull-Rom spline interpolation
- Gaussian smoothing
- Real-time path updates

**Algorithm Workflow:**
```python
class WirePathCreator:
    def create_smooth_path(self, bracket_positions: np.ndarray) -> np.ndarray:
        """
        Generate ultra-smooth wire path through bracket positions
        
        Steps:
        1. Fit dental arch curve (parabolic least-squares)
        2. Generate intermediate points (3 per segment)
        3. Catmull-Rom interpolation (300 points/segment)
        4. Multi-pass Gaussian smoothing (σ=12.0, 5 passes)
        5. Validate path (no self-intersections, proper clearance)
        
        Returns: np.ndarray of shape (N, 3) representing smooth path
        """
        
        # Phase 1: Arch curve fitting
        arch_curve = self._fit_dental_arch(bracket_positions)
        
        # Phase 2: Intermediate point generation
        dense_points = self._generate_intermediate_points(bracket_positions, arch_curve)
        
        # Phase 3: Catmull-Rom spline interpolation
        interpolated_path = self._catmull_rom_interpolate(dense_points, num_points=300)
        
        # Phase 4: Multi-stage Gaussian smoothing
        smooth_path = self._gaussian_smooth(interpolated_path, sigma=12.0, passes=5)
        
        # Phase 5: Validation
        if not self._validate_path(smooth_path):
            raise PathValidationError("Generated path failed validation")
            
        return smooth_path
```

**Smoothing Parameters:**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `points_per_segment` | 300 | High-resolution interpolation |
| `sigma` | 12.0 | Gaussian kernel width (smoothness) |
| `smoothing_passes` | 5 | Number of smoothing iterations |
| `intermediate_points` | 3 | Points between each bracket |

#### 4. Tooth Detector

**File:** `detection/tooth_detector.py`

**Algorithm:** Angular Segmentation

```python
class ToothDetector:
    def detect_teeth(self, crown_mesh, num_teeth=14):
        """
        Detect tooth positions using angular segmentation
        
        Algorithm:
        1. Convert crown vertices to cylindrical coordinates (r, θ, z)
        2. Divide 360° into N angular sectors (N = num_teeth)
        3. Group vertices by angular sector
        4. Find centroid of each sector = tooth position
        
        Complexity: O(V) where V = number of vertices
        """
        
        # Convert to polar coordinates
        vertices = crown_mesh.vertices
        r, theta, z = self._cartesian_to_polar(vertices)
        
        # Angular bins (e.g., 14 teeth = 25.7° per tooth)
        angle_step = 360 / num_teeth
        bins = [(i * angle_step, (i + 1) * angle_step) for i in range(num_teeth)]
        
        tooth_positions = []
        for start_angle, end_angle in bins:
            # Find vertices in this angular range
            mask = (theta >= start_angle) & (theta < end_angle)
            sector_vertices = vertices[mask]
            
            # Centroid = tooth position
            if len(sector_vertices) > 0:
                centroid = np.mean(sector_vertices, axis=0)
                tooth_positions.append(centroid)
                
        return np.array(tooth_positions)
```

#### 5. Export Manager

**File:** `export/export_manager.py`

**Responsibilities:**
- Convert wire path to manufacturing formats
- G-code generation (Marlin/Grbl)
- Arduino/ESP32 code generation
- STL mesh export

**G-Code Generation:**

```python
class ExportManager:
    def export_gcode(self, wire_path: np.ndarray, config: GCodeConfig) -> str:
        """
        Generate G-code for CNC wire bender
        
        Args:
            wire_path: Nx3 array of (X, Y, Z) coordinates in mm
            config: Feed rates, safety height, flavor (Marlin/Grbl)
            
        Returns:
            String containing G-code program
        """
        
        gcode_lines = []
        
        # Header
        gcode_lines.append("; Orthodontic Wire G-Code")
        gcode_lines.append(f"; Generated: {datetime.now().isoformat()}")
        gcode_lines.append(f"; Points: {len(wire_path)}")
        
        # Initialization
        gcode_lines.append("G21 ; Set units to millimeters")
        gcode_lines.append("G90 ; Absolute positioning")
        gcode_lines.append("G28 ; Home all axes")
        gcode_lines.append(f"G0 Z{config.safety_height} F{config.rapid_feed_rate}")
        
        # Path commands
        for i, point in enumerate(wire_path):
            x, y, z = point
            if i == 0:
                # Rapid move to first point
                gcode_lines.append(f"G0 X{x:.3f} Y{y:.3f} Z{z:.3f}")
            else:
                # Linear move with feed rate
                gcode_lines.append(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f} F{config.work_feed_rate}")
                
        # Footer
        gcode_lines.append(f"G0 Z{config.safety_height}")
        gcode_lines.append("G28 X Y ; Home X and Y")
        gcode_lines.append("M30 ; End program")
        
        return "\n".join(gcode_lines)
```

### Data Flow

**Automatic Mode Workflow:**

```
[User clicks "Load STL"]
         ↓
[STL Importer reads file] → [Mesh displayed in 3D viewport]
         ↓
[User clicks "Generate Wire"]
         ↓
[Workflow Manager] → [Tooth Detector] → Detects 14 tooth positions
         ↓
[Bracket Positioner] → Calculates optimal bracket placement
         ↓
[Wire Path Creator] → Generates smooth path (4,200 points)
         ↓
[3D Visualizer] → Renders wire overlay on mesh
         ↓
[User clicks "Export"]
         ↓
[Export Manager] → Generates G-code/Arduino code/STL
         ↓
[File saved to disk] ✅
```

### Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **GUI Framework** | PyQt5 5.15+ | Main window, controls, layout |
| **3D Visualization** | PyVista 0.46+ | Interactive 3D rendering |
| **3D Graphics Engine** | VTK 9.5+ | Underlying graphics library |
| **Mesh Processing** | Open3D 0.19+ | STL import, mesh operations |
| **Mesh Utilities** | trimesh 4.6+ | STL validation, export |
| **Numerical Computing** | NumPy, SciPy | Array operations, interpolation |
| **Algorithms** | Custom Python | Tooth detection, wire generation |
| **Export Formats** | Custom generators | G-code, Arduino, STL |

---

## Data Requirements

### DR-1: Input Data

**STL File Format:**

```
Specification:
- Format: ASCII or Binary STL
- Coordinate System: Right-handed (X: left-right, Y: front-back, Z: up-down)
- Units: Millimeters (assumed, not enforced in STL format)
- Mesh Quality: Manifold (closed surface), no holes, no self-intersections
- Size: 50K - 1M vertices (typical intraoral scan)

Typical File Size:
- ASCII STL: 50MB - 200MB
- Binary STL: 5MB - 20MB (preferred)
```

**Example Binary STL Structure:**

```
[80-byte header]
[4-byte unsigned int: number of triangles]
[For each triangle:]
  [12 bytes: normal vector (3 floats)]
  [12 bytes: vertex 1 (3 floats)]
  [12 bytes: vertex 2 (3 floats)]
  [12 bytes: vertex 3 (3 floats)]
  [2 bytes: attribute byte count]
```

**Validation Checks:**

```python
def validate_stl_mesh(mesh):
    """Validate imported STL mesh"""
    
    checks = []
    
    # 1. Is mesh closed (manifold)?
    checks.append(("Manifold", mesh.is_watertight))
    
    # 2. Are normals consistent?
    checks.append(("Consistent Normals", mesh.is_winding_consistent))
    
    # 3. Reasonable size?
    bbox = mesh.get_axis_aligned_bounding_box()
    size = bbox.get_extent()
    checks.append(("Size", 20 < size[0] < 100))  # Width: 20-100mm
    
    # 4. Sufficient detail?
    checks.append(("Vertices", 10000 < len(mesh.vertices) < 2000000))
    
    return all(result for name, result in checks)
```

### DR-2: Internal Data Structures

**Tooth Detection Result:**

```python
@dataclass
class ToothDetectionResult:
    """Result of tooth detection algorithm"""
    
    num_teeth_detected: int
    tooth_positions: np.ndarray  # Shape: (N, 3) - XYZ coordinates
    tooth_boundaries: List[np.ndarray]  # Vertex indices per tooth
    confidence_scores: np.ndarray  # Shape: (N,) - 0.0 to 1.0
    detection_time_ms: float
    arch_type: ArchType  # Upper or Lower
```

**Wire Path Data:**

```python
@dataclass
class WirePath:
    """Generated wire path and metadata"""
    
    path_points: np.ndarray  # Shape: (M, 3) - High-resolution path
    bracket_positions: np.ndarray  # Shape: (N, 3) - Bracket locations
    num_segments: int
    total_length_mm: float
    smoothness_score: float  # Measure of curvature continuity
    generation_params: Dict[str, Any]
    timestamp: datetime
```

**Project Save File (JSON):**

```json
{
  "version": "1.0.0",
  "created": "2026-01-09T10:30:00Z",
  "last_modified": "2026-01-09T11:45:00Z",
  "patient_id": "",  // Optional, not collected by app
  "stl_file": {
    "path": "/path/to/original.stl",
    "hash": "sha256:abc123...",
    "arch_type": "upper"
  },
  "workflow": {
    "mode": "hybrid",
    "tooth_count": 14,
    "bracket_positions": [[x1, y1, z1], [x2, y2, z2], ...],
    "control_points": [[x1, y1, z1], ...]  // Manual mode
  },
  "wire_parameters": {
    "height_offset_mm": 2.5,
    "depth_offset_mm": 0.0,
    "smoothing_sigma": 12.0,
    "smoothing_passes": 5
  },
  "wire_path": {
    "points": [[x1, y1, z1], [x2, y2, z2], ...],  // Simplified (every Nth point)
    "length_mm": 145.3,
    "smoothness_score": 0.95
  },
  "exports": [
    {
      "format": "gcode",
      "file": "wire_2026-01-09.gcode",
      "timestamp": "2026-01-09T11:45:00Z"
    }
  ]
}
```

### DR-3: Export Data Formats

**G-Code Output:**

```gcode
; Orthodontic Wire G-Code
; Generated: 2026-01-09T11:45:00Z
; Points: 4200
; Estimated Time: 8m 32s

G21 ; Set units to millimeters
G90 ; Absolute positioning
G28 ; Home all axes
G0 Z10.0 F3000 ; Move to safety height

; Wire path begins
G0 X12.345 Y5.678 Z2.500 F3000
G1 X12.389 Y5.702 Z2.498 F1500
G1 X12.433 Y5.726 Z2.495 F1500
; ... (4200 points total)

; Return to home
G0 Z10.0 F3000
G28 X Y
M30 ; End program
```

**Arduino/ESP32 Code Output:**

```cpp
// Orthodontic Wire Bending Program
// Generated: 2026-01-09T11:45:00Z
// Target: ESP32 + AccelStepper library

#include <AccelStepper.h>

// Wire path coordinates (mm)
const int NUM_POINTS = 4200;
const float wire_path[][3] = {
  {12.345, 5.678, 2.500},
  {12.389, 5.702, 2.498},
  {12.433, 5.726, 2.495},
  // ... (remaining points)
};

// Stepper motor setup
AccelStepper stepperX(AccelStepper::DRIVER, STEP_PIN_X, DIR_PIN_X);
AccelStepper stepperY(AccelStepper::DRIVER, STEP_PIN_Y, DIR_PIN_Y);
AccelStepper stepperZ(AccelStepper::DRIVER, STEP_PIN_Z, DIR_PIN_Z);

void setup() {
  // Motor configuration
  stepperX.setMaxSpeed(1000);
  stepperX.setAcceleration(500);
  // ... (Y and Z setup)
  
  // Home all axes
  homeAllAxes();
  
  Serial.begin(115200);
  Serial.println("Wire bending program ready");
}

void loop() {
  for (int i = 0; i < NUM_POINTS; i++) {
    moveToPoint(wire_path[i][0], wire_path[i][1], wire_path[i][2]);
  }
  
  Serial.println("Program complete");
  while(true) {}  // Halt
}

void moveToPoint(float x, float y, float z) {
  // Convert mm to steps (200 steps/mm assumed)
  long targetX = x * 200;
  long targetY = y * 200;
  long targetZ = z * 200;
  
  stepperX.moveTo(targetX);
  stepperY.moveTo(targetY);
  stepperZ.moveTo(targetZ);
  
  // Coordinated movement
  while (stepperX.distanceToGo() != 0 || 
         stepperY.distanceToGo() != 0 || 
         stepperZ.distanceToGo() != 0) {
    stepperX.run();
    stepperY.run();
    stepperZ.run();
  }
}
```

---

## Integration Requirements

### INT-1: Intraoral Scanner Integration

**Supported Scanners (via STL export):**

| Scanner Brand | Export Format | Notes |
|---------------|---------------|-------|
| iTero (Align) | STL | Standard export, high quality |
| 3Shape TRIOS | STL | Excellent mesh quality |
| Carestream CS 3600 | STL | Good quality |
| Medit i500 | STL | Budget-friendly option |
| Planmeca Emerald | STL | High-end, large files |

**Integration Method:**
- No direct API integration (scanners are closed systems)
- User manually exports STL from scanner software
- App provides import instructions for each major scanner

**Future Enhancement (Phase 3):**
- Monitor folder for auto-import (watches scanner export directory)
- Batch import for multiple scans

### INT-2: CNC Wire Bender Integration

**Target Machines:**

1. **Commercial Benders:**
   - OrthoBend (hypothetical, for illustration)
   - Custom lab-built CNC benders

2. **DIY Solutions:**
   - Arduino/ESP32 + stepper motors
   - Raspberry Pi + GRBL HAT
   - 3-axis CNC frame conversion

**G-Code Compatibility:**
- **Marlin Flavor:** Used by many 3D printers, easily adaptable
- **Grbl Flavor:** Standard for CNC mills/routers
- **Custom Flavors:** User-configurable via export settings

**Communication:**
- **Phase 1 (Current):** File-based (save G-code, load into machine controller)
- **Phase 3 (Future):** Direct serial/USB communication
  - Serial port selection in UI
  - Real-time streaming of G-code
  - Emergency stop button
  - Progress monitoring

### INT-3: CAD Software Integration

**Export to CAD:**

- **STL Mesh Export:** Import into Fusion 360, SolidWorks, Rhino
- **Use Case:** Create wire jigs, verify clearances, 3D print verification models

**Future Enhancement:**
- **STEP/IGES Export:** Parametric curves (not just mesh)
- **DXF Export:** 2D projections for orthodontic records

---

## Testing & Quality Assurance

### Test Strategy

**Testing Pyramid:**

```
              /\
             /  \    Unit Tests (60%)
            /    \   - Individual functions
           /------\  - Fast, isolated
          /        \ 
         /   E2E    \ Integration Tests (30%)
        /   Tests    \- Component interactions
       /    (10%)     \- Workflow validation
      /________________\
     
     System/End-to-End Tests
     - Full user workflows
     - Cross-platform validation
```

### Test Cases

#### TC-1: STL Import

| Test ID | Scenario | Input | Expected Output | Priority |
|---------|----------|-------|-----------------|----------|
| TC-1.1 | Valid binary STL | standard_upper.stl (200K vertices) | Mesh displayed, no errors | P0 |
| TC-1.2 | Valid ASCII STL | sample_lower.stl | Mesh displayed, slower import | P1 |
| TC-1.3 | Corrupted file | broken.stl | Error message: "Invalid STL format" | P0 |
| TC-1.4 | Large file (1M vertices) | large_scan.stl | Import with progress bar, < 5s | P1 |
| TC-1.5 | Non-manifold mesh | open_mesh.stl | Warning: "Mesh has holes, results may vary" | P1 |

#### TC-2: Tooth Detection

| Test ID | Scenario | Anatomy Type | Expected Teeth | Accuracy Target | Priority |
|---------|----------|--------------|----------------|-----------------|----------|
| TC-2.1 | Normal spacing | Ideal Class I | 14 teeth | 100% detection | P0 |
| TC-2.2 | Mild crowding | 2mm overlap | 14 teeth | > 95% detection | P0 |
| TC-2.3 | Moderate crowding | 4mm overlap | 14 teeth | > 85% detection | P1 |
| TC-2.4 | Large gaps | 3mm diastema | 14 teeth | > 90% detection | P1 |
| TC-2.5 | Missing tooth | #9 (central incisor) | 13 teeth | Detect gap correctly | P1 |
| TC-2.6 | Rotated tooth | 45° rotation | 14 teeth | > 90% detection | P2 |

#### TC-3: Wire Generation Accuracy

**Validation Method:**
- Compare generated wire against expert-designed reference wire
- Measure RMS deviation at bracket positions

| Test ID | Anatomy | Reference Wire | Target Deviation | Priority |
|---------|---------|----------------|------------------|----------|
| TC-3.1 | Ideal Class I | Expert manual wire | < 0.15mm RMS | P0 |
| TC-3.2 | Class II | Commercial CAD wire | < 0.20mm RMS | P0 |
| TC-3.3 | Crowded case | Expert manual wire | < 0.25mm RMS | P1 |

#### TC-4: Cross-Platform Compatibility

| Test ID | Platform | Configuration | Test Scope | Priority |
|---------|----------|---------------|------------|----------|
| TC-4.1 | Windows 10 | Core i5, 8GB RAM, Intel HD 630 | Full workflow | P0 |
| TC-4.2 | Windows 11 | Core i7, 16GB RAM, NVIDIA GTX | Full workflow | P0 |
| TC-4.3 | macOS 14 (Intel) | MacBook Pro 2019 | Full workflow | P0 |
| TC-4.4 | macOS 14 (M1) | MacBook Air M1 | Full workflow, Metal API | P0 |
| TC-4.5 | Ubuntu 22.04 | Core i5, 8GB RAM, AMD GPU | Full workflow | P1 |
| TC-4.6 | Fedora 38 | Core i7, 16GB RAM, Intel GPU | Full workflow | P2 |

#### TC-5: Performance Benchmarks

| Test ID | Operation | Input Size | Target Time | Priority |
|---------|-----------|------------|-------------|----------|
| TC-5.1 | STL import | 200K vertices | < 3 seconds | P0 |
| TC-5.2 | Tooth detection | 200K vertices | < 10 seconds | P0 |
| TC-5.3 | Wire generation | 14 teeth | < 2 seconds | P0 |
| TC-5.4 | Real-time wire update (drag) | 14 teeth | < 200ms | P1 |
| TC-5.5 | G-code export | 4,200 points | < 1 second | P1 |

### Automated Testing

**Unit Tests (pytest):**

```python
# tests/test_wire_path_creator.py

import pytest
import numpy as np
from wire.wire_path_creator import WirePathCreator

class TestWirePathCreator:
    def test_create_smooth_path_basic(self):
        """Test smooth path generation with simple input"""
        creator = WirePathCreator()
        
        # 3 bracket positions in a line
        brackets = np.array([
            [0.0, 0.0, 0.0],
            [5.0, 0.0, 0.0],
            [10.0, 0.0, 0.0]
        ])
        
        path = creator.create_smooth_path(brackets)
        
        # Verify output shape
        assert path.shape[1] == 3  # X, Y, Z columns
        assert path.shape[0] > 100  # At least 100 interpolated points
        
        # Verify path passes through brackets (±0.1mm tolerance)
        for bracket in brackets:
            distances = np.linalg.norm(path - bracket, axis=1)
            assert np.min(distances) < 0.1
            
    def test_smoothness_metric(self):
        """Test that generated path is smooth (no sharp corners)"""
        creator = WirePathCreator()
        
        brackets = np.array([
            [0.0, 0.0, 0.0],
            [5.0, 1.0, 0.0],
            [10.0, 0.0, 0.0]
        ])
        
        path = creator.create_smooth_path(brackets)
        
        # Calculate curvature at each point
        curvatures = self._calculate_curvature(path)
        
        # No curvature should exceed threshold (no sharp bends)
        max_curvature = np.max(curvatures)
        assert max_curvature < 0.5  # Threshold in 1/mm
        
    def _calculate_curvature(self, path):
        """Helper: Calculate curvature at each point"""
        # ... (curvature formula implementation)
```

**Integration Tests:**

```python
# tests/test_workflow_integration.py

import pytest
from core.workflow_manager import WorkflowManager, WorkflowMode
from tests.fixtures import load_test_stl

class TestWorkflowIntegration:
    @pytest.fixture
    def workflow_manager(self):
        return WorkflowManager()
        
    def test_automatic_workflow_end_to_end(self, workflow_manager):
        """Test complete automatic workflow"""
        
        # Load test STL
        mesh = load_test_stl("tests/data/ideal_upper.stl")
        
        # Execute automatic workflow
        result = workflow_manager.process_automatic_mode(mesh)
        
        # Verify results
        assert result.num_teeth_detected == 14
        assert result.wire_path is not None
        assert len(result.wire_path) > 1000  # High-resolution path
        assert result.generation_time_ms < 15000  # < 15 seconds
```

### Manual Testing Checklist

**Pre-Release QA:**

- [ ] **Installation & Setup**
  - [ ] Clean install on Windows 10/11
  - [ ] Clean install on macOS (Intel + Apple Silicon)
  - [ ] Clean install on Ubuntu 22.04
  - [ ] All dependencies install correctly
  - [ ] App launches within 5 seconds

- [ ] **Core Workflows**
  - [ ] Automatic Mode: Load STL → Generate wire → Export (< 5 min)
  - [ ] Manual Mode: Place 5+ control points → Generate wire
  - [ ] Hybrid Mode: Auto-detect → Drag spheres → Refine wire

- [ ] **UI/UX**
  - [ ] All buttons respond to clicks
  - [ ] Sliders update values smoothly
  - [ ] Keyboard shortcuts work (I/K/J/L/F3/F4/F5)
  - [ ] Tooltips appear on hover
  - [ ] No UI freezing during long operations

- [ ] **3D Visualization**
  - [ ] Mesh renders correctly
  - [ ] Wire overlay displays properly
  - [ ] Camera controls work (rotate, pan, zoom)
  - [ ] No flickering or artifacts
  - [ ] Frame rate > 30 FPS

- [ ] **Exports**
  - [ ] G-code exports and opens in text editor
  - [ ] Arduino code compiles without errors
  - [ ] STL mesh opens in CAD software (Fusion 360, Meshmixer)

- [ ] **Error Handling**
  - [ ] Corrupted STL shows clear error message
  - [ ] Out-of-memory handled gracefully (large files)
  - [ ] App doesn't crash on invalid input

---

## Release Criteria

### Version 1.0 Release Checklist

#### Functional Completeness
- [x] **Core Algorithms Implemented**
  - [x] Tooth detection (angular segmentation)
  - [x] Bracket positioning
  - [x] Wire path generation (Catmull-Rom + Gaussian smoothing)
  - [x] Multi-stage smoothing (σ=12.0, 5 passes)

- [x] **Three Workflow Modes**
  - [x] Automatic Mode
  - [x] Manual Mode (FIXR-like)
  - [x] Hybrid Mode (draggable spheres)

- [x] **Export Formats**
  - [x] G-code (Marlin/Grbl)
  - [x] Arduino/ESP32 code
  - [x] STL mesh

- [ ] **User Interface**
  - [x] PyQt5 main window with 3D viewport
  - [ ] Futuristic gradient design (Phase 2 enhancement)
  - [x] Control panel with sliders and buttons
  - [x] Keyboard shortcuts

#### Quality Assurance
- [ ] **Testing**
  - [ ] 50+ test cases passed (unit + integration)
  - [ ] Tested on 20+ diverse dental anatomies
  - [ ] Zero critical bugs remaining
  - [ ] < 5 known minor bugs (documented in issue tracker)

- [ ] **Performance**
  - [ ] STL import < 3s (200K vertices)
  - [ ] Wire generation < 2s
  - [ ] No memory leaks during extended use

- [ ] **Cross-Platform**
  - [ ] Tested on Windows 10 & 11
  - [ ] Tested on macOS 12+ (Intel & Apple Silicon)
  - [ ] Tested on Ubuntu 20.04+

#### Documentation
- [ ] **User Documentation**
  - [ ] README.md with quick start guide
  - [ ] Installation instructions (all platforms)
  - [ ] Tutorial: Automatic workflow (with screenshots)
  - [ ] Tutorial: Manual workflow (with screenshots)
  - [ ] Keyboard shortcuts reference
  - [ ] Troubleshooting guide

- [ ] **Developer Documentation**
  - [x] BRD (Business Requirements Document)
  - [x] PRD (Product Requirements Document)
  - [ ] API documentation (docstrings)
  - [ ] Architecture diagrams
  - [ ] Contributing guidelines (CONTRIBUTING.md)

- [ ] **Clinical Documentation**
  - [ ] Accuracy validation report (comparison to reference wires)
  - [ ] 5+ case studies with before/after images
  - [ ] Disclaimer and liability notice

#### Deployment
- [ ] **Packaging**
  - [ ] Windows installer (.msi or .exe)
  - [ ] macOS disk image (.dmg)
  - [ ] Linux AppImage or Flatpak
  - [ ] requirements.txt for pip install

- [ ] **Distribution**
  - [ ] GitHub release with binaries
  - [ ] Release notes (CHANGELOG.md)
  - [ ] License file (MIT or Apache 2.0)

#### Marketing & Outreach
- [ ] **Website/Landing Page**
  - [ ] Project description and key features
  - [ ] Screenshots and demo video
  - [ ] Download links
  - [ ] Contact information

- [ ] **Community**
  - [ ] GitHub repository public
  - [ ] Issue tracker enabled
  - [ ] Discussion forum (GitHub Discussions)
  - [ ] Social media presence (Twitter/LinkedIn)

### Go/No-Go Decision Criteria

**GO if:**
- ✅ All P0 (Must-Have) features complete
- ✅ < 5 known bugs, all P3 (Low) severity or lower
- ✅ Tested on 3+ platforms successfully
- ✅ User documentation complete
- ✅ At least 3 beta testers provide positive feedback

**NO-GO if:**
- ❌ Any P0 feature incomplete
- ❌ Critical bugs (data loss, crashes)
- ❌ Fails on primary platform (Windows or macOS)
- ❌ Documentation incomplete

---

**Document End - PRD v1.0**
