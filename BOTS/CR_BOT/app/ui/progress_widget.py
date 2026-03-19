# app/ui/progress_widget.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt


STAGES = [
    ("transcription", "Transcription"),
    ("summarization", "Résumé"),
    ("generation", "Génération"),
]


class ProgressWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._bars = {}
        for key, label in STAGES:
            container = QWidget()
            vlayout = QVBoxLayout(container)
            vlayout.setContentsMargins(0, 0, 0, 0)
            vlayout.setSpacing(4)

            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 11px; opacity: 0.7;")
            vlayout.addWidget(lbl)

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setFixedHeight(6)
            bar.setTextVisible(False)
            vlayout.addWidget(bar)

            layout.addWidget(container)
            self._bars[key] = bar

    def update_stage(self, stage: str, percent: int):
        if stage in self._bars:
            self._bars[stage].setValue(percent)

    def reset(self):
        for bar in self._bars.values():
            bar.setValue(0)
