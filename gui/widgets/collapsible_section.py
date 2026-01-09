"""
Collapsible Section Widget
Modern collapsible section with smooth animation
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer


class CollapsibleSection(QWidget):
    """
    Modern collapsible section with smooth animation.
    Similar to OrthoGen interface style.
    """
    
    # Signal emitted when section is expanded/collapsed
    toggled = pyqtSignal(bool)
    
    def __init__(self, title, section_number=None, parent=None):
        super().__init__(parent)
        self.is_expanded = False  # Start collapsed
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
        
        # Chevron icon (up/down) - start with collapsed arrow
        self.chevron = QLabel("▶")
        self.chevron.setStyleSheet("font-size: 12px; color: #718096;")
        header_layout.addWidget(self.chevron)
        
        section_layout.addWidget(self.header)
        
        # Content area
        self.content_widget = QWidget()
        self.content_widget.setObjectName("sectionContent")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 10, 20, 20)
        self.content_layout.setSpacing(16)  # Increased spacing for less crowded look
        
        section_layout.addWidget(self.content_widget)
        
        main_layout.addWidget(self.section_container)
        
        # Animation
        self.animation = QPropertyAnimation(self.content_widget, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Set initial state - collapsed
        self.content_widget.setMaximumHeight(0)
        
    def add_widget(self, widget):
        """Add a widget to the content area."""
        self.content_layout.addWidget(widget)
        # Update height after adding widget
        QTimer.singleShot(0, self.update_content_height)
        
    def add_layout(self, layout):
        """Add a layout to the content area."""
        self.content_layout.addLayout(layout)
        # Update height after adding layout
        QTimer.singleShot(0, self.update_content_height)
    
    def update_content_height(self):
        """Update the content widget height to fit contents"""
        if self.is_expanded:
            self.content_widget.setMaximumHeight(16777215)
            self.content_widget.adjustSize()
        
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
        
        # Force layout update
        self.content_widget.adjustSize()
        content_height = self.content_widget.sizeHint().height()
        
        # Animate expansion
        self.animation.setStartValue(0)
        self.animation.setEndValue(content_height)
        self.animation.finished.connect(self._on_expand_finished)
        self.animation.start()
        
        self.toggled.emit(True)
    
    def _on_expand_finished(self):
        """Called when expand animation finishes - remove height limit"""
        if self.is_expanded:
            self.content_widget.setMaximumHeight(16777215)  # Remove limit
        try:
            self.animation.finished.disconnect(self._on_expand_finished)
        except:
            pass
        
    def collapse(self):
        """Collapse the section."""
        
        self.is_expanded = False
        self.chevron.setText("▶")
        
        # Animate collapse
        self.animation.setStartValue(self.content_widget.height())
        self.animation.setEndValue(0)
        self.animation.start()
        
        self.toggled.emit(False)
