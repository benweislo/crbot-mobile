# CR_BOT Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a white-label desktop app + API proxy that generates branded meeting minutes from audio recordings.

**Architecture:** Four independent subsystems built in order: (1) API proxy with license validation, Gladia transcription relay, and Anthropic summarization relay; (2) Desktop pipeline engine — branding, audio scanning, HTML generation, orchestration; (3) PySide6 desktop UI; (4) PyInstaller packaging and CI/CD.

**Tech Stack:** Python 3.12, FastAPI, httpx, PySide6, anthropic SDK, PyInstaller, pytest, GitHub Actions

**Spec:** `BOTS/CR_BOT/docs/superpowers/specs/2026-03-19-cr-bot-design.md`

**Reference code:** Existing pipeline at `MEETINGS/.skills/meeting-transcriber/scripts/` (transcribe.py, summarize.py, generate_html.py)

---

## File Structure

```
BOTS/CR_BOT/
├── proxy/
│   ├── requirements.txt          ← FastAPI, httpx, uvicorn
│   ├── main.py                   ← FastAPI app, CORS, lifespan
│   ├── config.py                 ← Env vars (API keys, profile storage URL)
│   ├── auth.py                   ← License validation logic
│   ├── rate_limit.py             ← Per-key rate limiting
│   ├── routes/
│   │   ├── auth_routes.py        ← POST /auth/validate
│   │   ├── transcribe_routes.py  ← POST /transcribe (Gladia relay)
│   │   └── summarize_routes.py   ← POST /summarize (Anthropic relay)
│   └── tests/
│       ├── conftest.py           ← FastAPI test client fixture
│       ├── test_auth.py
│       ├── test_transcribe.py
│       ├── test_summarize.py
│       └── test_rate_limit.py
├── app/
│   ├── requirements.txt          ← PySide6, httpx, anthropic
│   ├── main.py                   ← PySide6 entry point
│   ├── config.py                 ← Local settings (paths, proxy URL)
│   ├── pipeline/
│   │   ├── scanner.py            ← Audio file detection, date grouping
│   │   ├── transcribe.py         ← Calls proxy /transcribe
│   │   ├── summarize.py          ← Calls proxy /summarize
│   │   ├── html_generator.py     ← Branded HTML from CR + profile
│   │   ├── orchestrator.py       ← Chains stages, partial progress
│   │   └── html_template.py      ← HTML template string with CSS vars
│   ├── branding/
│   │   ├── profile.py            ← Download/cache brand profile
│   │   └── models.py             ← BrandProfile dataclass
│   ├── auth/
│   │   └── license.py            ← License validation via proxy
│   ├── ui/
│   │   ├── main_window.py        ← Main window layout
│   │   ├── license_dialog.py     ← First-launch license entry
│   │   ├── settings_dialog.py    ← Settings screen
│   │   ├── history_panel.py      ← CR history list
│   │   ├── progress_widget.py    ← 3-step progress bar
│   │   └── theme.py              ← QSS stylesheet from brand colors
│   └── tests/
│       ├── conftest.py
│       ├── test_scanner.py
│       ├── test_html_generator.py
│       ├── test_orchestrator.py
│       ├── test_profile.py
│       └── test_license.py
├── profiles/
│   └── default/
│       ├── brand.json
│       ├── logo.b64
│       ├── font_regular.b64
│       └── font_bold.b64
├── build/
│   ├── cr_bot.spec               ← PyInstaller spec
│   └── build.yml                 ← GitHub Actions workflow
├── .gitignore
└── README.md
```

---

## Chunk 1: Project Setup + API Proxy

### Task 1: Project Scaffolding

**Files:**
- Create: `BOTS/CR_BOT/.gitignore`
- Create: `BOTS/CR_BOT/proxy/requirements.txt`
- Create: `BOTS/CR_BOT/app/requirements.txt`
- Create: `BOTS/CR_BOT/proxy/tests/conftest.py`
- Create: `BOTS/CR_BOT/app/tests/conftest.py`

- [ ] **Step 1: Create .gitignore**

```gitignore
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
dist/
build_output/
.env
proxy/licenses.json
app/.crbot/
.superpowers/
*.spec
```

- [ ] **Step 2: Create proxy requirements.txt**

```
fastapi==0.115.*
uvicorn[standard]==0.34.*
httpx==0.28.*
python-multipart==0.0.*
anthropic==0.52.*
pytest==8.*
pytest-asyncio==0.25.*
```

- [ ] **Step 3: Create app requirements.txt**

```
PySide6==6.8.*
httpx==0.28.*
pytest==8.*
```

- [ ] **Step 4: Create proxy test conftest**

```python
# proxy/tests/conftest.py
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def sample_license_data():
    """Sample license table for testing."""
    return {
        "CRBOT-test-1111-2222-333333333333": {
            "client_id": "client_abc",
            "status": "active",
            "expiry_date": "2027-01-01",
            "profile_url": "https://storage.example.com/profiles/client_abc"
        },
        "CRBOT-test-expired-0000-000000000000": {
            "client_id": "client_expired",
            "status": "active",
            "expiry_date": "2020-01-01",
            "profile_url": ""
        },
        "CRBOT-test-inactive-0000-000000000000": {
            "client_id": "client_inactive",
            "status": "inactive",
            "expiry_date": "2027-01-01",
            "profile_url": ""
        }
    }
```

- [ ] **Step 5: Create app test conftest**

```python
# app/tests/conftest.py
import pytest
from pathlib import Path
import tempfile


@pytest.fixture
def tmp_dir():
    """Temporary directory for test files."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def sample_brand():
    """Sample brand profile dict."""
    return {
        "company_name": "Test Corp",
        "primary_color": "#2563EB",
        "secondary_color": "#7C3AED",
        "background_color": "#0A0A0F",
        "text_color": "#E5E5E5",
        "font_family": "TestFont",
        "footer_text": "Test Corp — CR auto",
        "language": "fr",
        "context": "Test Corp est une agence digitale.",
        "cr_sections": {"summary": True, "detailed": True}
    }
```

- [ ] **Step 6: Install proxy dependencies and verify**

Run: `cd BOTS/CR_BOT/proxy && pip install -r requirements.txt`
Expected: All packages install successfully

- [ ] **Step 7: Install app dependencies and verify**

Run: `cd BOTS/CR_BOT/app && pip install -r requirements.txt`
Expected: All packages install successfully

- [ ] **Step 8: Commit**

```bash
git add BOTS/CR_BOT/.gitignore BOTS/CR_BOT/proxy/requirements.txt BOTS/CR_BOT/app/requirements.txt BOTS/CR_BOT/proxy/tests/conftest.py BOTS/CR_BOT/app/tests/conftest.py
git commit -m "feat(cr_bot): project scaffolding with proxy and app requirements"
```

---

### Task 2: Proxy Config + License Validation Module

**Files:**
- Create: `BOTS/CR_BOT/proxy/config.py`
- Create: `BOTS/CR_BOT/proxy/auth.py`
- Create: `BOTS/CR_BOT/proxy/tests/test_auth.py`

- [ ] **Step 1: Write failing tests for license validation**

```python
# proxy/tests/test_auth.py
import pytest
from proxy.auth import LicenseManager


class TestLicenseManager:
    def test_valid_active_license(self, sample_license_data, tmp_path):
        path = tmp_path / "licenses.json"
        import json
        path.write_text(json.dumps(sample_license_data))
        mgr = LicenseManager(path)
        result = mgr.validate("CRBOT-test-1111-2222-333333333333")
        assert result is not None
        assert result["client_id"] == "client_abc"
        assert result["valid"] is True

    def test_expired_license(self, sample_license_data, tmp_path):
        path = tmp_path / "licenses.json"
        import json
        path.write_text(json.dumps(sample_license_data))
        mgr = LicenseManager(path)
        result = mgr.validate("CRBOT-test-expired-0000-000000000000")
        assert result["valid"] is False
        assert "expired" in result.get("reason", "").lower()

    def test_inactive_license(self, sample_license_data, tmp_path):
        path = tmp_path / "licenses.json"
        import json
        path.write_text(json.dumps(sample_license_data))
        mgr = LicenseManager(path)
        result = mgr.validate("CRBOT-test-inactive-0000-000000000000")
        assert result["valid"] is False

    def test_unknown_key(self, sample_license_data, tmp_path):
        path = tmp_path / "licenses.json"
        import json
        path.write_text(json.dumps(sample_license_data))
        mgr = LicenseManager(path)
        result = mgr.validate("CRBOT-unknown-0000-0000-000000000000")
        assert result["valid"] is False

    def test_missing_file_raises(self, tmp_path):
        path = tmp_path / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            LicenseManager(path)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd BOTS/CR_BOT && python -m pytest proxy/tests/test_auth.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'proxy.auth'`

- [ ] **Step 3: Create proxy config**

```python
# proxy/config.py
import os

GLADIA_API_KEY = os.environ.get("GLADIA_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
PROFILE_STORAGE_URL = os.environ.get("PROFILE_STORAGE_URL", "")
LICENSE_FILE = os.environ.get("LICENSE_FILE", "licenses.json")
```

- [ ] **Step 4: Implement LicenseManager**

```python
# proxy/auth.py
import json
from datetime import date
from pathlib import Path


class LicenseManager:
    def __init__(self, license_file: Path):
        if not license_file.exists():
            raise FileNotFoundError(f"License file not found: {license_file}")
        self._path = license_file
        self._load()

    def _load(self):
        self._licenses = json.loads(self._path.read_text(encoding="utf-8"))

    def validate(self, key: str) -> dict:
        """Validate a license key. Returns dict with 'valid', 'client_id', optionally 'reason'."""
        entry = self._licenses.get(key)
        if entry is None:
            return {"valid": False, "reason": "Unknown license key"}

        if entry.get("status") != "active":
            return {"valid": False, "reason": "License inactive"}

        expiry = entry.get("expiry_date", "")
        if expiry and date.fromisoformat(expiry) < date.today():
            return {"valid": False, "reason": "License expired"}

        return {
            "valid": True,
            "client_id": entry["client_id"],
            "profile_url": entry.get("profile_url", ""),
        }
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd BOTS/CR_BOT && python -m pytest proxy/tests/test_auth.py -v`
Expected: 5 passed

