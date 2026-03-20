from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QFileDialog, QComboBox, QGroupBox, QFormLayout, QColorDialog,
    QTabWidget, QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.ui.history_panel import HistoryPanel
from app.config.manager import ConfigManager


class SettingsDialog(QDialog):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self._config = config.copy()
        self._config["theme"] = config.get("theme", {}).copy()
        self.setWindowTitle("Paramètres")
        self.setMinimumWidth(540)
        self.setMinimumHeight(640)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Tabs: Paramètres | Historique
        tabs = QTabWidget()
        layout.addWidget(tabs, stretch=1)

        # --- Tab 1: Settings ---
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_layout.setSpacing(12)
        tabs.addTab(settings_tab, "Paramètres")

        # --- Tab 2: Historique ---
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        self._history = HistoryPanel()
        history_layout.addWidget(self._history)
        tabs.addTab(history_tab, "Historique")

        # Load history data
        config_mgr = ConfigManager(Path(self._config.get("audio_folder", ".")))
        history_data = config_mgr.load_history()
        html_folder = Path(self._config.get("output_folder", "."))
        self._history.load(html_folder, history_data)

        # Folders group (on settings tab)
        folders_group = QGroupBox("Dossiers")
        folders_layout = QFormLayout()

        self._audio_edit = QLineEdit(self._config.get("audio_folder", ""))
        audio_row = QHBoxLayout()
        audio_row.addWidget(self._audio_edit)
        audio_btn = QPushButton("...")
        audio_btn.setFixedWidth(32)
        audio_btn.clicked.connect(lambda: self._browse("audio_folder", self._audio_edit))
        audio_row.addWidget(audio_btn)
        folders_layout.addRow("Dossier audio:", audio_row)

        self._output_edit = QLineEdit(self._config.get("output_folder", ""))
        output_row = QHBoxLayout()
        output_row.addWidget(self._output_edit)
        output_btn = QPushButton("...")
        output_btn.setFixedWidth(32)
        output_btn.clicked.connect(lambda: self._browse("output_folder", self._output_edit))
        output_row.addWidget(output_btn)
        folders_layout.addRow("Dossier output:", output_row)

        folders_group.setLayout(folders_layout)
        settings_layout.addWidget(folders_group)

        # Summary group
        summary_group = QGroupBox("Résumé")
        summary_layout = QVBoxLayout()
        summary_layout.addWidget(QLabel("Prompt système:"))
        self._prompt_edit = QTextEdit()
        self._prompt_edit.setPlainText(self._config.get("system_prompt", ""))
        self._prompt_edit.setMinimumHeight(120)
        summary_layout.addWidget(self._prompt_edit)

        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("Langue:"))
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(["fr", "en", "es"])
        self._lang_combo.setCurrentText(self._config.get("language", "fr"))
        lang_row.addWidget(self._lang_combo)
        lang_row.addStretch()
        summary_layout.addLayout(lang_row)

        summary_group.setLayout(summary_layout)
        settings_layout.addWidget(summary_group)

        # Theme group
        theme_group = QGroupBox("Apparence")
        theme_layout = QFormLayout()
        theme = self._config.get("theme", {})

        self._color_btns = {}
        for key, label in [("primary", "Couleur primaire"), ("secondary", "Couleur secondaire"), ("tertiary", "Couleur tertiaire"), ("background", "Background"), ("text_primary", "Texte")]:
            btn = QPushButton(theme.get(key, "#000"))
            btn.setFixedWidth(120)
            color = theme.get(key, "#000")
            btn.setStyleSheet(f"background-color: {color}; color: white; border-radius: 4px; padding: 4px;")
            btn.clicked.connect(lambda checked=False, k=key, b=btn: self._pick_color(k, b))
            self._color_btns[key] = btn
            theme_layout.addRow(label + ":", btn)

        self._logo_edit = QLineEdit(self._config.get("logo_path", ""))
        logo_row = QHBoxLayout()
        logo_row.addWidget(self._logo_edit)
        logo_btn = QPushButton("Changer")
        logo_btn.clicked.connect(self._pick_logo)
        logo_row.addWidget(logo_btn)
        theme_layout.addRow("Logo:", logo_row)

        theme_group.setLayout(theme_layout)
        settings_layout.addWidget(theme_group)

        # API group
        api_group = QGroupBox("API")
        api_layout = QFormLayout()
        self._gladia_edit = QLineEdit(self._config.get("gladia_api_key", ""))
        self._gladia_edit.setEchoMode(QLineEdit.Password)
        api_layout.addRow("Clé Gladia:", self._gladia_edit)
        api_group.setLayout(api_layout)
        settings_layout.addWidget(api_group)

        # Buttons
        btn_layout = QHBoxLayout()
        reset_btn = QPushButton("Réinitialiser")
        reset_btn.clicked.connect(self._reset)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        save_btn = QPushButton("Sauvegarder")
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _browse(self, key: str, edit: QLineEdit):
        folder = QFileDialog.getExistingDirectory(self, "Choisir un dossier", edit.text())
        if folder:
            edit.setText(folder)

    def _pick_color(self, key: str, btn: QPushButton):
        current = QColor(self._config["theme"].get(key, "#000"))
        color = QColorDialog.getColor(current, self, f"Choisir {key}")
        if color.isValid():
            hex_color = color.name()
            self._config["theme"][key] = hex_color
            btn.setText(hex_color)
            btn.setStyleSheet(f"background-color: {hex_color}; color: white; border-radius: 4px; padding: 4px;")

    def _pick_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir un logo", "", "Images (*.png *.jpg *.svg)")
        if path:
            self._logo_edit.setText(path)

    def _reset(self):
        from app.config.defaults import DEFAULT_CONFIG
        self._config = DEFAULT_CONFIG.copy()
        self._config["theme"] = DEFAULT_CONFIG["theme"].copy()
        self._audio_edit.setText(self._config.get("audio_folder", ""))
        self._output_edit.setText(self._config.get("output_folder", ""))
        self._prompt_edit.setPlainText(self._config.get("system_prompt", ""))
        self._lang_combo.setCurrentText(self._config.get("language", "fr"))
        self._gladia_edit.setText("")
        self._logo_edit.setText(self._config.get("logo_path", ""))
        for key, btn in self._color_btns.items():
            color = self._config["theme"].get(key, "#000")
            btn.setText(color)
            btn.setStyleSheet(f"background-color: {color}; color: white; border-radius: 4px; padding: 4px;")

    def get_config(self) -> dict:
        self._config["audio_folder"] = self._audio_edit.text()
        self._config["output_folder"] = self._output_edit.text()
        self._config["system_prompt"] = self._prompt_edit.toPlainText()
        self._config["language"] = self._lang_combo.currentText()
        self._config["gladia_api_key"] = self._gladia_edit.text()
        self._config["logo_path"] = self._logo_edit.text()
        return self._config
