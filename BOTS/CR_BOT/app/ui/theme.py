# app/ui/theme.py
from app.branding.models import BrandProfile


def build_stylesheet(profile: BrandProfile) -> str:
    """Generate QSS stylesheet from brand profile."""
    return f"""
    QMainWindow, QDialog {{
        background-color: {profile.background_color};
        color: {profile.text_color};
    }}
    QPushButton {{
        background-color: {profile.primary_color};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {profile.secondary_color};
    }}
    QPushButton:disabled {{
        background-color: #555;
        color: #888;
    }}
    QLabel {{
        color: {profile.text_color};
    }}
    QLineEdit {{
        background-color: rgba(255,255,255,0.05);
        color: {profile.text_color};
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 6px;
        padding: 8px;
    }}
    QListWidget {{
        background-color: rgba(255,255,255,0.03);
        color: {profile.text_color};
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
    }}
    QListWidget::item {{
        padding: 8px;
    }}
    QListWidget::item:selected {{
        background-color: {profile.primary_color};
    }}
    QProgressBar {{
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 4px;
        text-align: center;
        color: {profile.text_color};
    }}
    QProgressBar::chunk {{
        background-color: {profile.primary_color};
        border-radius: 3px;
    }}
    """
