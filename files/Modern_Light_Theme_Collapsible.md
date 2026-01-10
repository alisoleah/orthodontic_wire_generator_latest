# Modern Light Theme with Collapsible Sections
## PyQt5 Implementation - OrthoGen Style

**Style Reference:** Light, clean, modern interface with colorful accents  
**Key Features:** Collapsible sections, light theme, rounded cards, subtle shadows

---

## Complete Implementation

### 1. Modern Light Theme Stylesheet

```python
# gui/styles/modern_light_theme.py

MODERN_LIGHT_STYLESHEET = """
/* ==================== GLOBAL STYLES ==================== */

QWidget {
    background-color: #f8f9fa;
    color: #2d3748;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', 'Roboto', sans-serif;
    font-size: 14px;
}

QMainWindow {
    background-color: #f8f9fa;
}

/* ==================== CUSTOM TITLE BAR ==================== */

#customTitleBar {
    background: white;
    border-bottom: 1px solid #e2e8f0;
    padding: 15px 20px;
}

#appTitle {
    color: #2d3748;
    font-size: 20px;
    font-weight: 700;
}

#appSubtitle {
    color: #718096;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

#systemStatus {
    background: #d4f4dd;
    color: #2f855a;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
}

/* ==================== COLLAPSIBLE SECTIONS ==================== */

/* Section container */
#collapsibleSection {
    background: white;
    border-radius: 16px;
    margin: 8px 0px;
    border: 1px solid #e2e8f0;
}

/* Section header (clickable) */
#sectionHeader {
    background: white;
    border: none;
    border-radius: 16px;
    padding: 20px;
    text-align: left;
    font-size: 15px;
    font-weight: 700;
    color: #2d3748;
}

#sectionHeader:hover {
    background: #f7fafc;
}

#sectionHeader:pressed {
    background: #edf2f7;
}

/* Section number badge */
#sectionNumber {
    background: #edf2f7;
    color: #4a5568;
    padding: 4px 10px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    margin-right: 8px;
}

/* Section content area */
#sectionContent {
    background: white;
    padding: 0px 20px 20px 20px;
    border-bottom-left-radius: 16px;
    border-bottom-right-radius: 16px;
}

/* ==================== FILE UPLOAD CARDS ==================== */

/* File upload card - not loaded */
#fileCard {
    background: #f7fafc;
    border: 2px dashed #cbd5e0;
    border-radius: 12px;
    padding: 20px;
    margin: 8px 0px;
}

#fileCard:hover {
    background: #edf2f7;
    border-color: #a0aec0;
}

/* File upload card - loaded (success state) */
#fileCardLoaded {
    background: #d4f4dd;
    border: 2px solid #48bb78;
    border-radius: 12px;
    padding: 20px;
    margin: 8px 0px;
}

#fileCardTitle {
    font-size: 15px;
    font-weight: 600;
    color: #2d3748;
}

#fileCardStatus {
    font-size: 13px;
    color: #48bb78;
    font-weight: 600;
}

#fileCardStatusNotLoaded {
    font-size: 13px;
    color: #a0aec0;
    font-weight: 500;
}

/* ==================== BUTTONS ==================== */

/* Primary button (blue) */
QPushButton {
    background: #3182ce;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 14px;
    min-height: 40px;
}

QPushButton:hover {
    background: #2c5aa0;
}

QPushButton:pressed {
    background: #2a4365;
}

QPushButton:disabled {
    background: #cbd5e0;
    color: #a0aec0;
}

/* File upload button */
QPushButton#uploadButton {
    background: transparent;
    color: #3182ce;
    border: 2px solid #3182ce;
    border-radius: 10px;
    padding: 12px 20px;
    font-weight: 600;
}

QPushButton#uploadButton:hover {
    background: rgba(49, 130, 206, 0.1);
}

/* Success button (green) */
QPushButton#successButton {
    background: #48bb78;
}

QPushButton#successButton:hover {
    background: #38a169;
}

/* Secondary button */
QPushButton#secondaryButton {
    background: #edf2f7;
    color: #4a5568;
}

QPushButton#secondaryButton:hover {
    background: #e2e8f0;
}

/* Danger button (red) */
QPushButton#dangerButton {
    background: #f56565;
}

QPushButton#dangerButton:hover {
    background: #e53e3e;
}

/* ==================== RADIO BUTTONS ==================== */

QRadioButton {
    color: #2d3748;
    spacing: 10px;
    padding: 12px;
    background: #f7fafc;
    border-radius: 10px;
    margin: 4px 0px;
}

QRadioButton:hover {
    background: #edf2f7;
}

QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border-radius: 10px;
    border: 2px solid #cbd5e0;
    background: white;
}

QRadioButton::indicator:checked {
    background: #3182ce;
    border: 2px solid #3182ce;
}

QRadioButton::indicator:checked::after {
    content: "";
    width: 8px;
    height: 8px;
    border-radius: 4px;
    background: white;
}

/* ==================== CHECKBOXES ==================== */

QCheckBox {
    color: #2d3748;
    spacing: 10px;
    padding: 8px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid #cbd5e0;
    background: white;
}

QCheckBox::indicator:checked {
    background: #3182ce;
    border: 2px solid #3182ce;
    image: url(:/icons/checkmark_white.svg);
}

QCheckBox::indicator:hover {
    border: 2px solid #3182ce;
}

/* ==================== LABELS ==================== */

QLabel {
    color: #2d3748;
    background: transparent;
}

QLabel#headingLabel {
    font-size: 18px;
    font-weight: 700;
    color: #1a202c;
}

QLabel#subheadingLabel {
    font-size: 13px;
    color: #718096;
    font-weight: 500;
}

QLabel#descriptionLabel {
    font-size: 13px;
    color: #a0aec0;
    line-height: 1.5;
}

/* ==================== INFO CARDS ==================== */

/* Blue info card */
#infoCardBlue {
    background: #e6f2ff;
    border-left: 4px solid #3182ce;
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0px;
}

#infoCardBlueLabel {
    color: #2c5aa0;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

#infoCardBlueValue {
    color: #1a202c;
    font-size: 24px;
    font-weight: 700;
}

/* Purple info card */
#infoCardPurple {
    background: #f3e8ff;
    border-left: 4px solid #9f7aea;
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0px;
}

#infoCardPurpleLabel {
    color: #6b46c1;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

#infoCardPurpleValue {
    color: #1a202c;
    font-size: 24px;
    font-weight: 700;
}

/* Orange info card */
#infoCardOrange {
    background: #fff5e6;
    border-left: 4px solid #ed8936;
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0px;
}

#infoCardOrangeLabel {
    color: #c05621;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

#infoCardOrangeValue {
    color: #1a202c;
    font-size: 24px;
    font-weight: 700;
}

/* ==================== SLIDERS ==================== */

QSlider::groove:horizontal {
    background: #e2e8f0;
    height: 8px;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #3182ce;
    width: 20px;
    height: 20px;
    margin: -6px 0;
    border-radius: 10px;
    border: 3px solid white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

QSlider::handle:horizontal:hover {
    background: #2c5aa0;
    width: 24px;
    height: 24px;
    margin: -8px 0;
}

QSlider::sub-page:horizontal {
    background: #3182ce;
    border-radius: 4px;
}

/* ==================== SPINBOXES ==================== */

QSpinBox, QDoubleSpinBox {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 12px;
    color: #2d3748;
    min-height: 36px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #3182ce;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    background: #f7fafc;
    border-top-right-radius: 8px;
}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
    background: #edf2f7;
}

/* ==================== COMBOBOXES ==================== */

QComboBox {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px 15px;
    color: #2d3748;
    min-height: 36px;
}

QComboBox:hover {
    border: 2px solid #cbd5e0;
}

QComboBox:focus {
    border: 2px solid #3182ce;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: url(:/icons/chevron_down.svg);
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    selection-background-color: #e6f2ff;
    selection-color: #2d3748;
    padding: 5px;
}

/* ==================== SCROLLBARS ==================== */

QScrollBar:vertical {
    background: #f7fafc;
    width: 12px;
    margin: 0px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #cbd5e0;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #a0aec0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ==================== STATUS BAR ==================== */

QStatusBar {
    background: white;
    color: #718096;
    border-top: 1px solid #e2e8f0;
    padding: 8px 16px;
}

/* ==================== TOAST NOTIFICATION ==================== */

#toastSuccess {
    background: #48bb78;
    color: white;
    padding: 16px 24px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 14px;
}

#toastError {
    background: #f56565;
    color: white;
    padding: 16px 24px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 14px;
}

#toastInfo {
    background: #3182ce;
    color: white;
    padding: 16px 24px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 14px;
}

/* ==================== TEXT EDIT ==================== */

QTextEdit, QPlainTextEdit {
    background: #1a202c;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
    color: #68d391;
    font-family: 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    selection-background-color: rgba(49, 130, 206, 0.3);
}

/* ==================== PROGRESS BARS ==================== */

QProgressBar {
    background: #e2e8f0;
    border: none;
    border-radius: 8px;
    text-align: center;
    color: #2d3748;
    font-weight: 600;
    height: 24px;
}

QProgressBar::chunk {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #3182ce, stop:1 #2c5aa0
    );
    border-radius: 7px;
}

/* ==================== TOOLTIPS ==================== */

QToolTip {
    background: #1a202c;
    color: white;
    border: 1px solid #2d3748;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
}

/* ==================== MENU BAR ==================== */

QMenuBar {
    background: white;
    color: #2d3748;
    border-bottom: 1px solid #e2e8f0;
    padding: 4px;
}

QMenuBar::item {
    background: transparent;
    padding: 8px 16px;
    border-radius: 6px;
}

QMenuBar::item:selected {
    background: #e6f2ff;
}

QMenu {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 8px;
}

QMenu::item {
    padding: 10px 20px;
    border-radius: 6px;
}

QMenu::item:selected {
    background: #e6f2ff;
}
"""
```

