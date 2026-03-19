# app/main.py
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.config import load_config, save_config, PROFILE_DIR, CACHE_DIR
from app.branding.models import BrandProfile
from app.branding.profile import ProfileManager
from app.ui.license_dialog import LicenseDialog
from app.ui.main_window import MainWindow
from app.ui.theme import build_stylesheet


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CR_BOT")

    config = load_config()
    profile_mgr = ProfileManager(cache_dir=PROFILE_DIR)

    # First launch: license activation
    if not config.get("license_key"):
        dialog = LicenseDialog(proxy_url=config["proxy_url"])
        if dialog.exec():
            result = dialog.get_result()
            config["license_key"] = result["key"]
            # Download branding profile
            if "profile_url" in result:
                profile_mgr.download_and_cache(result["profile_url"])
            save_config(config)
        else:
            sys.exit(0)

    # Load profile
    profile = profile_mgr.load_cached()
    if profile is None:
        profile = BrandProfile()  # Use defaults if no profile cached

    # Apply theme
    app.setStyleSheet(build_stylesheet(profile))

    # Show main window
    window = MainWindow(config, profile)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
