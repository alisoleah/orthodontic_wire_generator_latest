# Product Roadmap
## Orthodontic Wire Generator - Future Development

**Last Updated:** January 9, 2026  
**Current Version:** 0.5.0 (Pre-Release)  
**Target Version 1.0:** Q2 2026

---

## Vision

Transform orthodontic wire design from a manual, time-intensive process into an automated, AI-powered workflow accessible to practitioners worldwide. Our goal is to become the de facto open-source alternative to commercial CAD/CAM systems like FIXR and SureSmile.

---

## Current Status (January 2026)

### ✅ Completed Features

**Core Functionality:**
- ✅ Angular segmentation tooth detection (14-16 teeth)
- ✅ Ultra-smooth wire generation (Catmull-Rom + Gaussian smoothing)
- ✅ Three workflow modes (Automatic, Manual, Hybrid)
- ✅ Real-time 3D visualization with PyVista
- ✅ Draggable control points for manual refinement
- ✅ Dual-arch support with collision detection

**Export Capabilities:**
- ✅ G-code for CNC wire benders (Marlin/Grbl)
- ✅ Arduino/ESP32 code for DIY robots
- ✅ STL mesh export for 3D printing
- ✅ Keyboard shortcuts for precision control

**Platform Support:**
- ✅ Windows 10/11 (64-bit)
- ✅ macOS 12+ (Intel and Apple Silicon)
- ✅ Linux (Ubuntu, Fedora, Arch)

### ⏳ In Progress

- ⏳ **Futuristic gradient UI design** (see UI Design Goals below)
- ⏳ **Clinical validation** (testing on 50+ diverse anatomies)
- ⏳ **Cross-platform installers** (MSI, DMG, AppImage)
- ⏳ **Comprehensive documentation** (user manual, video tutorials)

---

## Release Timeline

### Phase 1: Foundation & Validation (Q1 2026) - **CURRENT**

**Goal:** Establish clinical credibility and core functionality stability.

**Milestones:**

| Milestone | Target Date | Status | Owner |
|-----------|-------------|--------|-------|
| Complete futuristic UI design | Jan 15, 2026 | ⏳ In Progress | Aly |
| Clinical validation (50+ cases) | Feb 15, 2026 | ⏳ Planning | TBD (seeking orthodontist) |
| Cross-platform installers | Feb 28, 2026 | ⏳ Planning | Aly |
| User documentation & tutorials | Mar 15, 2026 | ⏳ Planning | TBD (technical writer) |
| **Version 1.0 Release** | **Mar 31, 2026** | ⏳ On Track | Aly |

**Deliverables:**
- ✅ Stable feature/smoothwire branch
- ⏳ Clinical validation report (accuracy ±0.15mm target)
- ⏳ Professional website/landing page
- ⏳ 5+ case studies with orthodontist testimonials
- ⏳ Installer packages for Windows, macOS, Linux
- ⏳ Video tutorials (YouTube)

**Success Metrics:**
- 50 active users within 30 days of launch
- < 3 critical bugs reported
- Average user satisfaction score > 4.5/5.0

---

### Phase 2: Polish & Professional Features (Q2-Q3 2026)

**Goal:** Elevate to professional-grade commercial alternative.

**Key Features:**

#### 2.1 Advanced UI/UX Enhancements
**Target:** April 2026  
**Priority:** High

- **Onboarding Wizard** for first-time users
  - Interactive tutorial (5 steps)
  - Sample project walkthrough
  - Tooltip system for all features

- **Advanced Visualization**
  - Multi-view support (front, side, occlusal, oblique)
  - Measurement tools (distance, angle, curvature)
  - Wireframe/solid/transparent display modes
  - Light/shadow quality settings

- **Workspace Customization**
  - Resizable panels
  - Theme selection (Dark Gradient, Light, High Contrast)
  - Custom keyboard shortcuts
  - Workspace layouts (save/load configurations)

#### 2.2 Batch Processing (Laboratory Workflows)
**Target:** May 2026  
**Priority:** Medium

Enable dental laboratories to process multiple cases efficiently:

```
Batch Workflow:
1. Load folder with 10+ STL files
2. Auto-generate wires for all cases
3. Review and approve each wire
4. Batch export to G-code or STL
5. Generate summary report (PDF)
```

