"""
Modern Light Theme for Orthodontic Wire Generator
Clean, modern interface with colorful accents and collapsible sections
"""

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
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #718096;
    margin-right: 10px;
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

/* ==================== GROUP BOX ==================== */

QGroupBox {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    margin-top: 20px;
    padding: 20px 16px 16px 16px;
    font-weight: 600;
    font-size: 13px;
    color: #718096;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 12px;
    color: #718096;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 1px;
}
"""


def get_stylesheet():
    """Get the complete modern light theme stylesheet"""
    return MODERN_LIGHT_STYLESHEET
