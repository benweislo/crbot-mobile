# Installation Guide — New Laptop Setup

> **Usage:** Après avoir copié ce dossier sur le nouveau PC, ouvre un terminal dans ce dossier, lance Claude Code, et dis : **"install"**
> Claude lira ce fichier et exécutera tout.

> **IMPORTANT — Chemins dynamiques :** Ce script utilise `$WORKSPACE` (le dossier où se trouve ce fichier) et `$HOME` (le profil utilisateur). Aucun chemin n'est hardcodé — ça fonctionne quel que soit l'emplacement du dossier ou le nom d'utilisateur Windows.

---

## PRE-REQUIS MANUELS (à faire AVANT de lancer Claude)

Ces étapes nécessitent un navigateur et des téléchargements. Fais-les en premier :

### 1. Installer les outils de base

| Outil | Version | Lien |
|-------|---------|------|
| **Git** | >= 2.53 | https://git-scm.com/downloads/win |
| **Node.js** | >= 22.x (LTS) | https://nodejs.org/ |
| **Python** | >= 3.13.x | https://www.python.org/downloads/ (cocher "Add to PATH") |
| **Claude Code** | latest | `npm install -g @anthropic-ai/claude-code` |

### 2. Se connecter à Claude Code

```bash
claude login
```
Connecte-toi avec ton compte Anthropic (plan Max).

### 3. Créer le dossier des clés API

```bash
mkdir -p "$HOME/ENV"
```

Crée le fichier `$HOME/ENV/.env` (ex: `C:\Users\TonNom\ENV\.env`) avec tes clés :

```env
VIMEO_ACCESS_TOKEN=ton_token_vimeo
OPENAI_API_KEY=sk-proj-xxx
GEMINI_API_KEY=AIzaSyxxx
PINECONE_API_KEY=pcsk_xxx
YOUTUBE_API_KEY=AIzaSyxxx
KIE_AI_API_KEY=ton_token_kie
GLADIA_API_KEY=ton_token_gladia
```

---

## INSTALLATION AUTOMATIQUE (Claude exécute tout ci-dessous)

Quand l'utilisateur dit **"install"**, exécuter toutes les étapes suivantes dans l'ordre.

**Convention de chemins :**
- `$WORKSPACE` = le dossier où se trouve ce fichier `NEW_INSTALL.md` (là où Claude est lancé, le `pwd`)
- `$HOME` = le profil utilisateur Windows (ex: `C:\Users\Ben` ou `C:\Users\TonNom`)
- Détecter `$WORKSPACE` avec `pwd` au début de l'installation
- Détecter `$HOME` avec `echo $HOME` ou `echo $USERPROFILE`

### ÉTAPE 1 — Détecter les chemins et vérifier les prérequis

```bash
# Détecter le workspace (là où Claude est lancé)
WORKSPACE=$(pwd)
echo "WORKSPACE: $WORKSPACE"
echo "HOME: $HOME"

# Vérifier les outils
node -v    # doit être >= 22.x
npm -v     # doit être >= 11.x
python --version  # doit être >= 3.13
pip --version
git --version
claude --version
```

Si un outil manque, **STOP** et demander à l'utilisateur de l'installer manuellement (voir section PRE-REQUIS ci-dessus).

Vérifier que `$HOME/ENV/.env` existe et contient les clés API. Sinon, **STOP** et demander à l'utilisateur de le créer.

### ÉTAPE 2 — Configurer Claude Code (settings globaux)

