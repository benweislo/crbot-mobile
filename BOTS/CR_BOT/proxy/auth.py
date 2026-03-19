import json
from datetime import date
from pathlib import Path


class LicenseManager:
    def __init__(self, license_file: Path):
        if not license_file.exists():
            raise FileNotFoundError(f"License file not found: {license_file}")
        self._path = license_file
        self._load()

    def _load(self):
        self._licenses = json.loads(self._path.read_text(encoding="utf-8"))

    def validate(self, key: str) -> dict:
        """Validate a license key. Returns dict with 'valid', 'client_id', optionally 'reason'."""
        entry = self._licenses.get(key)
        if entry is None:
            return {"valid": False, "reason": "Unknown license key"}

        if entry.get("status") != "active":
            return {"valid": False, "reason": "License inactive"}

        expiry = entry.get("expiry_date", "")
        if expiry and date.fromisoformat(expiry) < date.today():
            return {"valid": False, "reason": "License expired"}

        return {
            "valid": True,
            "client_id": entry["client_id"],
            "profile_url": entry.get("profile_url", ""),
        }
