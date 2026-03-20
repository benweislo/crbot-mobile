# Mon CR Desktop App — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a PySide6 desktop app that auto-detects new meeting audio files, transcribes via Gladia, summarizes via local `claude -p`, and generates branded HTML reports with WSLO.lab theming.

**Architecture:** Pipeline-based: Scanner → Transcriber (Gladia API) → Summarizer (`claude -p` subprocess) → HTML Generator. UI runs on main thread, pipeline runs in QThread worker with Qt signal communication. Config persisted in `config.json`, history in `history.json`.

**Tech Stack:** Python 3.10+, PySide6, requests, Claude Code CLI (`claude -p`)

**Spec:** `MEETINGS/docs/superpowers/specs/2026-03-20-mon-cr-desktop-design.md`

**Reference code:**
- Existing transcriber: `MEETINGS/.skills/meeting-transcriber/scripts/transcribe.py`
- Existing summarizer: `MEETINGS/.skills/meeting-transcriber/scripts/summarize.py`
- Existing HTML generator: `MEETINGS/.skills/meeting-transcriber/scripts/generate_html.py`
- CR_BOT orchestrator pattern: `BOTS/CR_BOT/app/pipeline/orchestrator.py`
- CR_BOT theme pattern: `BOTS/CR_BOT/app/ui/theme.py`
- WSLO.lab logo: `WSLO.lab/website/public/logo-wslo.png` (488KB PNG)
- Base64 assets (fonts/logo): `MEETINGS/.skills/meeting-transcriber/scripts/_font_*_b64.txt`, `_logo_b64.txt`

---

## Chunk 1: Foundation (Config + Scanner + Tests)

### Task 1: Project scaffold + config defaults

**Files:**
- Create: `MEETINGS/app/__init__.py`
- Create: `MEETINGS/app/config/__init__.py`
- Create: `MEETINGS/app/config/defaults.py`
- Create: `MEETINGS/app/pipeline/__init__.py`
- Create: `MEETINGS/app/ui/__init__.py`
- Create: `MEETINGS/tests/__init__.py`
- Create: `MEETINGS/tests/test_config.py`

- [ ] **Step 1: Create directory structure**

```bash
cd C:/Users/User/WORK/MEETINGS
mkdir -p app/config app/pipeline app/ui app/assets/fonts tests
touch app/__init__.py app/config/__init__.py app/pipeline/__init__.py app/ui/__init__.py tests/__init__.py
```

- [ ] **Step 2: Write the failing test for defaults**

Create `tests/test_config.py`:
```python
from app.config.defaults import DEFAULT_CONFIG, WSLO_THEME


def test_default_config_has_required_keys():
    required = [
        "audio_folder", "output_folder", "transcript_folder",
        "cr_folder", "language", "gladia_api_key", "system_prompt", "theme", "logo_path",
    ]
    for key in required:
        assert key in DEFAULT_CONFIG, f"Missing key: {key}"


def test_wslo_theme_has_all_colors():
    colors = [
        "primary", "secondary", "tertiary", "background",
        "surface", "surface_elevated", "text_primary", "text_secondary", "danger",
    ]
    for color in colors:
        assert color in WSLO_THEME, f"Missing color: {color}"
        assert WSLO_THEME[color].startswith("#"), f"{color} must be hex"


def test_default_config_audio_folder_points_to_meetings():
    assert "MEETINGS" in DEFAULT_CONFIG["audio_folder"]


def test_default_system_prompt_is_french_cr():
    prompt = DEFAULT_CONFIG["system_prompt"]
    assert "COMPTE RENDU" in prompt
    assert "THÈMES ABORDÉS" in prompt
    assert "ACTIONS" in prompt
    assert "TOUT EN DÉTAILS" in prompt
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m pytest tests/test_config.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'app.config.defaults'`

- [ ] **Step 4: Implement defaults.py**

Create `app/config/defaults.py`:
```python
from pathlib import Path

MEETINGS_ROOT = Path(__file__).resolve().parent.parent.parent  # -> MEETINGS/

WSLO_THEME = {
    "primary": "#8B5CF6",
    "secondary": "#6366F1",
    "tertiary": "#2DD4BF",
    "background": "#0B0F1A",
    "surface": "#111827",
    "surface_elevated": "#1A2035",
    "text_primary": "#EDF0F7",
    "text_secondary": "#8891AB",
    "danger": "#F87171",
}

DEFAULT_SYSTEM_PROMPT = """Tu es un assistant expert en rédaction de comptes rendus professionnels.
On te fournit la transcription d'une réunion. Tu dois générer un Compte Rendu (CR) structuré en respectant exactement le format suivant. Rédige en français professionnel.

============================================================
COMPTE RENDU DE RÉUNION
============================================================

  Date     : [date extraite de la transcription]
  Durée    : [durée estimée]
  Fichiers : [noms des fichiers]

------------------------------------------------------------
THÈMES ABORDÉS
------------------------------------------------------------
  • [Thème 1]
  • [Thème 2]
  (Liste courte, à puces, des grands sujets abordés)

------------------------------------------------------------
ACTIONS / PROCHAINES ÉTAPES
------------------------------------------------------------
  Pour chaque personne identifiée, lister ses actions :
  NOM_PERSONNE :
  1. [Action claire et précise]
  2. [Action]

------------------------------------------------------------
CONCLUSION DU MEETING
------------------------------------------------------------
  → [Résumé global de la fin de la réunion et du sentiment général]

------------------------------------------------------------
TOUT EN DÉTAILS
------------------------------------------------------------
  Pour chaque thème abordé, détailler rigoureusement :
  ## 1. [Titre du thème]
  - Ce qui a été discuté exactement
  - Les propositions et débats
  - Qui a dit quoi (Speaker 1, Speaker 2...)
  Être exhaustif mais concis. Ne rien inventer.

============================================================
FIN DU COMPTE RENDU
============================================================"""

DEFAULT_CONFIG = {
    "audio_folder": str(MEETINGS_ROOT),
    "output_folder": str(MEETINGS_ROOT / "html"),
    "transcript_folder": str(MEETINGS_ROOT / "output"),
    "cr_folder": str(MEETINGS_ROOT / "CR"),
    "language": "fr",
    "gladia_api_key": "",
    "system_prompt": DEFAULT_SYSTEM_PROMPT,
    "theme": WSLO_THEME.copy(),
    "logo_path": "assets/logo-wslo.png",
}
```

- [ ] **Step 5: Run test to verify it passes**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m pytest tests/test_config.py -v
```
Expected: 4 PASSED

- [ ] **Step 6: Commit**

```bash
cd C:/Users/User/WORK/MEETINGS
git add app/ tests/
git commit -m "feat(mon-cr): project scaffold + config defaults with WSLO theme"
```

---

### Task 2: Config manager (load/save config.json + history.json)

**Files:**
- Create: `MEETINGS/app/config/manager.py`
- Create: `MEETINGS/tests/test_config_manager.py`

- [ ] **Step 1: Write failing tests for ConfigManager**

Create `tests/test_config_manager.py`:
```python
import json
from pathlib import Path
from app.config.manager import ConfigManager


def test_creates_default_config_on_first_load(tmp_path):
    mgr = ConfigManager(tmp_path)
    config = mgr.load()
    assert config["language"] == "fr"
    assert (tmp_path / "config.json").exists()


def test_saves_and_loads_custom_value(tmp_path):
    mgr = ConfigManager(tmp_path)
    config = mgr.load()
    config["language"] = "en"
    mgr.save(config)

    mgr2 = ConfigManager(tmp_path)
    loaded = mgr2.load()
    assert loaded["language"] == "en"


def test_loads_gladia_key_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GLADIA_API_KEY", "test-key-123")
    mgr = ConfigManager(tmp_path)
    config = mgr.load()
    # env var fills empty config value
    assert config["gladia_api_key"] == "test-key-123"


def test_config_value_overrides_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GLADIA_API_KEY", "env-key")
    # Pre-write config with a key
    (tmp_path / "config.json").write_text(
        json.dumps({"gladia_api_key": "config-key"}), encoding="utf-8"
    )
    mgr = ConfigManager(tmp_path)
    config = mgr.load()
    assert config["gladia_api_key"] == "config-key"


