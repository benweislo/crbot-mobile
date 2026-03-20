import webbrowser
import tempfile
import os
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QFrame,
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QPixmap, QPainter, QColor, QIcon, QPainterPath

from app.config.manager import ConfigManager
from app.pipeline.scanner import AudioScanner
from app.pipeline.orchestrator import PipelineOrchestrator, PipelineResult
from app.ui.progress_widget import ProgressWidget
from app.ui.settings_dialog import SettingsDialog
from app.ui.theme import build_stylesheet
from app.assets import load_logo_b64, load_font_b64


STAGE_INDEX = {"transcription": 0, "summarization": 1, "generation": 2}

GEAR_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#8891AB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
<circle cx="12" cy="12" r="3"/>
<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
</svg>"""


def _make_circle_pixmap(path: Path, size: int) -> QPixmap | None:
    """Load an image and crop it to a perfect circle with transparency."""
    if not path.exists():
        return None
    src = QPixmap(str(path)).scaled(size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    result = QPixmap(size, size)
    result.fill(Qt.transparent)
    painter = QPainter(result)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
    clip = QPainterPath()
    clip.addEllipse(0, 0, size, size)
    painter.setClipPath(clip)
    painter.drawPixmap(0, 0, src)
    painter.end()
    return result


class ClickableLabel(QLabel):
    """QLabel that emits a click signal."""
    from PySide6.QtCore import Signal as _Sig
    clicked = _Sig()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class BackgroundWidget(QWidget):
    """Central widget with background image large (fills) + dark overlay."""

    def __init__(self, bg_path: str, parent=None):
        super().__init__(parent)
        self._bg_pixmap = None
        if Path(bg_path).exists():
            self._bg_pixmap = QPixmap(bg_path)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.fillRect(self.rect(), QColor("#0B0F1A"))
        if self._bg_pixmap:
            scaled = self._bg_pixmap.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.setOpacity(0.45)
            painter.drawPixmap(x, y, scaled)
            painter.setOpacity(1.0)
        painter.end()
        super().paintEvent(event)


class GlassFrame(QFrame):
    """Frosted glass container."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            GlassFrame {
                background-color: rgba(11, 15, 26, 0.65);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 14px;
            }
        """)


class PipelineWorker(QThread):
    """Runs pipeline in background thread."""
    stage_changed = Signal(str, int)
    progress = Signal(str)
    session_complete = Signal(str, list)
    error = Signal(str, str)
    finished_all = Signal()

    def __init__(self, config: dict, sessions: list[dict]):
        super().__init__()
        self._config = config
        self._sessions = sessions

    def run(self):
        config = self._config.copy()
        config["_logo_b64"] = load_logo_b64()
        config["_font_regular_b64"] = load_font_b64("DMSans-Regular.ttf")
        config["_font_bold_b64"] = load_font_b64("DMSans-Bold.ttf")

        def on_progress(stage, msg):
            idx = STAGE_INDEX.get(stage, 0)
            self.stage_changed.emit(stage, idx)
            self.progress.emit(msg)

        orch = PipelineOrchestrator(config=config, on_progress=on_progress)

        for session in self._sessions:
            result = orch.run(session["files"], date_str=session["date"])
            if result.success and result.output_path:
                filenames = [f.name for f in session["files"]]
                self.session_complete.emit(str(result.output_path), filenames)
            elif not result.success:
                self.error.emit(result.stage_failed, result.error)

        self.finished_all.emit()


class MainWindow(QMainWindow):
    WINDOW_WIDTH = 500
    WINDOW_HEIGHT = 440

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mon CR — wslo.lab")
        self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        self._config_mgr = ConfigManager(Path(__file__).parent.parent.parent)
        self._config = self._config_mgr.load()
        self._worker: PipelineWorker | None = None
        self._pending_sessions: list[dict] = []

        # Load circular button pixmaps
        assets = Path(__file__).parent.parent / "assets"
        self._btn_go_pixmap = _make_circle_pixmap(assets / "btn_go.png", 150)
        self._btn_go_active_pixmap = _make_circle_pixmap(assets / "btn_go_active.png", 150)

        self._init_ui()
        self._apply_theme()
        self._refresh_state()

    def _init_ui(self):
        bg_path = str(Path(__file__).parent.parent / "assets" / "background-neon.png")
        central = BackgroundWidget(bg_path)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        # Header: logo + settings gear
        header = QHBoxLayout()
        self._logo_label = QLabel()
        logo_path = Path(__file__).parent.parent / "assets" / "logo-wslo.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path)).scaledToHeight(56, Qt.SmoothTransformation)
            self._logo_label.setPixmap(pixmap)
        header.addWidget(self._logo_label)
        header.addStretch()

        settings_btn = QPushButton()
        settings_btn.setObjectName("settingsBtn")
        settings_btn.setFixedSize(40, 40)
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.setToolTip("Paramètres")
        svg_path = os.path.join(tempfile.gettempdir(), "moncr_gear.svg")
        with open(svg_path, "w") as f:
            f.write(GEAR_SVG)
        settings_btn.setIcon(QIcon(svg_path))
        settings_btn.setIconSize(QSize(22, 22))
        settings_btn.clicked.connect(self._open_settings)
        header.addWidget(settings_btn)
        layout.addLayout(header)

        # Status
        self._status_label = QLabel("● Prêt")
        self._status_label.setObjectName("statusLabel")
        layout.addWidget(self._status_label)

        self._pending_label = QLabel("Fichiers en attente: 0")
        self._pending_label.setObjectName("pendingLabel")
        layout.addWidget(self._pending_label)

        # GO button — pure circular image via QLabel (no button chrome)
        self._go_label = ClickableLabel()
        self._go_label.setCursor(Qt.PointingHandCursor)
        self._go_label.setAlignment(Qt.AlignCenter)
        self._go_label.setFixedSize(150, 150)
        if self._btn_go_pixmap:
            self._go_label.setPixmap(self._btn_go_pixmap)
        self._go_label.clicked.connect(self._start_pipeline)
        layout.addWidget(self._go_label, alignment=Qt.AlignCenter)

        # Progress inside glass frame
        self._glass_frame = GlassFrame()
        glass_layout = QVBoxLayout(self._glass_frame)
        glass_layout.setContentsMargins(16, 12, 16, 12)
        glass_layout.setSpacing(8)

        progress_label = QLabel("PROGRESSION")
        progress_label.setObjectName("sectionLabel")
        glass_layout.addWidget(progress_label)

        self._progress = ProgressWidget(theme=self._config.get("theme"))
        glass_layout.addWidget(self._progress)

        layout.addWidget(self._glass_frame)
        layout.addStretch()

    def _set_go_button_state(self, active: bool):
        pixmap = self._btn_go_active_pixmap if active else self._btn_go_pixmap
        if pixmap:
            self._go_label.setPixmap(pixmap)

    def _apply_theme(self):
        theme = self._config.get("theme", {})
        if theme:
            self.setStyleSheet(build_stylesheet(theme))

    def _refresh_state(self):
        history = self._config_mgr.load_history()
        processed = {e["file"] for e in history.get("processed", [])}

        audio_folder = Path(self._config["audio_folder"])
        scanner = AudioScanner(audio_folder, processed)
        self._pending_sessions = scanner.scan_grouped()

        total_files = sum(len(s["files"]) for s in self._pending_sessions)
        self._pending_label.setText(f"Fichiers en attente: {total_files}")

        if total_files == 0:
            self._status_label.setText("● Tout est à jour")
            self._status_label.setStyleSheet("color: #2DD4BF;")
        else:
            self._status_label.setText("● Prêt")
            self._status_label.setStyleSheet("color: #2DD4BF;")

    def _start_pipeline(self):
        if not self._pending_sessions:
            self._status_label.setText("● Tout est à jour")
            return

        if not self._config.get("gladia_api_key"):
            QMessageBox.warning(self, "API manquante", "Configurez la clé Gladia dans les paramètres.")
            self._open_settings()
            return

        self._go_label.setEnabled(False)
        self._set_go_button_state(True)
        self._status_label.setText("● En cours...")
        self._status_label.setStyleSheet("color: #10B981;")

        self._worker = PipelineWorker(self._config, self._pending_sessions)
        self._worker.stage_changed.connect(self._on_stage_changed)
        self._worker.progress.connect(self._on_progress)
        self._worker.session_complete.connect(self._on_session_complete)
        self._worker.error.connect(self._on_error)
        self._worker.finished_all.connect(self._on_finished)
        self._worker.start()

    def _on_stage_changed(self, stage: str, index: int):
        self._progress.set_stage(index)

    def _on_progress(self, message: str):
        self._status_label.setText(f"● {message}")

    def _on_session_complete(self, html_path: str, filenames: list):
        for name in filenames:
            self._config_mgr.add_to_history(name, html_path)
        webbrowser.open(Path(html_path).as_uri())

    def _on_error(self, stage: str, message: str):
        self._status_label.setText(f"● Erreur ({stage})")
        self._status_label.setStyleSheet("color: #F87171;")
        self._set_go_button_state(False)
        self._go_label.setEnabled(True)
        QMessageBox.critical(self, f"Erreur — {stage}", message)

    def _on_finished(self):
        self._go_label.setEnabled(True)
        self._set_go_button_state(False)
        self._progress.reset()
        self._worker = None
        self._refresh_state()

    def _open_settings(self):
        dlg = SettingsDialog(self._config, self)
        if dlg.exec():
            self._config = dlg.get_config()
            self._config_mgr.save(self._config)
            self._apply_theme()
            self._refresh_state()
