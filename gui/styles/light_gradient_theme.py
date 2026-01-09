"""
Glass-Morphism Theme for Orthodontic Wire Generator
Modern, futuristic light theme with translucency and gradients
"""

# Color Palette - Glass-Morphism Medical Future
COLORS = {
    # Backgrounds - Subtle gradients
    'background_gradient_start': '#eff9ff',  # Alice Blue
    'background_gradient_end': '#e0f7fa',    # Cyan tint
    'background_solid': '#F0F4F8',           # Fallback
    
    # Glass Panels - Translucent
    'glass_panel': 'rgba(255, 255, 255, 0.75)',
    'glass_border': 'rgba(255, 255, 255, 0.9)',
    'glass_shadow': 'rgba(0, 0, 0, 0.08)',
    
    # Text
    'text_primary': '#2D3748',      # Charcoal (not pure black)
    'text_secondary': '#718096',    # Cool Gray
    'text_disabled': '#CBD5E0',
    'text_on_gradient': '#ffffff',
    
    # Accent Gradients - Teal/Mint
    'gradient_primary_start': '#38ef7d',  # Lime Green
    'gradient_primary_end': '#11998e',    # Teal
    'gradient_secondary_start': '#00C9FF', # Cyan
    'gradient_secondary_end': '#92FE9D',   # Lime
    'gradient_accent_start': '#43cea2',    # Teal
    'gradient_accent_end': '#185a9d',      # Blue
    
    # Semantic Colors
    'success': '#38ef7d',
    'warning': '#ffc107',
    'error': '#ff6b6b',
    'info': '#00C9FF',
    
    # Neumorphism (etched areas)
    'neumorphic_bg': '#e8f0f7',
    'neumorphic_shadow_light': 'rgba(255, 255, 255, 0.8)',
    'neumorphic_shadow_dark': 'rgba(0, 0, 0, 0.1)',
}