**Features:**
- Queue management (add, remove, reorder cases)
- Progress tracking (X of Y complete)
- Batch export settings (apply to all cases)
- Summary report with thumbnails

**Target User:** Dental lab technicians processing 20-50 wires per week.

#### 2.3 Enhanced Export Options
**Target:** June 2026  
**Priority:** Medium

- **CSV Point Cloud:** For data analysis or custom processing
- **JSON Format:** Coordinates + metadata (teeth detected, parameters used)
- **PDF Report:** Clinical documentation with:
  - 3D renderings of mesh + wire
  - Bracket positions table
  - Wire specifications (length, material, dimensions)
  - Generation parameters
  - Signature field for orthodontist approval

- **G-code Flavors:**
  - RepRap (3D printer firmware)
  - LinuxCNC (industrial CNC)
  - Mach3/Mach4 (hobbyist CNC)
  - Custom G-code templates (user-definable)

#### 2.4 Performance Optimization
**Target:** June 2026  
**Priority:** High

**Goals:**
- STL import: < 2s (current: ~3s) for 200K vertices
- Tooth detection: < 5s (current: ~10s)
- Wire generation: < 1s (current: ~2s)
- Real-time update: < 100ms (current: ~200ms)

**Approach:**
- Profile with cProfile/line_profiler
- Optimize NumPy operations (vectorization)
- Consider Cython for critical algorithms
- Multi-threading for I/O operations
- GPU acceleration for mesh processing (optional)

#### 2.5 Improved Error Handling & Recovery
**Target:** July 2026  
**Priority:** High

- **Auto-save:** Save project every 5 minutes
- **Crash recovery:** Restore last saved state on restart
- **Detailed error messages:** Explain what went wrong and how to fix
- **Undo/Redo:** Full undo stack (50 actions)
- **Safe mode:** Launch with minimal features if crash on startup

**Deliverables (Phase 2):**
- Version 2.0 release
- Professional marketing materials (website, demo videos)
- Conference presentation (AAO Annual Session)
- Peer-reviewed publication submission (AJODO or similar)

**Success Metrics:**
- 200 active users
- 10+ dental laboratories using batch processing
- Average design time < 3 minutes (down from 5 minutes)

---

### Phase 3: Manufacturing Integration (Q4 2026)

**Goal:** Close the loop from design to physical wire production.

**Key Features:**

#### 3.1 Direct CNC Machine Control
**Target:** October 2026  
**Priority:** High

**Serial/USB Communication:**
- Real-time G-code streaming to machine
- Emergency stop button (halt immediately)
- Progress monitoring (X% complete, time remaining)
- Machine status display (idle, working, error)

**Supported Machines:**
- Generic Marlin/Grbl controllers
- Arduino/ESP32-based DIY wire benders
- Commercial CNC wire benders (partner integrations)

**User Interface:**
```
┌─────────────────────────────────────┐
│ Machine Control Panel               │
├─────────────────────────────────────┤
│ Port: /dev/ttyUSB0  [▾] [Connect]  │
│ Status: ● Connected                 │
│                                     │
│ Progress: ████████░░░░░░ 60%       │
│ Time Remaining: 3m 45s              │
│                                     │
│ [⏸ Pause] [⏹ Stop] [🚨 E-STOP]    │
└─────────────────────────────────────┘
```

#### 3.2 Material Database
**Target:** October 2026  
**Priority:** Medium

Store properties of common orthodontic wire materials:

| Material | Elastic Modulus (GPa) | Yield Strength (MPa) | Typical Sizes |
|----------|----------------------|---------------------|---------------|
| Stainless Steel (SS) | 200 | 1,600 | 0.014" - 0.021" |
| Nickel-Titanium (NiTi) | 83 | 900 | 0.012" - 0.020" |
| Beta-Titanium (TMA) | 65 | 690 | 0.017" - 0.021" |
| CoCr (Elgiloy) | 180 | 1,200 | 0.016" - 0.020" |

**Usage:**
- Select material before export → adjust G-code feed rates
- Calculate spring-back compensation
- Validate wire dimensions (ensure manufacturability)

