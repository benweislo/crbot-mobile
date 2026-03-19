# CR_BOT — Design Specification

**Date:** 2026-03-19
**Status:** Draft
**Author:** Ben Weislo + Claude

---

## 1. Overview

CR_BOT is a white-label desktop application that automatically generates branded meeting minutes (comptes rendus) from audio recordings. Each client receives a personalized app with their visual identity. The product is sold as a monthly subscription with all API costs handled centrally.

### Product Vision

A client installs CR_BOT, enters their license key, and clicks one button to generate a professional, branded HTML meeting report from their audio recording. Zero technical knowledge required.

---

## 2. Architecture

### 2.1 System Components

```
┌─────────────────────────────────────────────────────┐
│                   OPERATOR INFRA                    │
│                                                     │
│  ┌──────────────┐    ┌──────────────┐              │
│  │ Profile       │    │ API Proxy    │              │
│  │ Storage       │    │ (FastAPI)    │              │
│  │ (S3/R2)      │    │              │              │
│  └──────┬───────┘    └──────┬───────┘              │
└─────────┼───────────────────┼───────────────────────┘
          │                   │
┌─────────┼───────────────────┼───────────────────────┐
│         ▼                   ▼       CLIENT DESKTOP   │
│  ┌──────────────┐    ┌──────────────┐              │
│  │ Branding     │    │ Pipeline     │              │
│  │ Profile      │    │ Engine       │              │
│  │ (cached)     │    │              │              │
│  └──────────────┘    └──┬───┬───┬───┘              │
│              ┌──────────┘   │   └──────────┐       │
│              ▼              ▼              ▼        │
│        Transcription   Summarization  HTML Gen     │
│        (Gladia)        (Claude S4)    (local)      │
│                                          │         │
│                                     CR.html        │
│                                  (+ optional upload)│
└─────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

| Component | Tech | Role |
|-----------|------|------|
| Desktop app | Python 3.12 + PySide6 | Client UI, pipeline orchestration, HTML generation |
| API Proxy | FastAPI on VPS/serverless | License validation, API key relay (Gladia + Anthropic) |
| Profile Storage | S3 / Cloudflare R2 | Per-client branding assets (logo, colors, fonts, template) |
| Build pipeline | PyInstaller + NSIS (Win) / DMG (Mac) + GitHub Actions | Cross-platform installers, auto-update |

---

## 3. Desktop Application

### 3.1 UI (PySide6)

**Main window — minimalist:**
- Client logo (top)
- Large central button: "Générer le compte rendu"
- Status/progress area (bottom): 3-step progress (Transcription → Résumé → Génération)
- Settings gear icon (top-right)
- History panel: list of previously generated CRs, click to open

**Settings screen:**
- Audio source folder (local path, default: Audio Capturer Pro output)
- CR output folder (local path)
- Upload option (V2): FTP/SFTP or shared folder path. MVP: CR output to local folder only.
- Meeting language (FR default, extensible)

### 3.2 First Launch Flow

1. User enters license key
2. App contacts proxy → validates key → downloads branding profile
3. App renders in client's brand colors
4. User configures audio folder in settings
5. Ready

### 3.3 Daily Usage Flow

1. User records meeting with Audio Capturer Pro
2. Opens CR_BOT, clicks the button
3. App scans the configured audio folder for **unprocessed** files (any file not yet in the local CR history, regardless of date). Presents the list to the user with checkboxes — files from today are pre-selected. User confirms which files to process.
4. Pipeline runs on selected files → generates branded CR HTML
5. If upload configured → pushes file automatically
6. Notification: "CR ready" + link to open file

**Edge cases:** If no audio files are found, the app shows "Aucun fichier audio trouvé dans [dossier configuré]". If the user has unprocessed files from previous days, they appear in the list (unchecked by default).

### 3.4 Auto-Update

- App checks for new version on startup (non-blocking)
- Discrete notification "Update available" — no forced updates
- Update URL served by the proxy or a static endpoint

---

## 4. API Proxy

### 4.1 Stack

FastAPI (Python), deployed on a **VPS** (Railway, Fly.io, or similar). Serverless is not suitable because the `/transcribe` endpoint handles large audio file uploads (potentially hundreds of MB), which exceeds typical serverless payload limits (6-10 MB).

### 4.2 Endpoints

| Method | Endpoint | Input | Output |
|--------|----------|-------|--------|
| POST | `/auth/validate` | `{ license_key }` | `{ valid, client_id, profile_url }` or `{ valid: false }` |
| POST | `/transcribe` | Multipart form: `license_key` (field) + `audio` (file, streamed) | `{ transcript }` |
| POST | `/summarize` | `{ license_key, transcript }` | `{ summary }` |

**Audio upload details:** The `/transcribe` endpoint accepts multipart form data. The proxy streams the audio file directly to Gladia's upload endpoint without buffering the entire file in memory (using `httpx` streaming or chunked transfer). This keeps proxy memory usage constant regardless of file size. Request timeout: 600s (10 min) to accommodate large files on slow connections.

### 4.3 Design Principles

- **Stateless** — no content is stored. Audio and text pass through memory only, discarded after response.
- **Persistent data** — only the license table: `key → client_id → status (active/inactive) → expiry_date`. SQLite or JSON file for MVP.
- **Rate limiting** — per license key: max 10 requests/minute, max 50 CRs/day. These limits are generous for normal use and prevent abuse. Configurable per client if needed.
- **Minimal logging** — log `client_id`, timestamp, audio duration (for billing). Never log content.
- **API keys** — Gladia and Anthropic keys stored as environment variables on the server. Never exposed to clients.

### 4.4 License System

- UUID-based keys: `CRBOT-a3f7b2c1-xxxx-xxxx-xxxxxxxxxxxx`
- App sends key with every API call
- Proxy validates: key exists? subscription active? not expired? → OK or denied
- MVP: license table managed manually (add/deactivate clients)

---

## 5. Profile Storage

### 5.1 Structure

```
profiles/
├── client_abc123/
│   ├── brand.json
│   ├── logo.b64
│   ├── font_regular.b64
│   ├── font_bold.b64
│   └── template.html       (optional override)
├── client_def456/
│   └── ...
└── default/
    └── ...                  (fallback template)
