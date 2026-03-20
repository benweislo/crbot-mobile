"""
Full HTML template for meeting CR pages.
Ported from MEETINGS/.skills/meeting-transcriber/scripts/generate_html.py
with all hardcoded colors replaced by configurable theme dict values.
"""

import re


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert '#RRGGBB' to (r, g, b) tuple."""
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[1:4][:2], 16), int(h[4:6], 16)


def _hex_to_rgb_str(hex_color: str) -> str:
    """Convert '#RRGGBB' to 'r,g,b' string for use in rgba()."""
    r, g, b = _hex_to_rgb(hex_color)
    return f"{r},{g},{b}"


def _details_to_html(details_text: str, theme: dict) -> str:
    """Convert the 'TOUT EN DÉTAILS' markdown-like text to HTML.

    Ported from generate_html.py lines 118-174.
    Handles: ## headings, bullet points, bold markdown, speaker tags,
    list open/close tracking.
    """
    html_parts: list[str] = []
    lines = details_text.strip().split("\n")
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Section headers (## 1. Title)
        h2_match = re.match(r"^##\s+\d+\.\s*(.*)", stripped)
        if h2_match:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            title = h2_match.group(1)
            # Extract speaker info if present
            speaker_match = re.match(r"(.*?)\s*—\s*(Speaker\s+\d+.*)", title)
            if speaker_match:
                html_parts.append(
                    f'<h3 class="detail-title">{speaker_match.group(1)}'
                    f'<span class="speaker-tag">{speaker_match.group(2)}</span></h3>'
                )
            else:
                html_parts.append(f'<h3 class="detail-title">{title}</h3>')
            continue

        # Bullet points
        bullet = re.match(r"^[-•]\s+(.*)", stripped)
        if bullet:
            if not in_list:
                html_parts.append('<ul class="detail-list">')
                in_list = True
            text = bullet.group(1)
            # Bold text
            text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
            html_parts.append(f"  <li>{text}</li>")
            continue

        # Empty line
        if not stripped:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            continue

        # Regular paragraph
        if in_list:
            html_parts.append("</ul>")
            in_list = False
        text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", stripped)
        html_parts.append(f'<p class="detail-paragraph">{text}</p>')

    if in_list:
        html_parts.append("</ul>")

    return "\n".join(html_parts)


def build_html(
    data: dict,
    theme: dict,
    logo_b64: str = "",
    font_regular_b64: str = "",
    font_bold_b64: str = "",
) -> str:
    """Build the full self-contained HTML page from parsed CR data and theme.

    Color mapping from original Melies template:
      #050505           -> theme['background']
      #110a1a           -> theme['surface']
      #e2e8f0           -> theme['text_primary']
      #6e3ea8           -> theme['primary']
      #E93F7F           -> theme['secondary']
      #cbd5e0, #a0aec0  -> theme['text_secondary']
      #4a5568           -> theme['text_secondary']
      rgba(74,41,113,..) -> derived from theme['primary']
      rgba(233,63,127,..)-> derived from theme['secondary']
      rgba(91,84,224,..) -> derived from theme['secondary']
      CeraPro font      -> AppFont (conditional on font_b64 presence)
    """
    # Derive RGB strings for rgba() usage
    primary_rgb = _hex_to_rgb_str(theme["primary"])
    secondary_rgb = _hex_to_rgb_str(theme["secondary"])
    tertiary_rgb = _hex_to_rgb_str(theme.get("tertiary", theme["secondary"]))

    # Font family: use AppFont if base64 fonts provided, else system fonts
    if font_regular_b64:
        font_family = "AppFont"
        font_face_css = f"""
        @font-face {{
            font-family: 'AppFont';
            src: url('data:font/woff2;base64,{font_regular_b64}') format('woff2');
            font-weight: 400;
            font-style: normal;
        }}
        @font-face {{
            font-family: 'AppFont';
            src: url('data:font/woff2;base64,{font_bold_b64}') format('woff2');
            font-weight: 700;
            font-style: normal;
        }}"""
    else:
        font_family = "system-ui"
        font_face_css = ""

    # Build themes list HTML
    themes_html = "\n".join(
        f'        <li><span class="theme-dot"></span>{t}</li>' for t in data["themes"]
    )

    # Build actions list HTML
    actions_html = "\n".join(
        f'        <li><span class="action-num">{i + 1}</span>{a}</li>'
        for i, a in enumerate(data["actions"])
    )

    # Build conclusion HTML
    conclusion_html = "\n".join(
        f'        <p class="conclusion-item">\u2192 {c}</p>' for c in data["conclusion"]
    )

    # Build details HTML
    details_html = _details_to_html(data["details"], theme) if data["details"].strip() else ""

    # Date display
    date_display = data["date"] if data["date"] else "Date inconnue"

    # Logo HTML (only if provided)
    logo_html = (
        f'<img class="logo" src="data:image/png;base64,{logo_b64}" alt="Logo">'
        if logo_b64
        else ""
    )

    # Theme color shortcuts
    bg = theme["background"]
    surface = theme["surface"]
    text1 = theme["text_primary"]
    text2 = theme["text_secondary"]
    primary = theme["primary"]
    secondary = theme["secondary"]
    tertiary = theme.get("tertiary", theme["secondary"])

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CR R\u00e9union \u2014 {date_display}</title>
    <style>{font_face_css}

        *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: '{font_family}', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-weight: 400;
            background: linear-gradient(to bottom, {bg} 0%, {surface} 100%);
            color: {text1};
            min-height: 100vh;
            line-height: 1.7;
            overflow-x: hidden;
        }}

        /* Bokeh lights */
        .bokeh {{
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }}
        .bokeh .orb {{
            position: absolute;
            border-radius: 50%;
            mix-blend-mode: screen;
            filter: blur(100px);
        }}
        .orb-1 {{
            width: 60vw; height: 60vw;
            top: -20%; left: -15%;
            background: radial-gradient(circle, rgba({primary_rgb},0.35) 0%, transparent 70%);
            animation: float1 20s ease-in-out infinite;
        }}
        .orb-2 {{
            width: 50vw; height: 50vw;
            bottom: -10%; right: -10%;
            background: radial-gradient(circle, rgba({secondary_rgb},0.25) 0%, transparent 70%);
            animation: float2 25s ease-in-out infinite;
        }}
        .orb-3 {{
            width: 35vw; height: 35vw;
            top: 40%; left: 50%;
            background: radial-gradient(circle, rgba({tertiary_rgb},0.20) 0%, transparent 70%);
            animation: float3 18s ease-in-out infinite;
        }}

        @keyframes float1 {{ 0%,100% {{ transform: translate(0,0); }} 50% {{ transform: translate(30px,-40px); }} }}
        @keyframes float2 {{ 0%,100% {{ transform: translate(0,0); }} 50% {{ transform: translate(-25px,35px); }} }}
        @keyframes float3 {{ 0%,100% {{ transform: translate(0,0); }} 50% {{ transform: translate(-20px,-30px); }} }}

        /* Film grain */
        .grain {{
            position: fixed;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            pointer-events: none;
            z-index: 1;
            opacity: 0.12;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='1.7' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
            animation: grain 0.8s steps(1) infinite;
        }}
        @keyframes grain {{ 0%,100% {{ transform: translate(0,0); }} 10% {{ transform: translate(-5%,-10%); }} 30% {{ transform: translate(3%,2%); }} 50% {{ transform: translate(-2%,5%); }} 70% {{ transform: translate(5%,-3%); }} 90% {{ transform: translate(-3%,8%); }} }}

        /* Vignette */
        .vignette {{
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            pointer-events: none;
            z-index: 1;
            background: radial-gradient(circle at 50% 50%, rgba(0,0,0,0) 35%, rgba(0,0,0,0.45) 100%);
        }}

        /* Content */
        .container {{
            position: relative;
            z-index: 2;
            max-width: 820px;
            margin: 0 auto;
            padding: 60px 32px 80px;
        }}

        /* Header */
        .header {{
            text-align: center;
            margin-bottom: 56px;
        }}
        .logo {{
            width: 64px;
            height: 64px;
            margin-bottom: 24px;
            opacity: 0.85;
        }}
        .header h1 {{
            font-weight: 700;
            font-size: 2rem;
            background: linear-gradient(135deg, {primary}, {secondary});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 16px;
            letter-spacing: -0.02em;
        }}
        .meta {{
            display: flex;
            justify-content: center;
            gap: 28px;
            flex-wrap: wrap;
        }}
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: {text2};
            font-size: 0.9rem;
        }}
        .meta-icon {{
            width: 18px;
            height: 18px;
            opacity: 0.7;
        }}

        /* Section cards */
        .section {{
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 36px 32px;
            margin-bottom: 28px;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            transition: border-color 0.3s ease;
        }}
        .section:hover {{
            border-color: rgba({primary_rgb},0.25);
        }}
        .section-label {{
            font-weight: 700;
            font-size: 0.75rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: {primary};
            margin-bottom: 20px;
        }}

        /* Themes */
        .themes-list {{
            list-style: none;
        }}
        .themes-list li {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 8px 0;
            font-size: 0.95rem;
            color: {text2};
            border-bottom: 1px solid rgba(255,255,255,0.04);
        }}
        .themes-list li:last-child {{ border-bottom: none; }}
        .theme-dot {{
            width: 8px;
            height: 8px;
            min-width: 8px;
            border-radius: 50%;
            background: linear-gradient(135deg, {primary}, {secondary});
            margin-top: 8px;
        }}

        /* Actions */
        .actions-list {{
            list-style: none;
            counter-reset: none;
        }}
        .actions-list li {{
            display: flex;
            align-items: flex-start;
            gap: 14px;
            padding: 10px 0;
            font-size: 0.95rem;
            color: {text2};
            border-bottom: 1px solid rgba(255,255,255,0.04);
        }}
        .actions-list li:last-child {{ border-bottom: none; }}
        .action-num {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 26px;
            height: 26px;
            min-width: 26px;
            border-radius: 8px;
            background: rgba({primary_rgb},0.25);
            color: {primary};
            font-weight: 700;
            font-size: 0.8rem;
            margin-top: 1px;
        }}

        /* Conclusion */
        .conclusion-item {{
            padding: 6px 0;
            font-size: 0.95rem;
            color: {text2};
            padding-left: 20px;
            border-left: 2px solid {tertiary};
            margin-bottom: 10px;
        }}

        /* Details */
        .detail-title {{
            font-weight: 700;
            font-size: 1.1rem;
            color: {text1};
            margin: 28px 0 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.08);
        }}
        .detail-title:first-child {{ margin-top: 0; }}
        .speaker-tag {{
            font-weight: 400;
            font-size: 0.8rem;
            color: {secondary};
            margin-left: 10px;
            opacity: 0.8;
        }}
        .detail-paragraph {{
            font-size: 0.93rem;
            color: {text2};
            margin-bottom: 10px;
            line-height: 1.75;
        }}
        .detail-list {{
            list-style: none;
            padding-left: 0;
            margin-bottom: 12px;
        }}
        .detail-list li {{
            position: relative;
            padding: 4px 0 4px 20px;
            font-size: 0.93rem;
            color: {text2};
            line-height: 1.7;
        }}
        .detail-list li::before {{
            content: '';
            position: absolute;
            left: 4px;
            top: 14px;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: rgba({primary_rgb},0.5);
        }}
        .detail-list li strong {{
            color: {text1};
        }}

        /* Footer */
        .footer {{
            text-align: center;
            margin-top: 48px;
            padding-top: 28px;
            border-top: 1px solid rgba(255,255,255,0.06);
            color: {text2};
            font-size: 0.8rem;
        }}

        /* Print */
        @media print {{
            body {{ background: #fff; color: #1a202c; }}
            .bokeh, .grain, .vignette {{ display: none; }}
            .section {{ border: 1px solid #e2e8f0; background: #fff; }}
            .header h1 {{ color: {primary}; -webkit-text-fill-color: {primary}; }}
            .theme-dot {{ background: {primary}; }}
            .action-num {{ background: #f0e6ff; color: {primary}; }}
            .conclusion-item {{ border-left-color: {secondary}; color: #4a5568; }}
        }}

        @media (max-width: 640px) {{
            .container {{ padding: 32px 18px 48px; }}
            .section {{ padding: 24px 20px; }}
            .header h1 {{ font-size: 1.5rem; }}
            .meta {{ gap: 16px; }}
        }}
    </style>
</head>
<body>
    <div class="bokeh">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
    </div>
    <div class="grain"></div>
    <div class="vignette"></div>

    <div class="container">
        <header class="header">
            {logo_html}
            <h1>Compte Rendu de R\u00e9union</h1>
            <div class="meta">
                <span class="meta-item">
                    <svg class="meta-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                    {date_display}
                </span>
                <span class="meta-item">
                    <svg class="meta-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                    {data["duree"]}
                </span>
            </div>
        </header>

        <section class="section">
            <div class="section-label">Th\u00e8mes abord\u00e9s</div>
            <ul class="themes-list">
{themes_html}
            </ul>
        </section>

        <section class="section">
            <div class="section-label">Actions / Prochaines \u00e9tapes</div>
            <ul class="actions-list">
{actions_html}
            </ul>
        </section>

        <section class="section">
            <div class="section-label">Conclusion</div>
{conclusion_html}
        </section>

        {"<section class='section'><div class='section-label'>Tout en d\u00e9tails</div>" + details_html + "</section>" if details_html else ""}

        <footer class="footer">
            G\u00e9n\u00e9r\u00e9 par Mon CR \u2014 wslo.lab
        </footer>
    </div>
</body>
</html>"""
