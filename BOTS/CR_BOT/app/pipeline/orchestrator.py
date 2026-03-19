import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from app.branding.models import BrandProfile
from app.pipeline.transcribe import TranscribeClient
from app.pipeline.summarize import SummarizeClient
from app.pipeline.html_generator import HtmlGenerator


@dataclass
class PipelineResult:
    success: bool
    output_path: Path | None = None
    error: str = ""
    stage_failed: str = ""


class PipelineOrchestrator:
    def __init__(
        self,
        proxy_url: str,
        license_key: str,
        cache_dir: Path,
        output_dir: Path,
        context: str = "",
        language: str = "fr",
        on_progress: Callable[[str, int], None] | None = None,
    ):
        self._transcribe_client = TranscribeClient(proxy_url, license_key)
        self._summarize_client = SummarizeClient(proxy_url, license_key)
        self._cache_dir = cache_dir
        self._output_dir = output_dir
        self._context = context
        self._language = language
        self._on_progress = on_progress or (lambda stage, pct: None)

    def run(self, audio_files: list[Path], profile: BrandProfile) -> PipelineResult:
        """Run the full pipeline on a list of audio files (one meeting)."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._output_dir.mkdir(parents=True, exist_ok=True)

        # Use first file's stem as the base name
        base_name = audio_files[0].stem

        current_stage = ""
        try:
            # Stage 1: Transcription
            current_stage = "transcription"
            transcript = self._stage_transcribe(audio_files, base_name)

            # Stage 2: Summarization
            current_stage = "summarization"
            summary = self._stage_summarize(transcript, base_name)

            # Stage 3: HTML Generation
            current_stage = "generation"
            output_path = self._stage_html(summary, profile, base_name)

            return PipelineResult(success=True, output_path=output_path)

        except Exception as e:
            return PipelineResult(success=False, error=str(e), stage_failed=current_stage)

    def _stage_transcribe(self, audio_files: list[Path], base_name: str) -> str:
        """Transcribe audio files. Uses cache if available."""
        cache_path = self._cache_dir / f"{base_name}_transcript.txt"

        if cache_path.exists():
            return cache_path.read_text(encoding="utf-8")

        self._on_progress("transcription", 0)

        transcripts = []
        for i, audio in enumerate(audio_files):
            result = self._transcribe_client.transcribe(audio, self._language)
            transcripts.append(result["full_text"])
            self._on_progress("transcription", int((i + 1) / len(audio_files) * 100))

        full_transcript = "\n\n".join(transcripts)
        cache_path.write_text(full_transcript, encoding="utf-8")
        return full_transcript

    def _stage_summarize(self, transcript: str, base_name: str) -> str:
        """Summarize transcript. Uses cache if available."""
        cache_path = self._cache_dir / f"{base_name}_summary.txt"

        if cache_path.exists():
            return cache_path.read_text(encoding="utf-8")

        self._on_progress("summarization", 0)
        summary = self._summarize_client.summarize(transcript, self._context, self._language)
        self._on_progress("summarization", 100)

        cache_path.write_text(summary, encoding="utf-8")
        return summary

    def _stage_html(self, summary: str, profile: BrandProfile, base_name: str) -> Path:
        """Generate HTML from summary + profile."""
        self._on_progress("generation", 0)

        # Extract date from summary for filename
        date_match = re.search(r"Date\s*:\s*(\d{2})/(\d{2})/(\d{4})", summary)
        if date_match:
            d, m, y = date_match.group(1), date_match.group(2), date_match.group(3)
            filename = f"{y}_{m}_{d}_CR_{base_name}.html"
        else:
            filename = f"CR_{base_name}.html"

        output_path = self._output_dir / filename
        generator = HtmlGenerator(profile)
        generator.generate_to_file(summary, output_path)

        self._on_progress("generation", 100)
        return output_path