- [ ] **Step 6: Commit**

```bash
git add BOTS/CR_BOT/proxy/config.py BOTS/CR_BOT/proxy/auth.py BOTS/CR_BOT/proxy/tests/test_auth.py
git commit -m "feat(cr_bot): license validation module with tests"
```

---

### Task 3: Auth Endpoint + FastAPI App

**Files:**
- Create: `BOTS/CR_BOT/proxy/main.py`
- Create: `BOTS/CR_BOT/proxy/routes/auth_routes.py`

- [ ] **Step 1: Write failing test for /auth/validate endpoint**

Add to `proxy/tests/test_auth.py`:

```python
# Add at the top of the file:
from fastapi.testclient import TestClient
import json as json_module

class TestAuthEndpoint:
    def _make_app(self, tmp_path, license_data):
        """Create a FastAPI app with test license data."""
        path = tmp_path / "licenses.json"
        path.write_text(json_module.dumps(license_data))
        import os
        os.environ["LICENSE_FILE"] = str(path)
        # Force reimport to pick up new env
        from proxy.main import create_app
        app = create_app(license_file=path)
        return TestClient(app)

    def test_validate_valid_key(self, sample_license_data, tmp_path):
        client = self._make_app(tmp_path, sample_license_data)
        resp = client.post("/auth/validate", json={"license_key": "CRBOT-test-1111-2222-333333333333"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is True
        assert data["client_id"] == "client_abc"

    def test_validate_invalid_key(self, sample_license_data, tmp_path):
        client = self._make_app(tmp_path, sample_license_data)
        resp = client.post("/auth/validate", json={"license_key": "CRBOT-fake-0000"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd BOTS/CR_BOT && python -m pytest proxy/tests/test_auth.py::TestAuthEndpoint -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'proxy.main'`

- [ ] **Step 3: Create FastAPI app factory**

```python
# proxy/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from proxy.auth import LicenseManager


def create_app(license_file: Path | None = None) -> FastAPI:
    if license_file is None:
        from proxy.config import LICENSE_FILE
        license_file = Path(LICENSE_FILE)

    license_mgr = LicenseManager(license_file)

    app = FastAPI(title="CR_BOT Proxy")
    app.state.license_mgr = license_mgr

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["POST"],
        allow_headers=["*"],
    )

    from proxy.routes.auth_routes import router as auth_router
    app.include_router(auth_router)

    return app
```

- [ ] **Step 4: Create auth routes**

```python
# proxy/routes/auth_routes.py
from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class ValidateRequest(BaseModel):
    license_key: str


@router.post("/auth/validate")
async def validate_license(req: ValidateRequest, request: Request):
    mgr = request.app.state.license_mgr
    result = mgr.validate(req.license_key)
    return result
```

- [ ] **Step 5: Create `__init__.py` files for proper imports**

Create empty `proxy/__init__.py`, `proxy/routes/__init__.py`, `proxy/tests/__init__.py`.

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd BOTS/CR_BOT && python -m pytest proxy/tests/test_auth.py -v`
Expected: 7 passed (5 unit + 2 endpoint)

- [ ] **Step 7: Commit**

```bash
git add BOTS/CR_BOT/proxy/main.py BOTS/CR_BOT/proxy/routes/auth_routes.py BOTS/CR_BOT/proxy/__init__.py BOTS/CR_BOT/proxy/routes/__init__.py BOTS/CR_BOT/proxy/tests/__init__.py BOTS/CR_BOT/proxy/tests/test_auth.py
git commit -m "feat(cr_bot): /auth/validate endpoint with FastAPI"
```

---

### Task 4: Transcription Endpoint (Gladia Relay)

**Files:**
- Create: `BOTS/CR_BOT/proxy/routes/transcribe_routes.py`
- Create: `BOTS/CR_BOT/proxy/tests/test_transcribe.py`

**Key design:** The proxy receives the audio file via multipart upload, relays it to Gladia's upload endpoint, starts transcription, polls until done, and returns the structured transcript. The proxy uses `httpx` for async streaming.

**Gladia flow (from existing transcribe.py):**
1. `POST https://api.gladia.io/v2/upload` with audio file → get `audio_url`
2. `POST https://api.gladia.io/v2/transcription` with `{audio_url, diarization: true, language}` → get `result_url`
3. `GET result_url` polling until `status == "done"` → get utterances

- [ ] **Step 1: Write failing tests**

```python
# proxy/tests/test_transcribe.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd BOTS/CR_BOT && python -m pytest proxy/tests/test_transcribe.py -v`
Expected: FAIL

- [ ] **Step 3: Implement transcribe route**

```python
# proxy/routes/transcribe_routes.py
import asyncio
import httpx
import logging
from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException

from proxy.config import GLADIA_API_KEY

router = APIRouter()
logger = logging.getLogger(__name__)

GLADIA_UPLOAD_URL = "https://api.gladia.io/v2/upload"
GLADIA_TRANSCRIPTION_URL = "https://api.gladia.io/v2/transcription"
POLL_INTERVAL = 5  # seconds
MAX_POLL_ATTEMPTS = 120  # 10 minutes max


async def relay_to_gladia(audio_bytes: bytes, filename: str, language: str = "fr") -> dict:
    """Upload audio to Gladia, start transcription, poll until done."""
    headers = {"x-gladia-key": GLADIA_API_KEY}

    async with httpx.AsyncClient(timeout=600) as client:
        # Step 1: Upload audio
        upload_resp = await client.post(
            GLADIA_UPLOAD_URL,
            headers=headers,
            files={"audio": (filename, audio_bytes, "audio/mpeg")},
        )
        if upload_resp.status_code != 200:
            raise HTTPException(502, f"Gladia upload failed: {upload_resp.status_code}")

        audio_url = upload_resp.json().get("audio_url")

        # Step 2: Start transcription
        trans_resp = await client.post(
            GLADIA_TRANSCRIPTION_URL,
            headers=headers,
            json={"audio_url": audio_url, "diarization": True, "language": language},
        )
        if trans_resp.status_code != 201:
            raise HTTPException(502, f"Gladia transcription failed: {trans_resp.status_code}")

        result_url = trans_resp.json().get("result_url")

        # Step 3: Poll for results
        for _ in range(MAX_POLL_ATTEMPTS):
            poll_resp = await client.get(result_url, headers=headers)
            poll_data = poll_resp.json()
            status = poll_data.get("status")

            if status == "done":
                break
            elif status == "error":
                raise HTTPException(502, "Gladia processing error")

            await asyncio.sleep(POLL_INTERVAL)
        else:
            raise HTTPException(504, "Gladia transcription timed out")

    # Parse utterances
    utterances = poll_data.get("result", {}).get("transcription", {}).get("utterances", [])
    segments = []
    full_text_parts = []

    for u in utterances:
        speaker = f"Speaker {u.get('speaker', '?')}"
        text = u.get("text", "").strip()
        segments.append({
            "start": u.get("start", 0.0),
            "end": u.get("end", 0.0),
            "speaker": speaker,
            "text": text,
        })
        full_text_parts.append(f"[{speaker}] {text}")

    duration = segments[-1]["end"] if segments else 0.0

    return {
        "segments": segments,
        "full_text": "\n".join(full_text_parts),
        "duration_seconds": duration,
    }


@router.post("/transcribe")
async def transcribe(
    request: Request,
    license_key: str = Form(...),
    audio: UploadFile = File(...),
    language: str = Form("fr"),
):
    # Validate license
    mgr = request.app.state.license_mgr
    auth = mgr.validate(license_key)
    if not auth["valid"]:
        raise HTTPException(403, auth.get("reason", "Invalid license"))

    logger.info(f"Transcribe request from {auth['client_id']}: {audio.filename}")

    # Note: reads full file into memory. For very large files (>500MB),
    # consider streaming via httpx. Acceptable for typical meeting audio (<200MB).
    audio_bytes = await audio.read()
    result = await relay_to_gladia(audio_bytes, audio.filename or "audio.mp3", language)

    logger.info(f"Transcription complete for {auth['client_id']}: {result['duration_seconds']:.0f}s audio")
    return result
```

- [ ] **Step 4: Register transcribe router in main.py**

Add to `proxy/main.py` in `create_app()`:

```python
    from proxy.routes.transcribe_routes import router as transcribe_router
    app.include_router(transcribe_router)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd BOTS/CR_BOT && python -m pytest proxy/tests/test_transcribe.py -v`
Expected: 2 passed

- [ ] **Step 6: Commit**

```bash
git add BOTS/CR_BOT/proxy/routes/transcribe_routes.py BOTS/CR_BOT/proxy/tests/test_transcribe.py BOTS/CR_BOT/proxy/main.py
git commit -m "feat(cr_bot): /transcribe endpoint with Gladia relay"
```

---

### Task 5: Summarization Endpoint (Anthropic Relay)

**Files:**
- Create: `BOTS/CR_BOT/proxy/routes/summarize_routes.py`
- Create: `BOTS/CR_BOT/proxy/tests/test_summarize.py`

- [ ] **Step 1: Write failing tests**

```python
# proxy/tests/test_summarize.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd BOTS/CR_BOT && python -m pytest proxy/tests/test_summarize.py -v`
Expected: FAIL

- [ ] **Step 3: Implement summarize route**