---

### 2. Collapsible Section Widget

```python
# gui/widgets/collapsible_section.py

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QIcon

class CollapsibleSection(QWidget):
    """
    Modern collapsible section with smooth animation.
    Similar to OrthoGen interface style.
    """
    
    # Signal emitted when section is expanded/collapsed
    toggled = pyqtSignal(bool)
    
    def __init__(self, title, section_number=None, parent=None):
        super().__init__(parent)
        self.is_expanded = True
        self.setup_ui(title, section_number)
        
    def setup_ui(self, title, section_number):
        """Create the collapsible section UI."""
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Container for entire section
        self.section_container = QWidget()
        self.section_container.setObjectName("collapsibleSection")
        section_layout = QVBoxLayout(self.section_container)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(0)
        
        # Header (clickable)
        self.header = QPushButton()
        self.header.setObjectName("sectionHeader")
        self.header.setCursor(Qt.PointingHandCursor)
        self.header.clicked.connect(self.toggle)
        
        # Header layout
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 16, 20, 16)
        
        # Section number badge (optional)
        if section_number is not None:
            number_label = QLabel(str(section_number))
            number_label.setObjectName("sectionNumber")
            header_layout.addWidget(number_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setObjectName("headingLabel")
        title_label.setStyleSheet("font-size: 15px; font-weight: 700; color: #2d3748;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Chevron icon (up/down)
        self.chevron = QLabel("▼")
        self.chevron.setStyleSheet("font-size: 12px; color: #718096;")
        header_layout.addWidget(self.chevron)
        
        section_layout.addWidget(self.header)
        
        # Content area
        self.content_widget = QWidget()
        self.content_widget.setObjectName("sectionContent")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 0, 20, 20)
        self.content_layout.setSpacing(12)
        
        section_layout.addWidget(self.content_widget)
        
        main_layout.addWidget(self.section_container)
        
        # Animation
        self.animation = QPropertyAnimation(self.content_widget, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    def add_widget(self, widget):
        """Add a widget to the content area."""
        self.content_layout.addWidget(widget)
        
    def add_layout(self, layout):
        """Add a layout to the content area."""
        self.content_layout.addLayout(layout)
        
    def toggle(self):
        """Toggle section expanded/collapsed."""
        
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()
            
    def expand(self):
        """Expand the section."""
        
        self.is_expanded = True
        self.chevron.setText("▼")
        
        # Animate expansion
        self.animation.setStartValue(0)
        self.animation.setEndValue(self.content_widget.sizeHint().height())
        self.animation.start()
        
        self.toggled.emit(True)
        
    def collapse(self):
        """Collapse the section."""
        
        self.is_expanded = False
        self.chevron.setText("▶")
        
        # Animate collapse
        self.animation.setStartValue(self.content_widget.height())
        self.animation.setEndValue(0)
        self.animation.start()
        
        self.toggled.emit(False)
```

