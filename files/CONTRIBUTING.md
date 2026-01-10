# Contributing to Orthodontic Wire Generator

Thank you for your interest in contributing to the Orthodontic Wire Generator! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Requirements](#testing-requirements)
6. [Pull Request Process](#pull-request-process)
7. [Areas for Contribution](#areas-for-contribution)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background or experience level.

### Expected Behavior

- Be respectful and constructive in discussions
- Accept feedback gracefully
- Focus on what's best for the project and community
- Show empathy towards other contributors

### Unacceptable Behavior

- Harassment, discrimination, or inappropriate comments
- Trolling, insulting, or personal attacks
- Publishing others' private information
- Any conduct that could be considered unprofessional

---

## Getting Started

### Prerequisites

**Required:**
- Python 3.7 - 3.11
- Git
- Basic understanding of orthodontics or CAD/CAM workflows (helpful but not required)

**Recommended:**
- Experience with PyQt5, PyVista, or NumPy
- Access to dental STL files for testing
- Familiarity with orthodontic terminology

### Setting Up Development Environment

1. **Fork and Clone the Repository:**

```bash
git clone https://github.com/YOUR_USERNAME/orthodontic_wire_generator_latest.git
cd orthodontic_wire_generator_latest
git checkout feature/smoothwire  # Work on the latest branch
```

2. **Create Virtual Environment:**

```bash
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

3. **Install Dependencies:**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies (pytest, etc.)
```

4. **Verify Installation:**

```bash
python run_app.py  # Should launch the application
pytest tests/      # Should run all tests
```

5. **Create Feature Branch:**

```bash
git checkout -b feature/your-feature-name
```

---

## Development Workflow

### Branch Strategy

- **main:** Stable release branch (protected)
- **feature/smoothwire:** Current development branch
- **feature/[name]:** New features (branch from feature/smoothwire)
- **bugfix/[name]:** Bug fixes
- **docs/[name]:** Documentation updates

### Commit Message Format

Use semantic commit messages:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```
feat(wire): Add support for 12-tooth arches

- Modify ToothDetector to accept configurable tooth count
- Add UI dropdown for selecting tooth count
- Update tests for new parameter

Closes #42
```

```
fix(visualization): Resolve sphere widget crash on macOS

The sphere widget was causing crashes on macOS due to OpenGL
compatibility issues. This fix uses OSMesa renderer as fallback.

Fixes #53
```

### Development Cycle

1. **Create Issue (if applicable):**
   - Describe the problem or feature
   - Add relevant labels (bug, enhancement, etc.)
   - Wait for maintainer approval before starting work

2. **Develop:**
   - Write code following coding standards
   - Add/update tests
   - Update documentation

3. **Test Locally:**
   - Run all tests: `pytest tests/`
   - Test manually with diverse STL files
   - Check cross-platform compatibility (if possible)

4. **Commit and Push:**
   - Commit changes with semantic messages
   - Push to your fork: `git push origin feature/your-feature-name`

5. **Create Pull Request:**
   - Follow PR template
   - Link related issues
   - Request review from maintainers

---

## Coding Standards

### Python Style Guide

Follow **PEP 8** with some modifications:

**Line Length:**
- 100 characters maximum (not 79)
- Use implicit line continuation for long expressions

**Naming Conventions:**
- Classes: `PascalCase` (e.g., `WirePathCreator`)
- Functions/Methods: `snake_case` (e.g., `create_smooth_path`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_VERTICES`)
- Private methods: `_leading_underscore` (e.g., `_calculate_curvature`)

**Imports:**
```python
# Standard library
import os
import sys

# Third-party
import numpy as np
import open3d as o3d
from PyQt5.QtWidgets import QMainWindow

# Local
from core.workflow_manager import WorkflowManager
from wire.wire_path_creator import WirePathCreator
```

### Docstrings

Use **NumPy-style docstrings**:

```python
def create_smooth_path(bracket_positions, sigma=12.0, smoothing_passes=5):
    """
    Generate ultra-smooth wire path through bracket positions.
    
    This function uses a multi-stage algorithm combining Catmull-Rom spline
    interpolation with multi-pass Gaussian smoothing to create clinically
    appropriate wire paths.
    
    Parameters
    ----------
    bracket_positions : np.ndarray
        Nx3 array of bracket XYZ coordinates in millimeters.
    sigma : float, optional
        Gaussian smoothing kernel size. Larger values produce smoother
        curves but may deviate from bracket positions. Default is 12.0.
    smoothing_passes : int, optional
        Number of Gaussian smoothing iterations. Default is 5.
        
    Returns
    -------
    np.ndarray
        Mx3 array of high-resolution wire path points (M >> N).
        
    Raises
    ------
    ValidationError
        If the generated path deviates more than 0.2mm from any bracket.
        
    Examples
    --------
    >>> brackets = np.array([[0, 0, 0], [5, 0, 0], [10, 0, 0]])
    >>> wire = create_smooth_path(brackets)
    >>> print(wire.shape)
    (1200, 3)
    
    Notes
    -----
    The algorithm complexity is O(N * M) where N is the number of brackets
    and M is the total number of output points. Typical execution time is
    1-2 seconds for 14 brackets.
    """
```

### Type Hints

Use type hints for function signatures:

```python
from typing import List, Tuple, Optional
import numpy as np

def detect_teeth(
    mesh: o3d.geometry.TriangleMesh,
    num_teeth: int = 14,
    arch_type: str = "upper"
) -> Tuple[np.ndarray, List[float]]:
    """
    Detect tooth positions and return positions with confidence scores.
    
    Parameters
    ----------
    mesh : o3d.geometry.TriangleMesh
        Dental arch mesh.
    num_teeth : int, optional
        Expected number of teeth to detect. Default is 14.
    arch_type : str, optional
        "upper" or "lower". Default is "upper".
        
    Returns
    -------
    positions : np.ndarray
        Nx3 array of tooth positions.
    confidences : List[float]
        Confidence score (0.0 to 1.0) for each detected tooth.
    """
```

### Code Organization

**Single Responsibility Principle:**
- Each class should have one primary responsibility
- Each function should do one thing well
- Maximum function length: ~50 lines (guideline, not hard rule)

**Example:**

```python
# GOOD: Focused responsibilities
class ToothDetector:
    """Handles tooth detection only."""
    def detect_teeth(self, mesh): ...
    
class BracketPositioner:
    """Handles bracket placement only."""
    def position_brackets(self, teeth): ...
    
class WirePathCreator:
    """Handles wire generation only."""
    def create_smooth_path(self, brackets): ...

# BAD: Mixed responsibilities
class ToothAndWireProcessor:
    """Does everything (too broad)."""
    def detect_teeth(self, mesh): ...
    def position_brackets(self, teeth): ...
    def create_wire(self, brackets): ...
```

---

## Testing Requirements

### Test Coverage

- **Minimum coverage:** 70% for new code
- **Critical components:** 90%+ coverage (algorithms, data handling)
- **UI code:** Lower priority for coverage (focus on integration tests)

### Test Types

#### 1. Unit Tests

Test individual functions in isolation:

```python
# tests/test_wire_path_creator.py

import pytest
import numpy as np
from wire.wire_path_creator import WirePathCreator

class TestWirePathCreator:
    @pytest.fixture
    def creator(self):
        return WirePathCreator()
        
    def test_straight_line_path(self, creator):
        """Test with collinear points."""
        brackets = np.array([
            [0.0, 0.0, 0.0],
            [5.0, 0.0, 0.0],
            [10.0, 0.0, 0.0]
        ])
        
        path = creator.create_smooth_path(brackets)
        
        # All Y coordinates should be near 0
        assert np.allclose(path[:, 1], 0.0, atol=0.01)
        
    def test_passes_through_brackets(self, creator):
        """Test that path passes through each bracket."""
        brackets = np.array([
            [0.0, 0.0, 0.0],
            [5.0, 2.0, 0.0],
            [10.0, 0.0, 0.0]
        ])
        
        path = creator.create_smooth_path(brackets)
        
        for bracket in brackets:
            distances = np.linalg.norm(path - bracket, axis=1)
            min_distance = np.min(distances)
            assert min_distance < 0.15, f"Path misses bracket by {min_distance}mm"
```

#### 2. Integration Tests

Test component interactions:

```python
# tests/test_workflow_integration.py

from core.workflow_manager import WorkflowManager
from tests.utils import load_test_mesh

def test_automatic_workflow_end_to_end():
    """Test complete automatic workflow."""
    manager = WorkflowManager()
    mesh = load_test_mesh("ideal_upper.stl")
    
    result = manager.process_automatic_mode(mesh)
    
    assert result.success is True
    assert result.num_teeth_detected == 14
    assert result.wire_path is not None
    assert len(result.wire_path) > 1000
```

#### 3. Manual Tests

For UI and visual features, provide manual test instructions:

```markdown
## Manual Test: Draggable Sphere Widgets

**Objective:** Verify real-time wire updates when dragging control points.

**Steps:**
1. Launch app: `python run_app.py`
2. Load STL: `STLfiles/ideal_upper.stl`
3. Click "Generate Wire" (Automatic Mode)
4. Click "Hybrid Mode" (F5)
5. Left-click and drag any sphere widget
6. Observe wire path updates in real-time

**Expected Result:**
- Wire updates within 200ms of releasing drag
- No flickering or visual artifacts
- Wire still passes through all bracket positions

**Pass/Fail:** _______
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_wire_path_creator.py

# Run specific test
pytest tests/test_wire_path_creator.py::TestWirePathCreator::test_straight_line_path

# Run tests in parallel (faster)
pytest tests/ -n 4
```

### Test Data

- **Location:** `tests/fixtures/` directory
- **STL Files:** Include diverse anatomies (normal, crowded, gaps)
- **Size:** Keep test files small (<5MB) to avoid bloating repository
- **Licensing:** Ensure test data has appropriate permissions

---

## Pull Request Process

### Before Submitting PR

- [ ] Code follows coding standards
- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated (docstrings, README, etc.)
- [ ] No merge conflicts with target branch
- [ ] Commits are clean and well-organized

### PR Template

```markdown
## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## Related Issues

Closes #[issue_number]

## Testing

Describe how you tested your changes:
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] Tested on [Windows/macOS/Linux]

## Screenshots (if applicable)

[Add screenshots for UI changes]

## Checklist

- [ ] My code follows the project's coding standards
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have updated documentation as needed
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing tests pass locally
```

### Review Process

1. **Automated Checks:**
   - CI/CD pipeline runs tests
   - Code linting (Pylint/Flake8)
   - Coverage report generated

2. **Manual Review:**
   - At least one maintainer reviews code
   - Feedback provided via comments
   - Revisions requested if needed

3. **Approval and Merge:**
   - Once approved, maintainer merges PR
   - Branch deleted after merge (keep repo clean)

### Review Timeline

- **Response time:** 3-5 business days for initial review
- **Urgent fixes:** Reviewed within 24 hours (security, critical bugs)
- **Large PRs:** May take longer; consider breaking into smaller PRs

---

## Areas for Contribution

### High-Priority Tasks

#### 1. Clinical Validation
**Skills:** Access to dental scans, orthodontic knowledge  
**Effort:** Medium-Large

Test the application on diverse dental anatomies and compare generated wires to expert-designed wires. Document accuracy metrics (RMS deviation, bracket precision).

**Deliverables:**
- Test report with 20+ diverse cases
- Accuracy metrics (RMS deviation)
- Failure case documentation

#### 2. Cross-Platform Testing
**Skills:** Access to Windows/macOS/Linux  
**Effort:** Small-Medium

Test application on different platforms and document platform-specific issues.

**Focus Areas:**
- macOS (Intel vs Apple Silicon)
- Windows (various GPU vendors)
- Linux (Ubuntu, Fedora, Arch)

#### 3. Futuristic UI Design
**Skills:** UI/UX design, PyQt5  
**Effort:** Large

Redesign the interface with modern gradient-based aesthetics (see PRD for design specs).

**Deliverables:**
- PyQt5 stylesheets
- UI mockups/wireframes
- Smooth animations and transitions

### Medium-Priority Tasks

#### 4. Performance Optimization
**Skills:** Python profiling, algorithm optimization  
**Effort:** Medium

Profile the application and optimize bottlenecks (especially tooth detection and wire generation).

**Target Metrics:**
- STL import: < 3s (200K vertices)
- Wire generation: < 2s
- Real-time update: < 200ms

#### 5. Export Format Expansion
**Skills:** G-code, CAD formats  
**Effort:** Small-Medium

Add support for additional export formats:
- CSV point cloud
- JSON (coordinates + metadata)
- STEP/IGES (parametric curves)
- DXF (2D projections)

#### 6. Documentation & Tutorials
**Skills:** Technical writing, video editing  
**Effort:** Small-Medium

Create comprehensive documentation and video tutorials:
- Quick start guide
- Workflow tutorials (Auto, Manual, Hybrid)
- Troubleshooting guide
- Video walkthroughs

### Advanced Tasks (Future)

#### 7. Machine Learning Tooth Detection
**Skills:** PyTorch/TensorFlow, 3D point clouds  
**Effort:** Large

Replace angular segmentation with ML-based detection for better accuracy on crowded teeth.

**Approach:**
- Train PointNet or PointTransformer model
- Collect/generate training data (500-1000 labeled scans)
- Integrate model into workflow manager

#### 8. Bracket Prescription Databases
**Skills:** Orthodontic knowledge, database design  
**Effort:** Medium

Implement support for different bracket systems (Roth, MBT, Andrews) with torque/tip adjustments.

#### 9. Cloud Features
**Skills:** Backend development (Flask/FastAPI), cloud platforms  
**Effort:** Large

Build cloud-based case storage and collaboration features:
- RESTful API for case management
- User authentication
- Real-time collaboration (WebSockets)

---

## Questions?

- **GitHub Issues:** For bug reports and feature requests
- **GitHub Discussions:** For general questions and ideas
- **Email:** Contact maintainer via GitHub profile

Thank you for contributing to the Orthodontic Wire Generator! 🦷✨
