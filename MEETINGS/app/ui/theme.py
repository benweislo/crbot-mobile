def build_stylesheet(theme: dict) -> str:
    bg = theme["background"]
    surface = theme["surface"]
    surface_el = theme["surface_elevated"]
    primary = theme["primary"]
    secondary = theme["secondary"]
    tertiary = theme["tertiary"]
    text = theme["text_primary"]
    text_muted = theme["text_secondary"]
    danger = theme["danger"]

    return f"""
    QMainWindow, QDialog {{
        background-color: {bg};
        color: {text};
    }}
    QWidget {{
        color: {text};
    }}
    QPushButton#generateBtn {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {primary}, stop:0.5 {secondary}, stop:1 {tertiary});
        color: white;
        border: none;
        border-radius: 12px;
        padding: 16px 32px;
        font-size: 16px;
        font-weight: bold;
        min-height: 48px;
    }}
    QPushButton#generateBtn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {secondary}, stop:0.5 {tertiary}, stop:1 {primary});
    }}
    QPushButton#generateBtn:disabled {{
        background: {surface_el};
        color: {text_muted};
    }}
    QPushButton {{
        background-color: {surface_el};
        color: {text};
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background-color: {primary};
        color: white;
    }}
    QPushButton:disabled {{
        background-color: {surface};
        color: {text_muted};
    }}
    QLabel {{
        color: {text};
    }}
    QLabel#statusLabel {{
        font-size: 14px;
    }}
    QLabel#pendingLabel {{
        color: {text_muted};
        font-size: 13px;
    }}
    QLabel#sectionLabel {{
        color: {text_muted};
        font-size: 12px;
        font-weight: bold;
        letter-spacing: 1px;
    }}
    QLineEdit, QTextEdit {{
        background-color: rgba(255,255,255,0.05);
        color: {text};
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 10px;
        font-size: 13px;
    }}
    QLineEdit:focus, QTextEdit:focus {{
        border-color: {primary};
    }}
    QListWidget {{
        background-color: rgba(255,255,255,0.03);
        color: {text};
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 4px;
    }}
    QListWidget::item {{
        padding: 10px 12px;
        border-radius: 8px;
        margin: 2px;
    }}
    QListWidget::item:hover {{
        background-color: {surface_el};
    }}
    QListWidget::item:selected {{
        background-color: {primary};
    }}
    QComboBox {{
        background-color: {surface_el};
        color: {text};
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 8px 12px;
    }}
    QScrollBar:vertical {{
        background: {surface};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {surface_el};
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    """
