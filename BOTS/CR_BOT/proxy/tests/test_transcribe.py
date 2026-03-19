import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
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


class TestTranscribeEndpoint:
    def test_rejects_invalid_license(self, app_client):
        resp = app_client.post(
            "/transcribe",
            data={"license_key": "CRBOT-fake"},
            files={"audio": ("test.mp3", b"fake-audio", "audio/mpeg")},
        )
        assert resp.status_code == 403

    @patch("proxy.routes.transcribe_routes.relay_to_gladia")
    def test_returns_transcript_on_success(self, mock_relay, app_client):
        mock_relay.return_value = {
            "segments": [
                {"start": 0.0, "end": 5.0, "speaker": "Speaker 1", "text": "Bonjour à tous"}
            ],
            "full_text": "[Speaker 1] Bonjour à tous",
            "duration_seconds": 5.0,
        }
        resp = app_client.post(
            "/transcribe",
            data={"license_key": VALID_KEY},
            files={"audio": ("test.mp3", b"fake-audio", "audio/mpeg")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "segments" in data
        assert data["segments"][0]["text"] == "Bonjour à tous"
