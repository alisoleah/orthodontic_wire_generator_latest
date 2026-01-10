# Professional Orthodontic Wire Standards - Research Findings

## Key Standards
- **ISO 15841:2006/2014** - International standard for orthodontic wires
- **ANSI/ADA Standard No. 32** - American standard for orthodontic wires

## Wire Material Properties (from PMC5021743)

### NiTi Wire Characteristics
- **Superelasticity**: Load-deflection curve with horizontal plateau during unloading
- **Force delivery at 2mm deflection**: 1.0-2.0 N (102-204 gf)
- **Plateau slope**: 0.129-0.353 N/mm (lower is better for constant force)
- **Heat treatment effects**: 
  - 400°C: Preserves superelastic properties
  - 600°C: Causes Ti-rich precipitates, loses superelasticity

### Clinical Wire Sizes (from constants.py - already implemented)
- Round: 0.012", 0.014", 0.016", 0.018", 0.020"
- Rectangular: 0.016x0.022", 0.018x0.025", 0.019x0.025", 0.021x0.025"

## Dental Arch Dimensions (from PMC5885126)
- **Upper arch inter-canine**: 34.99 ± 3.8 mm
- **Upper arch inter-molar**: 35.97 ± 4.6 mm
- **Arch form**: Beta function mathematical representation (Braun 1998)

## Wire Bending Constraints
- **Minimum bend radius**: 1.5-2.25 mm for round beaks (from clinical studies)
- **Bending angles**: 6°-54° achievable with robotic systems
- **Minimum step**: 0.5-0.7 mm for precision bending

## Key Improvements Needed for Professional Wire

### 1. Material-Specific Parameters
- Different materials (NiTi, TMA, SS) have different min bend radii
- NiTi superelastic: ~2.0 mm minimum bend radius
- Stainless steel: Can achieve tighter bends (~1.5 mm)
- TMA (Beta-Ti): ~2.5 mm minimum bend radius

### 2. Clinical Force Delivery
- Optimal force range: 0.5-2.0 N for tooth movement
- Force should remain constant (flat plateau)
- Avoid stress concentrations at bends

### 3. Arch Form Accuracy
- Must follow natural dental arch curvature
- Inter-bracket distances vary by tooth type
- Anterior region needs smoother curves than posterior

### 4. Manufacturing Constraints
- G-code must respect minimum bend radius
- Wire feed accuracy: ±0.1 mm
- Bend angle accuracy: ±1°