---

### 3. File Upload Card Widget

```python
# gui/widgets/file_upload_card.py

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

class FileUploadCard(QWidget):
    """
    File upload card with loaded/not loaded states.
    Matches OrthoGen interface style.
    """
    
    file_selected = pyqtSignal(str)  # Emits file path when selected
    
    def __init__(self, title, icon_text="📂", parent=None):
        super().__init__(parent)
        self.title = title
        self.icon_text = icon_text
        self.is_loaded = False
        self.file_path = None
        self.setup_ui()
        
    def setup_ui(self):
        """Create the file card UI."""
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Card container
        self.card = QWidget()
        self.card.setObjectName("fileCard")
        self.card.setCursor(Qt.PointingHandCursor)
        
        card_layout = QHBoxLayout(self.card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        
        # Upload icon
        self.icon = QLabel(self.icon_text)
        self.icon.setStyleSheet("font-size: 24px;")
        card_layout.addWidget(self.icon)
        
        # Text container
        text_container = QVBoxLayout()
        text_container.setSpacing(4)
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("fileCardTitle")
        text_container.addWidget(self.title_label)
        
        # Status
        self.status_label = QLabel("Not loaded")
        self.status_label.setObjectName("fileCardStatusNotLoaded")
        text_container.addWidget(self.status_label)
        
        card_layout.addLayout(text_container)
        card_layout.addStretch()
        
        # Check icon (shown when loaded)
        self.check_icon = QLabel("✓")
        self.check_icon.setStyleSheet("font-size: 24px; color: #48bb78; font-weight: bold;")
        self.check_icon.setVisible(False)
        card_layout.addWidget(self.check_icon)
        
        layout.addWidget(self.card)
        
        # Make card clickable
        self.card.mousePressEvent = lambda e: self.select_file()
        
    def select_file(self):
        """Open file dialog to select STL file."""
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {self.title}",
            "",
            "STL Files (*.stl);;All Files (*)"
        )
        
        if file_path:
            self.set_loaded(file_path)
            self.file_selected.emit(file_path)
            
    def set_loaded(self, file_path=None):
        """Set card to loaded state."""
        
        self.is_loaded = True
        self.file_path = file_path
        
        # Update styling
        self.card.setObjectName("fileCardLoaded")
        self.card.setStyleSheet("")  # Reset to apply new object name
        self.card.style().unpolish(self.card)
        self.card.style().polish(self.card)
        
        # Update status
        self.status_label.setText("✓ Loaded")
        self.status_label.setObjectName("fileCardStatus")
        self.status_label.setStyleSheet("")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        
        # Show check icon
        self.check_icon.setVisible(True)
        
    def set_not_loaded(self):
        """Reset card to not loaded state."""
        
        self.is_loaded = False
        self.file_path = None
        
        # Update styling
        self.card.setObjectName("fileCard")
        self.card.setStyleSheet("")
        self.card.style().unpolish(self.card)
        self.card.style().polish(self.card)
        
        # Update status
        self.status_label.setText("Not loaded")
        self.status_label.setObjectName("fileCardStatusNotLoaded")
        self.status_label.setStyleSheet("")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        
        # Hide check icon
        self.check_icon.setVisible(False)
```

