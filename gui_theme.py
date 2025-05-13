PRIMARY_YELLOW = "#FFD600"
ACCENT_PURPLE = "#6A4CFF"
BG_LIGHT = "#F9FAFB"
CARD_BG = "#FFFFFF"
TEXT_DARK  = "#111827"
SHADOW_COLOR   = "rgba(0, 0, 0, 0.1)"

GLOBAL_QSS = f"""
QWidget {{
    background-color: {BG_LIGHT};
    color: {TEXT_DARK};
    font-family: 'Segoe UI', sans-serif;
    font-size: 10pt;
}}

#Header {{
    background-color: {CARD_BG};
    border-bottom: 1px solid #DDD;
}}

#Header QLabel#AppTitle {{
    font-size: 20pt;
    font-weight: bold;
}}

QGroupBox {{
    background-color: {CARD_BG};
    border: 1px solid #DDD;
    border-radius: 8px;
    margin-top: 10px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 3px 0 3px;
    background-color: {CARD_BG};
}}

QLineEdit {{
    border: 1px solid #CCC;
    border-radius: 6px;
    padding: 6px;
    background: {CARD_BG};
}}

QPushButton#PrimaryButton {{
    background-color: {PRIMARY_YELLOW};
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
}}
QPushButton#PrimaryButton:hover {{
    background-color: #FFEA70;
}}
QPushButton#PrimaryButton:pressed {{
    background-color: #E6C200;
}}

QPushButton#SecondaryButton {{
    background-color: transparent;
    color: {ACCENT_PURPLE};
    border: 2px solid {ACCENT_PURPLE};
    border-radius: 8px;
    padding: 8px 16px;
}}
QPushButton#SecondaryButton:hover {{
    background-color: {ACCENT_PURPLE}20;
}}

QSlider::groove:horizontal {{
    height: 6px;
    background: #DDD;
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: {ACCENT_PURPLE};
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}}

QProgressBar {{
    border: 1px solid #CCC;
    border-radius: 8px;
    text-align: center;
    height: 24px;
}}
QProgressBar::chunk {{
    background-color: {ACCENT_PURPLE};
    border-radius: 8px;
}}

QPlainTextEdit {{
    background: {CARD_BG};
    border: 1px solid #CCC;
    border-radius: 8px;
}}

"""
