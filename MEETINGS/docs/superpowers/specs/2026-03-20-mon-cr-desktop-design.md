# Mon CR — Desktop Meeting Minutes App

**Date:** 2026-03-20
**Author:** Ben Weislo
**Status:** Design approved

## Overview

Desktop PySide6 application for automated meeting minutes generation. Scans a configured audio folder for new recordings, transcribes via Gladia API, summarizes via local Claude Code CLI (`claude -p`), and generates branded HTML reports. Designed for personal use with WSLO.lab branding as default theme.

## Goals

- One-click CR generation from audio recordings
- Zero API cost for summarization (uses local Claude Code subscription)
- Configurable theming, prompts, and paths
- Reuses existing MEETINGS folder structure and outputs

## Non-Goals

- Multi-client / white-label support (that's CR_BOT)
- Cloud deployment or proxy server
- Real-time transcription or live recording

## Architecture

```
┌──────────────────────────────────────┐
│         PySide6 Desktop App          │
│                                      │
│  ┌──────────┐  ┌──────────────────┐  │
│  │ Scanner  │  │  Settings Panel  │  │
│  │ (auto)   │  │  (paths, prompt, │  │
│  │          │  │   theme, logo)   │  │
│  └────┬─────┘  └──────────────────┘  │
│       │                              │
│  ┌────▼─────────────────────────┐    │
│  │  Pipeline Orchestrator       │    │
│  │  (runs in QThread worker)    │    │
│  │  1. Transcriber (Gladia API) │    │
│  │  2. Summarizer (claude -p)   │    │
│  │  3. HTML Generator (local)   │    │
│  └──────────────────────────────┘    │
│       │ signals: stage_changed,      │
│       │ progress, finished, error    │
│  ┌────▼─────────────────────────┐    │
│  │  UI: Progress + History      │    │
│  └──────────────────────────────┘    │
└──────────────────────────────────────┘
```

## Threading Model

The pipeline runs in a **`QThread`** worker to keep the UI responsive during long operations (Gladia upload, Claude processing). Communication between worker and UI via Qt signals:

| Signal | Payload | Purpose |
|--------|---------|---------|
| `stage_changed(str, int)` | stage name, stage index (0-2) | Updates progress indicator |
| `progress(str)` | status message | Updates status label |
| `session_complete(str)` | HTML output path | Adds to history, opens browser |
| `error(str, str)` | stage name, error message | Shows error in UI |
| `finished()` | — | Re-enables Generate button, resets status |

The "Générer CR" button is **disabled** while a pipeline is running. All pending sessions are processed **sequentially** in a single worker run (one after another).

## Pipeline Stages

### Stage 1: Scanner

- Scans configured audio folder for supported formats: `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.wma`, `.aac`, `.webm`
- Compares against `history.json` to identify unprocessed files
- Groups files from the same **calendar day** as a single meeting session (e.g. two recordings from 2026-03-20 = one CR)
- `history.json` format:
  ```json
  {
    "processed": [
      {
        "file": "2026_03_20_meeting.mp3",
        "processed_at": "2026-03-20T14:30:00",
        "html_output": "html/2026_03_20_CR_meeting.html"
      }
    ]
  }
  ```

### Stage 2: Transcriber (Gladia API)

- Uploads audio to Gladia API (`https://api.gladia.io/v2/upload`)
- Starts transcription with diarization enabled
- Polls for completion
- Outputs structured transcript to `output/<stem>_meeting_CR.txt`
- API key loaded from `C:\Users\User\ENV\` (environment variable `GLADIA_API_KEY`)
- Timeout: 600s for large files

### Stage 3: Summarizer (local Claude Code)

- Runs `claude -p` as subprocess with the CR system prompt
- Pipes transcript text as the user prompt via stdin
- System prompt is configurable via Settings (stored in `config.json`)
- Command invocation:
  ```python
  result = subprocess.run(
      ["claude", "-p", "--system-prompt", system_prompt, "Voici la transcription complète de la réunion :"],
      input=transcript_text,
      capture_output=True, text=True, timeout=600
  )
  ```
- Default system prompt (from proven MEETINGS pipeline):
  ```
  Tu es un assistant expert en rédaction de comptes rendus professionnels.
  On te fournit la transcription d'une réunion. Tu dois générer un Compte Rendu (CR)
  structuré en respectant exactement le format suivant :

  ============================================================
  COMPTE RENDU DE RÉUNION
  ============================================================
    Date     : {date}
    Durée    : {duree}
    Fichiers : {fichier}
  ------------------------------------------------------------
  THÈMES ABORDÉS
  ------------------------------------------------------------
    - Liste courte, à puces, des grands sujets abordés
  ------------------------------------------------------------
  ACTIONS / PROCHAINES ÉTAPES
  ------------------------------------------------------------
    - Actions claires et précises, PAR PERSONNE avec détails
  ------------------------------------------------------------
  CONCLUSION DU MEETING
  ------------------------------------------------------------
    - Résumé global
  ------------------------------------------------------------
  TOUT EN DÉTAILS
  ------------------------------------------------------------
    - Sections thématiques numérotées, exhaustives
  ============================================================
  FIN DU COMPTE RENDU
  ============================================================
  ```
- Output: `CR/<stem>_meeting_CR.txt`

### Stage 4: HTML Generator

- Parses CR text into sections (themes, actions, conclusion, details)
- Injects brand assets from config (colors, logo, fonts)
- Uses HTML template with CSS variables for theming
- Effects: bokeh orbs, film grain, vignette, glass-morphism cards
- Print-friendly CSS included
- Output: `html/YYYY_MM_DD_CR_<stem>.html`
- Auto-opens in default browser on completion

## User Interface

### Main Window

```
┌─────────────────────────────────────────┐
│  [wslo.lab logo]          [⚙ Settings]  │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  Status: ● Prêt                         │
│  Fichiers en attente: 2                 │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │     [ Générer CR ]              │    │
│  │  (gradient violet→teal button)  │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ── Progression ─────────────────────   │
│  ○ Transcription    ○ Résumé   ○ HTML   │
│                                         │
│  ── Historique ──────────────────────   │
│  │ 2026-03-19 — Réunion pédagogique │   │
│  │ 2026-03-12 — Point projet E-Mel  │   │
│  │ 2026-02-26 — Brief vidéo         │   │
│  └───────────────────────────────────   │
└─────────────────────────────────────────┘
```

- **Logo:** WSLO.lab logo top-left (loaded from config, default: logo-wslo.png embedded as base64)
- **Settings gear:** Top-right, opens Settings dialog
- **Status indicator:** Green dot = ready, orange = processing, red = error
- **Pending count:** Number of unprocessed audio files detected
- **Generate button:** Large, gradient violet→teal, centered
- **Progress bar:** 3-step indicator with labels, fills as pipeline progresses
- **History list:** Clickable rows — click opens the HTML in browser. Sorted by date descending. Populated from two sources: (1) `history.json` for app-generated CRs, (2) scan of `html/` folder for pre-existing CR files (from the old MEETINGS pipeline). This ensures first-launch shows full history.

### Settings Dialog

```
┌─────────────────────────────────────────┐
│  Paramètres                      [ X ]  │
│                                         │
│  ── Dossiers ────────────────────────   │
│  Dossier audio:  [C:\...\MEETINGS  ][…] │
│  Dossier output: [C:\...\html      ][…] │
│                                         │
│  ── Résumé ──────────────────────────   │
│  Prompt système:                        │
│  ┌─────────────────────────────────┐    │
│  │ Tu es un assistant spécialisé   │    │
│  │ dans la rédaction de comptes    │    │
│  │ rendus de réunion...            │    │
│  └─────────────────────────────────┘    │
│  Langue: [Français ▼]                   │
│                                         │
│  ── Apparence ───────────────────────   │
│  Couleur primaire:   [■ #8B5CF6] [🎨]  │
│  Couleur secondaire: [■ #6366F1] [🎨]  │
│  Couleur tertiaire:  [■ #2DD4BF] [🎨]  │
│  Background:         [■ #0B0F1A] [🎨]  │
│  Texte:              [■ #EDF0F7] [🎨]  │
│  Logo: [logo-wslo.png        ] [Changer]│
│                                         │
│  ── API ─────────────────────────────   │
│  Clé Gladia: [••••••••••••••••] [👁]    │
│                                         │
│       [ Réinitialiser ]  [ Sauvegarder ]│
└─────────────────────────────────────────┘
```

## Theming

### Default Theme: WSLO.lab

| Role | Color | Hex |
|------|-------|-----|
| Background | Dark blue-black | `#0B0F1A` |
| Surface | Dark blue-grey | `#111827` |
| Surface elevated | Medium dark | `#1A2035` |
| Primary | Violet | `#8B5CF6` |
| Secondary | Indigo | `#6366F1` |
| Tertiary | Teal | `#2DD4BF` |
| Text primary | Lavender-white | `#EDF0F7` |
| Text secondary | Muted blue | `#8891AB` |
| Danger | Red | `#F87171` |

### UI Effects (PySide6)

- **Glass-morphism:** Semi-transparent cards (`rgba` backgrounds with ~80% opacity) painted over pre-blurred background pixmap. No native backdrop-blur in Qt — approximate by painting blurred orbs behind, then overlaying semi-transparent card surfaces.
- **Gradient button:** QPalette gradient from violet (#8B5CF6) through indigo (#6366F1) to teal (#2DD4BF)
- **Subtle orbs:** Painted via `QPainter` — 2-3 large blurred circles (violet, teal) in background
- **Font:** DM Sans (embedded) for body text, fallback to system sans-serif

### Theme in HTML Output

The HTML template uses the same color palette from config. CSS variables:
```css
:root {
  --primary: #8B5CF6;
  --secondary: #6366F1;
  --tertiary: #2DD4BF;
  --bg: #0B0F1A;
  --surface: #111827;
  --text: #EDF0F7;
  --text-muted: #8891AB;
}
```

## Configuration

### config.json (persisted at app root)

```json
{
  "audio_folder": "C:\\Users\\User\\WORK\\MEETINGS",
  "output_folder": "C:\\Users\\User\\WORK\\MEETINGS\\html",
  "transcript_folder": "C:\\Users\\User\\WORK\\MEETINGS\\output",
  "cr_folder": "C:\\Users\\User\\WORK\\MEETINGS\\CR",
  "language": "fr",
  "gladia_api_key": "",
  "system_prompt": "Tu es un assistant spécialisé...",
  "theme": {
    "primary": "#8B5CF6",
    "secondary": "#6366F1",
    "tertiary": "#2DD4BF",
    "background": "#0B0F1A",
    "surface": "#111827",
    "surface_elevated": "#1A2035",
    "text_primary": "#EDF0F7",
    "text_secondary": "#8891AB",
    "danger": "#F87171"
  },
  "logo_path": "assets/logo-wslo.png"
}
```

- On first launch, if `config.json` doesn't exist, create from defaults
- Gladia API key priority: (1) `config.json` value if set, (2) env var `GLADIA_API_KEY` from `C:\Users\User\ENV\.env`, (3) prompt user in Settings on first launch
- All paths use forward slashes internally, converted for OS display

### history.json (persisted at app root)

Tracks processed files to avoid reprocessing. Updated after each successful pipeline run.

## File Structure

```
MEETINGS/
├── app/
│   ├── main.py                 # Entry point, QApplication + window
│   ├── ui/
│   │   ├── main_window.py      # Main window layout + signals
│   │   ├── settings_dialog.py  # Settings panel
│   │   ├── progress_widget.py  # 3-step progress indicator
│   │   ├── history_panel.py    # CR history list
│   │   └── theme.py            # QSS stylesheet builder from config
│   ├── pipeline/
│   │   ├── scanner.py          # Audio folder scanner + history check
│   │   ├── transcriber.py      # Gladia API client
│   │   ├── summarizer.py       # claude -p subprocess wrapper
│   │   ├── html_generator.py   # CR → branded HTML
│   │   ├── html_template.py    # HTML template string with CSS vars
│   │   └── orchestrator.py     # Pipeline coordinator (scan→transcribe→summarize→html)
│   ├── config/
│   │   ├── defaults.py         # Default config values + WSLO theme
│   │   └── manager.py          # Load/save config.json + history.json
│   └── assets/
│       ├── logo-wslo.png       # Default logo (copied from WSLO.lab)
│       └── fonts/
│           └── DMSans-Regular.ttf
├── config.json                 # User settings (auto-created on first launch)
├── history.json                # Processing history
├── output/                     # Transcripts (existing)
├── CR/                         # CR text files (existing)
└── html/                       # HTML reports (existing)
```

## Error Handling

| Error | Behavior |
|-------|----------|
| No new audio files | Status: "Tout est à jour" (green) |
| Gladia API failure | Status: error message, retry button. If upload succeeded (URL cached), retry resumes from polling. Otherwise re-uploads. |
| `claude -p` failure | Status: error message with stderr output. Suggest checking Claude Code installation. |
| Concurrent click | Generate button disabled while pipeline runs. |
| Very large transcript (>150K tokens) | Log warning. Claude Code handles context natively — no truncation needed for now. |
| Malformed CR text | HTML generator uses raw text as fallback (single "Détails" section) |
| Config file corrupt | Reset to defaults, warn user |

## Dependencies

- **Python 3.10+** (already installed)
- **PySide6** (Qt for Python — desktop UI)
- **requests** (HTTP for Gladia API)
- **Claude Code CLI** (already installed — used via `claude -p`)

No other dependencies. Deliberately minimal.

## What We Reuse

| From | What |
|------|------|
| MEETINGS scripts | CR system prompt, HTML template structure (bokeh, glass-morphism, film grain) |
| MEETINGS folders | `output/`, `CR/`, `html/` directory structure |
| WSLO.lab | Logo PNG, color palette, DM Sans font |
| CR_BOT patterns | PipelineOrchestrator pattern, progress widget concept, history panel concept |

## Launch

```bash
cd C:\Users\User\WORK\MEETINGS
python app/main.py
```

Optional: create a Windows shortcut on desktop pointing to `pythonw app/main.py` with working directory set to `MEETINGS/`.