Créer le dossier si nécessaire, puis écrire `$HOME/.claude/settings.json` :

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "permissions": {
    "allow": [
      "Bash(*)"
    ],
    "defaultMode": "bypassPermissions"
  },
  "enabledPlugins": {
    "superpowers@superpowers-marketplace": true,
    "superpowers-chrome@superpowers-marketplace": true,
    "frontend-design@claude-plugins-official": true,
    "skill-creator@claude-plugins-official": true
  },
  "skipDangerousModePermissionPrompt": true,
  "effortLevel": "high"
}
```

### ÉTAPE 3 — Configurer les permissions locales du projet

Vérifier que `$WORKSPACE/.claude/settings.local.json` existe déjà (il est copié avec le dossier). Si absent, le recréer :

```json
{
  "permissions": {
    "allow": [
      "WebSearch",
      "WebFetch(domain:www.pinterest.com)",
      "WebFetch(domain:nelsonhurst.com)",
      "WebFetch(domain:sketchfab.com)",
      "WebFetch(domain:www.animstarter.com)",
      "Bash(python:*)",
      "Bash(curl:*)",
      "Bash(ping:*)",
      "Bash(nslookup:*)",
      "Bash(netsh advfirewall:*)",
      "Bash(tracert:*)",
      "Bash(powershell:*)",
      "Bash(ipconfig:*)",
      "Bash(tasklist:*)",
      "Bash(tailscale status:)",
      "WebFetch(domain:tempfile.aiquickdraw.com)",
      "WebFetch(domain:docs.kie.ai)",
      "Bash(code:*)",
      "Bash(du:*)",
      "WebFetch(domain:ramonarango.gumroad.com)",
      "WebFetch(domain:animatorsresourcekit.blog)",
      "WebFetch(domain:80.lv)",
      "WebFetch(domain:www.artstation.com)",
      "WebFetch(domain:smartscience.blog)",
      "WebFetch(domain:www.whitneyupdate.com)",
      "WebFetch(domain:www.creativebloq.com)",
      "WebFetch(domain:blog.cg-wire.com)",
      "WebFetch(domain:cypaint.com)",
      "WebFetch(domain:characterdesignreferences.com)",
      "WebFetch(domain:cara.app)",
      "WebFetch(domain:3d-model.org)",
      "Bash(bash:*)",
      "Bash(git config:*)",
      "Bash(ls:*)",
      "Bash(pip install:*)"
    ]
  }
}
```

### ÉTAPE 4 — Installer les packages Python (global)

Installer **tous** les packages en une seule commande pip :

```bash
pip install \
  requests==2.32.5 \
  python-dotenv==1.2.1 \
  openai==2.24.0 \
  Pillow==12.1.1 \
  numpy==2.3.5 \
  scipy==1.17.1 \
  scikit-image==0.26.0 \
  matplotlib==3.10.8 \
  mediapipe==0.10.32 \
  opencv-python==4.13.0.92 \
  opencv-contrib-python==4.13.0.92 \
  torch==2.10.0 \
  onnxruntime==1.24.3 \
  pytest==9.0.2 \
  tqdm==4.67.3 \
  rich==14.3.2 \
  pydantic==2.12.5 \
  pydantic-settings==2.13.0 \
  python-docx==1.2.0 \
  pdfminer.six==20251230 \
  pdfplumber==0.11.9 \
  PyMuPDF==1.27.1 \
  reportlab==4.4.10 \
  weasyprint==68.1 \
  imageio==2.37.2 \
  imageio-ffmpeg==0.6.0 \
  yt-dlp==2026.3.3 \
  sounddevice==0.5.5 \
  openai-whisper==20250625 \
  tiktoken==0.12.0 \
  mcp==1.26.0 \
  fastmcp==2.14.5 \
  anthropic \
  notebooklm-mcp-cli==0.3.2 \
  PyYAML==6.0.3 \
  httpx==0.28.1 \
  websockets==16.0 \
  typer==0.23.1 \
  colorama==0.4.6
```

> **Note:** PyTorch (`torch`) est un gros package (~2 GB). Si GPU NVIDIA disponible, installer la version CUDA à la place :
> ```bash
> pip install torch==2.10.0 --index-url https://download.pytorch.org/whl/cu126
> ```

### ÉTAPE 5 — Installer EMPATHIK en mode editable

```bash
pip install -e "$WORKSPACE/RIG/empathik[all]"
```

Cela installe le package `empathik` v0.5.0 avec toutes les dépendances optionnelles (PySide6, torch, pytest).

### ÉTAPE 6 — Installer les dépendances NPM des projets web

```bash
# E-MELIES (React + Vite)
cd "$WORKSPACE/E-MELIES/website" && npm install

# WSLO.lab (Next.js 16)
cd "$WORKSPACE/WSLO.lab/website" && npm install