GLASS_MORPHISM_STYLESHEET = f"""
/* ============================================
   MAIN WINDOW - Gradient Background
   ============================================ */
QMainWindow {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {COLORS['background_gradient_start']}, 
                                stop:1 {COLORS['background_gradient_end']});
}}

/* ============================================
   MENU BAR - Glass Effect
   ============================================ */
QMenuBar {{
    background-color: {COLORS['glass_panel']};
    border: none;
    border-bottom: 1px solid {COLORS['glass_border']};
    padding: 6px;
    color: {COLORS['text_primary']};
    border-radius: 0px;
}}

QMenuBar::item {{
    padding: 8px 16px;
    background: transparent;
    border-radius: 8px;
    color: {COLORS['text_primary']};
}}

QMenuBar::item:selected {{
    background-color: rgba(56, 239, 125, 0.15);
}}

QMenuBar::item:pressed {{
    background-color: rgba(56, 239, 125, 0.25);
}}

QMenu {{
    background-color: {COLORS['glass_panel']};
    border: 1px solid {COLORS['glass_border']};
    border-radius: 12px;
    padding: 8px;
}}

QMenu::item {{
    padding: 10px 28px 10px 16px;
    border-radius: 6px;
    color: {COLORS['text_primary']};
}}

QMenu::item:selected {{
    background-color: rgba(56, 239, 125, 0.15);
}}

/* ============================================
   GROUP BOX - Glass Panels (Floating Cards)
   ============================================ */
QGroupBox {{
    background-color: {COLORS['glass_panel']};
    border: 1px solid {COLORS['glass_border']};
    border-radius: 15px;
    margin-top: 24px;
    padding: 20px 16px 16px 16px;
    font-family: 'Inter', 'Segoe UI', 'SF Pro Display', sans-serif;
    font-weight: 600;
    font-size: 13px;
    color: {COLORS['text_secondary']};
    letter-spacing: 0.5px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 12px;
    color: {COLORS['text_secondary']};
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 1px;
}}

/* ============================================
   BUTTONS - Pill Shape with Gradients
   ============================================ */
QPushButton {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {COLORS['gradient_primary_start']}, 
                                stop:1 {COLORS['gradient_primary_end']});
    color: {COLORS['text_on_gradient']};
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 14px;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    min-height: 20px;
}}

QPushButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #4df18c, 
                                stop:1 #1faea2);
    padding: 11px 24px 13px 24px;  /* Slight lift effect */
}}

QPushButton:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #2dd96d, 
                                stop:1 #0e8878);
    padding: 12px 24px;
}}

QPushButton:disabled {{
    background: #e2e8f0;
    color: {COLORS['text_disabled']};
}}

/* Secondary Button Style */
QPushButton[buttonStyle="secondary"] {{
    background: #e2e8f0;
    color: {COLORS['text_secondary']};
    border: none;
}}

QPushButton[buttonStyle="secondary"]:hover {{
    background: #d4dde6;
}}

/* ============================================
   LABELS
   ============================================ */
QLabel {{
    color: {COLORS['text_primary']};
    font-size: 14px;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background: transparent;
}}

QLabel[labelStyle="header"] {{
    font-size: 16px;
    font-weight: 700;
    color: {COLORS['text_primary']};
    text-transform: uppercase;
    letter-spacing: 1px;
}}

QLabel[labelStyle="subheader"] {{
    font-size: 14px;
    font-weight: 600;
    color: {COLORS['text_secondary']};
}}

/* ============================================
   SLIDERS - Modern with Gradient
   ============================================ */
QSlider::groove:horizontal {{
    background: rgba(0, 0, 0, 0.08);
    height: 6px;
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {COLORS['gradient_secondary_start']}, 
                                stop:1 {COLORS['gradient_secondary_end']});
    width: 20px;
    height: 20px;
    border-radius: 10px;
    margin: -7px 0;
    border: 3px solid white;
    box-shadow: 0 2px 8px rgba(0, 201, 255, 0.3);
}}

QSlider::handle:horizontal:hover {{
    width: 22px;
    height: 22px;
    margin: -8px 0;
    box-shadow: 0 4px 12px rgba(0, 201, 255, 0.5);
}}

QSlider::sub-page:horizontal {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {COLORS['gradient_secondary_start']}, 
                                stop:1 {COLORS['gradient_secondary_end']});
    border-radius: 3px;
}}

/* ============================================
   LINE EDIT - Soft Rounded Inputs
   ============================================ */
QLineEdit {{
    background-color: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 10px;
    padding: 10px 14px;
    color: {COLORS['text_primary']};
    font-size: 14px;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}}

QLineEdit:focus {{
    border: 2px solid {COLORS['gradient_secondary_start']};
    padding: 9px 13px;
    background-color: white;
}}

QLineEdit:disabled {{
    background-color: #f7fafc;
    color: {COLORS['text_disabled']};
}}

/* ============================================
   COMBO BOX - Rounded Dropdowns
   ============================================ */
QComboBox {{
    background-color: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 10px;
    padding: 10px 14px;
    color: {COLORS['text_primary']};
    font-size: 14px;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    min-width: 120px;
}}

QComboBox:hover {{
    border: 1px solid {COLORS['gradient_secondary_start']};
    background-color: white;
}}

QComboBox:focus {{
    border: 2px solid {COLORS['gradient_secondary_start']};
    padding: 9px 13px;
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {COLORS['text_secondary']};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['glass_panel']};
    border: 1px solid {COLORS['glass_border']};
    border-radius: 10px;
    padding: 6px;
    selection-background-color: rgba(56, 239, 125, 0.15);
    selection-color: {COLORS['text_primary']};
}}

/* ============================================
   SPIN BOX
   ============================================ */
QSpinBox, QDoubleSpinBox {{
    background-color: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 10px;
    padding: 10px 14px;
    color: {COLORS['text_primary']};
    font-size: 14px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 2px solid {COLORS['gradient_secondary_start']};
    padding: 9px 13px;
}}

/* ============================================
   STATUS BAR - Glass Bottom Bar
   ============================================ */
QStatusBar {{
    background-color: {COLORS['glass_panel']};
    color: {COLORS['text_secondary']};
    border-top: 1px solid {COLORS['glass_border']};
    padding: 8px 12px;
    font-size: 13px;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}}

QStatusBar::item {{
    border: none;
}}

/* ============================================
   PROGRESS BAR - Gradient Fill
   ============================================ */
QProgressBar {{
    background-color: rgba(0, 0, 0, 0.05);
    border: none;
    border-radius: 8px;
    height: 10px;
    text-align: center;
    color: {COLORS['text_primary']};
    font-weight: 600;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {COLORS['gradient_primary_start']}, 
                                stop:1 {COLORS['gradient_primary_end']});
    border-radius: 8px;
}}

/* ============================================
   SCROLL BAR - Minimal Modern
   ============================================ */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    border-radius: 5px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: rgba(0, 0, 0, 0.15);
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: rgba(0, 0, 0, 0.25);
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    border-radius: 5px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background: rgba(0, 0, 0, 0.15);
    border-radius: 5px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background: rgba(0, 0, 0, 0.25);
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ============================================
   TAB WIDGET - Glass Tabs
   ============================================ */
QTabWidget::pane {{
    background-color: {COLORS['glass_panel']};
    border: 1px solid {COLORS['glass_border']};
    border-radius: 12px;
    padding: 12px;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    padding: 12px 24px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 4px;
    font-weight: 600;
}}

QTabBar::tab:selected {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 {COLORS['gradient_primary_start']}, 
                                stop:1 {COLORS['gradient_primary_end']});
    color: {COLORS['text_on_gradient']};
}}

QTabBar::tab:hover:!selected {{
    background-color: rgba(56, 239, 125, 0.1);
}}

/* ============================================
   TOOL TIP - Floating Pill
   ============================================ */
QToolTip {{
    background-color: {COLORS['text_primary']};
    color: {COLORS['text_on_gradient']};
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}}

/* ============================================
   TABLE WIDGET - Glass Table
   ============================================ */
QTableWidget {{
    background-color: {COLORS['glass_panel']};
    border: 1px solid {COLORS['glass_border']};
    border-radius: 12px;
    gridline-color: rgba(0, 0, 0, 0.05);
    color: {COLORS['text_primary']};
}}

QTableWidget::item {{
    padding: 10px;
}}

QTableWidget::item:selected {{
    background-color: rgba(56, 239, 125, 0.15);
    color: {COLORS['text_primary']};
}}

QHeaderView::section {{
    background-color: rgba(255, 255, 255, 0.5);
    color: {COLORS['text_secondary']};
    padding: 10px;
    border: none;
    border-bottom: 1px solid rgba(0, 0, 0, 0.08);
    font-weight: 600;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.5px;
}}

/* ============================================
   RADIO BUTTON - Modern Circular
   ============================================ */
QRadioButton::indicator {{
    width: 18px;
    height: 18px;
}}

QRadioButton::indicator:unchecked {{
    border: 2px solid rgba(0, 0, 0, 0.2);
    border-radius: 9px;
    background-color: white;
}}

QRadioButton::indicator:checked {{
    border: 2px solid {COLORS['gradient_primary_end']};
    border-radius: 9px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {COLORS['gradient_primary_start']}, 
                                stop:1 {COLORS['gradient_primary_end']});
}}

/* ============================================
   CHECKBOX - Modern Square
   ============================================ */
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
}}

QCheckBox::indicator:unchecked {{
    border: 2px solid rgba(0, 0, 0, 0.2);
    border-radius: 4px;
    background-color: white;
}}

QCheckBox::indicator:checked {{
    border: 2px solid {COLORS['gradient_primary_end']};
    border-radius: 4px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {COLORS['gradient_primary_start']}, 
                                stop:1 {COLORS['gradient_primary_end']});
}}
"""


def get_stylesheet():
    """Get the complete glass-morphism theme stylesheet"""
    return GLASS_MORPHISM_STYLESHEET


def get_color(color_name):
    """Get a specific color from the theme palette"""
    return COLORS.get(color_name, '#000000')
