# app/ui/main_window.py
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QCheckBox, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QIcon

from app.branding.models import BrandProfile
from app.pipeline.scanner import AudioScanner
from app.pipeline.orchestrator import PipelineOrchestrator, PipelineResult
from app.ui.progress_widget import ProgressWidget
from app.ui.history_panel import HistoryPanel


class PipelineWorker(QThread):
    """Background thread for pipeline execution."""
    progress = Signal(str, int)  # stage, percent
    finished = Signal(object)   # PipelineResult

    def __init__(self, orchestrator, files, profile):
        super().__init__()
        self._orch = orchestrator
        self._files = files
        self._profile = profile

    def run(self):
        self._orch._on_progress = self.progress.emit
        result = self._orch.run(self._files, self._profile)
        self.finished.emit(result)


class MainWindow(QMainWindow):
    def __init__(self, config: dict, profile: BrandProfile):
        super().__init__()
        self._config = config
        self._profile = profile
        self._worker = None
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(f"CR_BOT — {self._profile.company_name}")
        self.setMinimumSize(500, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Logo
        if self._profile.logo_b64:
            import base64
            logo_label = QLabel()
            pixmap = QPixmap()
            pixmap.loadFromData(base64.b64decode(self._profile.logo_b64))
            logo_label.setPixmap(pixmap.scaledToHeight(48, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)

        # Title
        title = QLabel("Compte Rendu de Réunion")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {self._profile.primary_color};")
        layout.addWidget(title)

        # Generate button
        self._generate_btn = QPushButton("Générer le compte rendu")
        self._generate_btn.setFixedHeight(56)
        self._generate_btn.setStyleSheet("font-size: 16px;")
        self._generate_btn.clicked.connect(self._on_generate)
        layout.addWidget(self._generate_btn)

        # File selection area (hidden until scan)
        self._file_area = QScrollArea()
        self._file_area.setWidgetResizable(True)
        self._file_area.setVisible(False)
        self._file_container = QWidget()
        self._file_layout = QVBoxLayout(self._file_container)
        self._file_area.setWidget(self._file_container)
        layout.addWidget(self._file_area)

        # Confirm button (hidden until scan)
        self._confirm_btn = QPushButton("Lancer le traitement")
        self._confirm_btn.setVisible(False)
        self._confirm_btn.clicked.connect(self._on_confirm)
        layout.addWidget(self._confirm_btn)

        # Progress
        self._progress = ProgressWidget()
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        # Status
        self._status = QLabel("")
        self._status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status)

        # History
        history_label = QLabel("Historique")
        history_label.setStyleSheet("font-size: 12px; opacity: 0.6;")
        layout.addWidget(history_label)

        output_dir = Path(self._config.get("output_dir", ""))
        self._history = HistoryPanel(output_dir)
        layout.addWidget(self._history)

        # Settings button
        settings_btn = QPushButton("Paramètres")
        settings_btn.setStyleSheet("background-color: transparent; color: rgba(255,255,255,0.5); border: 1px solid rgba(255,255,255,0.1);")
        settings_btn.clicked.connect(self._on_settings)
        layout.addWidget(settings_btn)

    def _on_generate(self):
        """Scan for audio files and show checkboxes."""
        audio_dir = Path(self._config.get("audio_dir", ""))
        if not audio_dir.exists():
            QMessageBox.warning(self, "Erreur", f"Dossier audio introuvable : {audio_dir}\nVérifiez les paramètres.")
            return

        output_dir = Path(self._config.get("output_dir", ""))
        scanner = AudioScanner(audio_dir, output_dir / ".history.json")
        files = scanner.scan_unprocessed()

        if not files:
            self._status.setText(f"Aucun fichier audio trouvé dans {audio_dir}")
            return

        groups = scanner.group_by_date(files)
        self._checkboxes = []

        # Clear previous
        while self._file_layout.count():
            child = self._file_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for group in groups:
            for f in group.files:
                cb = QCheckBox(f"{f.name}  ({group.date_str})")
                cb.setChecked(group.is_today)
                cb.setProperty("path", str(f))
                self._file_layout.addWidget(cb)
                self._checkboxes.append(cb)

        self._file_area.setVisible(True)
        self._confirm_btn.setVisible(True)
        self._generate_btn.setVisible(False)

    def _on_confirm(self):
        """Start pipeline on selected files."""
        selected = [
            Path(cb.property("path"))
            for cb in self._checkboxes
            if cb.isChecked()
        ]
        if not selected:
            self._status.setText("Sélectionnez au moins un fichier.")
            return

        self._confirm_btn.setEnabled(False)
        self._progress.setVisible(True)
        self._progress.reset()
        self._status.setText("Traitement en cours...")

        output_dir = Path(self._config.get("output_dir", ""))
        cache_dir = Path(self._config.get("output_dir", "")) / ".crbot" / "cache"

        orch = PipelineOrchestrator(
            proxy_url=self._config["proxy_url"],
            license_key=self._config["license_key"],
            cache_dir=cache_dir,
            output_dir=output_dir,
            context=self._profile.context,
            language=self._config.get("language", "fr"),
        )

        self._worker = PipelineWorker(orch, selected, self._profile)
        self._worker.progress.connect(self._progress.update_stage)
        self._worker.finished.connect(self._on_pipeline_done)
        self._worker.start()

    def _on_pipeline_done(self, result: PipelineResult):
        self._confirm_btn.setEnabled(True)
        self._file_area.setVisible(False)
        self._confirm_btn.setVisible(False)
        self._generate_btn.setVisible(True)

        if result.success:
            self._status.setText(f"CR généré : {result.output_path.name}")
            # Mark files as processed
            audio_dir = Path(self._config.get("audio_dir", ""))
            output_dir = Path(self._config.get("output_dir", ""))
            scanner = AudioScanner(audio_dir, output_dir / ".history.json")
            for cb in self._checkboxes:
                if cb.isChecked():
                    scanner.mark_processed(Path(cb.property("path")))
            self._history.refresh()
        else:
            self._status.setText(f"Erreur : {result.error}")
            QMessageBox.critical(self, "Erreur", f"Le traitement a échoué :\n{result.error}")

    def _on_settings(self):
        from app.ui.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self._config, self)
        if dlg.exec():
            self._config.update(dlg.get_config())
            from app.config import save_config
            save_config(self._config)
            # Update history panel output dir and refresh
            self._history._output_dir = Path(self._config["output_dir"])
            self._history.refresh()