#### 3.3 Quality Control & Verification
**Target:** November 2026  
**Priority:** Medium

**Post-Manufacturing Inspection:**
- Import scanned wire (STL or point cloud)
- Overlay scanned wire on design wire
- Calculate deviation map (color-coded heatmap)
- Generate QC report (pass/fail, deviation statistics)

**Typical Workflow:**
```
1. Design wire in software
2. Export G-code → manufacture wire
3. Scan manufactured wire (3D scanner or intraoral scanner)
4. Import scan → compare to design
5. Approve or reject based on tolerance (±0.2mm typical)
```

#### 3.4 Partnership with CNC Manufacturer
**Target:** December 2026  
**Priority:** High

**Goal:** Validate software with real manufacturing equipment.

**Ideal Partner:**
- Small CNC wire bender manufacturer
- Willing to share machine specifications
- Provide test machine for development
- Co-market solution (their hardware + our software)

**Deliverables (Phase 3):**
- Version 3.0 release with manufacturing features
- Certified CNC partner (hardware + software bundle)
- Manufacturing guidelines document
- Quality control toolkit

**Success Metrics:**
- 5+ labs using direct CNC control
- 95%+ first-time-right manufacturing rate
- < 5% remake rate due to design issues

---

### Phase 4: Advanced Clinical Features (2027)

**Goal:** Expand clinical utility beyond basic wire design.

**Key Features:**

#### 4.1 Bracket Prescription Databases
**Target:** Q1 2027  
**Priority:** High

Support for major bracket systems:

**Prescriptions:**
1. **Standard Edgewise** (Tweed)
2. **Roth Prescription** (AJO-DO 2001)
3. **MBT (McLaughlin-Bennett-Trevisi)**
4. **Andrews Straight Wire**
5. **Custom** (user-defined)

**Each prescription includes:**
- Torque values (degrees) for each tooth
- Tip values (degrees)
- In-out compensation (mm)
- Rotation correction

**UI Addition:**
```
┌─────────────────────────────────┐
│ Bracket Prescription            │
├─────────────────────────────────┤
│ System: [Roth ▾]                │
│                                 │
│ Adjustments:                    │
│ ┌─────────────────────────────┐ │
│ │ Tooth  Torque   Tip   In-Out│ │
│ │ UR1    +12°    +5°    0.0mm │ │
│ │ UR2    +8°     +9°    0.0mm │ │
│ │ ...                         │ │
│ └─────────────────────────────┘ │
│                                 │
│ [Apply Prescription]            │
└─────────────────────────────────┘
```

#### 4.2 Treatment Staging (Progressive Arches)
**Target:** Q1 2027  
**Priority:** Medium

Design sequence of wires for gradual tooth movement:

**Concept:**
```
Stage 1 (Initial): Light force wire (fits current anatomy)
   ↓ 4-6 weeks
Stage 2 (Intermediate): Moderate force (50% to target)
   ↓ 4-6 weeks
Stage 3 (Final): Full correction (ideal arch form)
```

**Algorithm:**
- Input: Current tooth positions + target positions
- Output: 3-5 progressive wires (interpolated)
- Each wire exerts controlled force (3-5 oz typical)

**Use Cases:**
- Severe crowding (gradual expansion)
- Large gaps (gradual consolidation)
- Complex rotations (staged derotation)

#### 4.3 Biomechanical Analysis
**Target:** Q2 2027  
**Priority:** Low-Medium

**Force/Moment Calculations:**

Given wire properties and deflection, calculate:
- Force magnitude (Newtons) at each bracket
- Moment (Nmm) for torque application
- Center of resistance displacement
- Root resorption risk (based on force magnitude)

**Physics:**
```
F = k * δ  (Hooke's Law)

Where:
- F: Force on tooth (N)
- k: Wire stiffness = (E * I) / L³
- E: Elastic modulus (material property)
- I: Moment of inertia (wire cross-section)
- δ: Deflection distance (mm)
```

**Visualization:**
- Color-coded force map (green: safe, yellow: moderate, red: excessive)
- Vector arrows showing force direction
- Estimated tooth movement (mm/week)

