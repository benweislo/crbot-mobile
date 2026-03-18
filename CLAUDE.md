# D:\WORK — Ben Weislo's Workspace

## First Step

When starting any task from this directory, invoke the `workspace-context` skill to load full project awareness. This gives you comprehensive knowledge of all 11 project folders, their stacks, key files, and relationships.

## Quick Reference

| Folder | Alias | What | Run |
|--------|-------|------|-----|
| AI_BOX | aibox | AI course gen ("GO {Name}") | "GO Kevin_Bertelli" |
| E-MELIES | emelies | E-learning platform | `cd E-MELIES/website && npm run dev` |
| WSLO.lab | wslo | AI for 3D animation schools | `cd WSLO.lab/website && npm run dev` |
| RIG | empathik | AI motion capture Maya | See EMPATHIK_DESIGN.md |
| NANO | nano | Image gen (Kie.ai) + presentations | `python scrips/generate_kie.py` |
| MAIN_ALL | main_all | Brand assets (fonts, logos, colors) | Static |
| MASTERCLASS_V02 | masterclass | Raw content archive (118 GB) | Archive |
| SKILL_MASTER | skill_master | Skills repository (20 skills) | Reference |
| MEETINGS | meetings, reunion, cr | Meeting transcription & CR automation | See `.skills/meeting-transcriber/` |
| AI_TUNE | ai_tune, trading | Self-improving trading bot | `cd AI_TUNE && .venv/Scripts/python -m orchestrator.daemon` |
| présentation_melies_pour_frank | frank | HTML pitch presentation | Open HTML |

## Meeting CR Automation

When the user asks for a "compte rendu", "CR de réunion", or anything related to meeting transcription:
1. Go to `D:\WORK\MEETINGS`
2. Read the skill at `MEETINGS/.skills/meeting-transcriber/SKILL.md`
3. Follow the workflow at `MEETINGS/.agent/workflows/run.md`
4. Pipeline: Audio (.mp3) → Gladia API (transcription + diarization) → `output/` → OpenAI GPT-4o (summarization) → `CR/` → `generate_html.py` → `html/` (branded HTML)
5. Supports grouping same-day audio files as one meeting

## Key Rules

- **Language:** French for communication, English for code/docs
- **Exclude:** Never scan or include the NUTRIA folder
- **API keys:** Centralized at `C:\Users\Ben\ENV\`
- **GitHub:** benweislo
- **Detailed reference:** `D:\WORK\WORKSPACE_REFERENCE.md`
- **Each project may have its own CLAUDE.md** — read it before working on that project
- **Knowledge sync:** Whenever you update a skill/CLAUDE.md in a subfolder or discover new workspace info, **always propagate changes** to the root-level sources: this CLAUDE.md, the `workspace-context` skill, MEMORY.md, and WORKSPACE_REFERENCE.md. Root knowledge must never be stale.

## Project CLAUDE.md Files

- `AI_BOX/CLAUDE.md` — Full "GO {Expert}" pipeline spec (14 KB)
- `E-MELIES/CLAUDE.md` — Platform overview & content pipeline
- `E-MELIES/contenu/CLAUDE.md` — Video folder & Vimeo sync instructions
- `AI_TUNE/CLAUDE.md` — Trading bot architecture, autoresearch loop, Smart Vault rules
