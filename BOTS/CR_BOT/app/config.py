# app/config.py
import json
from pathlib import Path

DEFAULT_PROXY_URL = "https://crbot-proxy.example.com"
APP_DIR = Path.home() / ".crbot"
CONFIG_FILE = APP_DIR / "config.json"
CACHE_DIR = APP_DIR / "cache"
PROFILE_DIR = APP_DIR / "profile"


def load_config() -> dict:
    """Load local app config. Returns defaults if no config file."""
    defaults = {
        "proxy_url": DEFAULT_PROXY_URL,
        "license_key": "",
        "audio_dir": "",
        "output_dir": str(Path.home() / "Documents" / "CR_BOT"),
        "language": "fr",
    }
    if CONFIG_FILE.exists():
        saved = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        defaults.update(saved)
    return defaults


def save_config(config: dict):
    """Save config to disk."""
    APP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")
