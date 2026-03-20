"""
HtmlGenerator — converts structured CR text into a branded HTML page.
Uses configurable theme dict for all colors.
"""

import re
from pathlib import Path

from app.pipeline.html_template import build_html


def _parse_cr(text: str) -> dict:
    """Parse a structured CR text string into sections."""
    data = {
        "date": "",
        "duree": "",
        "fichier": "",
        "themes": [],
        "actions": [],
        "conclusion": [],
        "details": "",
    }
    current_section = None

    for line in text.split("\n"):
        stripped = line.strip()

        # Skip delimiters
        if stripped.startswith("====") or stripped.startswith("----"):
            continue
        if stripped in ("COMPTE RENDU DE RÉUNION", "FIN DU COMPTE RENDU"):
            continue

        # Detect section headers
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

        # Parse metadata (before any section)
        if current_section is None:
            if stripped.startswith("Date"):
                data["date"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("Durée"):
                data["duree"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("Fichier"):
                data["fichier"] = stripped.split(":", 1)[1].strip()
            continue

        # Parse content by section
        if current_section == "themes":
            m = re.match(r"^[•\-]\s*(.*)", stripped)
            if m:
                data["themes"].append(m.group(1))
        elif current_section == "actions":
            m = re.match(r"^\d+\.\s*(.*)", stripped)
            if m:
                data["actions"].append(m.group(1))
            elif stripped and not stripped.startswith("("):
                data["actions"].append(stripped)  # Person header line
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
    """Generates branded HTML pages from CR text using a configurable theme."""

    def __init__(
        self,
        theme: dict,
        logo_b64: str = "",
        font_regular_b64: str = "",
        font_bold_b64: str = "",
    ):
        self._theme = theme
        self._logo_b64 = logo_b64
        self._font_regular_b64 = font_regular_b64
        self._font_bold_b64 = font_bold_b64

    def generate(self, cr_text: str, output_path: Path) -> None:
        """Parse CR text and write a self-contained HTML file."""
        data = _parse_cr(cr_text)

        # Fallback: if nothing was parsed, dump the raw text into details
        if not data["themes"] and not data["actions"] and not data["details"].strip():
            data["details"] = cr_text

        html = build_html(
            data,
            self._theme,
            self._logo_b64,
            self._font_regular_b64,
            self._font_bold_b64,
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")
