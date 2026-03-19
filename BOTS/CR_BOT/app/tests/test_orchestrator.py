import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.pipeline.orchestrator import PipelineOrchestrator, PipelineResult


class TestPipelineOrchestrator:
    def _make_orchestrator(self, tmp_dir):
        return PipelineOrchestrator(
            proxy_url="https://proxy.test",
            license_key="CRBOT-test",
            cache_dir=tmp_dir / ".crbot" / "cache",
            output_dir=tmp_dir / "output",
            context="Test company",
            language="fr",
        )

    @patch("app.pipeline.orchestrator.TranscribeClient")
    @patch("app.pipeline.orchestrator.SummarizeClient")
    @patch("app.pipeline.orchestrator.HtmlGenerator")
    def test_full_pipeline(self, MockHtmlGen, MockSumm, MockTrans, tmp_dir, sample_brand):
        # Setup mocks
        MockTrans.return_value.transcribe.return_value = {
            "full_text": "[Speaker 1] Test",
            "segments": [{"start": 0, "end": 5, "speaker": "Speaker 1", "text": "Test"}],
            "duration_seconds": 5.0,
        }
        MockSumm.return_value.summarize.return_value = "THÈMES\n• Test"
        MockHtmlGen.return_value.generate_to_file = MagicMock()

        from app.branding.models import BrandProfile
        profile = BrandProfile.from_dict(sample_brand)

        orch = self._make_orchestrator(tmp_dir)
        audio = tmp_dir / "test.mp3"
        audio.write_bytes(b"fake")

        result = orch.run([audio], profile)
        assert result.success is True
        assert MockTrans.return_value.transcribe.called
        assert MockSumm.return_value.summarize.called

    @patch("app.pipeline.orchestrator.TranscribeClient")
    @patch("app.pipeline.orchestrator.SummarizeClient")
    @patch("app.pipeline.orchestrator.HtmlGenerator")
    def test_resumes_from_transcript(self, MockHtmlGen, MockSumm, MockTrans, tmp_dir, sample_brand):
        # Pre-populate transcript cache
        cache_dir = tmp_dir / ".crbot" / "cache"
        cache_dir.mkdir(parents=True)
        (cache_dir / "test_transcript.txt").write_text("[Speaker 1] Cached", encoding="utf-8")

        MockSumm.return_value.summarize.return_value = "THÈMES\n• Cached"
        MockHtmlGen.return_value.generate_to_file = MagicMock()

        from app.branding.models import BrandProfile
        profile = BrandProfile.from_dict(sample_brand)

        orch = self._make_orchestrator(tmp_dir)
        audio = tmp_dir / "test.mp3"
        audio.write_bytes(b"fake")

        result = orch.run([audio], profile)
        assert result.success is True
        # Should NOT have called transcribe since transcript was cached
        assert not MockTrans.return_value.transcribe.called
