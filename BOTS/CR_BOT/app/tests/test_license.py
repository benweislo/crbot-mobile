import pytest
import json
from unittest.mock import patch, MagicMock

from app.auth.license import LicenseClient


class TestLicenseClient:
    @patch("app.auth.license.httpx.Client")
    def test_validate_success(self, mock_client_cls):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"valid": True, "client_id": "abc", "profile_url": "https://store/abc"}
        mock_resp.raise_for_status = MagicMock()
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        lc = LicenseClient(proxy_url="https://proxy.example.com")
        result = lc.validate("CRBOT-test-key")
        assert result["valid"] is True
        assert result["client_id"] == "abc"

    @patch("app.auth.license.httpx.Client")
    def test_validate_invalid(self, mock_client_cls):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"valid": False, "reason": "Unknown key"}
        mock_resp.raise_for_status = MagicMock()
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        lc = LicenseClient(proxy_url="https://proxy.example.com")
        result = lc.validate("CRBOT-fake")
        assert result["valid"] is False
