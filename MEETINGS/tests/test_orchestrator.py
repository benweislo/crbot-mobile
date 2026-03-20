import re
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.pipeline.orchestrator import PipelineOrchestrator, PipelineResult
from app.config.defaults import DEFAULT_CONFIG


def _mock_audio(tmp_path, name="test.mp3") -> Path:
    p = tmp_path / name
    p.write_bytes(b"\x00" * 100)
    return p


def test_pipeline_result_dataclass():
    r = PipelineResult(success=True, output_path=Path("test.html"))
    assert r.success
    r2 = PipelineResult(success=False, error="fail", stage_failed="transcription")
    assert not r2.success


def test_orchestrator_runs_all_stages(tmp_path):
    config = DEFAULT_CONFIG.copy()
    config["transcript_folder"] = str(tmp_path / "output")
    config["cr_folder"] = str(tmp_path / "CR")
    config["output_folder"] = str(tmp_path / "html")
    config["gladia_api_key"] = "fake"
    config["theme"] = DEFAULT_CONFIG["theme"].copy()

    progress_calls = []
    orch = PipelineOrchestrator(
        config=config,
        on_progress=lambda stage, msg: progress_calls.append((stage, msg)),
    )

    audio = _mock_audio(tmp_path)
    with patch.object(orch._transcriber, "transcribe", return_value={"full_text": "Speaker 1 text", "segments": [], "duration": 60.0}):
        with patch.object(orch._summarizer, "summarize", return_value="COMPTE RENDU\nTest"):
            with patch.object(orch._html_gen, "generate"):
                result = orch.run([audio], date_str="2026_03_20")

    assert result.success
    assert any("transcription" in p[0] for p in progress_calls)
    assert any("summarization" in p[0] for p in progress_calls)


def test_orchestrator_uses_cache(tmp_path):
    config = DEFAULT_CONFIG.copy()
    config["transcript_folder"] = str(tmp_path / "output")
    config["cr_folder"] = str(tmp_path / "CR")
    config["output_folder"] = str(tmp_path / "html")
    config["gladia_api_key"] = "fake"
    config["theme"] = DEFAULT_CONFIG["theme"].copy()

    orch = PipelineOrchestrator(config=config)
    (tmp_path / "output").mkdir()
    (tmp_path / "output" / "test_meeting_CR.txt").write_text("cached transcript", encoding="utf-8")

    audio = _mock_audio(tmp_path)
    with patch.object(orch._transcriber, "transcribe") as mock_tr:
        with patch.object(orch._summarizer, "summarize", return_value="CR text"):
            with patch.object(orch._html_gen, "generate"):
                orch.run([audio], date_str="2026_03_20")

    mock_tr.assert_not_called()


def test_orchestrator_returns_error_on_failure(tmp_path):
    config = DEFAULT_CONFIG.copy()
    config["transcript_folder"] = str(tmp_path / "output")
    config["cr_folder"] = str(tmp_path / "CR")
    config["output_folder"] = str(tmp_path / "html")
    config["gladia_api_key"] = "fake"
    config["theme"] = DEFAULT_CONFIG["theme"].copy()

    orch = PipelineOrchestrator(config=config)
    audio = _mock_audio(tmp_path)
    with patch.object(orch._transcriber, "transcribe", side_effect=RuntimeError("API down")):
        result = orch.run([audio], date_str="2026_03_20")

    assert not result.success
    assert result.stage_failed == "transcription"
    assert "API down" in result.error