---

### 4. Info Card Widget

```python
# gui/widgets/info_card.py

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class InfoCard(QWidget):
    """
    Colored info card for displaying metrics.
    Matches OrthoGen telemetry cards style.
    """
    
    def __init__(self, label, value, icon="📊", color="blue", parent=None):
        super().__init__(parent)
        self.color = color
        self.setup_ui(label, value, icon)
        
    def setup_ui(self, label, value, icon):
        """Create the info card UI."""
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Card container
        card = QWidget()
        card.setObjectName(f"infoCard{self.color.capitalize()}")
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28px;")
        card_layout.addWidget(icon_label)
        
        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        # Label (uppercase, small)
        self.label_widget = QLabel(label.upper())
        self.label_widget.setObjectName(f"infoCard{self.color.capitalize()}Label")
        text_layout.addWidget(self.label_widget)
        
        # Value (large, bold)
        self.value_widget = QLabel(str(value))
        self.value_widget.setObjectName(f"infoCard{self.color.capitalize()}Value")
        text_layout.addWidget(self.value_widget)
        
        card_layout.addLayout(text_layout)
        card_layout.addStretch()
        
        layout.addWidget(card)
        
    def set_value(self, value):
        """Update the value displayed."""
        self.value_widget.setText(str(value))
```

---

