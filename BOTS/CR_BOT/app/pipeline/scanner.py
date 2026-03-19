import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".wma", ".aac", ".webm"}


@dataclass
class AudioGroup:
    date_str: str
    files: list[Path] = field(default_factory=list)
    is_today: bool = False


class AudioScanner:
    def __init__(self, audio_dir: Path, history_file: Path):
        self._audio_dir = audio_dir
        self._history_file = history_file
        self._processed: set[str] = set()
        self._load_history()

    def _load_history(self):
        if self._history_file.exists():
            data = json.loads(self._history_file.read_text(encoding="utf-8"))
            self._processed = set(data.get("processed", []))

    def _save_history(self):
        self._history_file.parent.mkdir(parents=True, exist_ok=True)
        self._history_file.write_text(
            json.dumps({"processed": sorted(self._processed)}),
            encoding="utf-8",
        )

    def scan_unprocessed(self) -> list[Path]:
        files = []
        for f in sorted(self._audio_dir.iterdir()):
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
                if str(f) not in self._processed:
                    files.append(f)
        return files

    def mark_processed(self, path: Path):
        self._processed.add(str(path))
        self._save_history()

    def group_by_date(self, files: list[Path]) -> list[AudioGroup]:
        groups: dict[str, AudioGroup] = {}
        today_str = date.today().strftime("%d/%m/%Y")

        for f in files:
            date_str = self._extract_date(f)
            if date_str not in groups:
                groups[date_str] = AudioGroup(
                    date_str=date_str,
                    is_today=(date_str == today_str),
                )
            groups[date_str].files.append(f)

        for g in groups.values():
            g.files.sort(key=lambda p: p.name)

        return sorted(groups.values(), key=lambda g: g.date_str, reverse=True)

    def _extract_date(self, path: Path) -> str:
        name = path.name

        m = re.match(r"(\d{4})_(\d{2})_(\d{2})", name)
        if m:
            return f"{m.group(3)}/{m.group(2)}/{m.group(1)}"

        m = re.match(r"AudioCapturer_(\d{4})(\d{2})(\d{2})", name)
        if m:
            return f"{m.group(3)}/{m.group(2)}/{m.group(1)}"

        from datetime import datetime
        mtime = path.stat().st_mtime
        return datetime.fromtimestamp(mtime).strftime("%d/%m/%Y")
