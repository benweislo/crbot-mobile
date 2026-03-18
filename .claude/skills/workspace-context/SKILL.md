---
name: workspace-context
description: >
  Load full D:\WORK workspace context for every task. Use this skill whenever
  the user works from D:\WORK or mentions any project folder: AI_BOX, E-MELIES,
  WSLO.lab, WSLO.lab, RIG/EMPATHIK, NANO, MAIN_ALL, MASTERCLASS_V02, SKILL_MASTER,
  présentation_melies_pour_frank, MEETINGS, or REMOTION. Also trigger when the user
  mentions: course generation, e-learning, animation, image generation, Kie.ai,
  Maya mocap, agency website, brand assets, presentations, skills repository,
  mRig, Vimeo, xAPI, CeraPro, synergology, compte rendu, CR, réunion, meeting,
  transcription, or any expert name (Kevin Bertelli, Thierry Dupont, Denis Brusseaux).
  This skill provides full project awareness so Claude can answer any question
  about the workspace without re-scanning.
---

# D:\WORK — Full Workspace Context

You are working in Ben Weislo's central workspace at `D:\WORK`. Ben is a Senior 3D Animator & Tech Lead at Ecole Georges Melies (animation/cinema school, France). Below is everything you need to know about every project.

For ultra-detailed information (full file trees, component lists, API specs), read `D:\WORK\WORKSPACE_REFERENCE.md`.

---

## Quick Project Map

| Folder | What It Is | Stack | Status |
|--------|-----------|-------|--------|
| **AI_BOX** | AI course generator ("GO {Name}" pipeline) | Claude-only, HTML output | 3 experts done |
| **E-MELIES** | E-learning platform "Animation d'Excellence" | React 19 + Vite 7 + Tailwind 4 + Vimeo | 8/11 modules, 30 videos |
| **WSLO.lab** | AI for 3D animation schools | Next.js 16 + React 19 + Tailwind v4 + next-intl | Rebranding |
| **RIG** | EMPATHIK — AI motion capture for Maya | Python 3.10+, PyTorch, MediaPipe, FLAME, PySide6 | Phase 5 (210 tests) |
| **NANO** | Image generation + presentations | Kie.ai API + Python scripts | 109 images, 100 prompts |
| **MAIN_ALL** | Brand assets (fonts, logos, colors) | Static assets | Stable |
| **MASTERCLASS_V02** | Raw masterclass content archive | PPT, video (118 GB) | Archive |
| **SKILL_MASTER** | Skills repository (4 local + 16 Anthropic) | Markdown skills | Stable |
| **MEETINGS** | Meeting transcription & CR automation | Gladia + GPT-4o, Python | Active (5 recordings) |
| **présentation_melies_pour_frank** | HTML pitch presentation | Self-contained HTML | Done |
| **REMOTION** | Empty placeholder | — | Unused |

---

## AI_BOX — AI Course Generator

**Path:** `D:\WORK\AI_BOX`
**CLAUDE.md:** `D:\WORK\AI_BOX\CLAUDE.md` (14 KB — full pipeline spec, READ THIS for any AI_BOX task)

**What:** Transforms raw expert materials into structured e-learning courses for Melies.
**Pipeline:** User says "GO {Expert_Name}" → Phase 1 (sort files) → Phase 2 (analyze + design) → Phase 3 (generate HTML + TXT)

**Experts done:**
- **Kevin Bertelli** (Technical Artist, Unreal/Lighting) — V02 complete. 20+ years, studios: TeamTO, Mikros. Credits: Miraculous Ladybug, Alan Wake 2
- **Thierry Dupont** (Lighting Supervisor) — V01 complete. 15+ years, studios: Illumination Mac Guff, Mikros Animation. Credits: Despicable Me 3, Asterix
- **Denis Brusseaux** (Narrative Director/Analyse Filmique) — V01 complete. Formation "Voir un film". Narrative Director Ubisoft, screenwriter, journalist. 68 Vimeo videos (~1M words transcripts). 6 modules / 19 chapitres: Regard → Langage → Suggestion → Narration → Genres → Culture

**Key paths:**
- Input: `AI_BOX/Expert_input/{Prenom_Nom}/ALL/` (drop files here)
- Output: `AI_BOX/Expert_output/{Prenom_Nom}/` (HTML + TXT deliverables)
- References: `AI_BOX/source_files/` (Melies docs, READ-ONLY)