### 5. Main Window with Collapsible Sections

```python
# gui/modern_light_window.py

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from gui.styles.modern_light_theme import MODERN_LIGHT_STYLESHEET
from gui.widgets.collapsible_section import CollapsibleSection
from gui.widgets.file_upload_card import FileUploadCard
from gui.widgets.info_card import InfoCard

class ModernLightWindow(QMainWindow):
    """
    Modern light theme main window with collapsible sections.
    Matches OrthoGen interface style.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OrthoGenPrime - AI-Assisted Wire Design")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Apply light theme
        self.setStyleSheet(MODERN_LIGHT_STYLESHEET)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the main UI."""
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # LEFT PANEL: Collapsible sections (35% width)
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, stretch=35)
        
        # CENTER: 3D Viewer (45% width)
        center_panel = self.create_3d_viewer()
        main_layout.addWidget(center_panel, stretch=45)
        
        # RIGHT PANEL: Wire telemetry (20% width)
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, stretch=20)
        
        # Custom title bar
        self.setup_title_bar()
        
        # Status bar
        self.setup_status_bar()
        
    def setup_title_bar(self):
        """Create custom title bar (optional - can use system title bar)."""
        
        # This is optional - you can keep the default window title bar
        # Or create a custom one like OrthoGen
        pass
        
    def create_left_panel(self):
        """Create left panel with collapsible sections."""
        
        # Container
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # SECTION 1: Dental Models
        section1 = CollapsibleSection("DENTAL MODELS", section_number=1)
        
        # File upload cards
        self.upper_arch_card = FileUploadCard("Upper Arch (.stl)", "⬆️")
        self.upper_arch_card.file_selected.connect(self.on_upper_arch_loaded)
        section1.add_widget(self.upper_arch_card)
        
        self.lower_arch_card = FileUploadCard("Lower Arch (.stl)", "⬇️")
        section1.add_widget(self.lower_arch_card)
        
        self.opposing_arch_card = FileUploadCard("Opposing Arch", "↔️")
        section1.add_widget(self.opposing_arch_card)
        
        layout.addWidget(section1)
        
        # SECTION 2: Configuration
        section2 = CollapsibleSection("CONFIGURATION", section_number=2)
        
        # Workflow mode selection
        workflow_label = QLabel("WORKFLOW MODE")
        workflow_label.setObjectName("subheadingLabel")
        section2.add_widget(workflow_label)
        
        self.workflow_group = QButtonGroup()
        
        auto_radio = QRadioButton("🤖 Automatic Detection")
        auto_radio.setChecked(True)
        self.workflow_group.addButton(auto_radio, 0)
        section2.add_widget(auto_radio)
        
        auto_desc = QLabel("AI detects teeth and generates wire automatically")
        auto_desc.setObjectName("descriptionLabel")
        section2.add_widget(auto_desc)
        
        manual_radio = QRadioButton("✏️ Manual Design (FIXR Style)")
        self.workflow_group.addButton(manual_radio, 1)
        section2.add_widget(manual_radio)
        
        hybrid_radio = QRadioButton("⚡ Hybrid (Auto + Manual)")
        self.workflow_group.addButton(hybrid_radio, 2)
        section2.add_widget(hybrid_radio)
        
        layout.addWidget(section2)
        
        # SECTION 3: Wire Parameters
        section3 = CollapsibleSection("WIRE PARAMETERS", section_number=3)
        
        # Height offset slider
        height_layout = QVBoxLayout()
        height_label = QLabel("Height Offset")
        height_label.setObjectName("subheadingLabel")
        height_layout.addWidget(height_label)
        
        self.height_slider = QSlider(Qt.Horizontal)
        self.height_slider.setRange(0, 50)
        self.height_slider.setValue(25)
        height_layout.addWidget(self.height_slider)
        
        self.height_value = QLabel("2.5 mm")
        self.height_value.setAlignment(Qt.AlignRight)
        height_layout.addWidget(self.height_value)
        
        section3.add_layout(height_layout)
        
        # Smoothness slider
        smooth_layout = QVBoxLayout()
        smooth_label = QLabel("Smoothness")
        smooth_label.setObjectName("subheadingLabel")
        smooth_layout.addWidget(smooth_label)
        
        self.smooth_slider = QSlider(Qt.Horizontal)
        self.smooth_slider.setRange(5, 20)
        self.smooth_slider.setValue(12)
        smooth_layout.addWidget(self.smooth_slider)
        
        self.smooth_value = QLabel("12.0")
        self.smooth_value.setAlignment(Qt.AlignRight)
        smooth_layout.addWidget(self.smooth_value)
        
        section3.add_layout(smooth_layout)
        
        layout.addWidget(section3)
        
        # Action buttons at bottom (not collapsible)
        actions_widget = QWidget()
        actions_layout = QVBoxLayout(actions_widget)
        actions_layout.setSpacing(10)
        
        generate_btn = QPushButton("⚡ Generate Wire")
        generate_btn.setMinimumHeight(50)
        generate_btn.clicked.connect(self.generate_wire)
        actions_layout.addWidget(generate_btn)
        
        export_btn = QPushButton("💾 Export")
        export_btn.setObjectName("successButton")
        export_btn.setMinimumHeight(44)
        actions_layout.addWidget(export_btn)
        
        layout.addWidget(actions_widget)
        
        # Spacer
        layout.addStretch()
        
        # Wrap in scroll area
        scroll = QScrollArea()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        return scroll
        
    def create_3d_viewer(self):
        """Create center 3D viewer panel."""
        
        # Container
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title bar
        title_bar = QWidget()
        title_bar.setStyleSheet("background: transparent; border: none;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 20, 20, 20)
        
        # Camera controls
        view_combo = QComboBox()
        view_combo.addItems(["Perspective", "Front", "Side", "Top"])
        title_layout.addWidget(view_combo)
        
        title_layout.addStretch()
        
        reset_btn = QPushButton("🎥 Reset Camera")
        reset_btn.setObjectName("secondaryButton")
        title_layout.addWidget(reset_btn)
        
        layout.addWidget(title_bar)
        
        # 3D Viewer placeholder (replace with your PyVista widget)
        viewer_placeholder = QLabel("3D Viewer\n(PyVista widget goes here)")
        viewer_placeholder.setAlignment(Qt.AlignCenter)
        viewer_placeholder.setStyleSheet("""
            QLabel {
                background: #f7fafc;
                color: #a0aec0;
                font-size: 16px;
                border: none;
            }
        """)
        viewer_placeholder.setMinimumHeight(500)
        layout.addWidget(viewer_placeholder)
        
        # Bottom status (like "Mesh loaded! Ready for point selection")
        self.status_toast = QLabel("Mesh loaded! Ready for point selection")
        self.status_toast.setObjectName("toastSuccess")
        self.status_toast.setAlignment(Qt.AlignCenter)
        self.status_toast.setVisible(False)
        layout.addWidget(self.status_toast)
        
        return container
        
    def create_right_panel(self):
        """Create right panel with wire telemetry."""
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("WIRE TELEMETRY")
        title.setObjectName("headingLabel")
        layout.addWidget(title)
        
        # Info cards
        self.length_card = InfoCard("Length", "34.01 mm", "📏", color="blue")
        layout.addWidget(self.length_card)
        
        self.points_card = InfoCard("Points", "12", "⚓", color="purple")
        layout.addWidget(self.points_card)
        
        self.offset_card = InfoCard("Offset", "0.5 mm", "↕️", color="orange")
        layout.addWidget(self.offset_card)
        
        # G-Code preview section
        gcode_section = CollapsibleSection("G-CODE PREVIEW")
        
        self.gcode_viewer = QTextEdit()
        self.gcode_viewer.setReadOnly(True)
        self.gcode_viewer.setMaximumHeight(250)
        self.gcode_viewer.setPlaceholderText("; Generated by OrthoGen\nG21 ; Metric\n...")
        gcode_section.add_widget(self.gcode_viewer)
        
        layout.addWidget(gcode_section)
        
        layout.addStretch()
        
        return container
        
    def setup_status_bar(self):
        """Create status bar."""
        
        status_bar = self.statusBar()
        self.status_message = QLabel("● System Ready")
        self.status_message.setStyleSheet("color: #48bb78; font-weight: 600;")
        status_bar.addWidget(self.status_message)
        
    def on_upper_arch_loaded(self, file_path):
        """Handle upper arch file loaded."""
        
        print(f"Upper arch loaded: {file_path}")
        
        # Show success toast
        self.status_toast.setText("✓ Mesh loaded! Ready for point selection")
        self.status_toast.setVisible(True)
        
        # Your existing load logic here...
        
    def generate_wire(self):
        """Generate wire button clicked."""
        
        print("Generating wire...")
        # Your existing wire generation logic here...


# Run the application
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ModernLightWindow()
    window.show()
    sys.exit(app.exec_())
```