```python
# proxy/routes/summarize_routes.py
import logging
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, field_validator

from proxy.config import ANTHROPIC_API_KEY

router = APIRouter()
logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """Tu es un assistant expert en rédaction de comptes rendus professionnels.
On te fournit la transcription d'une réunion. Tu dois générer un Compte Rendu (CR) structuré en respectant **exactement** le format suivant.

{context_block}

Rédige en {language}.

============================================================
COMPTE RENDU DE RÉUNION
============================================================

  Date     : {{date}}
  Durée    : {{durée}}

------------------------------------------------------------
THÈMES ABORDÉS
------------------------------------------------------------
  • [Thème 1]
  • [Thème 2]
  (Liste courte, à puces, des grands sujets abordés)

------------------------------------------------------------
ACTIONS / PROCHAINES ÉTAPES
------------------------------------------------------------

  Pour chaque personne identifiée, liste ses actions spécifiques :

  **[Nom/Speaker]:**
  1. [Action claire et précise]
  2. [Action]

  **[Nom/Speaker 2]:**
  1. [Action]

------------------------------------------------------------
CONCLUSION DU MEETING
------------------------------------------------------------
  → [Résumé global de la fin de la réunion et du sentiment général]

------------------------------------------------------------
TOUT EN DÉTAILS
------------------------------------------------------------
[Détaille rigoureusement chaque thème abordé :
 - Ce qui a été discuté exactement (idées, débats, propositions).
 - Le détail des actions à mener (qui fait quoi, comment, pourquoi).
 - Fais des paragraphes numérotés et organisés par thème.
 - Cite ce qu'ont dit les speakers de façon lisible et digeste.
 - Sois exhaustif mais concis. N'invente rien.]

============================================================
FIN DU COMPTE RENDU
============================================================"""


def build_system_prompt(context: str = "", language: str = "français") -> str:
    context_block = ""
    if context:
        context_block = f"Contexte de l'entreprise : {context}\nUtilise ce contexte pour mieux comprendre les termes techniques et les rôles des participants."
    return SYSTEM_PROMPT_TEMPLATE.format(context_block=context_block, language=language)


async def call_anthropic(transcript: str, context: str = "", language: str = "fr") -> str:
    """Call Anthropic API to summarize transcript."""
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    lang_map = {"fr": "français", "en": "English", "es": "español"}
    lang_name = lang_map.get(language, "français")

    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        temperature=0.3,
        system=build_system_prompt(context, lang_name),
        messages=[
            {"role": "user", "content": f"Voici la transcription complète de la réunion :\n\n{transcript}"}
        ],
    )
    return message.content[0].text


class SummarizeRequest(BaseModel):
    license_key: str
    transcript: str
    context: str = ""
    language: str = "fr"

    @field_validator("transcript")
    @classmethod
    def transcript_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Transcript cannot be empty")
        return v


@router.post("/summarize")
async def summarize(req: SummarizeRequest, request: Request):
    # Validate license
    mgr = request.app.state.license_mgr
    auth = mgr.validate(req.license_key)
    if not auth["valid"]:
        raise HTTPException(403, auth.get("reason", "Invalid license"))

    logger.info(f"Summarize request from {auth['client_id']}: {len(req.transcript)} chars")

    summary = await call_anthropic(req.transcript, req.context, req.language)

    logger.info(f"Summary complete for {auth['client_id']}: {len(summary)} chars output")
    return {"summary": summary}
```

- [ ] **Step 4: Register summarize router in main.py**

Add to `proxy/main.py` in `create_app()`:

```python
    from proxy.routes.summarize_routes import router as summarize_router
    app.include_router(summarize_router)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd BOTS/CR_BOT && python -m pytest proxy/tests/test_summarize.py -v`
Expected: 3 passed

- [ ] **Step 6: Commit**

```bash
git add BOTS/CR_BOT/proxy/routes/summarize_routes.py BOTS/CR_BOT/proxy/tests/test_summarize.py BOTS/CR_BOT/proxy/main.py
git commit -m "feat(cr_bot): /summarize endpoint with Anthropic Claude relay"
```

---

### Task 6: Rate Limiting Middleware

**Files:**
- Create: `BOTS/CR_BOT/proxy/rate_limit.py`
- Create: `BOTS/CR_BOT/proxy/tests/test_rate_limit.py`

- [ ] **Step 1: Write failing tests**

```python
# proxy/tests/test_rate_limit.py
import pytest
import time
from proxy.rate_limit import RateLimiter


class TestRateLimiter:
    def test_allows_under_limit(self):
        limiter = RateLimiter(max_per_minute=5, max_per_day=100)
        for _ in range(5):
            assert limiter.check("key1") is True

    def test_blocks_over_minute_limit(self):
        limiter = RateLimiter(max_per_minute=2, max_per_day=100)
        assert limiter.check("key1") is True
        assert limiter.check("key1") is True
        assert limiter.check("key1") is False

    def test_different_keys_independent(self):
        limiter = RateLimiter(max_per_minute=1, max_per_day=100)
        assert limiter.check("key1") is True
        assert limiter.check("key2") is True
        assert limiter.check("key1") is False

    def test_blocks_over_day_limit(self):
        limiter = RateLimiter(max_per_minute=100, max_per_day=2)
        assert limiter.check("key1") is True
        assert limiter.check("key1") is True
        assert limiter.check("key1") is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd BOTS/CR_BOT && python -m pytest proxy/tests/test_rate_limit.py -v`
Expected: FAIL

- [ ] **Step 3: Implement RateLimiter**

```python
# proxy/rate_limit.py
import time
from collections import defaultdict


class RateLimiter:
    """Simple in-memory rate limiter per key. Not persistent across restarts."""

    def __init__(self, max_per_minute: int = 10, max_per_day: int = 50):
        self.max_per_minute = max_per_minute
        self.max_per_day = max_per_day
        self._minute_windows: dict[str, list[float]] = defaultdict(list)
        self._day_windows: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str) -> bool:
        """Check if key is within rate limits. Records the attempt if allowed."""
        now = time.time()
        minute_ago = now - 60
        day_ago = now - 86400

        # Clean old entries
        self._minute_windows[key] = [t for t in self._minute_windows[key] if t > minute_ago]
        self._day_windows[key] = [t for t in self._day_windows[key] if t > day_ago]

        if len(self._minute_windows[key]) >= self.max_per_minute:
            return False
        if len(self._day_windows[key]) >= self.max_per_day:
            return False

        self._minute_windows[key].append(now)
        self._day_windows[key].append(now)
        return True
```

- [ ] **Step 4: Integrate rate limiter into proxy main.py**

Update `proxy/main.py` — add rate limiter to app state:

```python
from proxy.rate_limit import RateLimiter

# In create_app():
    app.state.rate_limiter = RateLimiter(max_per_minute=10, max_per_day=50)
```

Update `proxy/routes/transcribe_routes.py` and `proxy/routes/summarize_routes.py` — add rate check after license validation:

```python
    # After license validation, before processing:
    if not request.app.state.rate_limiter.check(license_key):
        raise HTTPException(429, "Rate limit exceeded")
```

- [ ] **Step 5: Run all proxy tests**

Run: `cd BOTS/CR_BOT && python -m pytest proxy/tests/ -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add BOTS/CR_BOT/proxy/rate_limit.py BOTS/CR_BOT/proxy/tests/test_rate_limit.py BOTS/CR_BOT/proxy/main.py BOTS/CR_BOT/proxy/routes/transcribe_routes.py BOTS/CR_BOT/proxy/routes/summarize_routes.py
git commit -m "feat(cr_bot): rate limiting middleware (10/min, 50/day per key)"
```

---

## Chunk 2: Desktop App — Pipeline Engine

### Task 7: Brand Profile Manager

**Files:**
- Create: `BOTS/CR_BOT/app/branding/models.py`
- Create: `BOTS/CR_BOT/app/branding/profile.py`
- Create: `BOTS/CR_BOT/app/tests/test_profile.py`
- Create: `BOTS/CR_BOT/app/__init__.py`
- Create: `BOTS/CR_BOT/app/branding/__init__.py`
- Create: `BOTS/CR_BOT/app/tests/__init__.py`

- [ ] **Step 1: Write failing tests**

```python
# app/tests/test_profile.py
import json
import pytest
from pathlib import Path

from app.branding.models import BrandProfile
from app.branding.profile import ProfileManager


class TestBrandProfile:
    def test_from_dict(self, sample_brand):
        profile = BrandProfile.from_dict(sample_brand)
        assert profile.company_name == "Test Corp"
        assert profile.primary_color == "#2563EB"

    def test_defaults_for_missing_fields(self):
        minimal = {"company_name": "Minimal"}
        profile = BrandProfile.from_dict(minimal)
        assert profile.primary_color == "#6e3ea8"  # default violet
        assert profile.language == "fr"


class TestProfileManager:
    def test_load_from_local_cache(self, tmp_dir, sample_brand):
        cache_dir = tmp_dir / ".crbot" / "profile"
        cache_dir.mkdir(parents=True)
        (cache_dir / "brand.json").write_text(json.dumps(sample_brand))
        (cache_dir / "logo.b64").write_text("FAKELOGO")
        (cache_dir / "font_regular.b64").write_text("FAKEFONT")
        (cache_dir / "font_bold.b64").write_text("FAKEFONTBOLD")

        mgr = ProfileManager(cache_dir=cache_dir)
        profile = mgr.load_cached()
        assert profile is not None
        assert profile.company_name == "Test Corp"
        assert profile.logo_b64 == "FAKELOGO"

    def test_no_cache_returns_none(self, tmp_dir):
        mgr = ProfileManager(cache_dir=tmp_dir / "nonexistent")
        assert mgr.load_cached() is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd BOTS/CR_BOT && python -m pytest app/tests/test_profile.py -v`