```

### 5.2 brand.json Schema

```json
{
  "company_name": "Acme Corp",
  "primary_color": "#2563EB",
  "secondary_color": "#7C3AED",
  "background_color": "#0A0A0F",
  "text_color": "#E5E5E5",
  "footer_text": "Acme Corp — Compte rendu généré automatiquement",
  "language": "fr",
  "context": "Acme Corp est une agence de communication digitale. Participants réguliers : Jean-Pierre (DT), Marie (DA), Samir (Chef de projet). Termes fréquents : sprint, brief client, BAT, maquette.",
  "cr_sections": {
    "summary": true,
    "detailed": true
  }
}
```

### 5.3 Onboarding Workflow

1. Operator scrapes client's website → extracts colors, logo, fonts
2. Creates `brand.json` + base64 assets
3. Pushes profile folder to storage
4. Generates license key in the license table
5. Sends client: license key + installer download link

### 5.4 Caching

The app downloads the profile on first launch and caches it locally. It re-downloads only when the remote profile has changed (via ETag or Last-Modified header).

---

## 6. Pipeline (Audio → CR HTML)

### 6.1 Stage 1 — Transcription (Gladia)

- **Input:** Audio file(s) from configured folder (`.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.wma`, `.aac`, `.webm`)
- **Process:** App sends audio to proxy → proxy relays to Gladia API with operator's key → returns timestamped transcript with speaker diarization
- **Output:** Structured transcript with `[Speaker X] [HH:MM:SS → HH:MM:SS] text`
- **Same-day grouping:** When the user selects multiple audio files for processing, files from the same calendar day (detected via filename pattern `YYYY_MM_DD_*` or `AudioCapturer_YYYYMMDD*`, falling back to file modification date) are grouped as one meeting. Grouped files are transcribed separately then their transcripts are concatenated chronologically (ordered by timestamp in filename or modification time) before being sent to summarization as a single document.

### 6.2 Stage 2 — Summarization (Claude Sonnet 4)

**Note:** The existing MEETINGS pipeline uses OpenAI GPT-4o. CR_BOT switches to Claude Sonnet 4 for better structured output quality, larger context window (200K vs 128K), and superior French language handling. The summarization system prompt will be adapted and tested against the existing GPT-4o output quality as a baseline.

- **Input:** Full transcript
- **Process:** App sends transcript to proxy → proxy relays to Anthropic API (Claude Sonnet 4, temperature 0.3)
- **System prompt includes:**
  - Output format specification (themes, actions, conclusion, detailed sections)
  - Client business context from `brand.json.context`
  - Language instruction
- **Output:** Structured CR with sections:
  - Thèmes abordés
  - Actions / Prochaines étapes (par personne avec détails)
  - Conclusion
  - Tout en détails (sections thématiques numérotées)

### 6.3 Stage 3 — HTML Generation (Local)

- **Input:** Structured CR + branding profile (cached)
- **Process:** Python template engine injects brand values into HTML template via CSS variables
- **Output:** Single self-contained HTML file with:
  - Two tabs: Résumé (themes + actions + conclusion) / Détaillé (full sections)
  - Client logo, colors, fonts (all base64-embedded)
  - Visual effects: bokeh, glass-morphism, film grain, vignette (in brand colors)
  - Print-friendly mode (auto-detects print, switches to light palette)
  - Tab switching via vanilla JS (no framework)
  - Zero external dependencies

---

## 7. Data Privacy & Security

### 7.1 Guarantees

| Aspect | Implementation |
|--------|---------------|
| Proxy storage | Stateless — zero content storage. Audio and text pass through memory only. |
| Anthropic API | Zero Data Retention policy — API data not stored or used for training. |
| Gladia API | Gladia offers a GDPR Data Processing Agreement (DPA). Operator must verify and sign Gladia's current DPA terms before making privacy claims to clients. |
| Transit | All communications over HTTPS (TLS 1.2+). |
| Final output | CR HTML exists only on client's local machine. Nothing stored in the cloud post-processing. |
| API keys | Operator's keys stored server-side only. Client never sees or handles API credentials. |

### 7.2 Commercial Privacy Statement

> "Your meetings remain confidential. Audio is encrypted in transit, processed by GDPR-compliant APIs with immediate deletion, and the meeting report is generated exclusively on your machine. No data is stored on our servers or by third parties."

---

## 8. Error Handling & Resilience

### 8.1 Network Failures

| Scenario | Behavior |
|----------|----------|
| Proxy unreachable at first launch | Show error: "Impossible de se connecter au serveur. Vérifiez votre connexion internet." + retry button |
| Proxy unreachable during pipeline | Retry 3x with exponential backoff (2s, 4s, 8s), then show error with option to retry manually |
| Transcription succeeds but summarization fails | Save transcript locally. Show error with option to retry summarization only (no need to re-transcribe) |
| Profile download fails | Use cached profile if available. If first launch (no cache), block with connection error |

### 8.2 Pipeline Partial Progress

Each pipeline stage saves its output locally before proceeding to the next. If the pipeline is interrupted:
- Transcript saved → summarization can restart from saved transcript
- Summary saved → HTML generation can restart from saved summary
- The app detects partial progress and offers to resume from the last completed stage

---

## 9. Business Model

- **Pricing:** Fixed monthly subscription per client
- **Includes:** Unlimited CR generation (within reasonable rate limits), all API costs, branding setup, updates
- **Onboarding:** Operator handles brand scraping, profile creation, and license provisioning
- **Support:** Operator manages updates, branding changes, and client issues

---

## 10. Packaging & Distribution

### 10.1 Build Targets

| Platform | Build Tool | Installer | Output |
|----------|-----------|-----------|--------|
| Windows | PyInstaller | NSIS or Inno Setup | `CR_BOT_Setup.exe` (~120-150 MB) |
| macOS | PyInstaller | DMG | `CR_BOT.dmg` (~120-150 MB) |

### 10.2 CI/CD

- Single Git repository (`BOTS/CR_BOT/`)
- GitHub Actions builds both installers on release tags
- Builds uploaded to storage (S3/GitHub Releases private)
- Operator sends download link to client

### 10.3 Auto-Update Mechanism

- App checks version endpoint on startup
- If newer version available → discrete notification (not forced)
- Client downloads and reinstalls (or in-app update in V2)

---

## 11. Future Enhancements (Not in V1)

- **Offline mode:** Whisper (local transcription) + local LLM (Ollama) for 100% offline processing
- **Advanced upload integrations:** SharePoint, Notion, Google Drive, WordPress API
- **Dashboard web:** Portal for the operator to manage clients, view usage stats, billing
- **Multi-language:** Support for EN, ES, DE meetings (already extensible via language config)
- **Custom CR templates:** Client-provided HTML templates via a template editor
- **In-app auto-update:** Seamless update without reinstall

---

## 12. Repository Structure (Planned)

```
BOTS/CR_BOT/
├── app/
│   ├── main.py              ← PySide6 entry point
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── settings.py
│   │   └── history.py
│   ├── pipeline/
│   │   ├── transcribe.py    ← Gladia via proxy
│   │   ├── summarize.py     ← Claude via proxy
│   │   └── generate_html.py ← Local HTML generation
│   ├── branding/
│   │   ├── profile.py       ← Download/cache branding profile
│   │   └── template.py      ← HTML template with CSS vars
│   ├── auth/
│   │   └── license.py       ← License validation via proxy
│   └── config/
│       └── settings.py      ← Local settings (paths, upload config)
├── proxy/
│   ├── main.py              ← FastAPI server
│   ├── auth.py              ← License validation
│   ├── routes/
│   │   ├── transcribe.py
│   │   └── summarize.py
│   └── licenses.json        ← License table (MVP, .gitignore'd, managed on server only)
├── profiles/
│   └── default/             ← Default branding template
├── build/
│   ├── windows/             ← NSIS/Inno Setup config
│   ├── macos/               ← DMG config
│   └── build.yml            ← GitHub Actions workflow
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-03-19-cr-bot-design.md
├── requirements.txt
└── README.md
```