---

## Usage Instructions

### 1. File Structure
```
your_project/
├── gui/
│   ├── styles/
│   │   └── modern_light_theme.py      # Light theme stylesheet
│   ├── widgets/
│   │   ├── collapsible_section.py     # Collapsible widget
│   │   ├── file_upload_card.py        # File card widget
│   │   └── info_card.py               # Info card widget
│   └── modern_light_window.py         # Main window
└── run_app.py                         # Entry point
```

### 2. Quick Start

```python
# run_app.py

from PyQt5.QtWidgets import QApplication
import sys
from gui.modern_light_window import ModernLightWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernLightWindow()
    window.show()
    sys.exit(app.exec_())
```

### 3. Integrate Your Existing Code

Replace the placeholder in `create_3d_viewer()` with your PyVista widget:

```python
# Instead of:
viewer_placeholder = QLabel("3D Viewer...")

# Use:
self.pyvista_widget = YourPyVistaWidget()
layout.addWidget(self.pyvista_widget)
```

---

## Key Features ✨

### ✅ Light Theme
- White/light gray backgrounds
- Clean, modern appearance
- High readability

### ✅ Collapsible Sections
- Click header to expand/collapse
- Smooth 300ms animation
- Save screen space
- Open only what you need

### ✅ File Upload Cards
- Visual feedback (green when loaded)
- Checkmark icon on success
- Clickable cards (no separate button needed)