**Disclaimer:** This is educational/planning tool only. Clinical validation required before patient treatment.

#### 4.4 AI-Powered Tooth Detection (ML Model)
**Target:** Q3 2027  
**Priority:** Medium

Replace angular segmentation with machine learning for better accuracy on:
- Severe crowding (>3mm overlap)
- Missing teeth (automatic gap detection)
- Rotated teeth (>30° rotation)
- Mixed dentition (primary + permanent teeth)

**Model Architecture:**
- **PointNet++ or PointTransformer** (3D point cloud networks)
- Input: 10K sampled points from dental arch mesh
- Output: Tooth segmentation mask + confidence scores

**Training Data:**
- 500-1000 labeled dental scans
- Manually annotated tooth boundaries
- Diverse anatomies (crowding, gaps, rotations, Class I/II/III)

**Performance Target:**
- 95%+ accuracy on standard anatomies
- 85%+ accuracy on severe crowding
- 90%+ accuracy on missing teeth

**Fallback:** Keep angular segmentation as fallback for users without GPU or when ML model fails.

**Deliverables (Phase 4):**
- Version 4.0 with advanced clinical features
- Clinical validation study (100+ cases)
- Peer-reviewed publication (AJODO, EJO, or Angle Orthodontist)
- FDA/CE regulatory pathway analysis

**Success Metrics:**
- 500+ active users
- 20+ orthodontic practices using treatment staging
- Published research validating accuracy and clinical outcomes

---

## UI Design Goals (Phase 1 Priority)

### Futuristic Gradient Theme

**Design Philosophy:**
> "Medical software meets sci-fi aesthetic - professional yet visually striking."

**Key Visual Elements:**

