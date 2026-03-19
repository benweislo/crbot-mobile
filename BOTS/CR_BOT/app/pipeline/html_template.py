"""
HTML template for branded CR output.
Uses CSS custom properties for brand colors.
Contains two tabs: Résumé and Détaillé.
Self-contained: all fonts, logos, and styles inline.
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="{language}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Compte Rendu — {company_name}</title>
<style>
@font-face {{
    font-family: '{font_family}';
    src: url(data:font/woff2;base64,{font_regular_b64}) format('woff2');
    font-weight: 400;
}}
@font-face {{
    font-family: '{font_family}';
    src: url(data:font/woff2;base64,{font_bold_b64}) format('woff2');
    font-weight: 700;
}}

:root {{
    --primary: {primary_color};
    --secondary: {secondary_color};
    --bg: {background_color};
    --text: {text_color};
    --card-bg: rgba(255,255,255,0.04);
    --card-border: rgba(255,255,255,0.08);
}}

* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    background: var(--bg);
    color: var(--text);
    font-family: '{font_family}', -apple-system, sans-serif;
    line-height: 1.7;
    min-height: 100vh;
}}

/* Bokeh */
.bokeh {{
    position: fixed; top:0; left:0; width:100%; height:100%;
    pointer-events: none; z-index:0; overflow:hidden;
}}
.bokeh .orb {{
    position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.15;
    animation: float 20s ease-in-out infinite;
}}
.orb:nth-child(1) {{ width:400px; height:400px; background:var(--primary); top:10%; left:20%; }}
.orb:nth-child(2) {{ width:300px; height:300px; background:var(--secondary); top:50%; right:10%; animation-delay:-7s; }}
.orb:nth-child(3) {{ width:350px; height:350px; background:var(--primary); bottom:10%; left:50%; animation-delay:-14s; }}
@keyframes float {{
    0%,100% {{ transform: translate(0,0); }}
    33% {{ transform: translate(30px,-20px); }}
    66% {{ transform: translate(-20px,30px); }}
}}

/* Film grain */
.grain {{
    position: fixed; top:0; left:0; width:100%; height:100%;
    pointer-events: none; z-index:1; opacity:0.03;
}}
.grain svg {{ width:100%; height:100%; }}

/* Vignette */
.vignette {{
    position: fixed; top:0; left:0; width:100%; height:100%;
    pointer-events: none; z-index:1;
    background: radial-gradient(ellipse at center, transparent 60%, var(--bg) 100%);
}}

/* Content */
.container {{
    position: relative; z-index:2;
    max-width: 900px; margin: 0 auto; padding: 60px 24px;
}}

/* Header */
.header {{
    text-align: center; margin-bottom: 48px;
}}
.logo {{
    max-height: 60px; margin-bottom: 24px;
}}
.title {{
    font-size: 2rem; font-weight: 700;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 12px;
}}
.meta {{
    font-size: 0.9rem; opacity: 0.6;
}}

/* Tabs */
.tabs {{
    display: flex; gap: 8px; margin-bottom: 32px; justify-content: center;
}}
.tab-btn {{
    padding: 10px 28px; border-radius: 24px; border: 1px solid var(--card-border);
    background: var(--card-bg); color: var(--text); cursor: pointer;
    font-family: inherit; font-size: 0.95rem; transition: all 0.2s;
}}
.tab-btn:hover {{ border-color: var(--primary); }}
.tab-btn.active {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: #fff; border-color: transparent;
}}
.tab-content {{ display: none; }}
.tab-content.active {{ display: block; }}

/* Cards */
.card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 28px; margin-bottom: 24px;
    backdrop-filter: blur(12px);
}}
.card h2 {{
    font-size: 1.1rem; font-weight: 700;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 16px;
    text-transform: uppercase; letter-spacing: 1px;
}}
.card ul {{ list-style: none; padding: 0; }}
.card li {{
    padding: 6px 0; padding-left: 20px;
    position: relative;
}}
.card li::before {{
    content: '•'; position: absolute; left: 0;
    color: var(--primary); font-weight: 700;
}}
.card ol {{ padding-left: 20px; }}
.card ol li {{ padding: 4px 0; }}
.card ol li::before {{ content: none; }}
.card p {{ margin-bottom: 12px; }}
.card strong {{ color: var(--primary); }}

/* Detail sections */
.detail-section {{ margin-bottom: 20px; }}
.detail-section h3 {{
    font-size: 1rem; font-weight: 700;
    color: var(--primary); margin-bottom: 8px;
}}

/* Footer */
.footer {{
    text-align: center; margin-top: 60px; padding-top: 24px;
    border-top: 1px solid var(--card-border);
    font-size: 0.8rem; opacity: 0.4;
}}

/* Print */
@media print {{
    body {{ background: #fff; color: #222; }}
    .bokeh, .grain, .vignette {{ display: none; }}
    .card {{ border: 1px solid #ddd; background: #fafafa; backdrop-filter: none; }}
    .card h2, .title {{ -webkit-text-fill-color: var(--primary); }}
    .tab-content {{ display: block !important; }}
    .tabs {{ display: none; }}
}}
</style>
</head>
<body>
<div class="bokeh"><div class="orb"></div><div class="orb"></div><div class="orb"></div></div>
<div class="grain"><svg><filter id="g"><feTurbulence baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/></filter><rect width="100%" height="100%" filter="url(#g)"/></svg></div>
<div class="vignette"></div>

<div class="container">
    <div class="header">
        {logo_html}
        <div class="title">Compte Rendu de Réunion</div>
        <div class="meta">{date} — {duree}</div>
    </div>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('resume')">Résumé</button>
        <button class="tab-btn" onclick="switchTab('detail')">Détaillé</button>
    </div>

    <div id="tab-resume" class="tab-content active">
        {resume_html}
    </div>

    <div id="tab-detail" class="tab-content">
        {detail_html}
    </div>

    <div class="footer">{footer_text}</div>
</div>

<script>
function switchTab(id) {{
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + id).classList.add('active');
    event.target.classList.add('active');
}}
</script>
</body>
</html>"""
