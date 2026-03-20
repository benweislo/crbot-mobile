from unittest.mock import patch, MagicMock
from pathlib import Path
from app.pipeline.transcriber import GladiaTranscriber


def _mock_audio(tmp_path) -> Path:
    p = tmp_path / "test.mp3"
    p.write_bytes(b"\x00" * 100)
    return p


def test_transcribe_returns_structured_result(tmp_path):
    audio = _mock_audio(tmp_path)
    transcriber = GladiaTranscriber(api_key="fake-key")

    mock_upload = MagicMock()
    mock_upload.status_code = 200
    mock_upload.json.return_value = {"audio_url": "https://gladia.io/fake"}

    mock_start = MagicMock()
    mock_start.status_code = 201
    mock_start.json.return_value = {"result_url": "https://gladia.io/results/1"}

    mock_poll = MagicMock()
    mock_poll.json.return_value = {
        "status": "done",
        "result": {
            "transcription": {
                "utterances": [
                    {"speaker": 1, "text": "Bonjour", "start": 0.0, "end": 1.0},
                    {"speaker": 2, "text": "Salut", "start": 1.0, "end": 2.0},
                ]
            }
        },
    }

    with patch("app.pipeline.transcriber.requests") as mock_req:
        mock_req.post.side_effect = [mock_upload, mock_start]
        mock_req.get.return_value = mock_poll
        result = transcriber.transcribe(audio)

    assert "[Speaker 1] Bonjour" in result["full_text"]
    assert "[Speaker 2] Salut" in result["full_text"]
    assert len(result["segments"]) == 2
    assert result["segments"][0]["start"] == 0.0


def test_transcribe_raises_on_upload_failure(tmp_path):
    audio = _mock_audio(tmp_path)
    transcriber = GladiaTranscriber(api_key="fake-key")

    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Server error"

    with patch("app.pipeline.transcriber.requests") as mock_req:
        mock_req.post.return_value = mock_resp
        try:
            transcriber.transcribe(audio)
            assert False, "Should have raised"
        except RuntimeError as e:
            assert "Upload failed" in str(e)
