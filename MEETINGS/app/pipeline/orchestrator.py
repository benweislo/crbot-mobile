from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from app.pipeline.transcriber import GladiaTranscriber
from app.pipeline.summarizer import ClaudeSummarizer
from app.pipeline.html_generator import HtmlGenerator


@dataclass
class PipelineResult:
    success: bool
    output_path: Path | None = None
    error: str = ""
    stage_failed: str = ""


class PipelineOrchestrator:
    def __init__(self, config: dict, on_progress: Callable[[str, str], None] | None = None):
        self._config = config
        self._transcript_dir = Path(config["transcript_folder"])
        self._cr_dir = Path(config["cr_folder"])
        self._output_dir = Path(config["output_folder"])
        self._on_progress = on_progress or (lambda stage, msg: None)

        self._transcriber = GladiaTranscriber(
            api_key=config.get("gladia_api_key", ""),
            language=config.get("language", "fr"),
        )
        self._summarizer = ClaudeSummarizer(system_prompt=config.get("system_prompt", ""))
        self._html_gen = HtmlGenerator(
            theme=config.get("theme", {}),
            logo_b64=config.get("_logo_b64", ""),
            font_regular_b64=config.get("_font_regular_b64", ""),
            font_bold_b64=config.get("_font_bold_b64", ""),
        )

    def run(self, audio_files: list[Path], date_str: str) -> PipelineResult:
        self._transcript_dir.mkdir(parents=True, exist_ok=True)
        self._cr_dir.mkdir(parents=True, exist_ok=True)
        self._output_dir.mkdir(parents=True, exist_ok=True)

        base_name = audio_files[0].stem
        current_stage = ""
        try:
            current_stage = "transcription"
            self._on_progress("transcription", "Transcription en cours...")
            transcript = self._stage_transcribe(audio_files, base_name)

            current_stage = "summarization"
            self._on_progress("summarization", "Résumé en cours...")
            summary = self._stage_summarize(transcript, base_name)

            current_stage = "generation"
            self._on_progress("generation", "Génération HTML...")
            output_path = self._stage_html(summary, base_name, date_str)

            return PipelineResult(success=True, output_path=output_path)
        except Exception as e:
            return PipelineResult(success=False, error=str(e), stage_failed=current_stage)

    def _stage_transcribe(self, audio_files: list[Path], base_name: str) -> str:
        cache_path = self._transcript_dir / f"{base_name}_meeting_CR.txt"
        if cache_path.exists():
            return cache_path.read_text(encoding="utf-8")

        all_text_parts = []
        time_offset = 0.0
        for audio in audio_files:
            result = self._transcriber.transcribe(audio)
            all_text_parts.append(result["full_text"])
            if result["segments"]:
                time_offset += result["segments"][-1]["end"]

        full = "\n\n".join(all_text_parts)
        cache_path.write_text(full, encoding="utf-8")
        return full

    def _stage_summarize(self, transcript: str, base_name: str) -> str:
        cache_path = self._cr_dir / f"{base_name}_meeting_CR.txt"
        if cache_path.exists():
            return cache_path.read_text(encoding="utf-8")
        summary = self._summarizer.summarize(transcript)
        cache_path.write_text(summary, encoding="utf-8")
        return summary

    def _stage_html(self, summary: str, base_name: str, date_str: str) -> Path:
        filename = f"{date_str}_CR_{base_name}.html"
        output_path = self._output_dir / filename
        self._html_gen.generate(summary, output_path)
        return output_path
