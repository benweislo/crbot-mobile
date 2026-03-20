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
