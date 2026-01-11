"""
Info Card Widget
Colored info card for displaying metrics
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
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
