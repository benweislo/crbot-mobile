import webbrowser
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap

from app.config.manager import ConfigManager
from app.pipeline.scanner import AudioScanner
from app.pipeline.orchestrator import PipelineOrchestrator, PipelineResult
from app.ui.progress_widget import ProgressWidget
from app.ui.history_panel import HistoryPanel
from app.ui.settings_dialog import SettingsDialog
from app.ui.theme import build_stylesheet
from app.assets import load_logo_b64, load_font_b64


STAGE_INDEX = {"transcription": 0, "summarization": 1, "generation": 2}


class PipelineWorker(QThread):
    """Runs pipeline in background thread."""
    stage_changed = Signal(str, int)
    progress = Signal(str)
    session_complete = Signal(str, list)  # html_path, [filenames]
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mon CR — wslo.lab")
        self.setMinimumSize(480, 640)

        self._config_mgr = ConfigManager(Path(__file__).parent.parent.parent)
        self._config = self._config_mgr.load()
        self._worker: PipelineWorker | None = None
        self._pending_sessions: list[dict] = []

        self._init_ui()
        self._apply_theme()
        self._refresh_state()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header: logo + settings
        header = QHBoxLayout()
        self._logo_label = QLabel()
        logo_path = Path(__file__).parent.parent / "assets" / "logo-wslo.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path)).scaledToHeight(48, Qt.SmoothTransformation)
            self._logo_label.setPixmap(pixmap)
        header.addWidget(self._logo_label)
        header.addStretch()

        settings_btn = QPushButton("\u2699")
        settings_btn.setFixedSize(36, 36)
        settings_btn.clicked.connect(self._open_settings)
        header.addWidget(settings_btn)
        layout.addLayout(header)

        # Separator
        sep = QLabel()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: rgba(255,255,255,0.06);")
        layout.addWidget(sep)

        # Status
        self._status_label = QLabel("\u25cf Pr\u00eat")
        self._status_label.setObjectName("statusLabel")
        layout.addWidget(self._status_label)

        self._pending_label = QLabel("Fichiers en attente: 0")
        self._pending_label.setObjectName("pendingLabel")
        layout.addWidget(self._pending_label)

        # Generate button
        self._generate_btn = QPushButton("G\u00e9n\u00e9rer CR")
        self._generate_btn.setObjectName("generateBtn")
        self._generate_btn.setCursor(Qt.PointingHandCursor)
        self._generate_btn.clicked.connect(self._start_pipeline)
        layout.addWidget(self._generate_btn)

        # Progress
        progress_label = QLabel("PROGRESSION")
        progress_label.setObjectName("sectionLabel")
        layout.addWidget(progress_label)
        self._progress = ProgressWidget(theme=self._config.get("theme"))
        layout.addWidget(self._progress)

        # History
        history_label = QLabel("HISTORIQUE")
        history_label.setObjectName("sectionLabel")
        layout.addWidget(history_label)
        self._history = HistoryPanel()
        layout.addWidget(self._history, stretch=1)

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
            self._status_label.setText("\u25cf Tout est \u00e0 jour")
            self._status_label.setStyleSheet("color: #2DD4BF;")
        else:
            self._status_label.setText("\u25cf Pr\u00eat")
            self._status_label.setStyleSheet("color: #2DD4BF;")

        html_folder = Path(self._config["output_folder"])
        self._history.load(html_folder, history)

    def _start_pipeline(self):
        if not self._pending_sessions:
            self._status_label.setText("\u25cf Tout est \u00e0 jour")
            return

        if not self._config.get("gladia_api_key"):
            QMessageBox.warning(self, "API manquante", "Configurez la cl\u00e9 Gladia dans les param\u00e8tres.")
            self._open_settings()
            return

        self._generate_btn.setEnabled(False)
        self._status_label.setText("\u25cf En cours...")
        self._status_label.setStyleSheet("color: #8B5CF6;")

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
        self._status_label.setText(f"\u25cf {message}")

    def _on_session_complete(self, html_path: str, filenames: list):
        for name in filenames:
            self._config_mgr.add_to_history(name, html_path)
        webbrowser.open(Path(html_path).as_uri())

    def _on_error(self, stage: str, message: str):
        self._status_label.setText(f"\u25cf Erreur ({stage})")
        self._status_label.setStyleSheet("color: #F87171;")
        QMessageBox.critical(self, f"Erreur \u2014 {stage}", message)

    def _on_finished(self):
        self._generate_btn.setEnabled(True)
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