Expected: FAIL

- [ ] **Step 3: Implement BrandProfile dataclass**

```python
# app/branding/models.py
from dataclasses import dataclass, field


@dataclass
class BrandProfile:
    company_name: str = "Company"
    primary_color: str = "#6e3ea8"
    secondary_color: str = "#E93F7F"
    background_color: str = "#050505"
    text_color: str = "#E5E5E5"
    font_family: str = "CeraPro"
    footer_text: str = "Compte rendu généré automatiquement"
    language: str = "fr"
    context: str = ""
    logo_b64: str = ""
    font_regular_b64: str = ""
    font_bold_b64: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "BrandProfile":
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)
```

- [ ] **Step 4: Implement ProfileManager**

```python
# app/branding/profile.py
import json
import httpx
from pathlib import Path

from app.branding.models import BrandProfile


class ProfileManager:
    def __init__(self, cache_dir: Path):
        self._cache_dir = cache_dir

    def load_cached(self) -> BrandProfile | None:
        """Load profile from local cache. Returns None if not cached."""
        brand_path = self._cache_dir / "brand.json"
        if not brand_path.exists():
            return None

        data = json.loads(brand_path.read_text(encoding="utf-8"))
        profile = BrandProfile.from_dict(data)

        # Load assets
        logo_path = self._cache_dir / "logo.b64"
        if logo_path.exists():
            profile.logo_b64 = logo_path.read_text(encoding="utf-8").strip()

        font_reg_path = self._cache_dir / "font_regular.b64"
        if font_reg_path.exists():
            profile.font_regular_b64 = font_reg_path.read_text(encoding="utf-8").strip()

        font_bold_path = self._cache_dir / "font_bold.b64"
        if font_bold_path.exists():
            profile.font_bold_b64 = font_bold_path.read_text(encoding="utf-8").strip()

        return profile

    def download_and_cache(self, profile_url: str) -> BrandProfile:
        """Download profile from remote URL and cache locally."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        with httpx.Client(timeout=30) as client:
            # Download brand.json
            resp = client.get(f"{profile_url}/brand.json")
            resp.raise_for_status()
            brand_data = resp.json()
            (self._cache_dir / "brand.json").write_text(
                json.dumps(brand_data, indent=2), encoding="utf-8"
            )

            # Download assets (optional, don't fail if missing)
            for asset in ["logo.b64", "font_regular.b64", "font_bold.b64"]:
                try:
                    asset_resp = client.get(f"{profile_url}/{asset}")
                    asset_resp.raise_for_status()
                    (self._cache_dir / asset).write_text(
                        asset_resp.text.strip(), encoding="utf-8"
                    )
                except httpx.HTTPError:
                    pass  # Asset optional

        return self.load_cached()
```

- [ ] **Step 5: Create __init__.py files**

Create empty `app/__init__.py`, `app/branding/__init__.py`, `app/tests/__init__.py`.

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd BOTS/CR_BOT && python -m pytest app/tests/test_profile.py -v`
Expected: 3 passed

- [ ] **Step 7: Commit**

```bash
git add BOTS/CR_BOT/app/branding/ BOTS/CR_BOT/app/tests/test_profile.py BOTS/CR_BOT/app/__init__.py BOTS/CR_BOT/app/tests/__init__.py
git commit -m "feat(cr_bot): brand profile manager with caching"
```

---

### Task 8: Audio File Scanner

**Files:**
- Create: `BOTS/CR_BOT/app/pipeline/__init__.py`
- Create: `BOTS/CR_BOT/app/pipeline/scanner.py`
- Create: `BOTS/CR_BOT/app/tests/test_scanner.py`

- [ ] **Step 1: Write failing tests**

```python
# app/tests/test_scanner.py
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
        # Find the March 19 group
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd BOTS/CR_BOT && python -m pytest app/tests/test_scanner.py -v`
Expected: FAIL

- [ ] **Step 3: Implement AudioScanner**

```python
# app/pipeline/scanner.py
import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".wma", ".aac", ".webm"}


@dataclass
class AudioGroup:
    date_str: str  # "DD/MM/YYYY"
    files: list[Path] = field(default_factory=list)
    is_today: bool = False


class AudioScanner:
    def __init__(self, audio_dir: Path, history_file: Path):
        self._audio_dir = audio_dir
        self._history_file = history_file
        self._processed: set[str] = set()
        self._load_history()

    def _load_history(self):
        if self._history_file.exists():
            data = json.loads(self._history_file.read_text(encoding="utf-8"))
            self._processed = set(data.get("processed", []))

    def _save_history(self):
        self._history_file.parent.mkdir(parents=True, exist_ok=True)
        self._history_file.write_text(
            json.dumps({"processed": sorted(self._processed)}),
            encoding="utf-8",
        )

    def scan_unprocessed(self) -> list[Path]:
        """Return audio files in the audio dir that haven't been processed yet."""
        files = []
        for f in sorted(self._audio_dir.iterdir()):
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
                if str(f) not in self._processed:
                    files.append(f)
        return files

    def mark_processed(self, path: Path):
        """Mark a file as processed so it won't appear in future scans."""
        self._processed.add(str(path))
        self._save_history()

    def group_by_date(self, files: list[Path]) -> list[AudioGroup]:
        """Group files by calendar day, detected from filename or mtime."""
        groups: dict[str, AudioGroup] = {}
        today_str = date.today().strftime("%d/%m/%Y")

        for f in files:
            date_str = self._extract_date(f)
            if date_str not in groups:
                groups[date_str] = AudioGroup(
                    date_str=date_str,
                    is_today=(date_str == today_str),
                )
            groups[date_str].files.append(f)

        # Sort files within each group chronologically
        for g in groups.values():
            g.files.sort(key=lambda p: p.name)

        return sorted(groups.values(), key=lambda g: g.date_str, reverse=True)

    def _extract_date(self, path: Path) -> str:
        """Extract date from filename. Falls back to file modification date."""
        name = path.name

        # Pattern 1: YYYY_MM_DD_*
        m = re.match(r"(\d{4})_(\d{2})_(\d{2})", name)
        if m:
            return f"{m.group(3)}/{m.group(2)}/{m.group(1)}"

        # Pattern 2: AudioCapturer_YYYYMMDD*
        m = re.match(r"AudioCapturer_(\d{4})(\d{2})(\d{2})", name)
        if m:
            return f"{m.group(3)}/{m.group(2)}/{m.group(1)}"

        # Fallback: file modification date
        mtime = path.stat().st_mtime
        from datetime import datetime
        return datetime.fromtimestamp(mtime).strftime("%d/%m/%Y")
```

- [ ] **Step 4: Create pipeline __init__.py**

Create empty `app/pipeline/__init__.py`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd BOTS/CR_BOT && python -m pytest app/tests/test_scanner.py -v`
Expected: 5 passed

- [ ] **Step 6: Commit**

```bash
git add BOTS/CR_BOT/app/pipeline/scanner.py BOTS/CR_BOT/app/pipeline/__init__.py BOTS/CR_BOT/app/tests/test_scanner.py
git commit -m "feat(cr_bot): audio file scanner with date grouping and history"
```

---

### Task 9: HTML Generator (Branded Template)

**Files:**
- Create: `BOTS/CR_BOT/app/pipeline/html_template.py`
- Create: `BOTS/CR_BOT/app/pipeline/html_generator.py`
- Create: `BOTS/CR_BOT/app/tests/test_html_generator.py`

**Key design:** The HTML template uses CSS custom properties (variables) injected from the brand profile. The generator parses the structured CR text (same format as existing MEETINGS pipeline) and fills the template.

- [ ] **Step 1: Write failing tests**

```python
# app/tests/test_html_generator.py
import pytest
from pathlib import Path

from app.branding.models import BrandProfile
from app.pipeline.html_generator import HtmlGenerator


SAMPLE_CR = """============================================================
COMPTE RENDU DE RÉUNION
============================================================

  Date     : 19/03/2026
  Durée    : 45 minutes

------------------------------------------------------------
THÈMES ABORDÉS
------------------------------------------------------------
  • Budget Q2
  • Recrutement développeur

------------------------------------------------------------
ACTIONS / PROCHAINES ÉTAPES
------------------------------------------------------------

  **Marie:**
  1. Envoyer le budget révisé avant vendredi

  **Jean-Pierre:**
  1. Publier l'offre d'emploi sur LinkedIn

------------------------------------------------------------
CONCLUSION DU MEETING
------------------------------------------------------------
  → Réunion productive, prochaine étape vendredi.

------------------------------------------------------------
TOUT EN DÉTAILS
------------------------------------------------------------

1. Budget Q2

Le budget a été revu à la hausse de 15% pour intégrer les coûts serveur.

2. Recrutement développeur

Jean-Pierre va publier une offre pour un dev Python senior.

============================================================
FIN DU COMPTE RENDU
============================================================"""


class TestHtmlGenerator:
    def test_generates_valid_html(self, sample_brand):
        profile = BrandProfile.from_dict(sample_brand)
        gen = HtmlGenerator(profile)
        html = gen.generate(SAMPLE_CR)
        assert "<!DOCTYPE html>" in html
        assert "Test Corp" in html

    def test_contains_brand_colors(self, sample_brand):
        profile = BrandProfile.from_dict(sample_brand)
        gen = HtmlGenerator(profile)
        html = gen.generate(SAMPLE_CR)
        assert "#2563EB" in html  # primary color

    def test_contains_themes(self, sample_brand):
        profile = BrandProfile.from_dict(sample_brand)
        gen = HtmlGenerator(profile)
        html = gen.generate(SAMPLE_CR)
        assert "Budget Q2" in html
        assert "Recrutement" in html

    def test_contains_actions(self, sample_brand):
        profile = BrandProfile.from_dict(sample_brand)
        gen = HtmlGenerator(profile)
        html = gen.generate(SAMPLE_CR)
        assert "Marie" in html
        assert "budget révisé" in html

    def test_has_tab_switching(self, sample_brand):
        profile = BrandProfile.from_dict(sample_brand)
        gen = HtmlGenerator(profile)
        html = gen.generate(SAMPLE_CR)
        assert "tab-resume" in html or "tab-summary" in html
        assert "tab-detail" in html

    def test_self_contained(self, sample_brand):
        profile = BrandProfile.from_dict(sample_brand)
        gen = HtmlGenerator(profile)
        html = gen.generate(SAMPLE_CR)
        # No external links
        assert "http://" not in html.replace("<!DOCTYPE html>", "")
        assert "https://" not in html

    def test_saves_to_file(self, sample_brand, tmp_dir):
        profile = BrandProfile.from_dict(sample_brand)
        gen = HtmlGenerator(profile)
        out = tmp_dir / "test_cr.html"
        gen.generate_to_file(SAMPLE_CR, out)
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd BOTS/CR_BOT && python -m pytest app/tests/test_html_generator.py -v`
Expected: FAIL

