import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QFontDatabase, QFont

from app.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Mon CR")
    app.setOrganizationName("wslo.lab")

    # Load Segoe UI Variable or fallback to a clean sans-serif
    app.setFont(QFont("Segoe UI Variable", 10))

    icon_path = Path(__file__).parent / "assets" / "logo-wslo.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
