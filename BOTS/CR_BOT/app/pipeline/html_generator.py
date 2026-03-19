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
        # Each section heading is followed by content in the NEXT section
        sections = re.split(r"-{20,}", text)

        for i, section in enumerate(sections):
            header = section.strip().split("\n")[0].strip().upper() if section.strip() else ""

            # Try body from same section first, fall back to next section
            body_lines = section.strip().split("\n")[1:]
            body = "\n".join(body_lines).strip()
            if not body and i + 1 < len(sections):
                body = sections[i + 1].strip()

            if "TH\u00c8MES" in header or "THEMES" in header:
                data["themes"] = [
                    line.strip().lstrip("\u2022").lstrip("•").strip()
                    for line in body.split("\n")
                    if line.strip() and (line.strip().startswith("•") or line.strip().startswith("\u2022"))
                ]

            elif "ACTIONS" in header or "PROCHAINES" in header:
                data["actions"] = body

            elif "CONCLUSION" in header:
                data["conclusion"] = body.lstrip("→").lstrip("\u2192").strip()

            elif "TOUT EN" in header or "D\u00c9TAILS" in header or "DETAILS" in header:
                data["details"] = body

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