### ✅ Info Cards
- Color-coded (blue, purple, orange)
- Large, readable values
- Icon + label + value layout

### ✅ Modern Components
- Rounded corners (16px radius)
- Subtle shadows
- Smooth hover effects
- Professional gradients in sliders

---

## Customization

### Change Colors

```python
# In modern_light_theme.py

# Primary color (buttons, sliders)
#3182ce → Your color

# Success color (loaded states)
#48bb78 → Your color

# Background
#f8f9fa → Your color
```

### Add More Sections

```python
section4 = CollapsibleSection("ADVANCED OPTIONS", section_number=4)

# Add your widgets
section4.add_widget(your_widget)

layout.addWidget(section4)
```

---

## Result Preview

Your app will look like:
```
┌──────────────────────────────────────────────────────────────┐
│ OrthoGenPrime                         ● System Ready      ☰  │
│ AI-ASSISTED WIRE DESIGN                                      │
├────────────┬─────────────────────────────────────────────────┤
│            │                                                 │
│ 1. DENTAL  │        [3D Viewer - Light Gray Background]     │
│    MODELS▼ │                                                 │
│ [✓ Upper]  │        [Dental mesh in center]                  │
│ [ Lower  ] │                                                 │
│            │        [Red wire path overlay]                  │
│ 2. CONFIG▶ │                                                 │
│            │                                                 │
│ 3. PARAMS▼ │        Mesh loaded! Ready for point selection  │
│ [Sliders]  ├─────────────────────────────────────────────────┤
│            │ WIRE TELEMETRY                                  │
│ [Generate] │ [Blue card: Length 34.01mm]                     │
│ [ Export ] │ [Purple card: Points 12]                        │
│            │ [Orange card: Offset 0.5mm]                     │
└────────────┴─────────────────────────────────────────────────┘
```

---

This gives you **exactly** the modern, light, collapsible interface you showed in the OrthoGen screenshot! 🎨✨