- [ ] **Step 3: Create HTML template**

```python
# app/pipeline/html_template.py
"""
HTML template for branded CR output.
Uses CSS custom properties for brand colors.
Contains two tabs: Résumé and Détaillé.
Self-contained: all fonts, logos, and styles inline.
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="{language}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Compte Rendu — {company_name}</title>
<style>
@font-face {{
    font-family: '{font_family}';
    src: url(data:font/woff2;base64,{font_regular_b64}) format('woff2');
    font-weight: 400;
}}
@font-face {{
    font-family: '{font_family}';
    src: url(data:font/woff2;base64,{font_bold_b64}) format('woff2');
    font-weight: 700;
}}

:root {{
    --primary: {primary_color};
    --secondary: {secondary_color};
    --bg: {background_color};
    --text: {text_color};
    --card-bg: rgba(255,255,255,0.04);
    --card-border: rgba(255,255,255,0.08);
}}

* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    background: var(--bg);
    color: var(--text);
    font-family: '{font_family}', -apple-system, sans-serif;
    line-height: 1.7;
    min-height: 100vh;
}}

/* Bokeh */
.bokeh {{
    position: fixed; top:0; left:0; width:100%; height:100%;
    pointer-events: none; z-index:0; overflow:hidden;
}}
.bokeh .orb {{
    position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.15;
    animation: float 20s ease-in-out infinite;
}}
.orb:nth-child(1) {{ width:400px; height:400px; background:var(--primary); top:10%; left:20%; }}
.orb:nth-child(2) {{ width:300px; height:300px; background:var(--secondary); top:50%; right:10%; animation-delay:-7s; }}
.orb:nth-child(3) {{ width:350px; height:350px; background:var(--primary); bottom:10%; left:50%; animation-delay:-14s; }}
@keyframes float {{
    0%,100% {{ transform: translate(0,0); }}
    33% {{ transform: translate(30px,-20px); }}
    66% {{ transform: translate(-20px,30px); }}
}}

/* Film grain */
.grain {{
    position: fixed; top:0; left:0; width:100%; height:100%;
    pointer-events: none; z-index:1; opacity:0.03;
}}
.grain svg {{ width:100%; height:100%; }}

/* Vignette */
.vignette {{
    position: fixed; top:0; left:0; width:100%; height:100%;
    pointer-events: none; z-index:1;
    background: radial-gradient(ellipse at center, transparent 60%, var(--bg) 100%);
}}

/* Content */
.container {{
    position: relative; z-index:2;
    max-width: 900px; margin: 0 auto; padding: 60px 24px;
}}

/* Header */
.header {{
    text-align: center; margin-bottom: 48px;
}}
.logo {{
    max-height: 60px; margin-bottom: 24px;
}}
.title {{
    font-size: 2rem; font-weight: 700;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 12px;
}}
.meta {{
    font-size: 0.9rem; opacity: 0.6;
}}

/* Tabs */
.tabs {{
    display: flex; gap: 8px; margin-bottom: 32px; justify-content: center;
}}
.tab-btn {{
    padding: 10px 28px; border-radius: 24px; border: 1px solid var(--card-border);
    background: var(--card-bg); color: var(--text); cursor: pointer;
    font-family: inherit; font-size: 0.95rem; transition: all 0.2s;
}}
.tab-btn:hover {{ border-color: var(--primary); }}
.tab-btn.active {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff; border-color: transparent;
}}
.tab-content {{ display: none; }}
.tab-content.active {{ display: block; }}

/* Cards */
.card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 28px; margin-bottom: 24px;
    backdrop-filter: blur(12px);
}}
.card h2 {{
    font-size: 1.1rem; font-weight: 700;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 16px;
    text-transform: uppercase; letter-spacing: 1px;
}}
.card ul {{ list-style: none; padding: 0; }}
.card li {{
    padding: 6px 0; padding-left: 20px;
    position: relative;
}}
.card li::before {{
    content: '•'; position: absolute; left: 0;
    color: var(--primary); font-weight: 700;
}}
.card ol {{ padding-left: 20px; }}
.card ol li {{ padding: 4px 0; }}
.card ol li::before {{ content: none; }}
.card p {{ margin-bottom: 12px; }}
.card strong {{ color: var(--primary); }}

/* Detail sections */
.detail-section {{ margin-bottom: 20px; }}
.detail-section h3 {{
    font-size: 1rem; font-weight: 700;
    color: var(--primary); margin-bottom: 8px;
}}

/* Footer */
.footer {{
    text-align: center; margin-top: 60px; padding-top: 24px;
    border-top: 1px solid var(--card-border);
    font-size: 0.8rem; opacity: 0.4;
}}

/* Print */
@media print {{
    body {{ background: #fff; color: #222; }}
    .bokeh, .grain, .vignette {{ display: none; }}
    .card {{ border: 1px solid #ddd; background: #fafafa; backdrop-filter: none; }}
    .card h2, .title {{ -webkit-text-fill-color: var(--primary); }}
    .tab-content {{ display: block !important; }}
    .tabs {{ display: none; }}
}}
</style>
</head>
<body>
<div class="bokeh"><div class="orb"></div><div class="orb"></div><div class="orb"></div></div>
<div class="grain"><svg><filter id="g"><feTurbulence baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/></filter><rect width="100%" height="100%" filter="url(#g)"/></svg></div>
<div class="vignette"></div>

<div class="container">
    <div class="header">
        {logo_html}
        <div class="title">Compte Rendu de Réunion</div>
        <div class="meta">{date} — {duree}</div>
    </div>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('resume')">Résumé</button>
        <button class="tab-btn" onclick="switchTab('detail')">Détaillé</button>
    </div>

    <div id="tab-resume" class="tab-content active">
        {resume_html}
    </div>

    <div id="tab-detail" class="tab-content">
        {detail_html}
    </div>

    <div class="footer">{footer_text}</div>
</div>

<script>
function switchTab(id) {{
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + id).classList.add('active');
    event.target.classList.add('active');
}}
</script>
</body>
</html>"""
```

- [ ] **Step 4: Implement HtmlGenerator**

