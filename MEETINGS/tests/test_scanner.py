from pathlib import Path
from app.pipeline.scanner import AudioScanner


def _create_audio(tmp_path, name: str) -> Path:
    p = tmp_path / name
    p.write_bytes(b"\x00" * 100)
    return p


def test_finds_supported_audio_files(tmp_path):
    _create_audio(tmp_path, "meeting.mp3")
    _create_audio(tmp_path, "notes.txt")
    _create_audio(tmp_path, "call.wav")
    scanner = AudioScanner(tmp_path, set())
    files = scanner.scan()
    names = [f.name for f in files]
    assert "meeting.mp3" in names
    assert "call.wav" in names
    assert "notes.txt" not in names


def test_excludes_processed_files(tmp_path):
    _create_audio(tmp_path, "old.mp3")
    _create_audio(tmp_path, "new.mp3")
    scanner = AudioScanner(tmp_path, processed={"old.mp3"})
    files = scanner.scan()
    assert len(files) == 1
    assert files[0].name == "new.mp3"


def test_groups_by_calendar_day(tmp_path):
    _create_audio(tmp_path, "2026_03_20_morning.mp3")
    _create_audio(tmp_path, "2026_03_20_afternoon.mp3")
    _create_audio(tmp_path, "2026_03_19_meeting.mp3")
    scanner = AudioScanner(tmp_path, set())
    groups = scanner.scan_grouped()
    assert len(groups) == 2
    day_20 = [g for g in groups if "2026_03_20" in g["date"]][0]
    assert len(day_20["files"]) == 2


def test_groups_audiocapturer_format(tmp_path):
    _create_audio(tmp_path, "AudioCapturer_20260320143000.mp3")
    _create_audio(tmp_path, "AudioCapturer_20260320154900.mp3")
    scanner = AudioScanner(tmp_path, set())
    groups = scanner.scan_grouped()
    assert len(groups) == 1
    assert len(groups[0]["files"]) == 2


def test_empty_folder_returns_empty(tmp_path):
    scanner = AudioScanner(tmp_path, set())
    assert scanner.scan() == []
    assert scanner.scan_grouped() == []
