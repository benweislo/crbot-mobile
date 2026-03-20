import json
import os
from datetime import datetime
from pathlib import Path

from app.config.defaults import DEFAULT_CONFIG


class ConfigManager:
    def __init__(self, root_dir: Path):
        self._root = root_dir
        self._config_path = root_dir / "config.json"
        self._history_path = root_dir / "history.json"

    def load(self) -> dict:
        config = DEFAULT_CONFIG.copy()
        config["theme"] = DEFAULT_CONFIG["theme"].copy()

        if self._config_path.exists():
            try:
                saved = json.loads(self._config_path.read_text(encoding="utf-8"))
                for key, value in saved.items():
                    if key == "theme" and isinstance(value, dict):
                        config["theme"].update(value)
                    else:
                        config[key] = value
            except (json.JSONDecodeError, KeyError):
                pass

        # Fill Gladia key from env if empty
        if not config["gladia_api_key"]:
            env_key = os.environ.get("GLADIA_API_KEY", "")
            if not env_key:
                env_file = Path("C:/Users/User/ENV/.env")
                if env_file.exists():
                    for line in env_file.read_text(encoding="utf-8").splitlines():
                        if line.startswith("GLADIA_API_KEY="):
                            env_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break
            config["gladia_api_key"] = env_key

        # Only save if config file didn't exist (first launch)
        if not self._config_path.exists():
            self.save(config)
        return config

    def save(self, config: dict) -> None:
        self._config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def load_history(self) -> dict:
        if self._history_path.exists():
            try:
                return json.loads(self._history_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        return {"processed": []}

    def _save_history(self, history: dict) -> None:
        self._history_path.write_text(
            json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def add_to_history(self, filename: str, html_output: str) -> None:
        history = self.load_history()
        history["processed"].append({
            "file": filename,
            "processed_at": datetime.now().isoformat(),
            "html_output": html_output,
        })
        self._save_history(history)

    def is_processed(self, filename: str) -> bool:
        history = self.load_history()
        return any(e["file"] == filename for e in history["processed"])