```python
# app/pipeline/html_generator.py
import re
from pathlib import Path

from app.branding.models import BrandProfile
from app.pipeline.html_template import HTML_TEMPLATE


class HtmlGenerator:
    def __init__(self, profile: BrandProfile):
        self._profile = profile

    def generate(self, cr_text: str) -> str:
        """Generate self-contained HTML from structured CR text + brand profile."""
        parsed = self._parse_cr(cr_text)

        logo_html = ""
        if self._profile.logo_b64:
            logo_html = f'<img class="logo" src="data:image/png;base64,{self._profile.logo_b64}" alt="{self._profile.company_name}">'

        resume_html = self._build_resume(parsed)
        detail_html = self._build_detail(parsed)

        return HTML_TEMPLATE.format(
            language=self._profile.language,
            company_name=self._profile.company_name,
            font_family=self._profile.font_family,
            font_regular_b64=self._profile.font_regular_b64,
            font_bold_b64=self._profile.font_bold_b64,
            primary_color=self._profile.primary_color,
            secondary_color=self._profile.secondary_color,
            background_color=self._profile.background_color,
            text_color=self._profile.text_color,
            logo_html=logo_html,
            date=parsed.get("date", ""),
            duree=parsed.get("duree", ""),
            resume_html=resume_html,
            detail_html=detail_html,
            footer_text=self._profile.footer_text,
        )

    def generate_to_file(self, cr_text: str, output_path: Path):
        """Generate HTML and write to file."""
        html = self.generate(cr_text)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")

    def _parse_cr(self, text: str) -> dict:
        """Parse structured CR text into sections."""
        data = {"date": "", "duree": "", "themes": [], "actions": "", "conclusion": "", "details": ""}

        # Extract metadata
        date_m = re.search(r"Date\s*:\s*(.+)", text)
        if date_m:
            data["date"] = date_m.group(1).strip()
        duree_m = re.search(r"Dur[ée]e\s*:\s*(.+)", text)
        if duree_m:
            data["duree"] = duree_m.group(1).strip()

        # Split into sections by delimiter lines
        sections = re.split(r"-{20,}", text)

        for i, section in enumerate(sections):
            header = section.strip().split("\n")[0].strip().upper() if section.strip() else ""

            if "THÈMES" in header or "THEMES" in header:
                body = "\n".join(section.strip().split("\n")[1:])
                data["themes"] = [
                    line.strip().lstrip("•").strip()
                    for line in body.split("\n")
                    if line.strip() and line.strip().startswith("•")
                ]

            elif "ACTIONS" in header or "PROCHAINES" in header:
                data["actions"] = "\n".join(section.strip().split("\n")[1:]).strip()

            elif "CONCLUSION" in header:
                body = "\n".join(section.strip().split("\n")[1:])
                data["conclusion"] = body.strip().lstrip("→").strip()

            elif "TOUT EN" in header or "DÉTAILS" in header or "DETAILS" in header:
                data["details"] = "\n".join(section.strip().split("\n")[1:]).strip()

        return data

    def _build_resume(self, parsed: dict) -> str:
        """Build the Résumé tab HTML."""
        html = ""

        # Themes card
        if parsed["themes"]:
            items = "".join(f"<li>{t}</li>" for t in parsed["themes"])
            html += f'<div class="card"><h2>Thèmes abordés</h2><ul>{items}</ul></div>'

        # Actions card
        if parsed["actions"]:
            actions_html = self._format_actions(parsed["actions"])
            html += f'<div class="card"><h2>Actions / Prochaines étapes</h2>{actions_html}</div>'

        # Conclusion card
        if parsed["conclusion"]:
            html += f'<div class="card"><h2>Conclusion</h2><p>→ {parsed["conclusion"]}</p></div>'

        return html

    def _build_detail(self, parsed: dict) -> str:
        """Build the Détaillé tab HTML."""
        if not parsed["details"]:
            return '<div class="card"><p>Aucun détail disponible.</p></div>'

        # Split by numbered sections (1. Title, 2. Title, etc.)
        sections = re.split(r"\n(?=\d+\.\s)", parsed["details"])
        html = ""

        for section in sections:
            section = section.strip()
            if not section:
                continue
            lines = section.split("\n")
            title = lines[0].strip()
            body = "\n".join(lines[1:]).strip()
            # Convert paragraphs
            paragraphs = "".join(f"<p>{p.strip()}</p>" for p in body.split("\n\n") if p.strip())
            if not paragraphs:
                paragraphs = f"<p>{body}</p>"
            html += f'<div class="card"><div class="detail-section"><h3>{title}</h3>{paragraphs}</div></div>'

        return html or '<div class="card"><p>Aucun détail disponible.</p></div>'

    def _format_actions(self, actions_text: str) -> str:
        """Format actions text to HTML, preserving per-person grouping."""
        html = ""
        lines = actions_text.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("**") and line.endswith(":**"):
                # Person header
                name = line.strip("*").strip(":")
                html += f"<p><strong>{name}:</strong></p>"
            elif re.match(r"\d+\.\s", line):
                html += f"<p style='padding-left:20px;'>{line}</p>"
            else:
                html += f"<p>{line}</p>"

        return html
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd BOTS/CR_BOT && python -m pytest app/tests/test_html_generator.py -v`
Expected: 7 passed

- [ ] **Step 6: Commit**

```bash
git add BOTS/CR_BOT/app/pipeline/html_template.py BOTS/CR_BOT/app/pipeline/html_generator.py BOTS/CR_BOT/app/tests/test_html_generator.py
git commit -m "feat(cr_bot): branded HTML generator with tabs and CSS vars"
```

---

### Task 10: Proxy Client (App-side HTTP calls)

**Files:**
- Create: `BOTS/CR_BOT/app/pipeline/transcribe.py`
- Create: `BOTS/CR_BOT/app/pipeline/summarize.py`
- Create: `BOTS/CR_BOT/app/auth/__init__.py`
- Create: `BOTS/CR_BOT/app/auth/license.py`
- Create: `BOTS/CR_BOT/app/tests/test_license.py`

- [ ] **Step 1: Write failing tests for license client**

```python
# app/tests/test_license.py
import pytest
import json
from unittest.mock import patch, MagicMock

from app.auth.license import LicenseClient


class TestLicenseClient:
    @patch("app.auth.license.httpx.Client")
    def test_validate_success(self, mock_client_cls):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"valid": True, "client_id": "abc", "profile_url": "https://store/abc"}
        mock_resp.raise_for_status = MagicMock()
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        lc = LicenseClient(proxy_url="https://proxy.example.com")
        result = lc.validate("CRBOT-test-key")
        assert result["valid"] is True
        assert result["client_id"] == "abc"

    @patch("app.auth.license.httpx.Client")
    def test_validate_invalid(self, mock_client_cls):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"valid": False, "reason": "Unknown key"}
        mock_resp.raise_for_status = MagicMock()
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        lc = LicenseClient(proxy_url="https://proxy.example.com")
        result = lc.validate("CRBOT-fake")
        assert result["valid"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd BOTS/CR_BOT && python -m pytest app/tests/test_license.py -v`
Expected: FAIL

- [ ] **Step 3: Implement LicenseClient**

```python
# app/auth/license.py
import httpx


class LicenseClient:
    def __init__(self, proxy_url: str):
        self._proxy_url = proxy_url.rstrip("/")

    def validate(self, license_key: str) -> dict:
        """Validate license key against proxy. Returns dict with 'valid', 'client_id', 'profile_url'."""
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f"{self._proxy_url}/auth/validate",
                json={"license_key": license_key},
            )
            resp.raise_for_status()
            return resp.json()
```

- [ ] **Step 4: Implement transcribe client**

```python
# app/pipeline/transcribe.py
import httpx
from pathlib import Path


class TranscribeClient:
    def __init__(self, proxy_url: str, license_key: str):
        self._proxy_url = proxy_url.rstrip("/")
        self._license_key = license_key

    def transcribe(self, audio_path: Path, language: str = "fr") -> dict:
        """Send audio to proxy for transcription. Returns transcript dict."""
        with httpx.Client(timeout=600) as client:
            with open(audio_path, "rb") as f:
                resp = client.post(
                    f"{self._proxy_url}/transcribe",
                    data={"license_key": self._license_key, "language": language},
                    files={"audio": (audio_path.name, f, "audio/mpeg")},
                )
            resp.raise_for_status()
            return resp.json()
```

- [ ] **Step 5: Implement summarize client**

```python
# app/pipeline/summarize.py
import httpx


class SummarizeClient:
    def __init__(self, proxy_url: str, license_key: str):
        self._proxy_url = proxy_url.rstrip("/")
        self._license_key = license_key

    def summarize(self, transcript: str, context: str = "", language: str = "fr") -> str:
        """Send transcript to proxy for summarization. Returns CR text."""
        with httpx.Client(timeout=120) as client:
            resp = client.post(
                f"{self._proxy_url}/summarize",
                json={
                    "license_key": self._license_key,
                    "transcript": transcript,
                    "context": context,
                    "language": language,
                },
            )
            resp.raise_for_status()
            return resp.json()["summary"]
```

- [ ] **Step 6: Create __init__.py**

Create empty `app/auth/__init__.py`.

- [ ] **Step 7: Run tests to verify they pass**

Run: `cd BOTS/CR_BOT && python -m pytest app/tests/test_license.py -v`
Expected: 2 passed

- [ ] **Step 8: Commit**

```bash
git add BOTS/CR_BOT/app/auth/ BOTS/CR_BOT/app/pipeline/transcribe.py BOTS/CR_BOT/app/pipeline/summarize.py BOTS/CR_BOT/app/tests/test_license.py
git commit -m "feat(cr_bot): proxy client modules (license, transcribe, summarize)"
```

---

### Task 11: Pipeline Orchestrator

**Files:**
- Create: `BOTS/CR_BOT/app/pipeline/orchestrator.py`
- Create: `BOTS/CR_BOT/app/tests/test_orchestrator.py`

**Key design:** The orchestrator chains all pipeline stages. After each stage, it saves intermediate output to `.crbot/cache/` so it can resume from partial progress. Emits progress signals for the UI.

- [ ] **Step 1: Write failing tests**

```python
# app/tests/test_orchestrator.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd BOTS/CR_BOT && python -m pytest app/tests/test_orchestrator.py -v`
Expected: FAIL

- [ ] **Step 3: Implement PipelineOrchestrator**

```python
# app/pipeline/orchestrator.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd BOTS/CR_BOT && python -m pytest app/tests/test_orchestrator.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add BOTS/CR_BOT/app/pipeline/orchestrator.py BOTS/CR_BOT/app/tests/test_orchestrator.py
git commit -m "feat(cr_bot): pipeline orchestrator with partial progress recovery"
```

---

## Chunk 3: Desktop App — UI

### Task 12: App Config + License Dialog

**Files:**
- Create: `BOTS/CR_BOT/app/config.py`
- Create: `BOTS/CR_BOT/app/ui/__init__.py`
- Create: `BOTS/CR_BOT/app/ui/theme.py`
- Create: `BOTS/CR_BOT/app/ui/license_dialog.py`

- [ ] **Step 1: Create app config**

```python
# app/config.py
import json
from pathlib import Path

DEFAULT_PROXY_URL = "https://crbot-proxy.example.com"
APP_DIR = Path.home() / ".crbot"
CONFIG_FILE = APP_DIR / "config.json"
CACHE_DIR = APP_DIR / "cache"
PROFILE_DIR = APP_DIR / "profile"


def load_config() -> dict:
    """Load local app config. Returns defaults if no config file."""
    defaults = {
        "proxy_url": DEFAULT_PROXY_URL,
        "license_key": "",
        "audio_dir": "",
        "output_dir": str(Path.home() / "Documents" / "CR_BOT"),
        "language": "fr",
    }
    if CONFIG_FILE.exists():
        saved = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        defaults.update(saved)
    return defaults


def save_config(config: dict):
    """Save config to disk."""
    APP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")
```

- [ ] **Step 2: Create theme module**

