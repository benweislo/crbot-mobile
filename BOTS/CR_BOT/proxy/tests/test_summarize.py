import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from pathlib import Path

from proxy.main import create_app


@pytest.fixture
def app_client(sample_license_data, tmp_path):
    path = tmp_path / "licenses.json"
    path.write_text(json.dumps(sample_license_data))
    app = create_app(license_file=path)
    return TestClient(app)


VALID_KEY = "CRBOT-test-1111-2222-333333333333"


class TestSummarizeEndpoint:
    def test_rejects_invalid_license(self, app_client):
        resp = app_client.post(
            "/summarize",
            json={"license_key": "CRBOT-fake", "transcript": "some text"},
        )
        assert resp.status_code == 403

    @patch("proxy.routes.summarize_routes.call_anthropic")
    def test_returns_summary_on_success(self, mock_call, app_client):
        mock_call.return_value = "THÈMES ABORDÉS\n• Budget\n\nACTIONS\n1. Revoir le budget"
        resp = app_client.post(
            "/summarize",
            json={
                "license_key": VALID_KEY,
                "transcript": "[Speaker 1] On doit revoir le budget.",
                "context": "Agence digitale",
                "language": "fr",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "summary" in data
        assert "THÈMES" in data["summary"]

    def test_rejects_empty_transcript(self, app_client):
        resp = app_client.post(
            "/summarize",
            json={"license_key": VALID_KEY, "transcript": ""},
        )
        assert resp.status_code == 422 or resp.status_code == 400