def test_corrupted_config_resets_to_defaults(tmp_path):
    (tmp_path / "config.json").write_text("NOT JSON", encoding="utf-8")
    mgr = ConfigManager(tmp_path)
    config = mgr.load()
    assert config["language"] == "fr"


def test_history_empty_on_first_load(tmp_path):
    mgr = ConfigManager(tmp_path)
    history = mgr.load_history()
    assert history == {"processed": []}


def test_history_add_and_load(tmp_path):
    mgr = ConfigManager(tmp_path)
    mgr.add_to_history("test.mp3", "html/test.html")
    history = mgr.load_history()
    assert len(history["processed"]) == 1
    assert history["processed"][0]["file"] == "test.mp3"
    assert "processed_at" in history["processed"][0]


def test_is_processed(tmp_path):
    mgr = ConfigManager(tmp_path)
    assert not mgr.is_processed("test.mp3")
    mgr.add_to_history("test.mp3", "html/test.html")
    assert mgr.is_processed("test.mp3")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m pytest tests/test_config_manager.py -v
```
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement ConfigManager**

Create `app/config/manager.py`:
```python
import json
import os
from datetime import datetime
from pathlib import Path

from app.config.defaults import DEFAULT_CONFIG


class ConfigManager:
    def __init__(self, root_dir: Path):
        self._root = root_dir
        self._config_path = root_dir / "config.json"
        self._history_path = root_dir / "history.json"

    def load(self) -> dict:
        config = DEFAULT_CONFIG.copy()
        config["theme"] = DEFAULT_CONFIG["theme"].copy()

        if self._config_path.exists():
            try:
                saved = json.loads(self._config_path.read_text(encoding="utf-8"))
                # Merge saved over defaults (preserve new default keys)
                for key, value in saved.items():
                    if key == "theme" and isinstance(value, dict):
                        config["theme"].update(value)
                    else:
                        config[key] = value
            except (json.JSONDecodeError, KeyError):
                pass  # corrupted — use defaults

        # Fill Gladia key from env if empty
        if not config["gladia_api_key"]:
            env_key = os.environ.get("GLADIA_API_KEY", "")
            if not env_key:
                # Try loading from ENV directory
                env_file = Path("C:/Users/User/ENV/.env")
                if env_file.exists():
                    for line in env_file.read_text(encoding="utf-8").splitlines():
                        if line.startswith("GLADIA_API_KEY="):
                            env_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break
            config["gladia_api_key"] = env_key

        # Only save if config file didn't exist (first launch)
        if not self._config_path.exists():
            self.save(config)
        return config

    def save(self, config: dict) -> None:
        self._config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load_history(self) -> dict:
        if self._history_path.exists():
            try:
                return json.loads(self._history_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        return {"processed": []}

    def _save_history(self, history: dict) -> None:
        self._history_path.write_text(
            json.dumps(history, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def add_to_history(self, filename: str, html_output: str) -> None:
        history = self.load_history()
        history["processed"].append({
            "file": filename,
            "processed_at": datetime.now().isoformat(),
            "html_output": html_output,
        })
        self._save_history(history)

    def is_processed(self, filename: str) -> bool:
        history = self.load_history()
        return any(e["file"] == filename for e in history["processed"])
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m pytest tests/test_config_manager.py -v
```
Expected: 8 PASSED

- [ ] **Step 5: Commit**

```bash
cd C:/Users/User/WORK/MEETINGS
git add app/config/manager.py tests/test_config_manager.py
git commit -m "feat(mon-cr): config manager with load/save/history/env fallback"
```

---

### Task 3: Audio scanner

**Files:**
- Create: `MEETINGS/app/pipeline/scanner.py`
- Create: `MEETINGS/tests/test_scanner.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_scanner.py`:
```python
from pathlib import Path
from app.pipeline.scanner import AudioScanner


def _create_audio(tmp_path, name: str) -> Path:
    p = tmp_path / name
    p.write_bytes(b"\x00" * 100)
    return p


def test_finds_supported_audio_files(tmp_path):
    _create_audio(tmp_path, "meeting.mp3")
    _create_audio(tmp_path, "notes.txt")  # not audio
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
    # 2026_03_20 group has 2 files
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m pytest tests/test_scanner.py -v
```
Expected: FAIL

- [ ] **Step 3: Implement AudioScanner**

Create `app/pipeline/scanner.py`:
```python
import re
from pathlib import Path

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".wma", ".aac", ".webm"}


def _extract_date(filename: str) -> str:
    """Extract YYYY_MM_DD from filename, or return 'unknown'."""
    # Format: YYYY_MM_DD_*
    m = re.match(r"(\d{4})_(\d{2})_(\d{2})", filename)
    if m:
        return f"{m.group(1)}_{m.group(2)}_{m.group(3)}"
    # Format: AudioCapturer_YYYYMMDD*
    m = re.match(r"AudioCapturer_(\d{4})(\d{2})(\d{2})", filename)
    if m:
        return f"{m.group(1)}_{m.group(2)}_{m.group(3)}"
    return "unknown"


class AudioScanner:
    def __init__(self, audio_folder: Path, processed: set[str]):
        self._folder = audio_folder
        self._processed = processed

    def scan(self) -> list[Path]:
        """Return unprocessed audio files sorted by name."""
        if not self._folder.exists():
            return []
        files = [
            f for f in sorted(self._folder.iterdir())
            if f.is_file()
            and f.suffix.lower() in SUPPORTED_EXTENSIONS
            and f.name not in self._processed
        ]
        return files

    def scan_grouped(self) -> list[dict]:
        """Return unprocessed files grouped by calendar day."""
        files = self.scan()
        if not files:
            return []

        groups: dict[str, list[Path]] = {}
        for f in files:
            date = _extract_date(f.name)
            groups.setdefault(date, []).append(f)

        return [
            {"date": date, "files": sorted(paths, key=lambda p: p.name)}
            for date, paths in sorted(groups.items())
        ]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m pytest tests/test_scanner.py -v
```
Expected: 5 PASSED

- [ ] **Step 5: Commit**

```bash
cd C:/Users/User/WORK/MEETINGS
git add app/pipeline/scanner.py tests/test_scanner.py
git commit -m "feat(mon-cr): audio scanner with day-grouping and history filtering"
```

---

## Chunk 2: Pipeline stages (Transcriber + Summarizer + HTML Generator)

### Task 4: Transcriber (Gladia API client)

**Files:**
- Create: `MEETINGS/app/pipeline/transcriber.py`
- Create: `MEETINGS/tests/test_transcriber.py`

**Reference:** `MEETINGS/.skills/meeting-transcriber/scripts/transcribe.py` lines 42-113

- [ ] **Step 1: Write failing tests**

Create `tests/test_transcriber.py`:
```python
import json
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m pytest tests/test_transcriber.py -v
```

- [ ] **Step 3: Implement GladiaTranscriber**

Create `app/pipeline/transcriber.py`:
```python
import time
from pathlib import Path

import requests

GLADIA_UPLOAD_URL = "https://api.gladia.io/v2/upload"
GLADIA_TRANSCRIPTION_URL = "https://api.gladia.io/v2/transcription"


class GladiaTranscriber:
    def __init__(self, api_key: str, language: str = "fr", timeout: int = 600):
        self._api_key = api_key
        self._language = language
        self._timeout = timeout

    def transcribe(self, audio_path: Path) -> dict:
        """Transcribe audio via Gladia API. Returns {full_text, segments, duration}."""
        headers = {"x-gladia-key": self._api_key}

        # Upload
        with open(audio_path, "rb") as f:
            files = {"audio": (audio_path.name, f, "audio/mpeg")}
            resp = requests.post(GLADIA_UPLOAD_URL, headers=headers, files=files, timeout=self._timeout)

        if resp.status_code != 200:
            raise RuntimeError(f"Upload failed: {resp.status_code} - {resp.text}")

        audio_url = resp.json()["audio_url"]

        # Start transcription
        payload = {"audio_url": audio_url, "diarization": True, "language": self._language}
        resp = requests.post(GLADIA_TRANSCRIPTION_URL, headers=headers, json=payload, timeout=60)

        if resp.status_code != 201:
            raise RuntimeError(f"Transcription start failed: {resp.status_code} - {resp.text}")

        result_url = resp.json()["result_url"]

        # Poll for result
        start_time = time.time()
        while True:
            if time.time() - start_time > self._timeout:
                raise RuntimeError(f"Transcription timed out after {self._timeout}s")

            poll = requests.get(result_url, headers=headers, timeout=30)
            data = poll.json()
            status = data.get("status")

            if status == "done":
                break
            elif status == "error":
                raise RuntimeError("Gladia transcription processing failed")

            time.sleep(5)

        # Parse utterances
        utterances = data.get("result", {}).get("transcription", {}).get("utterances", [])
        segments = []
        full_text_parts = []

        for u in utterances:
            speaker = f"Speaker {u.get('speaker', '?')}"
            text = u.get("text", "").strip()
            formatted = f"[{speaker}] {text}"
            segments.append({
                "start": u.get("start", 0.0),
                "end": u.get("end", 0.0),
                "text": formatted,
            })
            full_text_parts.append(formatted)

        duration = segments[-1]["end"] if segments else 0.0

        return {
            "full_text": " ".join(full_text_parts),
            "segments": segments,
            "duration": duration,
        }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m pytest tests/test_transcriber.py -v
```
Expected: 2 PASSED

- [ ] **Step 5: Commit**

```bash
cd C:/Users/User/WORK/MEETINGS
git add app/pipeline/transcriber.py tests/test_transcriber.py
git commit -m "feat(mon-cr): Gladia API transcriber with diarization"
```

---

### Task 5: Summarizer (claude -p subprocess)

**Files:**
- Create: `MEETINGS/app/pipeline/summarizer.py`
- Create: `MEETINGS/tests/test_summarizer.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_summarizer.py`:
```python
from unittest.mock import patch, MagicMock
from app.pipeline.summarizer import ClaudeSummarizer


def test_summarize_calls_claude_with_correct_args():
    summarizer = ClaudeSummarizer(system_prompt="Test prompt")

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "COMPTE RENDU DE RÉUNION\nTest summary"
    mock_result.stderr = ""

    with patch("app.pipeline.summarizer.subprocess.run", return_value=mock_result) as mock_run:
        result = summarizer.summarize("transcript text here")

    args = mock_run.call_args
    cmd = args[0][0]  # first positional arg is the command list
    assert "claude" in cmd[0]
    assert "-p" in cmd
    assert "--system-prompt" in cmd
    assert result == "COMPTE RENDU DE RÉUNION\nTest summary"


def test_summarize_passes_transcript_as_stdin():
    summarizer = ClaudeSummarizer(system_prompt="Test")

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Summary"
    mock_result.stderr = ""

    with patch("app.pipeline.summarizer.subprocess.run", return_value=mock_result) as mock_run:
        summarizer.summarize("My transcript content")

    kwargs = mock_run.call_args[1]
    assert kwargs["input"] == "My transcript content"


def test_summarize_raises_on_failure():
    summarizer = ClaudeSummarizer(system_prompt="Test")

    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Error: claude not found"

    with patch("app.pipeline.summarizer.subprocess.run", return_value=mock_result):
        try:
            summarizer.summarize("text")
            assert False, "Should have raised"
        except RuntimeError as e:
            assert "claude" in str(e).lower() or "Error" in str(e)


def test_summarize_raises_on_timeout():
    summarizer = ClaudeSummarizer(system_prompt="Test", timeout=1)

    import subprocess
    with patch("app.pipeline.summarizer.subprocess.run", side_effect=subprocess.TimeoutExpired("claude", 1)):
        try:
            summarizer.summarize("text")
            assert False, "Should have raised"
        except RuntimeError as e:
            assert "timeout" in str(e).lower()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m pytest tests/test_summarizer.py -v
```

- [ ] **Step 3: Implement ClaudeSummarizer**

Create `app/pipeline/summarizer.py`:
```python
import subprocess


class ClaudeSummarizer:
    def __init__(self, system_prompt: str, timeout: int = 600):
        self._system_prompt = system_prompt
        self._timeout = timeout

    def summarize(self, transcript: str) -> str:
        """Summarize transcript using local claude -p subprocess."""
        cmd = [
            "claude", "-p",
            "--system-prompt", self._system_prompt,
            "Voici la transcription complète de la réunion :",
        ]

        try:
            result = subprocess.run(
                cmd,
                input=transcript,
                capture_output=True,
                text=True,
                timeout=self._timeout,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Claude summarization timed out after {self._timeout}s")

        if result.returncode != 0:
            raise RuntimeError(f"Claude failed (exit {result.returncode}): {result.stderr}")

        return result.stdout.strip()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m pytest tests/test_summarizer.py -v
```
Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
cd C:/Users/User/WORK/MEETINGS
git add app/pipeline/summarizer.py tests/test_summarizer.py
git commit -m "feat(mon-cr): claude -p subprocess summarizer"
```

---

### Task 6: HTML generator with configurable theming

**Files:**
- Create: `MEETINGS/app/pipeline/html_template.py`
- Create: `MEETINGS/app/pipeline/html_generator.py`
- Create: `MEETINGS/tests/test_html_generator.py`

**Reference:** `MEETINGS/.skills/meeting-transcriber/scripts/generate_html.py` — reuse `parse_cr()` logic and HTML template structure, but replace hardcoded Méliès colors with CSS variables from config theme.

- [ ] **Step 1: Write failing tests**

Create `tests/test_html_generator.py`:
```python
from pathlib import Path
from app.pipeline.html_generator import HtmlGenerator
from app.config.defaults import WSLO_THEME

SAMPLE_CR = """============================================================
COMPTE RENDU DE RÉUNION
============================================================

  Date     : 20/03/2026
  Durée    : 01:30:00
  Fichiers : test_meeting.mp3

------------------------------------------------------------
THÈMES ABORDÉS
------------------------------------------------------------
  • Planning du projet
  • Budget trimestriel

------------------------------------------------------------
ACTIONS / PROCHAINES ÉTAPES
------------------------------------------------------------
  1. Ben : finaliser le prototype
  2. Ali : préparer la démo

------------------------------------------------------------
CONCLUSION DU MEETING
------------------------------------------------------------
  → Bonne avancée, prochaine réunion lundi

------------------------------------------------------------
TOUT EN DÉTAILS
------------------------------------------------------------
  ## 1. Planning du projet
  - Discussion sur le calendrier Q2
  - **Deadline** fixée au 15 avril

============================================================
FIN DU COMPTE RENDU
============================================================"""


def test_generates_html_file(tmp_path):
    gen = HtmlGenerator(theme=WSLO_THEME)
    output = tmp_path / "test.html"
    gen.generate(SAMPLE_CR, output)
    assert output.exists()
    html = output.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html
    assert "Planning du projet" in html
    assert "Budget trimestriel" in html


def test_html_contains_theme_colors(tmp_path):
    gen = HtmlGenerator(theme=WSLO_THEME)
    output = tmp_path / "test.html"
    gen.generate(SAMPLE_CR, output)
    html = output.read_text(encoding="utf-8")
    assert "#8B5CF6" in html  # primary
    assert "#2DD4BF" in html  # tertiary
    assert "#0B0F1A" in html  # background


def test_html_contains_actions(tmp_path):
    gen = HtmlGenerator(theme=WSLO_THEME)
    output = tmp_path / "test.html"
    gen.generate(SAMPLE_CR, output)
    html = output.read_text(encoding="utf-8")
    assert "finaliser le prototype" in html
    assert "préparer la démo" in html


def test_html_contains_details_section(tmp_path):
    gen = HtmlGenerator(theme=WSLO_THEME)
    output = tmp_path / "test.html"
    gen.generate(SAMPLE_CR, output)
    html = output.read_text(encoding="utf-8")
    assert "Planning du projet" in html
    assert "Deadline" in html


def test_custom_theme_applied(tmp_path):
    custom = WSLO_THEME.copy()
    custom["primary"] = "#FF0000"
    gen = HtmlGenerator(theme=custom)
    output = tmp_path / "test.html"
    gen.generate(SAMPLE_CR, output)
    html = output.read_text(encoding="utf-8")
    assert "#FF0000" in html


def test_malformed_cr_fallback(tmp_path):
    gen = HtmlGenerator(theme=WSLO_THEME)
    output = tmp_path / "test.html"
    gen.generate("Just some random text\nNo structure here", output)
    assert output.exists()
    html = output.read_text(encoding="utf-8")
    assert "Just some random text" in html
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m pytest tests/test_html_generator.py -v
```

- [ ] **Step 3: Create HTML template**

Create `app/pipeline/html_template.py`. This file contains the full HTML template ported from `MEETINGS/.skills/meeting-transcriber/scripts/generate_html.py` (lines 202-559) with all hardcoded colors replaced by theme dict values.

**Color mapping (reference → theme key):**

| Original in generate_html.py | Theme key | Usage |
|---|---|---|
| `#050505` | `background` | body bg gradient start |
| `#110a1a` | `surface` | body bg gradient end |
| `#e2e8f0` | `text_primary` | body text color |
| `#6e3ea8` | `primary` | section-label, h1 gradient start, action-num color, detail-list bullet |
| `#E93F7F` | `secondary` | h1 gradient end, speaker-tag, conclusion border |
| `rgba(74,41,113,0.35)` | derive from `primary` | orb-1, action-num bg |
| `rgba(233,63,127,0.25)` | derive from `secondary` | orb-2, conclusion border |
| `rgba(91,84,224,0.20)` | derive from `secondary` | orb-3 |
| `#cbd5e0` | `text_secondary` | list item text, detail text |
| `#a0aec0` | `text_secondary` | meta-item, conclusion-item |
| `#4a5568` | `text_secondary` (darker) | footer |
| `#4A2971` | `primary` | print styles |
| `CeraPro` | `AppFont` | font-family (only if b64 provided) |

**Implementation instructions:**
1. Copy the `_details_to_html()` function verbatim from `generate_html.py` lines 118-174
2. Copy the complete `generate_html()` template from lines 202-559
3. Replace every hardcoded color per the mapping above
4. Replace `CeraPro` font references with `AppFont` (conditional on font_b64 params)
5. Replace the Méliès logo `<img>` with the passed `logo_b64` param
6. Replace footer text: `"Généré par Mon CR — wslo.lab"`
7. Keep ALL structure: bokeh orbs (3), film grain SVG, vignette, glass-morphism cards, SVG meta icons, print CSS, responsive CSS
8. Convert from f-string with `data["key"]` refs to function params

The `_details_to_html()` function handles:
- `## N. Title` → `<h3>` with optional speaker tag
- `- bullet` → `<ul><li>` with open/close state tracking
- `**bold**` → `<strong>`
- empty lines → close list
- plain text → `<p>`

This function must be copied exactly from lines 118-174 of `generate_html.py` — it is not trivial.

**Key differences from existing template:**
- All colors via params (not hardcoded)
- Logo from param (not hardcoded Méliès)
- Footer: "Généré par Mon CR — wslo.lab"
- Font: AppFont (DM Sans b64) or system fallback

- [ ] **Step 4: Implement HtmlGenerator**

Create `app/pipeline/html_generator.py`:
```python
import re
from pathlib import Path

from app.pipeline.html_template import build_html


def _parse_cr(text: str) -> dict:
    """Parse structured CR text into sections."""
    data = {"date": "", "duree": "", "fichier": "", "themes": [], "actions": [], "conclusion": [], "details": ""}
    current_section = None

    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("====") or stripped.startswith("----"):
            continue
        if stripped in ("COMPTE RENDU DE RÉUNION", "FIN DU COMPTE RENDU"):
            continue

        if stripped == "THÈMES ABORDÉS":
            current_section = "themes"
            continue
        elif stripped == "ACTIONS / PROCHAINES ÉTAPES":
            current_section = "actions"
            continue
        elif stripped == "CONCLUSION DU MEETING":
            current_section = "conclusion"
            continue
        elif stripped == "TOUT EN DÉTAILS":
            current_section = "details"
            continue

        if current_section is None:
            if stripped.startswith("Date"):
                data["date"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("Durée"):
                data["duree"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("Fichier"):
                data["fichier"] = stripped.split(":", 1)[1].strip()
            continue

        if current_section == "themes":
            m = re.match(r"^[•\-]\s*(.*)", stripped)
            if m:
                data["themes"].append(m.group(1))
        elif current_section == "actions":
            m = re.match(r"^\d+\.\s*(.*)", stripped)
            if m:
                data["actions"].append(m.group(1))
            elif stripped and not stripped.startswith("("):
                # Person header line (e.g. "BEN :") — keep as-is
                data["actions"].append(stripped)
        elif current_section == "conclusion":
            m = re.match(r"^→\s*(.*)", stripped)
            if m:
                data["conclusion"].append(m.group(1))
            elif stripped:
                data["conclusion"].append(stripped)
        elif current_section == "details":
            data["details"] += line + "\n"

    return data


class HtmlGenerator:
    def __init__(self, theme: dict, logo_b64: str = "", font_regular_b64: str = "", font_bold_b64: str = ""):
        self._theme = theme
        self._logo_b64 = logo_b64
        self._font_regular_b64 = font_regular_b64
        self._font_bold_b64 = font_bold_b64

    def generate(self, cr_text: str, output_path: Path) -> None:
        """Parse CR text and generate themed HTML file."""
        data = _parse_cr(cr_text)

        # Fallback for malformed CR: put raw text in details
        if not data["themes"] and not data["actions"] and not data["details"].strip():
            data["details"] = cr_text

        html = build_html(data, self._theme, self._logo_b64, self._font_regular_b64, self._font_bold_b64)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")
```

- [ ] **Step 5: Implement html_template.py**

Create `app/pipeline/html_template.py`. This is a large file (~400 lines). Port the HTML/CSS from `generate_html.py` lines 202-559, replacing hardcoded colors with theme dict values. Key structure:

```python
import re


def _details_to_html(details_text: str) -> str:
    """Convert TOUT EN DÉTAILS text to HTML."""
    # (port from generate_html.py lines 118-174)
    ...


def build_html(data: dict, theme: dict, logo_b64: str, font_regular_b64: str, font_bold_b64: str) -> str:
    """Build complete self-contained HTML page."""
    primary = theme["primary"]
    secondary = theme.get("secondary", theme["primary"])
    tertiary = theme.get("tertiary", theme["primary"])
    bg = theme["background"]
    surface = theme["surface"]
    text_primary = theme["text_primary"]
    text_secondary = theme["text_secondary"]

    # Build section HTML
    themes_html = "\n".join(f'<li><span class="theme-dot"></span>{t}</li>' for t in data["themes"])
    actions_html = "\n".join(f'<li><span class="action-num">{i+1}</span>{a}</li>' for i, a in enumerate(data["actions"]))
    conclusion_html = "\n".join(f'<p class="conclusion-item">→ {c}</p>' for c in data["conclusion"])
    details_html = _details_to_html(data["details"]) if data["details"].strip() else ""
    date_display = data["date"] if data["date"] else "Date inconnue"

    # Font face blocks (only if b64 provided)
    font_faces = ""
    if font_regular_b64:
        font_faces += f"""@font-face {{ font-family: 'AppFont'; src: url('data:font/woff2;base64,{font_regular_b64}') format('woff2'); font-weight: 400; }}"""
    if font_bold_b64:
        font_faces += f"""@font-face {{ font-family: 'AppFont'; src: url('data:font/woff2;base64,{font_bold_b64}') format('woff2'); font-weight: 700; }}"""

    font_family = "'AppFont', " if font_regular_b64 else ""
    logo_tag = f'<img class="logo" src="data:image/png;base64,{logo_b64}" alt="Logo">' if logo_b64 else ""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CR Réunion — {date_display}</title>
    <style>
        {font_faces}
        *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: {font_family}-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(to bottom, {bg} 0%, {surface} 100%);
            color: {text_primary};
            min-height: 100vh; line-height: 1.7; overflow-x: hidden;
        }}
        /* ... (full CSS ported from generate_html.py with {primary}, {secondary}, {tertiary}, etc.) ... */
        /* Include: bokeh orbs, film grain, vignette, glass-morphism cards, print CSS */
    </style>
</head>
<body>
    <!-- bokeh, grain, vignette divs -->
    <div class="container">
        <header class="header">
            {logo_tag}
            <h1>Compte Rendu de Réunion</h1>
            <!-- meta: date, duration -->
        </header>
        <!-- sections: themes, actions, conclusion, details -->
        <footer class="footer">Généré par Mon CR — wslo.lab</footer>
    </div>
</body>
</html>"""
```

**Important:** Port the FULL CSS from the existing `generate_html.py` (bokeh animations, film grain, vignette, print styles, responsive) — don't abbreviate. Replace every hardcoded Méliès color with the corresponding `theme` dict value.

- [ ] **Step 6: Run tests to verify they pass**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m pytest tests/test_html_generator.py -v
```
Expected: 6 PASSED

- [ ] **Step 7: Commit**

```bash
cd C:/Users/User/WORK/MEETINGS
git add app/pipeline/html_template.py app/pipeline/html_generator.py tests/test_html_generator.py
git commit -m "feat(mon-cr): HTML generator with configurable WSLO theme"
```

---

### Task 7: Pipeline orchestrator

**Files:**
- Create: `MEETINGS/app/pipeline/orchestrator.py`
- Create: `MEETINGS/tests/test_orchestrator.py`

**Reference:** `BOTS/CR_BOT/app/pipeline/orchestrator.py` — same pattern but with local classes.

- [ ] **Step 1: Write failing tests**

Create `tests/test_orchestrator.py`:
```python
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
    assert r.output_path == Path("test.html")
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
            with patch.object(orch._html_gen, "generate") as mock_html:
                result = orch.run([audio], date_str="2026_03_20")

    assert result.success
    # Transcribe and summarize were called
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

    # Pre-create cached transcript
    (tmp_path / "output").mkdir()
    (tmp_path / "output" / "test_meeting_CR.txt").write_text("cached transcript", encoding="utf-8")

    audio = _mock_audio(tmp_path)

    with patch.object(orch._transcriber, "transcribe") as mock_tr:
        with patch.object(orch._summarizer, "summarize", return_value="CR text"):
            with patch.object(orch._html_gen, "generate"):
                orch.run([audio], date_str="2026_03_20")

    # Transcriber should NOT have been called — cache hit
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m pytest tests/test_orchestrator.py -v
```

- [ ] **Step 3: Implement PipelineOrchestrator**

Create `app/pipeline/orchestrator.py`:
```python
import re
from dataclasses import dataclass, field
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
    def __init__(
        self,
        config: dict,
        on_progress: Callable[[str, str], None] | None = None,
    ):
        self._config = config
        self._transcript_dir = Path(config["transcript_folder"])
        self._cr_dir = Path(config["cr_folder"])
        self._output_dir = Path(config["output_folder"])
        self._on_progress = on_progress or (lambda stage, msg: None)

        self._transcriber = GladiaTranscriber(
            api_key=config.get("gladia_api_key", ""),
            language=config.get("language", "fr"),
        )
        self._summarizer = ClaudeSummarizer(
            system_prompt=config.get("system_prompt", ""),
        )
        self._html_gen = HtmlGenerator(
            theme=config.get("theme", {}),
            logo_b64=config.get("_logo_b64", ""),
            font_regular_b64=config.get("_font_regular_b64", ""),
            font_bold_b64=config.get("_font_bold_b64", ""),
        )

    def run(self, audio_files: list[Path], date_str: str) -> PipelineResult:
        """Run full pipeline for one session (group of audio files)."""
        self._transcript_dir.mkdir(parents=True, exist_ok=True)
        self._cr_dir.mkdir(parents=True, exist_ok=True)
        self._output_dir.mkdir(parents=True, exist_ok=True)

        base_name = audio_files[0].stem
        current_stage = ""

        try:
            # Stage 1: Transcription
            current_stage = "transcription"
            self._on_progress("transcription", "Transcription en cours...")
            transcript = self._stage_transcribe(audio_files, base_name)

            # Stage 2: Summarization
            current_stage = "summarization"
            self._on_progress("summarization", "Résumé en cours...")
            summary = self._stage_summarize(transcript, base_name)

            # Stage 3: HTML generation
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

        # Merge multiple files with time-offset continuity
        # (ported from existing transcribe.py lines 246-267)
        all_segments = []
        all_text_parts = []
        time_offset = 0.0

        for audio in audio_files:
            result = self._transcriber.transcribe(audio)
            for seg in result["segments"]:
                shifted = seg.copy()
                shifted["start"] += time_offset
                shifted["end"] += time_offset
                all_segments.append(shifted)
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m pytest tests/test_orchestrator.py -v
```
Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
cd C:/Users/User/WORK/MEETINGS
git add app/pipeline/orchestrator.py tests/test_orchestrator.py
git commit -m "feat(mon-cr): pipeline orchestrator with caching and progress signals"
```

---

## Chunk 3: UI (Theme + Widgets + Main Window)

### Task 8: Copy assets (logo + fonts)

**Files:**
- Copy: `WSLO.lab/website/public/logo-wslo.png` → `MEETINGS/app/assets/logo-wslo.png`
- Create: `MEETINGS/app/assets/__init__.py`

- [ ] **Step 1: Copy the WSLO logo**

```bash
cp C:/Users/User/WORK/WSLO.lab/website/public/logo-wslo.png C:/Users/User/WORK/MEETINGS/app/assets/logo-wslo.png
```

- [ ] **Step 2: Download DM Sans font**

DM Sans is available from Google Fonts. Download the Regular and Bold TTF files:

```bash
cd C:/Users/User/WORK/MEETINGS/app/assets/fonts
# If DM Sans is available locally from WSLO.lab node_modules or system, copy it.
# Otherwise download from Google Fonts CDN:
curl -L -o DMSans-Regular.ttf "https://fonts.gstatic.com/s/dmsans/v15/rP2Hp2ywxg089UriCZOIHTWEBlw.ttf"
curl -L -o DMSans-Bold.ttf "https://fonts.gstatic.com/s/dmsans/v15/rP2Cp2ywxg089UriASitCBimfWk.ttf"
```

If curl fails (corporate network), skip font embedding — the app will use system fallback.

- [ ] **Step 3: Create __init__.py for assets module**

Create `app/assets/__init__.py`:
```python
import base64
from pathlib import Path

ASSETS_DIR = Path(__file__).parent


def load_logo_b64() -> str:
    logo = ASSETS_DIR / "logo-wslo.png"
    if logo.exists():
        return base64.b64encode(logo.read_bytes()).decode("ascii")
    return ""


def load_font_b64(name: str) -> str:
    font = ASSETS_DIR / "fonts" / name
    if font.exists():
        return base64.b64encode(font.read_bytes()).decode("ascii")
    return ""
```

- [ ] **Step 4: Commit**

```bash
cd C:/Users/User/WORK/MEETINGS
git add app/assets/
git commit -m "feat(mon-cr): copy WSLO logo + DM Sans fonts + asset loader"
```

---

### Task 9: Theme system (QSS stylesheet builder)

**Files:**
- Create: `MEETINGS/app/ui/theme.py`
- Create: `MEETINGS/tests/test_theme.py`

**Reference:** `BOTS/CR_BOT/app/ui/theme.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_theme.py`:
```python
from app.ui.theme import build_stylesheet
from app.config.defaults import WSLO_THEME


def test_stylesheet_contains_background_color():
    qss = build_stylesheet(WSLO_THEME)
    assert "#0B0F1A" in qss


def test_stylesheet_contains_primary_color():
    qss = build_stylesheet(WSLO_THEME)
    assert "#8B5CF6" in qss


def test_stylesheet_has_button_styles():
    qss = build_stylesheet(WSLO_THEME)
    assert "QPushButton" in qss


def test_stylesheet_has_list_styles():
    qss = build_stylesheet(WSLO_THEME)
    assert "QListWidget" in qss


def test_custom_theme_applied():
    custom = WSLO_THEME.copy()
    custom["primary"] = "#FF0000"
    qss = build_stylesheet(custom)
    assert "#FF0000" in qss
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m pytest tests/test_theme.py -v
```

- [ ] **Step 3: Implement theme.py**

Create `app/ui/theme.py`:
```python
def build_stylesheet(theme: dict) -> str:
    """Generate QSS stylesheet from theme dict."""
    bg = theme["background"]
    surface = theme["surface"]
    surface_el = theme["surface_elevated"]
    primary = theme["primary"]
    secondary = theme["secondary"]
    tertiary = theme["tertiary"]
    text = theme["text_primary"]
    text_muted = theme["text_secondary"]
    danger = theme["danger"]

    return f"""
    QMainWindow, QDialog {{
        background-color: {bg};
        color: {text};
    }}
    QWidget {{
        color: {text};
    }}
    QPushButton#generateBtn {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {primary}, stop:0.5 {secondary}, stop:1 {tertiary});
        color: white;
        border: none;
        border-radius: 12px;
        padding: 16px 32px;
        font-size: 16px;
        font-weight: bold;
        min-height: 48px;
    }}
    QPushButton#generateBtn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {secondary}, stop:0.5 {tertiary}, stop:1 {primary});
    }}
    QPushButton#generateBtn:disabled {{
        background: {surface_el};
        color: {text_muted};
    }}
    QPushButton {{
        background-color: {surface_el};
        color: {text};
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background-color: {primary};
        color: white;
    }}
    QPushButton:disabled {{
        background-color: {surface};
        color: {text_muted};
    }}
    QLabel {{
        color: {text};
    }}
    QLabel#statusLabel {{
        font-size: 14px;
    }}
    QLabel#pendingLabel {{
        color: {text_muted};
        font-size: 13px;
    }}
    QLabel#sectionLabel {{
        color: {text_muted};
        font-size: 12px;
        font-weight: bold;
        letter-spacing: 1px;
    }}
    QLineEdit, QTextEdit {{
        background-color: rgba(255,255,255,0.05);
        color: {text};
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 10px;
        font-size: 13px;
    }}
    QLineEdit:focus, QTextEdit:focus {{
        border-color: {primary};
    }}
    QListWidget {{
        background-color: rgba(255,255,255,0.03);
        color: {text};
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 4px;
    }}
    QListWidget::item {{
        padding: 10px 12px;
        border-radius: 8px;
        margin: 2px;
    }}
    QListWidget::item:hover {{
        background-color: {surface_el};
    }}
    QListWidget::item:selected {{
        background-color: {primary};
    }}
    QComboBox {{
        background-color: {surface_el};
        color: {text};
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 8px 12px;
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QScrollBar:vertical {{
        background: {surface};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {surface_el};
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    """
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m pytest tests/test_theme.py -v
```
Expected: 5 PASSED

- [ ] **Step 5: Commit**

```bash
cd C:/Users/User/WORK/MEETINGS
git add app/ui/theme.py tests/test_theme.py
git commit -m "feat(mon-cr): QSS theme builder with WSLO gradient button"
```

---

### Task 10: Progress widget

**Files:**
- Create: `MEETINGS/app/ui/progress_widget.py`

- [ ] **Step 1: Create progress_widget.py**

```python
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt


class ProgressWidget(QWidget):
    """3-step progress indicator: Transcription → Résumé → HTML."""

    STAGES = ["Transcription", "Résumé", "HTML"]

    def __init__(self, theme: dict | None = None, parent=None):
        super().__init__(parent)
        self._current = -1  # -1 = idle
        self._labels: list[QLabel] = []
        self._dots: list[QLabel] = []
        # Theme colors (with defaults matching WSLO)
        self._c_done = (theme or {}).get("tertiary", "#2DD4BF")
        self._c_active = (theme or {}).get("primary", "#8B5CF6")
        self._c_text = (theme or {}).get("text_primary", "#EDF0F7")
        self._c_muted = (theme or {}).get("text_secondary", "#4D5575")
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        for i, name in enumerate(self.STAGES):
            dot = QLabel("○")
            dot.setAlignment(Qt.AlignCenter)
            dot.setFixedWidth(20)
            dot.setStyleSheet(f"font-size: 16px; color: {self._c_muted};")
            self._dots.append(dot)
            layout.addWidget(dot)

            label = QLabel(name)
            label.setStyleSheet(f"font-size: 13px; color: {self._c_muted};")
            self._labels.append(label)
            layout.addWidget(label)

            if i < len(self.STAGES) - 1:
                sep = QLabel("→")
                sep.setStyleSheet("color: #4D5575; font-size: 12px;")
                sep.setAlignment(Qt.AlignCenter)
                layout.addWidget(sep)

        layout.addStretch()

    def set_stage(self, index: int):
        """Set active stage (0-2). -1 = idle."""
        self._current = index
        for i, (dot, label) in enumerate(zip(self._dots, self._labels)):
            if i < index:
                dot.setText("●")
                dot.setStyleSheet(f"font-size: 16px; color: {self._c_done};")
                label.setStyleSheet(f"font-size: 13px; color: {self._c_done};")
            elif i == index:
                dot.setText("◉")
                dot.setStyleSheet(f"font-size: 16px; color: {self._c_active};")
                label.setStyleSheet(f"font-size: 13px; color: {self._c_text}; font-weight: bold;")
            else:
                dot.setText("○")
                dot.setStyleSheet(f"font-size: 16px; color: {self._c_muted};")
                label.setStyleSheet(f"font-size: 13px; color: {self._c_muted};")

    def reset(self):
        self.set_stage(-1)
        for dot, label in zip(self._dots, self._labels):
            dot.setText("○")
            dot.setStyleSheet(f"font-size: 16px; color: {self._c_muted};")
            label.setStyleSheet(f"font-size: 13px; color: {self._c_muted};")
```

- [ ] **Step 2: Commit**

```bash
cd C:/Users/User/WORK/MEETINGS
git add app/ui/progress_widget.py
git commit -m "feat(mon-cr): 3-step progress widget"
```

---

### Task 11: History panel

**Files:**
- Create: `MEETINGS/app/ui/history_panel.py`

- [ ] **Step 1: Create history_panel.py**

```python
import os
import re
import webbrowser
from pathlib import Path

from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt


class HistoryPanel(QListWidget):
    """Clickable list of generated CR HTML files."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.itemDoubleClicked.connect(self._open_html)

    def load(self, html_folder: Path, history: dict):
        """Load history from both history.json and existing HTML files."""
        self.clear()
        seen_paths: set[str] = set()
        entries: list[tuple[str, str, str]] = []  # (date_sort_key, display_text, path)

        # From history.json
        for item in history.get("processed", []):
            html_path = item.get("html_output", "")
            if html_path and html_path not in seen_paths:
                seen_paths.add(html_path)
                full = html_folder.parent / html_path if not Path(html_path).is_absolute() else Path(html_path)
                date_key = self._extract_date(full.name)
                entries.append((date_key, full.name, str(full)))

        # From html/ folder scan
        if html_folder.exists():
            for f in html_folder.glob("*.html"):
                if str(f) not in seen_paths and f.name not in [Path(s).name for s in seen_paths]:
                    date_key = self._extract_date(f.name)
                    entries.append((date_key, f.name, str(f)))

        # Sort by date descending
        entries.sort(key=lambda e: e[0], reverse=True)

        for date_key, display, path in entries:
            # Format display: "2026-03-20 — CR meeting"
            nice_date = date_key.replace("_", "-") if date_key != "0000_00_00" else "?"
            label = re.sub(r"^\d{4}_\d{2}_\d{2}_CR_?", "", Path(display).stem)
            label = label.replace("_", " ").strip() or "réunion"
            text = f"{nice_date} — {label}"

            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, path)
            self.addItem(item)

    def _extract_date(self, filename: str) -> str:
        m = re.match(r"(\d{4})_(\d{2})_(\d{2})", filename)
        if m:
            return f"{m.group(1)}_{m.group(2)}_{m.group(3)}"
        return "0000_00_00"

    def _open_html(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        if path and Path(path).exists():
            webbrowser.open(Path(path).as_uri())
```

- [ ] **Step 2: Commit**

```bash
cd C:/Users/User/WORK/MEETINGS
git add app/ui/history_panel.py
git commit -m "feat(mon-cr): history panel with html scan + history.json merge"
```

---

### Task 12: Settings dialog

**Files:**
- Create: `MEETINGS/app/ui/settings_dialog.py`

- [ ] **Step 1: Create settings_dialog.py**

```python
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QFileDialog, QComboBox, QGroupBox, QFormLayout, QColorDialog,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class SettingsDialog(QDialog):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self._config = config.copy()
        self._config["theme"] = config.get("theme", {}).copy()
        self.setWindowTitle("Paramètres")
        self.setMinimumWidth(520)
        self.setMinimumHeight(600)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # --- Folders ---
        folders_group = QGroupBox("Dossiers")
        folders_layout = QFormLayout()

        self._audio_edit = QLineEdit(self._config.get("audio_folder", ""))
        audio_row = QHBoxLayout()
        audio_row.addWidget(self._audio_edit)
        audio_btn = QPushButton("...")
        audio_btn.setFixedWidth(32)
        audio_btn.clicked.connect(lambda: self._browse("audio_folder", self._audio_edit))
        audio_row.addWidget(audio_btn)
        folders_layout.addRow("Dossier audio:", audio_row)

        self._output_edit = QLineEdit(self._config.get("output_folder", ""))
        output_row = QHBoxLayout()
        output_row.addWidget(self._output_edit)
        output_btn = QPushButton("...")
        output_btn.setFixedWidth(32)
        output_btn.clicked.connect(lambda: self._browse("output_folder", self._output_edit))
        output_row.addWidget(output_btn)
        folders_layout.addRow("Dossier output:", output_row)

        folders_group.setLayout(folders_layout)
        layout.addWidget(folders_group)

        # --- Résumé ---
        summary_group = QGroupBox("Résumé")
        summary_layout = QVBoxLayout()

        summary_layout.addWidget(QLabel("Prompt système:"))
        self._prompt_edit = QTextEdit()
        self._prompt_edit.setPlainText(self._config.get("system_prompt", ""))
        self._prompt_edit.setMinimumHeight(120)
        summary_layout.addWidget(self._prompt_edit)

        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("Langue:"))
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(["fr", "en", "es"])
        self._lang_combo.setCurrentText(self._config.get("language", "fr"))
        lang_row.addWidget(self._lang_combo)
        lang_row.addStretch()
        summary_layout.addLayout(lang_row)

        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        # --- Apparence ---
        theme_group = QGroupBox("Apparence")
        theme_layout = QFormLayout()
        theme = self._config.get("theme", {})

        self._color_btns = {}
        color_labels = [
            ("primary", "Couleur primaire"),
            ("secondary", "Couleur secondaire"),
            ("tertiary", "Couleur tertiaire"),
            ("background", "Background"),
            ("text_primary", "Texte"),
        ]
        for key, label in color_labels:
            btn = QPushButton(theme.get(key, "#000"))
            btn.setFixedWidth(120)
            color = theme.get(key, "#000")
            btn.setStyleSheet(f"background-color: {color}; color: white; border-radius: 4px; padding: 4px;")
            btn.clicked.connect(lambda checked=False, k=key, b=btn: self._pick_color(k, b))
            self._color_btns[key] = btn
            theme_layout.addRow(label + ":", btn)

        # Logo
        self._logo_edit = QLineEdit(self._config.get("logo_path", ""))
        logo_row = QHBoxLayout()
        logo_row.addWidget(self._logo_edit)
        logo_btn = QPushButton("Changer")
        logo_btn.clicked.connect(self._pick_logo)
        logo_row.addWidget(logo_btn)
        theme_layout.addRow("Logo:", logo_row)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # --- API ---
        api_group = QGroupBox("API")
        api_layout = QFormLayout()
        self._gladia_edit = QLineEdit(self._config.get("gladia_api_key", ""))
        self._gladia_edit.setEchoMode(QLineEdit.Password)
        api_layout.addRow("Clé Gladia:", self._gladia_edit)
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        reset_btn = QPushButton("Réinitialiser")
        reset_btn.clicked.connect(self._reset)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        save_btn = QPushButton("Sauvegarder")
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _browse(self, key: str, edit: QLineEdit):
        folder = QFileDialog.getExistingDirectory(self, "Choisir un dossier", edit.text())
        if folder:
            edit.setText(folder)

    def _pick_color(self, key: str, btn: QPushButton):
        current = QColor(self._config["theme"].get(key, "#000"))
        color = QColorDialog.getColor(current, self, f"Choisir {key}")
        if color.isValid():
            hex_color = color.name()
            self._config["theme"][key] = hex_color
            btn.setText(hex_color)
            btn.setStyleSheet(f"background-color: {hex_color}; color: white; border-radius: 4px; padding: 4px;")

    def _pick_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choisir un logo", "", "Images (*.png *.jpg *.svg)")
        if path:
            self._logo_edit.setText(path)

    def _reset(self):
        from app.config.defaults import DEFAULT_CONFIG
        self._config = DEFAULT_CONFIG.copy()
        self._config["theme"] = DEFAULT_CONFIG["theme"].copy()
        # Repopulate all UI fields with defaults
        self._audio_edit.setText(self._config.get("audio_folder", ""))
        self._output_edit.setText(self._config.get("output_folder", ""))
        self._prompt_edit.setPlainText(self._config.get("system_prompt", ""))
        self._lang_combo.setCurrentText(self._config.get("language", "fr"))
        self._gladia_edit.setText("")
        self._logo_edit.setText(self._config.get("logo_path", ""))
        for key, btn in self._color_btns.items():
            color = self._config["theme"].get(key, "#000")
            btn.setText(color)
            btn.setStyleSheet(f"background-color: {color}; color: white; border-radius: 4px; padding: 4px;")

    def get_config(self) -> dict:
        """Return updated config dict."""
        self._config["audio_folder"] = self._audio_edit.text()
        self._config["output_folder"] = self._output_edit.text()
        self._config["system_prompt"] = self._prompt_edit.toPlainText()
        self._config["language"] = self._lang_combo.currentText()
        self._config["gladia_api_key"] = self._gladia_edit.text()
        self._config["logo_path"] = self._logo_edit.text()
        return self._config
```

- [ ] **Step 2: Commit**

```bash
cd C:/Users/User/WORK/MEETINGS
git add app/ui/settings_dialog.py
git commit -m "feat(mon-cr): settings dialog with folders/prompt/theme/API"
```

---

### Task 13: Main window + pipeline worker thread

**Files:**
- Create: `MEETINGS/app/ui/main_window.py`
- Create: `MEETINGS/app/main.py`

This is the final integration task. The main window ties together: scanner, orchestrator (in QThread), progress widget, history panel, settings dialog, theme.

- [ ] **Step 1: Create main_window.py**

Create `app/ui/main_window.py`:
```python
import webbrowser
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap

from app.config.manager import ConfigManager
from app.pipeline.scanner import AudioScanner
from app.pipeline.orchestrator import PipelineOrchestrator, PipelineResult
from app.ui.progress_widget import ProgressWidget
from app.ui.history_panel import HistoryPanel
from app.ui.settings_dialog import SettingsDialog
from app.ui.theme import build_stylesheet
from app.assets import load_logo_b64, load_font_b64


STAGE_INDEX = {"transcription": 0, "summarization": 1, "generation": 2}


class PipelineWorker(QThread):
    """Runs pipeline in background thread."""
    stage_changed = Signal(str, int)   # stage_name, index
    progress = Signal(str)             # status message
    session_complete = Signal(str, list)  # html_output_path, [audio_filenames]
    error = Signal(str, str)           # stage_name, error_message
    finished_all = Signal()            # all sessions done

    def __init__(self, config: dict, sessions: list[dict]):
        super().__init__()
        self._config = config
        self._sessions = sessions

    def run(self):
        # Inject base64 assets into config for HTML generation
        config = self._config.copy()
        config["_logo_b64"] = load_logo_b64()
        config["_font_regular_b64"] = load_font_b64("DMSans-Regular.ttf")
        config["_font_bold_b64"] = load_font_b64("DMSans-Bold.ttf")

        def on_progress(stage, msg):
            idx = STAGE_INDEX.get(stage, 0)
            self.stage_changed.emit(stage, idx)
            self.progress.emit(msg)

        orch = PipelineOrchestrator(config=config, on_progress=on_progress)

        for session in self._sessions:
            result = orch.run(session["files"], date_str=session["date"])
            if result.success and result.output_path:
                filenames = [f.name for f in session["files"]]
                self.session_complete.emit(str(result.output_path), filenames)
            elif not result.success:
                self.error.emit(result.stage_failed, result.error)

        self.finished_all.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mon CR — wslo.lab")
        self.setMinimumSize(480, 640)

        self._config_mgr = ConfigManager(Path(__file__).parent.parent.parent)
        self._config = self._config_mgr.load()
        self._worker: PipelineWorker | None = None

        self._init_ui()
        self._apply_theme()
        self._refresh_state()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header: logo + settings
        header = QHBoxLayout()
        self._logo_label = QLabel()
        logo_path = Path(__file__).parent.parent / "assets" / "logo-wslo.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path)).scaledToHeight(48, Qt.SmoothTransformation)
            self._logo_label.setPixmap(pixmap)
        header.addWidget(self._logo_label)
        header.addStretch()

        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(36, 36)
        settings_btn.clicked.connect(self._open_settings)
        header.addWidget(settings_btn)
        layout.addLayout(header)

        # Separator
        sep = QLabel()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: rgba(255,255,255,0.06);")
        layout.addWidget(sep)

        # Status
        self._status_label = QLabel("● Prêt")
        self._status_label.setObjectName("statusLabel")
        layout.addWidget(self._status_label)

        self._pending_label = QLabel("Fichiers en attente: 0")
        self._pending_label.setObjectName("pendingLabel")
        layout.addWidget(self._pending_label)

        # Generate button
        self._generate_btn = QPushButton("Générer CR")
        self._generate_btn.setObjectName("generateBtn")
        self._generate_btn.setCursor(Qt.PointingHandCursor)
        self._generate_btn.clicked.connect(self._start_pipeline)
        layout.addWidget(self._generate_btn)

        # Progress
        progress_label = QLabel("PROGRESSION")
        progress_label.setObjectName("sectionLabel")
        layout.addWidget(progress_label)
        self._progress = ProgressWidget(theme=self._config.get("theme"))
        layout.addWidget(self._progress)

        # History
        history_label = QLabel("HISTORIQUE")
        history_label.setObjectName("sectionLabel")
        layout.addWidget(history_label)
        self._history = HistoryPanel()
        layout.addWidget(self._history, stretch=1)

    def _apply_theme(self):
        theme = self._config.get("theme", {})
        if theme:
            self.setStyleSheet(build_stylesheet(theme))

    def _refresh_state(self):
        """Scan for pending files and refresh history."""
        history = self._config_mgr.load_history()
        processed = {e["file"] for e in history.get("processed", [])}

        audio_folder = Path(self._config["audio_folder"])
        scanner = AudioScanner(audio_folder, processed)
        self._pending_sessions = scanner.scan_grouped()

        total_files = sum(len(s["files"]) for s in self._pending_sessions)
        self._pending_label.setText(f"Fichiers en attente: {total_files}")

        if total_files == 0:
            self._status_label.setText("● Tout est à jour")
            self._status_label.setStyleSheet("color: #2DD4BF;")
        else:
            self._status_label.setText("● Prêt")
            self._status_label.setStyleSheet("color: #2DD4BF;")

        html_folder = Path(self._config["output_folder"])
        self._history.load(html_folder, history)

    def _start_pipeline(self):
        if not self._pending_sessions:
            self._status_label.setText("● Tout est à jour")
            return

        if not self._config.get("gladia_api_key"):
            QMessageBox.warning(self, "API manquante", "Configurez la clé Gladia dans les paramètres.")
            self._open_settings()
            return

        self._generate_btn.setEnabled(False)
        self._status_label.setText("● En cours...")
        self._status_label.setStyleSheet("color: #8B5CF6;")

        self._worker = PipelineWorker(self._config, self._pending_sessions)
        self._worker.stage_changed.connect(self._on_stage_changed)
        self._worker.progress.connect(self._on_progress)
        self._worker.session_complete.connect(self._on_session_complete)
        self._worker.error.connect(self._on_error)
        self._worker.finished_all.connect(self._on_finished)
        self._worker.start()

    def _on_stage_changed(self, stage: str, index: int):
        self._progress.set_stage(index)

    def _on_progress(self, message: str):
        self._status_label.setText(f"● {message}")

    def _on_session_complete(self, html_path: str, filenames: list):
        # Record only this session's files in history
        for name in filenames:
            self._config_mgr.add_to_history(name, html_path)
        # Open in browser
        webbrowser.open(Path(html_path).as_uri())

    def _on_error(self, stage: str, message: str):
        self._status_label.setText(f"● Erreur ({stage})")
        self._status_label.setStyleSheet("color: #F87171;")
        QMessageBox.critical(self, f"Erreur — {stage}", message)

    def _on_finished(self):
        self._generate_btn.setEnabled(True)
        self._progress.reset()
        self._worker = None
        self._refresh_state()

    def _open_settings(self):
        dlg = SettingsDialog(self._config, self)
        if dlg.exec():
            self._config = dlg.get_config()
            self._config_mgr.save(self._config)
            self._apply_theme()
            self._refresh_state()
```

- [ ] **Step 2: Create main.py entry point**

Create `app/main.py`:
```python
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from app.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Mon CR")
    app.setOrganizationName("wslo.lab")

    # Set app icon
    icon_path = Path(__file__).parent / "assets" / "logo-wslo.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Test manual launch**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m app.main
```
Expected: Window opens with WSLO logo, dark theme, status shows pending count, history shows existing CRs.

- [ ] **Step 4: Commit**

```bash
cd C:/Users/User/WORK/MEETINGS
git add app/ui/main_window.py app/main.py
git commit -m "feat(mon-cr): main window with QThread pipeline, progress, history"
```

---

## Chunk 4: Integration + Polish

### Task 14: Install dependencies + end-to-end test

- [ ] **Step 1: Install PySide6 and requests**

```bash
pip install PySide6 requests
```

- [ ] **Step 2: Run all unit tests**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m pytest tests/ -v
```
Expected: All tests pass (config: 4, config_manager: 8, scanner: 5, transcriber: 2, summarizer: 4, html_generator: 6, orchestrator: 4, theme: 5 = ~38 tests)

- [ ] **Step 3: Manual integration test**

```bash
cd C:/Users/User/WORK/MEETINGS && python -m app.main
```

Verify:
1. Window launches with WSLO.lab logo and dark theme
2. Status shows correct pending file count
3. History shows existing HTML CRs (from old pipeline)
4. Settings dialog opens and saves
5. Close and relaunch — settings persisted

- [ ] **Step 4: Commit**

```bash
cd C:/Users/User/WORK/MEETINGS
git add -A
git commit -m "feat(mon-cr): integration verified, all tests passing"
```

---

### Task 15: Desktop shortcut (optional)

- [ ] **Step 1: Create a .bat launcher**

Create `MEETINGS/MonCR.bat`:
```batch
@echo off
cd /d "%~dp0"
pythonw -m app.main
```

- [ ] **Step 2: Create Windows shortcut on desktop**

```bash
# Create a shortcut pointing to MonCR.bat
# This can be done manually by right-clicking the .bat → Send to → Desktop
# Or via PowerShell:
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Mon CR.lnk'); $sc.TargetPath = 'C:\Users\User\WORK\MEETINGS\MonCR.bat'; $sc.WorkingDirectory = 'C:\Users\User\WORK\MEETINGS'; $sc.IconLocation = 'C:\Users\User\WORK\MEETINGS\app\assets\logo-wslo.png'; $sc.Save()"
```

- [ ] **Step 3: Commit**

```bash
cd C:/Users/User/WORK/MEETINGS
git add MonCR.bat
git commit -m "feat(mon-cr): desktop launcher batch file"
```

---

## Summary

| Task | Component | Tests | Est. |
|------|-----------|-------|------|
| 1 | Config defaults + scaffold | 4 | 5 min |
| 2 | Config manager | 8 | 10 min |
| 3 | Audio scanner | 5 | 8 min |
| 4 | Gladia transcriber | 2 | 8 min |
| 5 | Claude summarizer | 4 | 5 min |
| 6 | HTML generator + template | 6 | 15 min |
| 7 | Pipeline orchestrator | 4 | 10 min |
| 8 | Assets (logo + fonts) | — | 3 min |
| 9 | Theme (QSS builder) | 5 | 5 min |
| 10 | Progress widget | — | 3 min |
| 11 | History panel | — | 5 min |
| 12 | Settings dialog | — | 8 min |
| 13 | Main window + worker | — | 12 min |
| 14 | Integration test | — | 5 min |
| 15 | Desktop shortcut | — | 2 min |
| **Total** | | **~38** | |

**Dependencies between tasks:**
- Tasks 1-3 are sequential (each builds on prior)
- Tasks 4, 5, 6 are independent of each other (can be parallelized)
- Task 7 depends on 4, 5, 6
- Tasks 8, 9 are independent
- Tasks 10, 11, 12 are independent
- Task 13 depends on all prior tasks
- Task 14 depends on 13
- Task 15 depends on 14