```python
# app/ui/theme.py
from app.branding.models import BrandProfile


def build_stylesheet(profile: BrandProfile) -> str:
    """Generate QSS stylesheet from brand profile."""
    return f"""
    QMainWindow, QDialog {{
        background-color: {profile.background_color};
        color: {profile.text_color};
    }}
    QPushButton {{
        background-color: {profile.primary_color};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {profile.secondary_color};
    }}
    QPushButton:disabled {{
        background-color: #555;
        color: #888;
    }}
    QLabel {{
        color: {profile.text_color};
    }}
    QLineEdit {{
        background-color: rgba(255,255,255,0.05);
        color: {profile.text_color};
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 6px;
        padding: 8px;
    }}
    QListWidget {{
        background-color: rgba(255,255,255,0.03);
        color: {profile.text_color};
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
    }}
    QListWidget::item {{
        padding: 8px;
    }}
    QListWidget::item:selected {{
        background-color: {profile.primary_color};
    }}
    QProgressBar {{
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 4px;
        text-align: center;
        color: {profile.text_color};
    }}
    QProgressBar::chunk {{
        background-color: {profile.primary_color};
        border-radius: 3px;
    }}
    """
```

- [ ] **Step 3: Create license dialog**

```python
# app/ui/license_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt

from app.auth.license import LicenseClient


class LicenseDialog(QDialog):
    def __init__(self, proxy_url: str, parent=None):
        super().__init__(parent)
        self._proxy_url = proxy_url
        self._result = None
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("CR_BOT — Activation")
        self.setFixedSize(420, 220)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(32, 32, 32, 32)

        title = QLabel("Entrez votre clé de licence")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self._key_input = QLineEdit()
        self._key_input.setPlaceholderText("CRBOT-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        layout.addWidget(self._key_input)

        self._activate_btn = QPushButton("Activer")
        self._activate_btn.clicked.connect(self._on_activate)
        layout.addWidget(self._activate_btn)

        self._status = QLabel("")
        self._status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status)

    def _on_activate(self):
        key = self._key_input.text().strip()
        if not key:
            self._status.setText("Veuillez entrer une clé.")
            return

        self._activate_btn.setEnabled(False)
        self._status.setText("Vérification...")

        try:
            client = LicenseClient(self._proxy_url)
            result = client.validate(key)
            if result.get("valid"):
                self._result = {"key": key, **result}
                self.accept()
            else:
                reason = result.get("reason", "Clé invalide")
                self._status.setText(f"Erreur : {reason}")
        except Exception as e:
            self._status.setText("Impossible de se connecter au serveur.")
        finally:
            self._activate_btn.setEnabled(True)

    def get_result(self) -> dict | None:
        return self._result
```

- [ ] **Step 4: Create ui/__init__.py**

Create empty `app/ui/__init__.py`.

- [ ] **Step 5: Commit**

```bash
git add BOTS/CR_BOT/app/config.py BOTS/CR_BOT/app/ui/
git commit -m "feat(cr_bot): app config, theme, and license activation dialog"
```

---

### Task 13: Main Window

**Files:**
- Create: `BOTS/CR_BOT/app/ui/progress_widget.py`
- Create: `BOTS/CR_BOT/app/ui/history_panel.py`
- Create: `BOTS/CR_BOT/app/ui/main_window.py`

- [ ] **Step 1: Create progress widget**

```python
# app/ui/progress_widget.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt


STAGES = [
    ("transcription", "Transcription"),
    ("summarization", "Résumé"),
    ("generation", "Génération"),
]


class ProgressWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._bars = {}
        for key, label in STAGES:
            container = QWidget()
            vlayout = QVBoxLayout(container)
            vlayout.setContentsMargins(0, 0, 0, 0)
            vlayout.setSpacing(4)

            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 11px; opacity: 0.7;")
            vlayout.addWidget(lbl)

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setFixedHeight(6)
            bar.setTextVisible(False)
            vlayout.addWidget(bar)

            layout.addWidget(container)
            self._bars[key] = bar

    def update_stage(self, stage: str, percent: int):
        if stage in self._bars:
            self._bars[stage].setValue(percent)

    def reset(self):
        for bar in self._bars.values():
            bar.setValue(0)
```

- [ ] **Step 2: Create history panel**

```python
# app/ui/history_panel.py
import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt


class HistoryPanel(QListWidget):
    def __init__(self, output_dir: Path, parent=None):
        super().__init__(parent)
        self._output_dir = output_dir
        self.itemDoubleClicked.connect(self._on_open)
        self.refresh()

    def refresh(self):
        """Reload the list of CR HTML files."""
        self.clear()
        if not self._output_dir.exists():
            return
        files = sorted(
            self._output_dir.glob("*.html"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        for f in files:
            item = QListWidgetItem(f.name)
            item.setData(Qt.UserRole, str(f))
            self.addItem(item)

    def _on_open(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])
```

- [ ] **Step 3: Create main window**

```python
# app/ui/main_window.py
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QCheckBox, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QIcon

from app.branding.models import BrandProfile
from app.pipeline.scanner import AudioScanner
from app.pipeline.orchestrator import PipelineOrchestrator, PipelineResult
from app.ui.progress_widget import ProgressWidget
from app.ui.history_panel import HistoryPanel


class PipelineWorker(QThread):
    """Background thread for pipeline execution."""
    progress = Signal(str, int)  # stage, percent
    finished = Signal(object)   # PipelineResult

    def __init__(self, orchestrator, files, profile):
        super().__init__()
        self._orch = orchestrator
        self._files = files
        self._profile = profile

    def run(self):
        self._orch._on_progress = self.progress.emit
        result = self._orch.run(self._files, self._profile)
        self.finished.emit(result)


class MainWindow(QMainWindow):
    def __init__(self, config: dict, profile: BrandProfile):
        super().__init__()
        self._config = config
        self._profile = profile
        self._worker = None
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(f"CR_BOT — {self._profile.company_name}")
        self.setMinimumSize(500, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Logo
        if self._profile.logo_b64:
            import base64
            logo_label = QLabel()
            pixmap = QPixmap()
            pixmap.loadFromData(base64.b64decode(self._profile.logo_b64))
            logo_label.setPixmap(pixmap.scaledToHeight(48, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)

        # Title
        title = QLabel("Compte Rendu de Réunion")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {self._profile.primary_color};")
        layout.addWidget(title)

        # Generate button
        self._generate_btn = QPushButton("Générer le compte rendu")
        self._generate_btn.setFixedHeight(56)
        self._generate_btn.setStyleSheet("font-size: 16px;")
        self._generate_btn.clicked.connect(self._on_generate)
        layout.addWidget(self._generate_btn)

        # File selection area (hidden until scan)
        self._file_area = QScrollArea()
        self._file_area.setWidgetResizable(True)
        self._file_area.setVisible(False)
        self._file_container = QWidget()
        self._file_layout = QVBoxLayout(self._file_container)
        self._file_area.setWidget(self._file_container)
        layout.addWidget(self._file_area)

        # Confirm button (hidden until scan)
        self._confirm_btn = QPushButton("Lancer le traitement")
        self._confirm_btn.setVisible(False)
        self._confirm_btn.clicked.connect(self._on_confirm)
        layout.addWidget(self._confirm_btn)

        # Progress
        self._progress = ProgressWidget()
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        # Status
        self._status = QLabel("")
        self._status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status)

        # History
        history_label = QLabel("Historique")
        history_label.setStyleSheet("font-size: 12px; opacity: 0.6;")
        layout.addWidget(history_label)

        output_dir = Path(self._config.get("output_dir", ""))
        self._history = HistoryPanel(output_dir)
        layout.addWidget(self._history)

        # Settings button
        settings_btn = QPushButton("Paramètres")
        settings_btn.setStyleSheet("background-color: transparent; color: rgba(255,255,255,0.5); border: 1px solid rgba(255,255,255,0.1);")
        settings_btn.clicked.connect(self._on_settings)
        layout.addWidget(settings_btn)

    def _on_generate(self):
        """Scan for audio files and show checkboxes."""
        audio_dir = Path(self._config.get("audio_dir", ""))
        if not audio_dir.exists():
            QMessageBox.warning(self, "Erreur", f"Dossier audio introuvable : {audio_dir}\nVérifiez les paramètres.")
            return

        output_dir = Path(self._config.get("output_dir", ""))
        scanner = AudioScanner(audio_dir, output_dir / ".history.json")
        files = scanner.scan_unprocessed()

        if not files:
            self._status.setText(f"Aucun fichier audio trouvé dans {audio_dir}")
            return

        groups = scanner.group_by_date(files)
        self._checkboxes = []

        # Clear previous
        while self._file_layout.count():
            child = self._file_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for group in groups:
            for f in group.files:
                cb = QCheckBox(f"{f.name}  ({group.date_str})")
                cb.setChecked(group.is_today)
                cb.setProperty("path", str(f))
                self._file_layout.addWidget(cb)
                self._checkboxes.append(cb)

        self._file_area.setVisible(True)
        self._confirm_btn.setVisible(True)
        self._generate_btn.setVisible(False)

    def _on_confirm(self):
        """Start pipeline on selected files."""
        selected = [
            Path(cb.property("path"))
            for cb in self._checkboxes
            if cb.isChecked()
        ]
        if not selected:
            self._status.setText("Sélectionnez au moins un fichier.")
            return

        self._confirm_btn.setEnabled(False)
        self._progress.setVisible(True)
        self._progress.reset()
        self._status.setText("Traitement en cours...")

        output_dir = Path(self._config.get("output_dir", ""))
        cache_dir = Path(self._config.get("output_dir", "")) / ".crbot" / "cache"

        orch = PipelineOrchestrator(
            proxy_url=self._config["proxy_url"],
            license_key=self._config["license_key"],
            cache_dir=cache_dir,
            output_dir=output_dir,
            context=self._profile.context,
            language=self._config.get("language", "fr"),
        )

        self._worker = PipelineWorker(orch, selected, self._profile)
        self._worker.progress.connect(self._progress.update_stage)
        self._worker.finished.connect(self._on_pipeline_done)
        self._worker.start()

    def _on_pipeline_done(self, result: PipelineResult):
        self._confirm_btn.setEnabled(True)
        self._file_area.setVisible(False)
        self._confirm_btn.setVisible(False)
        self._generate_btn.setVisible(True)

        if result.success:
            self._status.setText(f"CR généré : {result.output_path.name}")
            # Mark files as processed
            audio_dir = Path(self._config.get("audio_dir", ""))
            output_dir = Path(self._config.get("output_dir", ""))
            scanner = AudioScanner(audio_dir, output_dir / ".history.json")
            for cb in self._checkboxes:
                if cb.isChecked():
                    scanner.mark_processed(Path(cb.property("path")))
            self._history.refresh()
        else:
            self._status.setText(f"Erreur : {result.error}")
            QMessageBox.critical(self, "Erreur", f"Le traitement a échoué :\n{result.error}")

    def _on_settings(self):
        from app.ui.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self._config, self)
        if dlg.exec():
            self._config.update(dlg.get_config())
            from app.config import save_config
            save_config(self._config)
            # Update history panel output dir and refresh
            self._history._output_dir = Path(self._config["output_dir"])
            self._history.refresh()
```