1. **Color Palette:**
   - Background: Dark navy (#1a1a2e)
   - Gradients: Blue-purple (#667eea → #764ba2), Cyan (#4facfe → #00f2fe)
   - Text: High-contrast white/gray (#e0e0e0)
   - Accents: Teal, magenta, cyan for highlights

2. **Material Design:**
   - **Glass-morphism:** Semi-transparent panels with backdrop blur
   - **Soft shadows:** Elevated elements (cards, buttons)
   - **Smooth animations:** 200-300ms ease-out transitions
   - **Hover effects:** Lift on buttons, glow on interactive elements

3. **Typography:**
   - Font: Inter or SF Pro Display (modern sans-serif)
   - Headers: 600-700 weight (semi-bold)
   - Body: 400 weight (regular)
   - Code: JetBrains Mono (for G-code, coordinates)

4. **Layout:**
```
┌────────────────────────────────────────────────────┐
│ ▶ Ortho Wire Gen    [Gradient Title Bar]    Help  │
├──────────┬─────────────────────────────────────────┤
│ Control  │                                         │
│ Panel    │         3D Viewport                     │
│ [Glass]  │         [Dark background]               │
│          │                                         │
│ ┌──────┐ │  🦷 Dental Mesh (light gray)            │
│ │ Load │ │  📐 Wire Path (cyan gradient)           │
│ │ STL  │ │  ⚫ Control Points (glowing spheres)   │
│ └──────┘ │                                         │
│          │                                         │
│ Mode:    │                                         │
│ [Auto ▾] │                                         │
│          │                                         │
├──────────┴─────────────────────────────────────────┤
│ Status: Wire generated (4,200 pts) | 0.8s | Ready │
└────────────────────────────────────────────────────┘
```

5. **Animations:**
   - **Wire generation:** Animated line drawing from start to end
   - **Mode switching:** Cross-fade between control panels
   - **Hover:** Buttons lift 2px with shadow increase
   - **Loading:** Gradient progress bar (animated shimmer)
   - **Completion:** Pulse effect + success notification

**Inspiration:**
- Apple's SF Symbols (iconography)
- Figma's UI (clean, modern)
- Unity Hub (gradient accents, dark theme)
- Adobe Creative Cloud (glass panels, smooth animations)

---

## Platform-Specific Enhancements

### Windows-Specific

- [ ] Start menu integration (shortcuts, recent files)
- [ ] Windows 11 snap layouts support
- [ ] High-DPI scaling (150%, 200%, 250%)
- [ ] File association (.stl → open with Ortho Wire Gen)

### macOS-Specific

- [ ] Spotlight integration (search within app)
- [ ] Touch Bar support (MacBook Pro)
- [ ] Retina display optimization (2x, 3x assets)
- [ ] Dark Mode sync with system preferences
- [ ] Notarization for Gatekeeper (signed .dmg)

### Linux-Specific

- [ ] Desktop entry file (show in app launcher)
- [ ] Wayland compatibility (in addition to X11)
- [ ] Distribution packages:
  - [ ] Ubuntu PPA
  - [ ] Arch AUR package
  - [ ] Flatpak (universal)
  - [ ] Snap package

---

## Long-Term Vision (2028+)

### Cloud & Collaboration Platform

**Goal:** Transform from desktop app to hybrid desktop+cloud platform.

**Features:**

#### 1. Cloud Case Storage
- Save projects to cloud (AWS S3, Google Cloud)
- Access from any device (desktop, tablet)
- Automatic backup and version history
- 5GB free storage, 50GB pro plan

#### 2. Real-Time Collaboration
- Multiple users edit same wire simultaneously
- Live cursors showing collaborators
- In-app chat/comments
- Permissions (view-only, edit, owner)

**Use Case:**
> Orthodontist designs initial wire, sends to lab technician for refinement, discusses changes in real-time.

#### 3. Practice Management Integration
- HIPAA-compliant patient record linking
- Integrate with Dolphin, OrthoTrac, etc.
- Export to patient portal
- Appointment scheduling integration

#### 4. Mobile Companion App (View-Only)
- iOS/Android app for viewing wires on-the-go
- 3D viewer with pinch-to-zoom
- Patient education tool (show proposed wire)

### AI-Powered Treatment Planning

**Goal:** Go beyond wire design to full treatment planning.

**Features:**

#### 1. Automatic Treatment Plan Generation
- Input: Current anatomy (STL) + desired outcome (Class I ideal)
- Output: Complete treatment plan including:
  - IPR requirements (interproximal reduction)
  - Extraction recommendations (if needed)
  - Treatment duration estimate
  - Wire sequence (5-10 progressive arches)
  - Expected tooth movements (3D animation)

#### 2. Outcome Prediction
- Train GAN (Generative Adversarial Network) on before/after scans
- Predict final tooth positions after treatment
- Visualize expected smile improvement
- Risk assessment (root resorption, gingival recession)

#### 3. Virtual Setup
- Digital tooth segmentation + movement planning
- Drag individual teeth to desired positions
- Auto-generate wire sequence to achieve setup
- Compare multiple treatment options (e.g., extract vs non-extract)

---

## Community & Ecosystem

### Open-Source Contributions

**Encourage community contributions in:**
- Platform-specific optimizations
- Export format plugins
- Translation/internationalization
- Clinical validation studies
- Educational content (tutorials, courses)

### Plugin Architecture (Future)

Allow third-party developers to extend functionality:

```python
# Example plugin: Custom bracket prescription
class CustomBracketPlugin:
    def __init__(self):
        self.name = "Custom Bracket System"
        self.version = "1.0.0"
        
    def apply_prescription(self, tooth_positions):
        # Custom logic for bracket placement
        return adjusted_positions
        
# Register plugin
PluginManager.register(CustomBracketPlugin())
```

**Potential Plugins:**
- Custom export formats (proprietary CNC machines)
- Machine learning models (alternative tooth detection)
- Integration with practice management systems
- Custom measurement tools
- Treatment planning templates

### Educational Partnerships

**Target:** Dental schools and orthodontic residency programs

**Offerings:**
- Free licenses for educational institutions
- Curriculum integration materials
- Guest lectures on digital orthodontics
- Research collaboration opportunities

**Benefits:**
- Train next generation of orthodontists on modern tools
- Generate research publications
- Build brand awareness and credibility
- Collect feedback from expert users

---

## Success Metrics Dashboard

### Version 1.0 (Launch)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Active Users | 50 | 0 | ⏳ Pre-launch |
| GitHub Stars | 100 | 0 | ⏳ Pre-launch |
| Wire Designs Created | 500 | 0 | ⏳ Pre-launch |
| Average Design Time | < 5 min | ~5 min | ✅ On target |
| User Satisfaction (NPS) | 40+ | N/A | ⏳ Post-launch survey |
| Critical Bugs | < 3 | 0 | ✅ Stable |

### Version 2.0 (6 months)

| Metric | Target | Tracking |
|--------|--------|----------|
| Active Users | 200 | Q2 2026 survey |
| Dental Labs Using Batch | 10 | Usage analytics |
| Average Design Time | < 3 min | Performance logs |
| Conference Presentations | 1 | AAO Annual Session |
| Peer-Reviewed Publications | 1 submission | AJODO submission |

### Version 3.0 (12 months)

| Metric | Target | Tracking |
|--------|--------|----------|
| Active Users | 500 | Q4 2026 survey |
| CNC Partnerships | 2-3 | Business development |
| Manufacturing Success Rate | > 95% | QC reports |
| Revenue (if SaaS) | $10K MRR | Stripe dashboard |

---

## Funding & Commercialization Strategy

### Phase 1: Open-Source Foundation (Current)

**Model:** Free, open-source (MIT or Apache 2.0 license)  
**Funding:** Self-funded development

**Benefits:**
- Build user base and credibility
- Community contributions
- Academic validation
- No pressure for immediate revenue

### Phase 2: Freemium Model (Q3 2026)

**Free Tier:**
- Desktop app (full functionality)
- Local file storage
- Community support (forums)

**Pro Tier ($49/month or $499/year):**
- Cloud storage (50GB)
- Priority support (email, video calls)
- Batch processing
- Advanced features (treatment staging, biomechanics)
- Early access to new features

**Target:** 5% conversion rate (10 paying users from 200 free users = $500/month)

### Phase 3: SaaS Platform (2027+)

**Enterprise Tier ($199/month per user):**
- Multi-user collaboration
- Practice management integration
- Compliance features (HIPAA, GDPR)
- Dedicated account manager
- Custom onboarding and training

**Target:** 20 enterprise customers × $199 = $4,000/month

**Alternative Revenue Streams:**
- **CNC Hardware Bundle:** Partner with manufacturer, revenue share
- **Consulting Services:** Custom development for labs/practices
- **Educational Workshops:** Training courses for orthodontists ($500-$1000 per attendee)

---

## Risk Mitigation

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| ML model fails to improve accuracy | Medium | Medium | Keep angular segmentation as reliable fallback |
| Cloud infrastructure costs explode | Low | High | Start with conservative limits (5GB storage), scale gradually |
| Cross-platform compatibility issues | Medium | Medium | Continuous integration testing on all platforms |

### Business Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Low user adoption | Medium | High | Focus on clinical validation, word-of-mouth marketing |
| Competition from established players | Medium | Medium | Emphasize cost advantage and open-source flexibility |
| Regulatory scrutiny (FDA/CE) | Low | High | Position as design tool, not diagnostic device; consult legal |

### Clinical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Generated wires cause patient harm | Low | Critical | Extensive validation, clear disclaimers, professional liability insurance |
| Accuracy insufficient for clinical use | Medium | High | Rigorous testing against expert wires, conservative default parameters |

---

## Conclusion

This roadmap outlines an ambitious multi-year vision for the Orthodontic Wire Generator, transforming it from a powerful desktop tool into a comprehensive platform for digital orthodontics. The phased approach allows for iterative validation and community feedback while maintaining focus on clinical accuracy and user experience.

**Next Steps:**
1. **Immediate (Jan 2026):** Complete futuristic UI redesign
2. **Q1 2026:** Clinical validation and Version 1.0 launch
3. **Q2-Q3 2026:** Polish features and batch processing (Version 2.0)
4. **Q4 2026:** Manufacturing integration (Version 3.0)
5. **2027+:** Advanced clinical features and cloud platform

**Join Us:**
We invite orthodontists, developers, and dental technologists to contribute to this open-source project. Together, we can democratize access to advanced orthodontic design tools.

---

**Questions or Suggestions?**  
Submit feedback via GitHub Issues or Discussions:  
https://github.com/alisoleah/orthodontic_wire_generator_latest

---

**Document End - ROADMAP.md v1.0**
