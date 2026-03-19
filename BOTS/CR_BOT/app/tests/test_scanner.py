import pytest
from pathlib import Path
from datetime import date

from app.pipeline.scanner import AudioScanner, AudioGroup


class TestAudioScanner:
    def test_finds_audio_files(self, tmp_dir):
        (tmp_dir / "meeting.mp3").write_bytes(b"fake")
        (tmp_dir / "notes.txt").write_text("not audio")
        (tmp_dir / "call.wav").write_bytes(b"fake")

        scanner = AudioScanner(audio_dir=tmp_dir, history_file=tmp_dir / "history.json")
        files = scanner.scan_unprocessed()
        assert len(files) == 2
        names = {f.name for f in files}
        assert names == {"meeting.mp3", "call.wav"}

    def test_excludes_processed_files(self, tmp_dir):
        (tmp_dir / "old.mp3").write_bytes(b"fake")
        (tmp_dir / "new.mp3").write_bytes(b"fake")

        scanner = AudioScanner(audio_dir=tmp_dir, history_file=tmp_dir / "history.json")
        scanner.mark_processed(tmp_dir / "old.mp3")

        files = scanner.scan_unprocessed()
        assert len(files) == 1
        assert files[0].name == "new.mp3"

    def test_groups_same_day_files(self, tmp_dir):
        (tmp_dir / "2026_03_19_morning.mp3").write_bytes(b"fake")
        (tmp_dir / "2026_03_19_afternoon.mp3").write_bytes(b"fake")
        (tmp_dir / "2026_03_18_meeting.mp3").write_bytes(b"fake")

        scanner = AudioScanner(audio_dir=tmp_dir, history_file=tmp_dir / "history.json")
        groups = scanner.group_by_date(scanner.scan_unprocessed())
        assert len(groups) == 2
        mar19 = [g for g in groups if g.date_str == "19/03/2026"]
        assert len(mar19) == 1
        assert len(mar19[0].files) == 2

    def test_extracts_date_from_audiocapturer_filename(self, tmp_dir):
        (tmp_dir / "AudioCapturer_20260319143022.mp3").write_bytes(b"fake")

        scanner = AudioScanner(audio_dir=tmp_dir, history_file=tmp_dir / "history.json")
        groups = scanner.group_by_date(scanner.scan_unprocessed())
        assert len(groups) == 1
        assert groups[0].date_str == "19/03/2026"

    def test_today_files_flagged(self, tmp_dir):
        today = date.today()
        fname = f"{today.strftime('%Y_%m_%d')}_test.mp3"
        (tmp_dir / fname).write_bytes(b"fake")
        (tmp_dir / "2020_01_01_old.mp3").write_bytes(b"fake")

        scanner = AudioScanner(audio_dir=tmp_dir, history_file=tmp_dir / "history.json")
        groups = scanner.group_by_date(scanner.scan_unprocessed())
        today_groups = [g for g in groups if g.is_today]
        assert len(today_groups) == 1