- [ ] **Step 4: Commit**

```bash
git add BOTS/CR_BOT/app/ui/progress_widget.py BOTS/CR_BOT/app/ui/history_panel.py BOTS/CR_BOT/app/ui/main_window.py
git commit -m "feat(cr_bot): main window with file selection, progress, and history"
```

---

### Task 14: Settings Dialog

**Files:**
- Create: `BOTS/CR_BOT/app/ui/settings_dialog.py`

- [ ] **Step 1: Create settings dialog**

```python
# app/ui/settings_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QComboBox
)


class SettingsDialog(QDialog):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self._config = dict(config)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Paramètres")
        self.setFixedSize(500, 300)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        # Audio folder
        layout.addWidget(QLabel("Dossier source audio :"))
        audio_row = QHBoxLayout()
        self._audio_input = QLineEdit(self._config.get("audio_dir", ""))
        audio_row.addWidget(self._audio_input)
        audio_browse = QPushButton("Parcourir")
        audio_browse.clicked.connect(lambda: self._browse(self._audio_input))
        audio_row.addWidget(audio_browse)
        layout.addLayout(audio_row)

        # Output folder
        layout.addWidget(QLabel("Dossier de sortie CR :"))
        output_row = QHBoxLayout()
        self._output_input = QLineEdit(self._config.get("output_dir", ""))
        output_row.addWidget(self._output_input)
        output_browse = QPushButton("Parcourir")
        output_browse.clicked.connect(lambda: self._browse(self._output_input))
        output_row.addWidget(output_browse)
        layout.addLayout(output_row)

        # Language
        layout.addWidget(QLabel("Langue des réunions :"))
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(["fr", "en", "es"])
        current = self._config.get("language", "fr")
        idx = self._lang_combo.findText(current)
        if idx >= 0:
            self._lang_combo.setCurrentIndex(idx)
        layout.addWidget(self._lang_combo)

        # Save button
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self._on_save)
        layout.addWidget(save_btn)

    def _browse(self, line_edit: QLineEdit):
        folder = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier")
        if folder:
            line_edit.setText(folder)

    def _on_save(self):
        self._config["audio_dir"] = self._audio_input.text().strip()
        self._config["output_dir"] = self._output_input.text().strip()
        self._config["language"] = self._lang_combo.currentText()
        self.accept()

    def get_config(self) -> dict:
        return self._config
```

- [ ] **Step 2: Commit**

```bash
git add BOTS/CR_BOT/app/ui/settings_dialog.py
git commit -m "feat(cr_bot): settings dialog (audio dir, output dir, language)"
```

---

### Task 15: App Entry Point

**Files:**
- Create: `BOTS/CR_BOT/app/main.py`

- [ ] **Step 1: Create app entry point**

```python
# app/main.py
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.config import load_config, save_config, PROFILE_DIR, CACHE_DIR
from app.branding.models import BrandProfile
from app.branding.profile import ProfileManager
from app.ui.license_dialog import LicenseDialog
from app.ui.main_window import MainWindow
from app.ui.theme import build_stylesheet


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CR_BOT")

    config = load_config()
    profile_mgr = ProfileManager(cache_dir=PROFILE_DIR)

    # First launch: license activation
    if not config.get("license_key"):
        dialog = LicenseDialog(proxy_url=config["proxy_url"])
        if dialog.exec():
            result = dialog.get_result()
            config["license_key"] = result["key"]
            # Download branding profile
            if "profile_url" in result:
                profile_mgr.download_and_cache(result["profile_url"])
            save_config(config)
        else:
            sys.exit(0)

    # Load profile
    profile = profile_mgr.load_cached()
    if profile is None:
        profile = BrandProfile()  # Use defaults if no profile cached

    # Apply theme
    app.setStyleSheet(build_stylesheet(profile))

    # Show main window
    window = MainWindow(config, profile)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify app starts (manual)**

Run: `cd BOTS/CR_BOT && python -m app.main`
Expected: License dialog appears (first launch) or main window if license already configured.

- [ ] **Step 3: Commit**

```bash
git add BOTS/CR_BOT/app/main.py
git commit -m "feat(cr_bot): app entry point with license flow and themed UI"
```

---

## Chunk 4: Build, Packaging & Default Profile

### Task 16: Default Branding Profile

**Files:**
- Create: `BOTS/CR_BOT/profiles/default/brand.json`

- [ ] **Step 1: Create default brand profile**

```json
{
    "company_name": "CR_BOT",
    "primary_color": "#6e3ea8",
    "secondary_color": "#E93F7F",
    "background_color": "#050505",
    "text_color": "#E5E5E5",
    "font_family": "system-ui",
    "footer_text": "Compte rendu généré automatiquement par CR_BOT",
    "language": "fr",
    "context": "",
    "cr_sections": {
        "summary": true,
        "detailed": true
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add BOTS/CR_BOT/profiles/default/brand.json
git commit -m "feat(cr_bot): default branding profile"
```

---

### Task 17: PyInstaller Configuration

**Files:**
- Create: `BOTS/CR_BOT/build/cr_bot.spec`

- [ ] **Step 1: Create PyInstaller spec**

```python
# build/cr_bot.spec
# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None
app_dir = Path("../app")

a = Analysis(
    [str(app_dir / "main.py")],
    pathex=[str(app_dir.parent)],
    binaries=[],
    datas=[
        (str(app_dir.parent / "profiles" / "default"), "profiles/default"),
    ],
    hiddenimports=["app.pipeline", "app.branding", "app.auth", "app.ui"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["proxy"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CR_BOT",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=None,  # Add icon path here when available
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="CR_BOT",
)
```

- [ ] **Step 2: Test build locally (Windows)**

Run: `cd BOTS/CR_BOT/build && pyinstaller cr_bot.spec --distpath ../dist`
Expected: `dist/CR_BOT/CR_BOT.exe` is created

- [ ] **Step 3: Commit**

```bash
git add BOTS/CR_BOT/build/cr_bot.spec
git commit -m "feat(cr_bot): PyInstaller spec for desktop build"
```

---

### Task 18: GitHub Actions CI/CD

**Files:**
- Create: `BOTS/CR_BOT/build/build.yml`

- [ ] **Step 1: Create GitHub Actions workflow**

```yaml
# build/build.yml
# Copy this to .github/workflows/build.yml when the repo is created on GitHub
name: Build CR_BOT

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r app/requirements.txt
          pip install pyinstaller
      - name: Build
        run: |
          cd build
          pyinstaller cr_bot.spec --distpath ../dist
      # V2: wrap dist/ output with NSIS installer for a proper .exe setup
      - uses: actions/upload-artifact@v4
        with:
          name: CR_BOT-Windows
          path: dist/CR_BOT/

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r app/requirements.txt
          pip install pyinstaller
      - name: Build
        run: |
          cd build
          pyinstaller cr_bot.spec --distpath ../dist
      - uses: actions/upload-artifact@v4
        with:
          name: CR_BOT-macOS
          path: dist/CR_BOT/

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r proxy/requirements.txt
          pip install -r app/requirements.txt
      - name: Run proxy tests
        run: python -m pytest proxy/tests/ -v
      - name: Run app tests
        run: python -m pytest app/tests/ -v
```

- [ ] **Step 2: Commit**

```bash
git add BOTS/CR_BOT/build/build.yml
git commit -m "feat(cr_bot): GitHub Actions CI/CD for Windows + macOS builds"
```

---

### Task 19: Final Integration Test

- [ ] **Step 1: Run all proxy tests**

Run: `cd BOTS/CR_BOT && python -m pytest proxy/tests/ -v`
Expected: All pass

- [ ] **Step 2: Run all app tests**

Run: `cd BOTS/CR_BOT && python -m pytest app/tests/ -v`
Expected: All pass

- [ ] **Step 3: Manual smoke test**

1. Start proxy locally: `cd BOTS/CR_BOT/proxy && uvicorn main:create_app --factory --port 8000`
2. Set env vars: `GLADIA_API_KEY`, `ANTHROPIC_API_KEY`
3. Create a test `licenses.json` with a test key
4. Run app: `cd BOTS/CR_BOT && python -m app.main`
5. Enter license key → verify branding loads → configure audio dir → generate a CR

- [ ] **Step 4: Final commit**

```bash
git add BOTS/CR_BOT/app/ BOTS/CR_BOT/proxy/ BOTS/CR_BOT/profiles/ BOTS/CR_BOT/build/ BOTS/CR_BOT/.gitignore
git commit -m "feat(cr_bot): complete CR_BOT v1 — proxy + desktop app + build pipeline"
```
