# app/ui/license_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt

from app.auth.license import LicenseClient


class LicenseDialog(QDialog):
    def __init__(self, proxy_url: str, parent=None):
        super().__init__(parent)
        self._proxy_url = proxy_url
        self._result = None
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("CR_BOT — Activation")
        self.setFixedSize(420, 220)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(32, 32, 32, 32)

        title = QLabel("Entrez votre clé de licence")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self._key_input = QLineEdit()
        self._key_input.setPlaceholderText("CRBOT-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        layout.addWidget(self._key_input)

        self._activate_btn = QPushButton("Activer")
        self._activate_btn.clicked.connect(self._on_activate)
        layout.addWidget(self._activate_btn)

        self._status = QLabel("")
        self._status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status)

    def _on_activate(self):
        key = self._key_input.text().strip()
        if not key:
            self._status.setText("Veuillez entrer une clé.")
            return

        self._activate_btn.setEnabled(False)
        self._status.setText("Vérification...")

        try:
            client = LicenseClient(self._proxy_url)
            result = client.validate(key)
            if result.get("valid"):
                self._result = {"key": key, **result}
                self.accept()
            else:
                reason = result.get("reason", "Clé invalide")
                self._status.setText(f"Erreur : {reason}")
        except Exception as e:
            self._status.setText("Impossible de se connecter au serveur.")
        finally:
            self._activate_btn.setEnabled(True)

    def get_result(self) -> dict | None:
        return self._result
