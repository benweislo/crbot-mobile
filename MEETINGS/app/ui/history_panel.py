import re
import webbrowser
from pathlib import Path

from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt


class HistoryPanel(QListWidget):
    """Clickable list of generated CR HTML files."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemDoubleClicked.connect(self._open_html)

    def load(self, html_folder: Path, history: dict):
        self.clear()
        seen_paths: set[str] = set()
        entries: list[tuple[str, str, str]] = []

        for item in history.get("processed", []):
            html_path = item.get("html_output", "")
            if html_path and html_path not in seen_paths:
                seen_paths.add(html_path)
                full = html_folder.parent / html_path if not Path(html_path).is_absolute() else Path(html_path)
                date_key = self._extract_date(full.name)
                entries.append((date_key, full.name, str(full)))

        if html_folder.exists():
            for f in html_folder.glob("*.html"):
                if str(f) not in seen_paths and f.name not in [Path(s).name for s in seen_paths]:
                    date_key = self._extract_date(f.name)
                    entries.append((date_key, f.name, str(f)))

        entries.sort(key=lambda e: e[0], reverse=True)

        for date_key, display, path in entries:
            nice_date = date_key.replace("_", "-") if date_key != "0000_00_00" else "?"
            label = re.sub(r"^\d{4}_\d{2}_\d{2}_CR_?", "", Path(display).stem)
            label = label.replace("_", " ").strip() or "réunion"
            text = f"{nice_date} — {label}"

            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, path)
            self.addItem(item)

    def _extract_date(self, filename: str) -> str:
        m = re.match(r"(\d{4})_(\d{2})_(\d{2})", filename)
        if m:
            return f"{m.group(1)}_{m.group(2)}_{m.group(3)}"
        return "0000_00_00"

    def _open_html(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        if path and Path(path).exists():
            webbrowser.open(Path(path).as_uri())
