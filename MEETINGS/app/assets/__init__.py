import base64
from pathlib import Path

ASSETS_DIR = Path(__file__).parent


def load_logo_b64() -> str:
    logo = ASSETS_DIR / "logo-wslo.png"
    if logo.exists():
        return base64.b64encode(logo.read_bytes()).decode("ascii")
    return ""


def load_font_b64(name: str) -> str:
    font = ASSETS_DIR / "fonts" / name
    if font.exists():
        return base64.b64encode(font.read_bytes()).decode("ascii")
    return ""
