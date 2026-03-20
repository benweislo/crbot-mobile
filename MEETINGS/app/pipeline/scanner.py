import re
from pathlib import Path

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".wma", ".aac", ".webm"}


def _extract_date(filename: str) -> str:
    m = re.match(r"(\d{4})_(\d{2})_(\d{2})", filename)
    if m:
        return f"{m.group(1)}_{m.group(2)}_{m.group(3)}"
    m = re.match(r"AudioCapturer_(\d{4})(\d{2})(\d{2})", filename)
    if m:
        return f"{m.group(1)}_{m.group(2)}_{m.group(3)}"
    return "unknown"


class AudioScanner:
    def __init__(self, audio_folder: Path, processed: set[str]):
        self._folder = audio_folder
        self._processed = processed

    def scan(self) -> list[Path]:
        if not self._folder.exists():
            return []
        return [
            f for f in sorted(self._folder.iterdir())
            if f.is_file()
            and f.suffix.lower() in SUPPORTED_EXTENSIONS
            and f.name not in self._processed
        ]

    def scan_grouped(self) -> list[dict]:
        files = self.scan()
        if not files:
            return []
        groups: dict[str, list[Path]] = {}
        for f in files:
            date = _extract_date(f.name)
            groups.setdefault(date, []).append(f)
        return [
            {"date": date, "files": sorted(paths, key=lambda p: p.name)}
            for date, paths in sorted(groups.items())
        ]
