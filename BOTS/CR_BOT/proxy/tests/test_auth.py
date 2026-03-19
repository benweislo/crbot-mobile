import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# TestLicenseManager — unit tests
# ---------------------------------------------------------------------------

class TestLicenseManager:
    def _make_license_file(self, tmp_path, data):
        """Write sample_license_data to a temp JSON file and return the Path."""
        lf = tmp_path / "licenses.json"
        lf.write_text(json.dumps(data), encoding="utf-8")
        return lf

    def test_valid_active_license(self, tmp_path, sample_license_data):
        from proxy.auth import LicenseManager

        lf = self._make_license_file(tmp_path, sample_license_data)
        mgr = LicenseManager(lf)
        result = mgr.validate("CRBOT-test-1111-2222-333333333333")

        assert result["valid"] is True
        assert result["client_id"] == "client_abc"

    def test_expired_license(self, tmp_path, sample_license_data):
        from proxy.auth import LicenseManager

        lf = self._make_license_file(tmp_path, sample_license_data)
        mgr = LicenseManager(lf)
        result = mgr.validate("CRBOT-test-expired-0000-000000000000")

        assert result["valid"] is False
        assert "expired" in result["reason"].lower()

    def test_inactive_license(self, tmp_path, sample_license_data):
        from proxy.auth import LicenseManager

        lf = self._make_license_file(tmp_path, sample_license_data)
        mgr = LicenseManager(lf)
        result = mgr.validate("CRBOT-test-inactive-0000-000000000000")

        assert result["valid"] is False

    def test_unknown_key(self, tmp_path, sample_license_data):
        from proxy.auth import LicenseManager

        lf = self._make_license_file(tmp_path, sample_license_data)
        mgr = LicenseManager(lf)
        result = mgr.validate("CRBOT-does-not-exist")

        assert result["valid"] is False

    def test_missing_file_raises(self, tmp_path):
        from proxy.auth import LicenseManager

        missing = tmp_path / "no_such_file.json"
        with pytest.raises(FileNotFoundError):
            LicenseManager(missing)


# ---------------------------------------------------------------------------
# TestAuthEndpoint — integration tests
# ---------------------------------------------------------------------------

class TestAuthEndpoint:
    def _make_client(self, tmp_path, sample_license_data):
        """Build a TestClient with a real license file."""
        lf = tmp_path / "licenses.json"
        lf.write_text(json.dumps(sample_license_data), encoding="utf-8")

        from proxy.main import create_app
        app = create_app(license_file=lf)
        return TestClient(app)

    def test_validate_valid_key(self, tmp_path, sample_license_data):
        client = self._make_client(tmp_path, sample_license_data)
        response = client.post(
            "/auth/validate",
            json={"license_key": "CRBOT-test-1111-2222-333333333333"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True

    def test_validate_invalid_key(self, tmp_path, sample_license_data):
        client = self._make_client(tmp_path, sample_license_data)
        response = client.post(
            "/auth/validate",
            json={"license_key": "CRBOT-does-not-exist"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
