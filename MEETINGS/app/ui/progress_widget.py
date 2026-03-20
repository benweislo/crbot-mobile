from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt


class ProgressWidget(QWidget):
    """3-step progress indicator: Transcription → Résumé → HTML."""

    STAGES = ["Transcription", "Résumé", "HTML"]

    def __init__(self, theme: dict | None = None, parent=None):
        super().__init__(parent)
        self._current = -1
        self._labels: list[QLabel] = []
        self._dots: list[QLabel] = []
        self._c_done = (theme or {}).get("tertiary", "#2DD4BF")
        self._c_active = (theme or {}).get("primary", "#8B5CF6")
        self._c_text = (theme or {}).get("text_primary", "#EDF0F7")
        self._c_muted = (theme or {}).get("text_secondary", "#4D5575")
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        for i, name in enumerate(self.STAGES):
            dot = QLabel("○")
            dot.setAlignment(Qt.AlignCenter)
            dot.setFixedWidth(20)
            dot.setStyleSheet(f"font-size: 16px; color: {self._c_muted};")
            self._dots.append(dot)
            layout.addWidget(dot)

            label = QLabel(name)
            label.setStyleSheet(f"font-size: 13px; color: {self._c_muted};")
            self._labels.append(label)
            layout.addWidget(label)

            if i < len(self.STAGES) - 1:
                sep = QLabel("→")
                sep.setStyleSheet("color: #4D5575; font-size: 12px;")
                sep.setAlignment(Qt.AlignCenter)
                layout.addWidget(sep)

        layout.addStretch()

    def set_stage(self, index: int):
        self._current = index
        for i, (dot, label) in enumerate(zip(self._dots, self._labels)):
            if i < index:
                dot.setText("●")
                dot.setStyleSheet(f"font-size: 16px; color: {self._c_done};")
                label.setStyleSheet(f"font-size: 13px; color: {self._c_done};")
            elif i == index:
                dot.setText("◉")
                dot.setStyleSheet(f"font-size: 16px; color: {self._c_active};")
                label.setStyleSheet(f"font-size: 13px; color: {self._c_text}; font-weight: bold;")
            else:
                dot.setText("○")
                dot.setStyleSheet(f"font-size: 16px; color: {self._c_muted};")
                label.setStyleSheet(f"font-size: 13px; color: {self._c_muted};")

    def reset(self):
        self.set_stage(-1)
        for dot, label in zip(self._dots, self._labels):
            dot.setText("○")
            dot.setStyleSheet(f"font-size: 16px; color: {self._c_muted};")
            label.setStyleSheet(f"font-size: 13px; color: {self._c_muted};")