**Philosophy:** "Timeless Knowledge First" — teach universal principles (timing, observation, storytelling), NOT software tutorials. Tools mentioned contextually, never as core subject.

**Melies Hierarchy:** Formation → Module → Chapitre → Partie (recording unit)
**Assessment:** Quiz (end of Chapitre/Module), Exercice (end of Module), Evaluation finale (end of Formation)

**Output format:** Self-contained HTML (Melies brand: #050505 bg, indigo/rose/violet gradient, CeraPro fonts embedded base64, bokeh orbs, film grain, vignette, glass-morphism cards). No external dependencies. Auto-versioning (V01 → V02 → V03, never overwrite). Restyle script: `Expert_output/_restyle.py`.

---

## E-MELIES — E-Learning Platform

**Path:** `D:\WORK\E-MELIES`
**CLAUDE.md:** `D:\WORK\E-MELIES\CLAUDE.md` (project overview)
**Run:** `cd D:\WORK\E-MELIES\website && npm run dev` → http://localhost:5173

**What:** React SPA for "Animation d'Excellence" training. 11 modules, 75 lessons, 30 Vimeo videos, interactive quizzes, xAPI learning analytics.

**Stack:** React 19.2 + Vite 7.2 + TypeScript + Tailwind 4.1 + Framer Motion 12 + @vimeo/player + @splinetool/react-spline + lucide-react + zod v4

**Key files:**
- `website/src/data.ts` — Master syllabus (11 modules, 75 lessons, FR+EN i18n strings, vimeoIds)
- `website/src/quizData.ts` — Quiz questions (Module 1-2 complete, FR+EN)
- `website/src/index.css` — Design tokens (primary #E93F7F, dark #14121f, accent #5b54e0)
- `website/src/components/Dashboard.tsx` — Main learning UI
- `website/src/components/VideoPlayer.tsx` — Vimeo embed + xAPI tracking
- `website/src/components/QuizPlayer.tsx` — Interactive quiz (70% pass threshold)
- `website/src/services/xapiClient.ts` — Learning analytics (play/pause/complete/score events)
- `contenu/vimeo_mapping.json` — 30 video metadata + embed URLs
- `contenu/vimeo_sync.py` — Upload/sync script (Vimeo API)

**Content pipeline:** Local .mov files → Vimeo (private, embed-only, folder 28112095) → React player (via vimeoId in data.ts)

**Modules (11):**
0. Introduction | 1. Uncanny Valley | 2. Observation | 3. Reference Video | 4. Psychological Credibility (synergology) | 5. Timing | 6. Humour* | 7. Storytelling | 8. Artisan & AI* | 9. Stress & Well-being* | 10. Bonus (Weight/Inertia)
(*not yet filmed)

**Design:** Dark glass-morphism (#14121f bg, #E93F7F hot pink → #9333EA purple gradient). Fonts: Outfit (headings), Inter (body). Framer Motion animations.

**Auth:** LocalStorage-based stub (WPO365 SSO planned for ecolemelies.fr)
**Deployment:** OVH VPS (vpsf39a6737.ovh.net) — pending
**Subtitles:** 28/30 videos have EN+FR, 2 bonus videos without

### Quiz Generation Pipeline (NotebookLM)

**Workflow doc:** `E-MELIES/.agent/workflows/add-quiz.md` — READ THIS for any quiz task
**NotebookLM notebook ID:** `2596347c-ab1f-489c-990b-6fad7c9855ac` ("quiz for e-melies")

**7-step process:**
1. **Pre-flight:** Check if quiz exists in `quizData.ts` for target lessonId
2. **Locate SRTs:** Find `_EN.srt` files in `contenu/ANIM_EX/{module_folder}/`
3. **Upload to NotebookLM:** `mcp_notebooklm_source_add` (source_type: "text", save source_ids)
4. **Generate quiz:** `mcp_notebooklm_studio_create` (artifact_type: "quiz", 10 questions/module, 5/chapter, difficulty: "medium", language: "en")
5. **Download:** `mcp_notebooklm_download_artifact` → raw JSON temp file
6. **Add to website:** Transform NotebookLM format → `quizData.ts` format (correctIndex 0-based, translate to FR, clean `$` signs)
7. **Cleanup:** Delete sources from NotebookLM, verify in dev server

**NotebookLM raw format:**
```json
{ "questions": [{ "question": "...", "answerOptions": [{ "text": "...", "isCorrect": true, "rationale": "..." }], "hint": "..." }] }
```

**quizData.ts format:**
```typescript
{lessonId}: { title: "Module X: Title", en: [{ question, options[], correctIndex, explanation, hint }], fr: [...translated] }
```

**Quizzes done:** Module 1 (lessonId 104, 9 questions), Module 2 (lessonId 203, 9 questions)
**Quizzes pending:** Module 4 Ch.2 (412), Module 4 Ch.3 (414), Module 5 Ch.1 (507)

---

## WSLO.lab — AI for 3D Animation Schools

**Path:** `D:\WORK\WSLO.lab`
**Handoff:** `D:\WORK\WSLO.lab\HANDOFF.md`
**Run:** `cd D:\WORK\WSLO.lab\website && npm run dev` → http://localhost:3000

**What:** Premium dark futuristic trilingual website for WSLO.lab — Ben's AI automation agency specialized in 3D animation schools. Rebranding in progress.

**Stack:** Next.js 16.1.6 + React 19.2 + TypeScript + Tailwind v4 (config in globals.css, NO tailwind.config.ts) + next-intl 4.8 + Framer Motion 12.34 + @tsparticles + lucide-react

**Languages:** EN (default), FR, ES — full translations in `website/messages/{en,fr,es}.json`
**Routing:** `/[locale]/` with next-intl middleware. Use `<Link>` from `@/i18n/navigation`, NOT `next/link`.

**Pages (5):**
1. **Home** — 10 sections: Hero, Problem, Services, WhyMe, HowItWorks, Stats, CaseStudies, Pricing, FAQ, FinalCTA
2. **Services** — 4 service cards (Automation, Chatbots, Websites, Software)
3. **About** — Mission, bio (Ben Weislo), 4 values, 6 expertise skills
4. **Contact** — Form (name, email, company, service dropdown, message) — UI only, no backend
5. **Case Studies** — 4 cards (E-commerce, Real Estate, Law Firm, Healthcare)

**Design system (`website/src/app/globals.css`):**
- Background: #060810 | Surface: #0C1019, #131A24, #1B2332
- Brand gradient: Violet #6C3FD1 → Indigo #7B7DC8 → Teal #5EBFAB
- Fonts: Sora (headings), DM Sans (body)
- Utilities: .gradient-text, .shimmer-text, .glass-card, .gradient-border, .orb-violet/teal/indigo, .aurora
- Git branch: `master`

**Key components:** `src/components/sections/` (10 homepage sections), `src/components/pages/` (4 page clients), `src/components/ui/` (SpotlightCard, AnimatedGradientText, AuroraBackground, BorderBeam, LightningArc, Text3D)

---

## RIG (EMPATHIK) — AI Motion Capture for Maya

**Path:** `D:\WORK\RIG`
**Design doc:** `D:\WORK\RIG\EMPATHIK_DESIGN.md` (42 KB, French — READ THIS FIRST for any RIG task)
**Code:** `D:\WORK\RIG\empathik/` (Git repo, 510+ commits)
**Version:** 0.5.0

**What:** External Python app that does AI-powered facial/body/hand tracking from video, then sends animation data to any Maya rig via TCP socket.

**Architecture:** Two-component system:
1. **External App** (Python 3.10+, PyTorch, MediaPipe, PySide6): Video → AI tracking → FLAME fitting → style processing → keyframes → JSON/TCP
2. **Maya Plugin** (Python): TCP receiver → rig scanner → AU-to-controller mapping → animation layers → keyframes

**AI Pipeline:** Video → MediaPipe (face 468 landmarks + body 33 + hands 21 + iris) → FLAME 3D model fitting → SMIRK (subtle expressions) → SPECTRE (mouth) → OpenFace 3.0 (18 AUs) → One-Euro filter → Style processing → Smart keyframes

**Key innovations:**
- **Dual-camera 90°:** Model-based fitting (not stereo) — front for eyes/mouth, side for jaw/cheek
- **Probe & Learn:** Blackbox rig understanding — test each controller, analyze deformation, classify to AUs
- **Self-correction:** Render rig → compare with video (SSIM + landmarks + perceptual loss) → adjust
- **Style Slider:** 0.0 (cartoon) to 1.0 (ultra-realistic), controls 52 parameters
- **Anti-uncanny valley:** 6 rules (bright eyes, 3-sec holds, micro-layers, active upper-face, natural asymmetry)
- **Presets:** pixar (0.25), arcane (0.40), realistic (0.95), anime (0.08)

**Key module paths:**
- `empathik/app/tracking/` — 4 trackers + filtering
- `empathik/app/flame/` — FLAME model, fitter, landmarks
- `empathik/app/style/` — Style processor, keyframe reducer, saccade generator, uncanny checker, presets
- `empathik/app/rig/` — Rig map, classifier, region detector, mapped applicator
- `empathik/app/correction/` — Self-correct loop, comparator
- `empathik/maya_plugin/` — Plugin entry, rig scanner (6-layer), probe engine, applicators, UI panel
- `empathik/tests/` — 45 files, 210+ tests

**Communication:** TCP socket localhost:7777, JSON format per frame
**Research:** `D:\WORK\RIG\research/` — 8 markdown files (facial mocap tools, FLAME, FACS, rig architecture, uncanny valley)

---

## NANO — Image Generation + Presentations

**Path:** `D:\WORK\NANO`

**What:** Three sub-projects:
1. **Image generation** via Kie.ai API (Nano Banana 2 model)
2. **Presentation generation** for Melies pitch
3. **mRig character design** exploration

**Image gen command:**
```bash
cd C:/Users/User/WORK/NANO && python scrips/generate_kie.py prompts/FILE.json images/FOLDER/OUTPUT.jpg
```
**API key:** `KIE_AI_API_KEY` in `C:\Users\Ben\ENV\.env`

**Inventory:**
- 100 JSON prompt files (8 slides + 10 mRig + 20 design styles + 20 character explorations + 2 model sheets + 40 logos)
- 109 generated images (41 design exploration in 3 rounds, 40 WSLO logos in 4 batches, 10 mRig model sheets, 8 backgrounds, 8 slide overlays)

**Presentation pipeline:**
1. `generate_backgrounds.py` → 8 cinematic bg images via Kie.ai (16:9, concurrent)
2. `build_slides.py` → PIL overlays text on backgrounds (CeraPro fonts, Melies colors)
3. `assemble_html.py` → Self-contained HTML with base64-embedded fonts/images/logos → `D:\WORK\présentation_melies_pour_frank\presentation_melies.html`

**mRig project:** Character design for 3D rigging. 3 body types (thin/medium/chubby), 3 face variants, expression sheets, hand ref, extreme poses. Pixar-adjacent style. Round 3 awaiting triage.

**Prompt best practices:** Camera mathematics (focal length, aperture, ISO), explicit imperfections ("mild redness, subtle freckles"), negative directives in positive prompt, mandatory negative stack ("plastic skin", "AI look").

---

## MEETINGS — Meeting Transcription & CR Automation

**Path:** `D:\WORK\MEETINGS`

**What:** Automated pipeline that transcribes meeting audio recordings and generates structured compte rendus (CR). Drop an audio file in the folder, run the pipeline, get a full transcript + concise summary.

**Trigger phrases:** "compte rendu", "CR de réunion", "transcription réunion", "réunion d'aujourd'hui"

**Pipeline:**
1. Audio file (.mp3/.wav/.m4a/etc.) → Gladia API (transcription + speaker diarization) → `output/<stem>_meeting_CR.txt` (full verbatim transcript with timestamps)
2. Full transcript → OpenAI GPT-4o (summarization, temp 0.3) → `CR/<stem>_meeting_CR.txt` (structured summary)
3. CR summary → `generate_html.py` → `html/<stem>.html` (self-contained branded HTML page — Méliès dark theme, CeraPro fonts, bokeh, film grain, glass-morphism cards, print-friendly)

**Skill:** `MEETINGS/.skills/meeting-transcriber/SKILL.md`
**Workflow:** `MEETINGS/.agent/workflows/run.md` (10-step automation)

**Scripts:**
- `MEETINGS/.skills/meeting-transcriber/scripts/transcribe.py` — Gladia API upload, diarization, multi-file merge with time offset
- `MEETINGS/.skills/meeting-transcriber/scripts/summarize.py` — GPT-4o structured summary generation
- `MEETINGS/.skills/meeting-transcriber/scripts/generate_html.py` — CR → self-contained HTML (Méliès charter, CeraPro embedded, `--all` flag for batch)

**CR output structure:**
- **THÈMES ABORDÉS** — Topics with key excerpts
- **ACTIONS/PROCHAINES ÉTAPES** — Numbered action items
- **CONCLUSION DU MEETING** — Overall summary
- **TOUT EN DÉTAILS** — Detailed breakdown by theme with speaker attribution

**File naming:** `YYYY_MM_DD_meeting.mp3` or `AudioCapturer_YYYYMMDDHHMMSS.mp3`
**Same-day grouping:** Multiple audio files from same session are auto-merged as one meeting.
**Supported formats:** .mp3, .wav, .m4a, .ogg, .flac, .wma, .aac, .webm
**APIs:** Gladia (key in transcribe.py), OpenAI (`OPENAI_API_KEY` env var)

**Usage:** When user asks for a meeting CR:
1. Read skill at `MEETINGS/.skills/meeting-transcriber/SKILL.md`
2. Follow workflow at `MEETINGS/.agent/workflows/run.md`
3. Scan for new audio files, transcribe, summarize, generate HTML

---

## MAIN_ALL — Brand Assets

**Path:** `D:\WORK\MAIN_ALL`

**Fonts:** CeraPro family (Thin, Light, Regular, Medium, Bold, Black) + Italic variants. Formats: .ttf, .eot, .woff, .woff2. Path: `CHARTE SITE INTERNET MELIES/_CHARTE SITE INTERNET/_FONT/CERAPRO/`

**7 Section Color Palettes:**
- General: #4A2971 (Violet Signature)
- Home: Indigo/Rose/Violet gradient
- Cinema: #055C79 (dark blue)
- Image Animee: #0793AD (cyan)
- Master: #4E55A2 (indigo)
- Prep Arts Appliques: #9D2E88 (magenta)
- Virtual Production: #00A4E2 (electric blue)

**Logos:** 25+ variants (AI/PDF/PNG) at `_LOGO MELIES 24/`. Includes social versions, crescent moon motif.
**Backgrounds:** 7 HTML bokeh backgrounds (1 per section) at `_BACKGROUND_PAGES/`
**Stars:** 16 decorative PNGs (2 styles: filled "Poids", striped "Rayee") at `_ETOILES/`

**Key docs:**
- `CHARTE_GRAPHIQUE_SITE_MELIES.md` — Full visual design system (colors, fonts, effects, animations)
- `BEN_SPEAKING_STYLE_GUIDE.md` — Ben's authentic voice (French-influenced English, teaching style, humor)

**Books:** Body language & acting theory (Stanislavski, Navarro, Turchet, Bowden, Biland) at `BOOKS/`
**Project docs:** INA pedagogical analysis, module templates, AI extraction summaries at `Documents_project_general/`

---

## MASTERCLASS_V02 — Raw Content Archive (118+ GB)

**Path:** `D:\WORK\MASTERCLASS_V02`

**Core:** "How To Be Imperfect" masterclass — Ben's signature presentation on animation psychology
- `HowToBeImperfect.pptx` (994 MB) — Main PowerPoint
- 10 exported video segments (.mov) — Specific demonstrations (micro-expressions, timing, observation, the "I don't know" test)

**Festival footage:** LIVE_MELIES/ — Festival Melies 2025 recording (114 GB, 5 camera angles)
**Research:** TEST/ — Jack Nicholson acting analysis, animal behavior studies, uncanny valley infographics, Mehrabian 7-38-55, synergology reference images
**Key research doc:** `synergology_micro-gestures_research.md` (52 KB) — Philippe Turchet's synergology system, Ekman comparison, 1500+ classified body signs

This content feeds into E-MELIES modules (especially Module 4: Psychological Credibility, Module 1: Uncanny Valley).

---

## SKILL_MASTER — Skills Repository

**Path:** `D:\WORK\SKILL_MASTER`

**3 Root skills** at `D:\WORK\.claude\skills/`:
1. `workspace-context` — Full workspace context loader
2. `extract-video-clips` — YouTube clip extraction for E-MELIES
3. `check-updates` — Manual skill update checker (`/check-updates`)

**4 Local skills** at `.agent/skills/`:
1. `creating-skills` — Skills 2.0 format guide (YAML frontmatter)
2. `executing-continuously` — High-autonomy execution mode
3. `processing-video-captions` — Video post-production (Auphonic + brand subtitles)
4. `ui-ux-pro-max` — Design intelligence (67 styles, 96 palettes, 57 font pairings, 99 UX guidelines, 13 tech stacks, 26 CSV databases)

**17 Anthropic reference skills** at `anthropic-skills/skills/`: algorithmic-art, brand-guidelines, canvas-design, claude-api (NEW), doc-coauthoring, docx, frontend-design, internal-comms, mcp-builder, pdf, pptx, skill-creator, slack-gif-creator, theme-factory, webapp-testing, web-artifacts-builder, xlsx

**Last synced:** 2026-03-12 (git pull + PR #210 frontend-design applied)

**Brand assets:** `brand_assets/` — logo_main.png, logo_mini.png, logo_square.png, brand_guidelines.md

---

## Global Configuration

- **API keys:** `C:\Users\Ben\ENV\` — central .env files for all projects
- **Melies dark theme:** #1a202c bg, #facc15 gold, #e2e8f0 text (used in AI_BOX, E-MELIES, NANO, presentations)
- **WSLO dark theme:** #060810 bg, violet→teal gradient (separate design system)
- **User:** Ben Weislo | **GitHub:** benweislo | **Language:** French (communication), English (code/docs)
- **Always exclude:** NUTRIA folder from any scans

---

## Cross-Project Relationships

```
MASTERCLASS_V02 (raw footage/research)
    ↓ feeds content
E-MELIES (platform) ← AI_BOX (generates course structures from expert interviews)
    ↑ uses brand
MAIN_ALL (fonts, colors, logos) → NANO (presentations) → présentation_melies_pour_frank
    ↑ uses brand                    ↑ also generates logos for
WSLO.lab (separate brand)           WSLO.lab (agency website)

RIG/EMPATHIK (independent tool, uses E-MELIES uncanny valley research)
SKILL_MASTER (independent skill repository, feeds automation workflows)
```

## Knowledge Sync Rule — MANDATORY

**Whenever you update a skill, CLAUDE.md, or any knowledge file in a subfolder project, OR whenever you discover new information about the workspace (new files, changed stacks, new features, new experts, status changes, etc.), you MUST also update the root-level knowledge sources:**

1. **This skill** (`D:\WORK\.claude\skills\workspace-context\SKILL.md`) — update the relevant project section with the new info
2. **Root CLAUDE.md** (`D:\WORK\CLAUDE.md`) — update if the change affects the quick reference table or key rules
3. **Auto-memory** (`C:\Users\Ben\.claude\projects\D--WORK\memory\MEMORY.md`) — update the relevant project details section
4. **WORKSPACE_REFERENCE.md** (`D:\WORK\WORKSPACE_REFERENCE.md`) — update if the change affects file trees, component lists, or API specs

**Examples of when to sync:**
- You add a quiz to E-MELIES → update "Quizzes done/pending" here, in MEMORY.md, and in WORKSPACE_REFERENCE.md
- You create a new skill in a project subfolder → update SKILL_MASTER section here + MEMORY.md
- A project's stack changes (new dependency, version bump) → update the stack info here + MEMORY.md
- A new expert is processed in AI_BOX → update "Experts done" here + MEMORY.md
- You discover a project has a new CLAUDE.md → add it to the root CLAUDE.md "Project CLAUDE.md Files" list
- A project status changes (e.g., "Phase 5" → "Phase 6") → update status everywhere

**This is not optional.** Root-level knowledge must always reflect the current state of the workspace. Never leave root docs stale after making changes in subfolders.

---

## How to Use This Context

When the user mentions a project by name or alias, you already know:
- What it does, what stack it uses, where the key files are
- Which CLAUDE.md to read for detailed instructions
- How to run it, build it, or extend it
- How it relates to other projects

For deeper details on any project, read `D:\WORK\WORKSPACE_REFERENCE.md`.
For project-specific instructions, read the project's own CLAUDE.md (AI_BOX and E-MELIES have them).
