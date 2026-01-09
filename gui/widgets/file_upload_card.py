"""
File Upload Card Widget
File upload card with loaded/not loaded states
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal


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
        
        # Status (hidden initially, shown when loaded)
        self.status_label = QLabel("")
        self.status_label.setObjectName("fileCardStatusNotLoaded")
        self.status_label.setVisible(False)  # Hide initially
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
        
        # Update status - show it now
        self.status_label.setText("✓ Loaded")
        self.status_label.setObjectName("fileCardStatus")
        self.status_label.setVisible(True)  # Show when loaded
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
        
        # Update status - hide it
        self.status_label.setText("")
        self.status_label.setObjectName("fileCardStatusNotLoaded")
        self.status_label.setVisible(False)  # Hide when not loaded
        self.status_label.setStyleSheet("")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        
        # Hide check icon
        self.check_icon.setVisible(False)
