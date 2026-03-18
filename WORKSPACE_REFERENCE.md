# D:\WORK — Complete Workspace Reference

> This file is the deep-dive companion to the `workspace-context` skill.
> It contains full file trees, component inventories, API details, and technical specs for every project.
> Last full scan: 2026-03-11

---

## Table of Contents

1. [AI_BOX](#ai_box)
2. [E-MELIES](#e-melies)
3. [WSLO.lab](#wslolab)
4. [RIG / EMPATHIK](#rig--empathik)
5. [NANO](#nano)
6. [MAIN_ALL](#main_all)
7. [MASTERCLASS_V02](#masterclass_v02)
8. [SKILL_MASTER](#skill_master)
9. [Presentation Frank](#présentation_melies_pour_frank)

---

## AI_BOX

### Full Directory Tree

```
AI_BOX/
├── CLAUDE.md                          [14 KB — Project brain, full pipeline spec]
├── docs/plans/
│   └── 2026-02-05-ai-box-design.md    [Design document]
├── source_files/                      [772 KB — READ-ONLY Melies reference docs]
│   ├── GUIDE_EXPERT.html              [Expert discovery interview framework]
│   ├── GUIDE_EXPERT_E_LEARNING.docx   [Full expert guide]
│   ├── Fonctionnement_du_site_E-Learning_Melies.html  [Platform architecture]
│   ├── Structure_et_nomenclature.docx [Course hierarchy & naming]
│   ├── workflow_melies_xapi.html      [xAPI workflow spec]
│   ├── Logo_ecole_Melies.png
│   ├── Logo_ecole_Melies_noir_blanc.png
│   └── LOGO_ecole_melies_ROND.png
├── Expert_input/
│   ├── README.md
│   ├── Kevin_Bertelli/
│   │   ├── ALL/                       [EMPTY — already sorted]
│   │   └── interview_decouverte/      [2 MP3 + 2 TXT transcripts]
│   └── Thierry_Dupont/
│       ├── ALL/                       [EMPTY — already sorted]
│       ├── interview_decouverte/      [1 TXT — meeting notes]
│       ├── documents/                 [3 TXT files]
│       └── references/                [1 TXT — Pixar article]
└── Expert_output/
    ├── README.md
    ├── _restyle.py                               [Batch restyle script — Melies brand]
    ├── Denis_Brusseaux/
    │   ├── Denis_Brusseaux_formation_V01.html/txt ← V01
    ├── Kevin_Bertelli/
    │   ├── Kevin_Bertelli_formation_V01.html/txt
    │   └── Kevin_Bertelli_formation_V02.html/txt  ← LATEST
    └── Thierry_Dupont/
        └── Thierry_Dupont_formation.html/txt       ← V01
```

### Expert Details

**Kevin Bertelli (sPiz)** — Technical Artist / Unreal Specialist
- Domain: Lighting, Rendering, Pipeline TD, Virtual Production
- Background: 20+ years (2 Minutes, Miraculous Corp, DARK MATTERS, TeamTO, Mikros Image)
- Credits: Les Legendaires, Miraculous Ladybug, Alan Wake 2
- Output V02: 4 modules — Principles of Narrative Lighting (not Unreal menus)
  - M1: What is light (philosophical/perceptual)
  - M2: Universal lighting principles (any software)
  - M3: Conceiving an eclairage (design thinking)
  - M4: Application in Unreal Engine

**Thierry Dupont** — Lighting Supervisor / Senior Artist
- Domain: Lighting, Rendering, Compositing
- Background: 15+ years (Illumination Mac Guff, Mikros Animation)
- Credits: Moi Moche et Mechant 3, Comme des Betes 2, Asterix, Pattie et la Colere de Poseidon
- Output V01: 4+ modules — Storytelling through lighting
  - M1: Understanding light (physics for artists)
  - M2: Color scripts & narrative direction
  - M3: Classical lighting schemas
  - M4: Studio pipeline (master lighting, passes, Arnold)

**Denis Brusseaux** — Narrative Director / Analyse Filmique
- Domain: Film analysis, narration, screenwriting, directing
- Background: Narrative Director Ubisoft, screenwriter, former journalist
- Formation: "Voir un film" — 6 modules / 19 chapitres / ~40 parties
  - M1: Le Regard (apprendre à voir)
  - M2: Le Langage Cinématographique (grammaire filmique)
  - M3: L'Art de la Suggestion (ce qu'on ne montre pas)
  - M4: Narration et Dramaturgie (structure narrative)
  - M5: Les Genres (codes et transgressions)
  - M6: Culture Cinématographique (patrimoine et références)
- Source: 68 Vimeo videos (~1M words transcripts from auto-generated FR captions)
  - 11 conférences Brusseaux
  - 43 séances d'analyse filmique
  - 14 analyses filmiques
- Input: `AI_BOX/Expert_input/Denis_Brusseaux/` (transcripts + analysis scripts)
- Output: `AI_BOX/Expert_output/Denis_Brusseaux/Denis_Brusseaux_formation_V01.html/txt`

### Pipeline Phases

**Phase 1 — File Sorting:** Sort `ALL/` into interview_decouverte/, capture_connaissance/, documents/, references/
**Phase 2 — Analysis:** Read all materials + Melies refs → Extended thinking → Optimal pedagogical structure
**Phase 3 — Generate:** HTML + TXT (Melies dark theme, self-contained, auto-versioned)

### Melies Domain Lists

**Animation:** Storyboard, Realisation animation, Layout 3D, Concept Art, Modelisation, Surfacing, Rigging, Animation basics, Acting & dialogue, FX, Lighting, Rendering, Compositing, Pipeline TD, Production animation

**Live Action:** Assistant realisateur, Chef operateur, Cadreur, Assistant camera, Gaffer, Grip, DIT, Son, Scripte, HMC, Costume, Decoration, Accessoires, Regie, SFX plateau, Cascades, Line producing

---

## E-MELIES

### Full Directory Tree

```
E-MELIES/
├── CLAUDE.md                    [Project overview]
├── STRUCTURE_PROJET.md          [Ecosystem map]
├── website/
│   ├── package.json             [React 19, Vite 7, Tailwind 4, Framer Motion 12]
│   ├── vite.config.js           [Vite + React plugin]
│   ├── tsconfig.json            [ES2020, strict mode]
│   ├── index.html               [HTML entry]
│   ├── public/logo.png          [40KB Melies logo]
│   ├── src/
│   │   ├── App.tsx              [Main router: home/dashboard]
│   │   ├── main.tsx             [Entry point]
│   │   ├── index.css            [Tailwind 4 + design tokens]
│   │   ├── data.ts              [11-module syllabus, 75 lessons, FR+EN]
│   │   ├── quizData.ts          [Quiz questions Module 1-2, FR+EN]
│   │   ├── components/
│   │   │   ├── App.tsx          [Global state: view, lang]
│   │   │   ├── Navbar.tsx       [Header + language switch]
│   │   │   ├── LandingPage.tsx  [Hero → Courses → Mentors → Footer]
│   │   │   ├── Hero.tsx         [Title gradient, animated orbs, stats bar]
│   │   │   ├── CoursesSection.tsx [Course cards: Anim Excellence + Unreal]
│   │   │   ├── MentorsSection.tsx [Mentor profiles]
│   │   │   ├── Dashboard.tsx    [Main learning UI: sidebar + player]
│   │   │   ├── Sidebar.tsx      [Module/lesson nav tree, expandable chapters]
│   │   │   ├── VideoPlayer.tsx  [Vimeo iframe + xAPI tracking]
│   │   │   ├── QuizPlayer.tsx   [Interactive quiz, 70% pass threshold]
│   │   │   ├── AuthContext.tsx  [User auth state]
│   │   │   ├── ProtectedRoute.tsx [Route guard]
│   │   │   ├── LoginPage.tsx    [Login form]
│   │   │   ├── LangSwitcher.tsx [FR/EN toggle]
│   │   │   ├── SplineBackground.tsx [3D Spline scene]
│   │   │   └── ParticlesBackground.tsx [Canvas particles]
│   │   ├── services/
│   │   │   ├── authService.ts   [Login/logout logic]
│   │   │   └── xapiClient.ts   [xAPI/LRS integration]
│   │   └── lib/utils.ts        [cn() Tailwind merger]
│   └── dist/                    [Build output]
├── contenu/
│   ├── .env                     [Vimeo API token]
│   ├── CLAUDE.md                [Video folder instructions]
│   ├── vimeo_mapping.json       [30 video metadata + embed URLs]
│   ├── vimeo_sync.py            [Upload/sync script, 579 lines]
│   ├── vimeo_audit.py           [Verification auditor]
│   ├── vimeo_final_check.py     [Quick status check]
│   ├── vimeo_fix_all.py         [Batch fix helper]
│   ├── upload_last_fr.py        [French subtitle uploader]
│   ├── ANIM_EX/                 [8 module folders, 29 .mov + 56 .srt]
│   │   ├── 00_introduction/     [1 video + EN/FR]
│   │   ├── 01_module_uncanny_valley/ [3 videos + EN/FR]
│   │   ├── 02_module_observation/ [2 videos + EN/FR]
│   │   ├── 03_module_ref/       [7 videos + EN/FR]
│   │   ├── 04_module_credibility_psy/ [9 videos + EN/FR]
│   │   ├── 05_module_timing/    [5 videos + EN/FR]
│   │   ├── 07_module_storytelling/ [1 video + EN/FR]
│   │   └── 10_module_bonus/     [2 videos, no subtitles]
│   └── [status/audit reports]
└── .agent/workflows/add-quiz.md [Quiz creation workflow]
```

### Module Detail (75 Lessons)

| # | Module | Lessons | Videos | Quiz | Status |
|---|--------|---------|--------|------|--------|
| 0 | Introduction | 2 | 1 | — | Done |
| 1 | Uncanny Valley | 4 | 3 | Yes | Done |
| 2 | Observation | 3 | 2 | Yes | Done |
| 3 | Reference Video | 10 | 7 | — | Done |
| 4 | Credibilite Psychologique | 16 | 9 | 2 | Done |
| 5 | Timing | 14 | 5 | 1 | Done |
| 6 | Humour | 6 | 0 | — | NOT FILMED |
| 7 | Storytelling | 4 | 1 | — | Done |
| 8 | Artisan & AI | 4 | 0 | — | NOT FILMED |
| 9 | Stress & Bien-etre | 4 | 0 | — | NOT FILMED |
| 10 | Bonus (Weight/Inertia) | 4 | 2 | — | Done (no subs) |

### Design Tokens (index.css)

```css
--color-melies-primary: #E93F7F;    /* Hot pink */
--color-melies-accent: #5b54e0;      /* Indigo */
--color-melies-purple: #9333EA;
--color-melies-dark: #14121f;        /* Background */
--color-melies-panel: #2a2740;
--color-melies-card: #1e1b2e;
--color-melies-text: #FFFFFF;
--color-melies-muted: #a0a0b4;
--color-melies-border: #2e2a45;
--font-display: "Outfit";
--font-body: "Inter";
```

### xAPI Tracking

Verbs: PLAYED, PAUSED, COMPLETED, PROGRESSED (25/50/75/100%), SCORED, ATTEMPTED, ANSWERED
Endpoint: `VITE_LRS_ENDPOINT` (default http://localhost:8081/data/xAPI)
Auth: `VITE_LRS_AUTH_KEY`

### Quiz Generation Pipeline (NotebookLM)

**Workflow:** `E-MELIES/.agent/workflows/add-quiz.md` (7-step process)
**NotebookLM notebook:** `2596347c-ab1f-489c-990b-6fad7c9855ac` ("quiz for e-melies")

**Process:**
1. Pre-flight: Check `quizData.ts` for existing quiz at target lessonId
2. Locate SRT files: `contenu/ANIM_EX/{module}/` → use `_EN.srt` files
3. Upload to NotebookLM: `mcp_notebooklm_source_add` (source_type: "text", save source_ids)
4. Generate quiz: `mcp_notebooklm_studio_create` (artifact_type: "quiz", 10 questions/module or 5/chapter, difficulty: "medium", language: "en", focus_prompt with key topics, confirm: true)
5. Download: `mcp_notebooklm_download_artifact` → temp JSON at `website/src/quiz_moduleX_raw.json`
6. Add to website: Transform to `quizData.ts` format (correctIndex 0-based, translate to FR, clean `$` from numbers)
7. Cleanup: `mcp_notebooklm_source_delete` for each source_id, verify in dev server

**NotebookLM raw output format:**
```json
{
  "title": "Quiz Title",
  "questions": [{
    "question": "...",
    "answerOptions": [{ "text": "...", "isCorrect": true, "rationale": "explanation" }],
    "hint": "..."
  }]
}
```

**quizData.ts target format:**
```typescript
interface QuizQuestion {
    question: string;
    options: string[];
    correctIndex: number;  // 0-based
    explanation: string;
    hint?: string;
}
interface QuizData {
    title: string;
    fr: QuizQuestion[];
    en: QuizQuestion[];
}
export const quizzes: Record<number, QuizData> = {
    104: { title: "Module 1: Uncanny Valley", en: [...], fr: [...] },
    203: { title: "Module 2: Observation", en: [...], fr: [...] },
};
```

**Quiz status:**

| LessonId | Module/Chapter | Questions | Status |
|----------|---------------|-----------|--------|
| 104 | Module 1: Uncanny Valley | 9 | Done (bilingual) |
| 203 | Module 2: Observation | 9 | Done (bilingual) |
| 412 | Module 4, Chapter 2 | — | Pending |
| 414 | Module 4, Chapter 3 | — | Pending |
| 507 | Module 5, Chapter 1 | — | Pending |

**Quiz Player features** (`QuizPlayer.tsx`):
- Bilingual (FR/EN), start screen with metadata, progressive questions, hint system
- Answer tracking with green/red highlighting, explanations after answer
- Score display with progress circle, 70% passing threshold
- xAPI tracking: ATTEMPTED (start), ANSWERED (per question), COMPLETED + SCORED (finish)

### Vimeo Integration

- Folder ID: 28112095 ("e-melies")
- 30 videos, all English language, private embed-only
- 28/30 have EN+FR subtitle tracks
- Vimeo token: `C:\Users\Ben\ENV\.env`
- Sync: `cd contenu && python vimeo_sync.py [--dry-run]`

---

## WSLO.lab

### Full Directory Tree

```
WSLO.lab/
├── HANDOFF.md                   [Complete handoff documentation]
├── handoff_context.md           [Gemini 3.1 Pro context]
├── docs/plans/
│   ├── 2026-02-20-ai-agency-website-design.md
│   └── 2026-02-20-ai-agency-website-plan.md
└── website/
    ├── package.json             [Next.js 16.1.6, React 19.2.3, next-intl 4.8.3]
    ├── next.config.ts           [withNextIntl plugin]
    ├── tsconfig.json            [@/* alias, ES2017]
    ├── messages/
    │   ├── en.json              [280 lines — English master]
    │   ├── fr.json              [280 lines — French]
    │   └── es.json              [280 lines — Spanish]
    └── src/
        ├── app/
        │   ├── globals.css      [Tailwind v4 @theme + utilities]
        │   ├── layout.tsx       [Root layout (minimal)]
        │   ├── page.tsx         [Root → redirect /en]
        │   └── [locale]/
        │       ├── layout.tsx   [Locale layout: fonts, providers, nav, footer]
        │       ├── page.tsx     [Homepage: 10 sections + FAQ schema]
        │       ├── services/page.tsx
        │       ├── about/page.tsx
        │       ├── contact/page.tsx
        │       └── case-studies/page.tsx
        ├── components/
        │   ├── Navbar.tsx       [Sticky, scroll blur, mobile menu]
        │   ├── Footer.tsx       [3-column, social icons]
        │   ├── LanguageSwitcher.tsx [EN|FR|ES pill toggle]
        │   ├── ParticleBackground.tsx
        │   ├── pages/
        │   │   ├── ServicesPageClient.tsx
        │   │   ├── AboutPageClient.tsx
        │   │   ├── ContactPageClient.tsx
        │   │   └── CaseStudiesPageClient.tsx
        │   ├── sections/
        │   │   ├── Hero.tsx, ProblemSection.tsx, Services.tsx
        │   │   ├── WhyMe.tsx, HowItWorks.tsx, Stats.tsx
        │   │   ├── CaseStudiesPreview.tsx, Pricing.tsx
        │   │   ├── FAQ.tsx, FinalCTA.tsx
        │   └── ui/
        │       ├── SpotlightCard.tsx    [Mouse-tracked radial gradient]
        │       ├── AnimatedGradientText.tsx
        │       ├── AuroraBackground.tsx
        │       ├── BorderBeam.tsx
        │       ├── LightningArc.tsx
        │       └── Text3D.tsx
        ├── i18n/
        │   ├── routing.ts      [locales: ["en","fr","es"], default "en"]
        │   ├── request.ts      [Server-side message loading]
        │   └── navigation.ts   [Locale-aware Link, redirect, useRouter, usePathname]
        └── middleware.ts       [next-intl locale detection]
```

### Design System (globals.css @theme)

```css
--color-background: #060810;
--color-surface: #0C1019;
--color-surface-2: #131A24;
--color-surface-3: #1B2332;
--color-text-primary: #E8ECF4;
--color-text-secondary: #7A829B;
--color-text-muted: #454D68;
--color-violet: #6C3FD1;
--color-violet-light: #8B6CE0;
--color-indigo: #7B7DC8;
--color-teal: #5EBFAB;
--color-mint: #82D4C3;
--color-danger: #E5484D;
--font-heading: var(--font-sora);
--font-body: var(--font-dm-sans);
```

### CSS Utilities

- `.gradient-text` — clip text to violet→indigo→teal gradient
- `.shimmer-text` — animated gradient (8s loop)
- `.glass-card` — frosted glass (opacity 0.5 + blur)
- `.gradient-border` — ::before pseudo with gradient mask
- `.orb-violet/teal/indigo` — blurred radial gradient circles
- `.grid-bg` — subtle grid pattern (80px spacing)
- `.aurora` — 3 drift animations, screen blend mode

### i18n Usage

```tsx
// Client components
const t = useTranslations("namespace");
t("key"); // simple string
t.raw("key"); // array/object

// Server components
const t = await getTranslations({ locale, namespace });
```

Translation namespaces: nav, hero, problem, services, whyMe, howItWorks, stats, caseStudies, pricing, faq, finalCta, footer, servicesPage, aboutPage, contactPage, caseStudiesPage

### Git

Branch: `master` | 4 commits (init → design system → i18n → components)

---

## RIG / EMPATHIK

### Full Directory Tree

```
RIG/
├── EMPATHIK_DESIGN.md           [42 KB — Design doc, French, READ FIRST]
├── empathik/                    [Git repo, 510+ commits, v0.5.0]
│   ├── app/
│   │   ├── __main__.py, __version__.py (0.5.0), main.py (CLI)
│   │   ├── pipeline.py, dual_pipeline.py
│   │   ├── tracking/           [face, body, hand, iris trackers + one_euro_filter]
│   │   ├── video/              [ingest, dual_loader, sync]
│   │   ├── flame/              [model, fitter, landmarks]
│   │   ├── refinement/         [openface.py — 18 AUs, gaze]
│   │   ├── calibration/        [session, camera geometry]
│   │   ├── rig/                [rig_map, rig_scanner, rig_classifier, region_detector, mapped_applicator]
│   │   ├── style/              [style_config (52 params), style_processor, keyframe_reducer, saccade_generator, uncanny_checker, presets]
│   │   ├── correction/         [self_correct, comparator (SSIM + perception)]
│   │   ├── gesture/            [micro_gesture — synergology detection]
│   │   ├── bridge/             [maya_bridge — TCP socket client]
│   │   ├── export/             [json_export — v4.0 format]
│   │   └── ui/                 [main_window — PySide6 app]
│   ├── maya_plugin/
│   │   ├── empathik_plugin.py  [Plugin entry, commandPort]
│   │   ├── empathik.mod        [Maya module definition]
│   │   ├── rig_scanner.py      [6-layer controller discovery]
│   │   ├── probe_engine.py     [Probe & learn (blackbox)]
│   │   ├── data_receiver.py    [TCP socket receiver]
│   │   ├── rig_applicator.py, apply_to_mrig.py, mapped_applicator.py
│   │   ├── layer_manager.py    [Animation layer creation]
│   │   ├── ui_panel.py         [PySide2 dockable panel]
│   │   ├── viewport_capture.py [Render for self-correction]
│   │   └── shelf_button.py     [Maya shelf integration]
│   ├── tests/                   [45 files, 210+ tests, ~3200 lines]
│   ├── models/                  [MediaPipe .task files ~41 MB]
│   ├── pyproject.toml, requirements.txt, README.md, EMPATHIK.bat
│   └── .git/
├── docs/plans/                  [5 phase plans]
├── test/                        [Manual test artifacts: .mp4, .json, analysis scripts]
│   └── feedback/                [.mov, .png, 230+ JPG keyframes]
└── research/                    [8 markdown files]
    ├── RESEARCH_SUMMARY.md
    ├── facial_mocap_tools.md, maya_rig_architecture.md
    ├── maya_rig_discovery_and_interaction.md
    ├── intelligent_rig_understanding_system.md
    ├── multiview_tracking_ai.md
    ├── uncanny_valley_analysis.md
    └── synergology_and_ekman.md
```

### Style Presets

| Preset | Slider | Target |
|--------|--------|--------|
| pixar | 0.25 | Exaggerated, smooth, bright eyes |
| arcane | 0.40 | Painterly, strong poses, selective detail |
| realistic | 0.95 | Subtle, high-frequency micro-expressions |
| anime | 0.08 | Maximum exaggeration, minimal keyframes |

### Rig Scanner: 6-Layer Discovery

1. Controller Tags (maya nodeType = "controller")
2. Selection Sets (named sets containing controls)
3. Character Sets (maya characterSets)
4. Name Pattern Regex (ctrl_, _CTRL, _ctl, etc.)
5. NURBS Curve Analysis (shape detection)
6. Graph Tracing (upstream connections from deformers)

### Dependencies (requirements.txt)

mediapipe, torch, torchvision, opencv-python, numpy, scipy, PySide6, pyopenface (optional), scikit-image

---

## NANO

### Full Directory Tree

```
NANO/
├── scrips/
│   ├── generate_kie.py          [6.2 KB — Primary image gen CLI]
│   └── get_kie_image.py         [Alternative retrieval]
├── prompts/                     [100 JSON prompt files]
│   ├── slide_1.json ... slide_8.json          [8 presentation backgrounds]
│   ├── mrig_01_*.json ... mrig_10_*.json      [10 model sheet prompts]
│   ├── design_01_*.json ... design_10_*.json  [10 archetype designs]
│   ├── design_01_pixar_sculpt.json ... design_10_moebius.json [10 style designs]
│   ├── explore_01_*.json ... explore_20_*.json [20 character explorations]
│   ├── model_sheet_turnaround.json, model_sheet_expressions.json
│   └── logos/
│       └── wslo_logo_01.json ... wslo_logo_40.json [40 logo prompts]
├── images/
│   ├── design_exploration/
│   │   ├── 1/ [15 images — Round 1]
│   │   ├── 2/ [11 images — Round 2]
│   │   └── 3/ [15 images — Round 3]
│   ├── LOGO_WSLO.lab/
│   │   ├── 1/ [10] | 2/ [11] | 3/ [13] | 4/ [6]
│   ├── mrig_model_sheet/        [10 images]
│   ├── model_sheet/             [empty]
│   └── pres_melies/             [8 bg + 8 slides]
├── assemble_html.py             [27 KB — Presentation assembler]
├── build_slides.py              [9.0 KB — Slide image generator (PIL)]
├── generate_backgrounds.py      [8.2 KB — Background gen (concurrent)]
├── extract.py                   [588 B — DOCX text extractor]
├── generate_explore_batch.sh    [Batch 1: designs 1-10]
├── generate_explore_batch2.sh   [Batch 2: designs 11-20]
├── skills/SKILL.md              [9.8 KB — Skill definition]
├── gemini.md                    [Project organizer guide]
├── master_prompt_reference.md   [8.9 KB — JSON schema guide]
├── font_bold_b64.txt, font_regular_b64.txt, font_thin_b64.txt [CeraPro base64]
├── logo_b64.txt                 [Melies logo base64]
└── res_melies.txt, res_melies2.txt [Presentation briefs]
```

### Kie.ai API Integration

```
Endpoint: https://api.kie.ai/api/v1/jobs/createTask
Model: nano-banana-2
Auth: Bearer {KIE_AI_API_KEY}
Polling: https://api.kie.ai/api/v1/jobs/recordInfo (60 attempts, 4s interval)
```

### mRig Model Sheet (10 images)

1. Turnaround thin (6 heads, ectomorph) — 376 KB
2. Turnaround medium (balanced) — 389 KB
3. Turnaround chubby (endomorph) — 474 KB
4. Body comparison (3 types side-by-side) — 399 KB
5. Face small nose — 567 KB
6. Face large nose — 493 KB
7. Face medium — 499 KB
8. Expression sheets — 111 KB
9. Hand reference — 342 KB
10. Extreme poses — 360 KB

### Design Exploration Styles

Archetype-based: Quiet Engineer, Street Runner, Brooding Artist, Tinkerer Nerd, Gentle Giant + 5 more
Style-based: Pixar Sculpt, SpiderVerse, Arcane Painterly, Anime Celshade, Ligne Claire, Ukiyoe, Art Deco, Stopmotion, Lowpoly, Moebius
Character-based (20): Daydreamer, Night Owl, Campus Rebel, Bookworm, Skater, Old Soul, Drifter, Musician, Athlete, Philosopher, Mechanic, Strategist, Farmboy, Coder, Boxer, Transfer, Graffiti, Medic, DJ, Watchmaker

---

## MAIN_ALL

### Full Directory Tree

```
MAIN_ALL/
├── CHARTE_GRAPHIQUE_SITE_MELIES.md  [8 KB — Full visual design system]
├── BEN_SPEAKING_STYLE_GUIDE.md      [8 KB — Ben's voice & teaching style]
├── BOOKS/                           [17 MB — Body language & acting]
│   ├── Ce que votre corps revele vraiment - Claudine Biland.pdf
│   ├── La formation de l'acteur - Constantin Stanislavski.pdf
│   ├── Le.Grand.Livre.De.La.Synergologie.2021.Philippe.Turchet.pdf
│   ├── The Dictionary of Body Language - Joe Navarro.pdf
│   └── Truth and Lies - Mark Bowden.pdf
├── CHARTE SITE INTERNET MELIES/
│   └── _CHARTE SITE INTERNET/
│       ├── _BACKGROUND_PAGES/       [7 HTML bokeh backgrounds, 1 per section]
│       ├── _COLORS/                 [Color palette .xlsx + reference JPEG]
│       ├── _ETOILES/                [16 star PNGs: "Poids" filled + "Rayee" striped]
│       ├── _FONT/CERAPRO/          [CeraPro: 6 weights × 2 styles, .ttf/.eot/.woff/.woff2]
│       └── _LOGO MELIES 24/        [25+ logo variants .ai/.pdf/.png, social versions]
├── Documents_project_general/       [516 KB]
│   ├── 01 Analyse Structurelle et Pédagogique des Modules INA.docx
│   ├── 02 Trame générique d'un module de formation.pdf
│   ├── Document de synthèse – Projet e-learning avec l'école Georges Méliès.pdf
│   └── extraction des diverses ia utilisé/
│       ├── extraction_de_chatgpt/claude/gemini.docx
│       ├── résumé.docx, résumé_pour_slides.docx
│       └── fonctionnement_AI_BOX_workflow_e-form.html
└── présentation_melies_pour_frank/  [possibly symlink]
```

### CeraPro Font Weights

| Weight | Style | Formats |
|--------|-------|---------|
| Thin (100) | Normal, Italic | .ttf, .eot, .woff, .woff2 |
| Light (300) | Normal, Italic | .ttf, .eot, .woff, .woff2 |
| Regular (400) | Normal, Italic | .ttf, .eot, .woff, .woff2 |
| Medium (500) | Normal, Italic | .ttf, .eot, .woff, .woff2 |
| Bold (700) | Normal, Italic | .ttf, .eot, .woff, .woff2 |
| Black (900) | Normal, Italic | .ttf, .eot, .woff, .woff2 |

### 7 Section Color Palettes (from charte)

| Section | Primary | Secondary | Notes |
|---------|---------|-----------|-------|
| General | #4A2971 (Violet) | — | Signature color |
| Home | Indigo/Rose/Violet | — | Gradient |
| Cinema | #055C79 | — | Dark blue |
| Image Animee | #0793AD | — | Cyan |
| Master | #4E55A2 | — | Indigo |
| Prep Arts | #9D2E88 | — | Magenta |
| Virtual Prod | #00A4E2 | — | Electric blue |

### Ben's Speaking Style (key points)

- French-influenced English, natural imperfections preserved
- Teaching: Simple concept → Physical demo → Real-world → Movie examples → Practice
- Signature phrases: "stuff like that", "basically", "the thing is", "obviously"
- Humor: Dark/dry, irreverent, never mean-spirited
- Natural patterns: "everyone have" (not "has"), "one of the responsible of that"

---

## MASTERCLASS_V02

### Content Inventory (118+ GB)

```
MASTERCLASS_V02/
├── HowToBeImperfect.pptx              [994 MB — Main masterclass]
├── EXPORT_part_of_masterclass/         [823 MB — 10 video segments]
│   ├── conscious_obsvervation.mov
│   ├── dont_fuck_with_me_fellas.mov
│   ├── heal_the_world.mov
│   ├── micro_expressions.mov
│   ├── pets_spoon_in_your_neck.mov
│   ├── sing_jello_dancing_around.mov
│   ├── the_idontknowtest.mov
│   ├── timing_thinking_process.mov
│   ├── with_thinking_pro_01.mov
│   └── with_thinking_pro_03.mov
├── LIVE_MELIES/                        [114 GB — Festival 2025]
│   ├── EXPORT/                        [2 master exports]
│   └── wetransfer_conference-festival-melies_2026-01-22_1311/
│       └── _BenWeislo/               [5 camera angles + .drp]
├── TEST/                              [1.8 GB — Research material]
│   ├── Jack Nicholson analysis (9 video clips)
│   ├── Animal behavior studies (cats, dogs, birds)
│   ├── Concept images (uncanny valley, Mehrabian, synergology)
│   └── Sorted reference videos
├── img_english/                       [80 MB — 11 infographic PNGs + 1 PDF]
├── files_random/                      [30 MB — Design files (.psd)]
├── new/                               [21 MB — Recent research images]
└── synergology_micro-gestures_research.md [52 KB — Comprehensive research]
```

### Key Research Topics

- Synergology (Philippe Turchet): 8 body segments, hemispheric laterality, 4 gesture types, 1500+ classified signs
- Paul Ekman: FACS, 44 AUs, 7 universal emotions, micro-expressions
- Mehrabian 7-38-55 Rule: 7% words, 38% vocal tone, 55% body language
- Uncanny Valley: Research-backed analysis from E-MELIES courses
- Acting Theory: Stanislavski, method acting, physical demonstration

---

## SKILL_MASTER

### Local Skills (4)

| Skill | Path | Purpose |
|-------|------|---------|
| creating-skills | `.agent/skills/creating-skills/` | Skills 2.0 format guide |
| executing-continuously | `.agent/skills/executing-continuously/` | High-autonomy mode |
| processing-video-captions | `.agent/skills/processing-video-captions/` | Video post-prod (Auphonic + subtitles) |
| ui-ux-pro-max | `.agent/skills/ui-ux-pro-max/` | Design intelligence (67 styles, 96 palettes, 57 fonts, 99 UX rules, 26 CSVs, 13 stacks) |

### Anthropic Reference Skills (16)

algorithmic-art, brand-guidelines, canvas-design, doc-coauthoring, docx, frontend-design, internal-comms, mcp-builder, pdf, pptx, skill-creator, slack-gif-creator, theme-factory, webapp-testing, web-artifacts-builder, xlsx

### ui-ux-pro-max Data Files (26 CSVs)

Root: charts, colors, icons, landing, products, react-performance, styles, typography, ui-reasoning, ux-guidelines, web-interface
Stacks: astro, flutter, html-tailwind, jetpack-compose, nextjs, nuxtjs, nuxt-ui, react, react-native, shadcn, svelte, swiftui, vue

---

## présentation_melies_pour_frank

Single self-contained HTML file (5.5 MB, 382 lines):
`D:\WORK\présentation_melies_pour_frank\presentation_melies.html`

Generated by NANO's `assemble_html.py` pipeline. Contains:
- Base64-embedded CeraPro fonts
- Base64-embedded backgrounds and Melies logo
- 8+ slides: Title → Ben's profile → Vision → 10-module curriculum → Team → Infrastructure → Tradition & Innovation → Next Steps (Annecy Festival 2026)
- Melies dark theme (#1a202c, #4a2971, #e93f7f, #facc15)
- Interactive: scroll-snap, keyboard nav, hover effects, fade-in animations
