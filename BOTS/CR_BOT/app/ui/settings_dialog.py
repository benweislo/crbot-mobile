# app/ui/settings_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QComboBox
)


class SettingsDialog(QDialog):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self._config = dict(config)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Paramètres")
        self.setFixedSize(500, 300)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        # Audio folder
        layout.addWidget(QLabel("Dossier source audio :"))
        audio_row = QHBoxLayout()
        self._audio_input = QLineEdit(self._config.get("audio_dir", ""))
        audio_row.addWidget(self._audio_input)
        audio_browse = QPushButton("Parcourir")
        audio_browse.clicked.connect(lambda: self._browse(self._audio_input))
        audio_row.addWidget(audio_browse)
        layout.addLayout(audio_row)

        # Output folder
        layout.addWidget(QLabel("Dossier de sortie CR :"))
        output_row = QHBoxLayout()
        self._output_input = QLineEdit(self._config.get("output_dir", ""))
        output_row.addWidget(self._output_input)
        output_browse = QPushButton("Parcourir")
        output_browse.clicked.connect(lambda: self._browse(self._output_input))
        output_row.addWidget(output_browse)
        layout.addLayout(output_row)

        # Language
        layout.addWidget(QLabel("Langue des réunions :"))
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(["fr", "en", "es"])
        current = self._config.get("language", "fr")
        idx = self._lang_combo.findText(current)
        if idx >= 0:
            self._lang_combo.setCurrentIndex(idx)
        layout.addWidget(self._lang_combo)

        # Save button
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self._on_save)
        layout.addWidget(save_btn)

    def _browse(self, line_edit: QLineEdit):
        folder = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier")
        if folder:
            line_edit.setText(folder)

    def _on_save(self):
        self._config["audio_dir"] = self._audio_input.text().strip()
        self._config["output_dir"] = self._output_input.text().strip()
        self._config["language"] = self._lang_combo.currentText()
        self.accept()

    def get_config(self) -> dict:
        return self._config
