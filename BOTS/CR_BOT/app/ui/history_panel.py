# app/ui/history_panel.py
import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt


class HistoryPanel(QListWidget):
    def __init__(self, output_dir: Path, parent=None):
        super().__init__(parent)
        self._output_dir = output_dir
        self.itemDoubleClicked.connect(self._on_open)
        self.refresh()

    def refresh(self):
        """Reload the list of CR HTML files."""
        self.clear()
        if not self._output_dir.exists():
            return
        files = sorted(
            self._output_dir.glob("*.html"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        for f in files:
            item = QListWidgetItem(f.name)
            item.setData(Qt.UserRole, str(f))
            self.addItem(item)

    def _on_open(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