# REMOTION (optionnel)
cd "$WORKSPACE/REMOTION" && npm install
```

### ÉTAPE 7 — Installer les plugins Claude Code

Les plugins sont enregistrés dans `settings.json` (étape 2). Au premier lancement de Claude Code, ils se téléchargent automatiquement. Mais pour forcer l'installation :

```bash
claude plugins install superpowers@superpowers-marketplace
claude plugins install superpowers-chrome@superpowers-marketplace
claude plugins install frontend-design@claude-plugins-official
claude plugins install skill-creator@claude-plugins-official
```

> **Note :** Si la commande `claude plugins install` n'existe pas dans ta version, les plugins se chargent automatiquement au premier lancement grâce au `settings.json`.

### ÉTAPE 8 — Vérifier que les skills sont en place

Les skills sont dans le dossier `$WORKSPACE/.claude/skills/` (copié avec le workspace). Vérifier :

```bash
ls "$WORKSPACE/.claude/skills/workspace-context/SKILL.md"
ls "$WORKSPACE/.claude/skills/extract-video-clips/SKILL.md"
ls "$WORKSPACE/.claude/skills/check-updates/SKILL.md"
```

Si un fichier manque, c'est que le dossier `.claude/` n'a pas été copié correctement. Recopier depuis l'ancien PC.

### ÉTAPE 9 — Configurer la mémoire Claude

La mémoire persistante de Claude est liée au **chemin du projet**. Sur l'ancien PC c'était `$HOME/.claude/projects/D--WORK/memory/`.

Sur le nouveau PC, Claude créera automatiquement un nouveau dossier mémoire basé sur le nouveau chemin du workspace. Il faut donc :

1. **Copier les fichiers mémoire** depuis l'ancien PC vers le nouveau chemin mémoire.
   Le chemin mémoire est dérivé du chemin workspace : les `/` et `\` deviennent `--`, les `:` deviennent `-`.
   Exemple : si le workspace est `E:\PROJECTS\WORK`, la mémoire sera dans `$HOME/.claude/projects/E--PROJECTS--WORK/memory/`

2. **Fichiers mémoire à copier :**
   - `MEMORY.md` (index principal)
   - `workspace-details.md`
   - `empathik-project.md`
   - `mrig-design-exploration.md`
   - `administration-billing.md`
   - `feedback_non_destructive.md`
   - `feedback_eye_ctrl_zero.md`
   - `feedback_offline_processing.md`

3. **Alternative :** Si pas de copie possible, la mémoire se reconstruira au fil des conversations.

### ÉTAPE 10 — Mettre à jour les chemins dans CLAUDE.md et le skill workspace-context

Les fichiers `CLAUDE.md` et le skill `workspace-context` contiennent des références à `D:\WORK`. Si le nouveau chemin est différent, faire un search-and-replace :

```bash
# Remplacer D:\WORK par le nouveau chemin dans les fichiers de config
# (seulement si le workspace n'est PAS à D:\WORK)
WORKSPACE=$(pwd)
if [ "$WORKSPACE" != "/d/WORK" ]; then
  # CLAUDE.md
  sed -i "s|D:\\\\WORK|${WORKSPACE}|g" "$WORKSPACE/CLAUDE.md"
  sed -i "s|D:/WORK|${WORKSPACE}|g" "$WORKSPACE/CLAUDE.md"

  # workspace-context skill
  sed -i "s|D:\\\\WORK|${WORKSPACE}|g" "$WORKSPACE/.claude/skills/workspace-context/SKILL.md"
  sed -i "s|D:/WORK|${WORKSPACE}|g" "$WORKSPACE/.claude/skills/workspace-context/SKILL.md"

  # WORKSPACE_REFERENCE.md
  sed -i "s|D:\\\\WORK|${WORKSPACE}|g" "$WORKSPACE/WORKSPACE_REFERENCE.md"
  sed -i "s|D:/WORK|${WORKSPACE}|g" "$WORKSPACE/WORKSPACE_REFERENCE.md"

  echo "Chemins mis à jour vers: $WORKSPACE"
fi
```

### ÉTAPE 11 — Vérification finale

Lancer ces tests pour confirmer que tout fonctionne :

```bash
# Python + packages critiques
python -c "import mediapipe; import cv2; import torch; import numpy; import openai; import requests; print('Python OK')"

# EMPATHIK
python -c "import empathik; print(f'EMPATHIK {empathik.__version__} OK')"

# Node.js + projets web
cd "$WORKSPACE/E-MELIES/website" && npx vite --version
cd "$WORKSPACE/WSLO.lab/website" && npx next --version

# Claude Code
claude --version

# Clés API
python -c "
from dotenv import load_dotenv
import os
load_dotenv(os.path.expanduser('~/ENV/.env'))
keys = ['OPENAI_API_KEY','VIMEO_ACCESS_TOKEN','KIE_AI_API_KEY','GLADIA_API_KEY']
for k in keys:
    status = 'OK' if os.getenv(k) else 'MISSING'
    print(f'{k}: {status}')
"
```

---

## RÉCAPITULATIF

| Catégorie | Éléments |
|-----------|----------|
| **Runtime** | Node.js 22.x, Python 3.13.x, Git 2.53+ |
| **CLI** | Claude Code (npm global), yt-dlp |
| **Python packages** | 50+ packages (torch, mediapipe, opencv, openai, whisper, etc.) |
| **NPM projects** | E-MELIES (React/Vite), WSLO.lab (Next.js), REMOTION |
| **Claude plugins** | superpowers, superpowers-chrome, frontend-design, skill-creator |
| **Claude skills** | workspace-context, extract-video-clips, check-updates |
| **Clés API** | Vimeo, OpenAI, Gemini, Pinecone, YouTube, Kie.ai, Gladia |
| **Config** | settings.json, settings.local.json, memory files |

## EN CAS DE PROBLÈME

- **PyTorch CUDA :** Si pas de GPU NVIDIA, `torch` s'installe en mode CPU (plus léger, ~200 MB au lieu de 2 GB)
- **PySide6 :** S'installe via `empathik[all]` — si ça échoue, `pip install PySide6>=6.5.0` séparément
- **weasyprint :** Nécessite GTK3 sur Windows — les wheels Windows récentes incluent les dépendances
- **node_modules :** Si `npm install` échoue, supprimer `node_modules` et `package-lock.json` puis réessayer
- **Mémoire Claude :** Le dossier mémoire est créé automatiquement au premier lancement de Claude dans le workspace
- **Chemin différent :** L'étape 10 met à jour automatiquement tous les chemins hardcodés si le workspace n'est pas à `D:\WORK`
