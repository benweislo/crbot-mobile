import type { ParsedCR, BrandProfile } from '../types';

/**
 * Parse structured CR text into sections.
 * Ported from Python html_generator.py — regex-based section extraction.
 */
export function parseCR(crText: string): ParsedCR {
  const dateMatch = crText.match(/Date\s*:\s*(.+)/);
  const dureeMatch = crText.match(/Dur[ée]e\s*:\s*(.+)/);

  // Split on delimiter lines (20+ dashes)
  const sections = crText.split(/^-{20,}$/m);

  let themes: string[] = [];
  let actions = '';
  let conclusion = '';
  let details = '';

  for (let i = 0; i < sections.length; i++) {
    const section = sections[i].trim();

    if (/TH[ÈE]MES\s+ABORD[ÉE]S/i.test(section)) {
      const content = (sections[i + 1] ?? '').trim();
      themes = content
        .split('\n')
        .map((line) => line.replace(/^\s*[•·\-]\s*/, '').trim())
        .filter((line) => line.length > 0);
    }

    if (/ACTIONS\s*\/?\s*PROCHAINES/i.test(section)) {
      actions = (sections[i + 1] ?? '').trim();
    }

    if (/CONCLUSION/i.test(section)) {
      conclusion = (sections[i + 1] ?? '')
        .trim()
        .replace(/^→\s*/, '');
    }

    if (/TOUT\s+EN\s+D[ÉE]TAILS/i.test(section)) {
      details = (sections[i + 1] ?? '').trim();
    }
  }

  return {
    date: dateMatch?.[1]?.trim() ?? '',
    duree: dureeMatch?.[1]?.trim() ?? '',
    themes,
    actions,
    conclusion,
    details,
  };
}

/**
 * Build the Résumé tab HTML from parsed CR.
 */
function buildResume(parsed: ParsedCR): string {
  const themesHtml = parsed.themes
    .map((t) => `<div class="theme-card"><span class="bullet">•</span> ${escapeHtml(t)}</div>`)
    .join('\n');

  let actionsHtml = '';
  if (parsed.actions) {
    // Split per-person blocks: **Name:** or NAME:
    const blocks = parsed.actions.split(/(?=\*\*[^*]+:\*\*|^[A-ZÀ-Ü][A-Za-zÀ-ü\s]+:\s*$)/m);
    actionsHtml = blocks
      .filter((b) => b.trim())
      .map((block) => {
        const lines = block.trim().split('\n');
        const header = lines[0]
          .replace(/\*\*/g, '')
          .replace(/:$/, '')
          .trim();
        const items = lines
          .slice(1)
          .map((l) => l.trim())
          .filter((l) => l)
          .map((l) => `<li>${escapeHtml(l.replace(/^\d+\.\s*/, ''))}</li>`)
          .join('\n');
        return `<div class="person-block"><div class="person-name">${escapeHtml(header)}</div><ol>${items}</ol></div>`;
      })
      .join('\n');
  }

  const conclusionHtml = parsed.conclusion
    ? `<div class="conclusion-box"><span class="arrow">→</span> ${escapeHtml(parsed.conclusion)}</div>`
    : '';

  return `
    <div class="section">
      <h2>Thèmes abordés</h2>
      ${themesHtml}
    </div>
    ${actionsHtml ? `<div class="section"><h2>Actions / Prochaines étapes</h2>${actionsHtml}</div>` : ''}
    ${conclusionHtml ? `<div class="section"><h2>Conclusion</h2>${conclusionHtml}</div>` : ''}
  `;
}

/**
 * Build the Détaillé tab HTML from parsed CR.
 */
function buildDetail(parsed: ParsedCR): string {
  if (!parsed.details) return '<p class="muted">Pas de détails disponibles.</p>';

  // Split on numbered sections: 1. Title, 2. Title, etc.
  const numbered = parsed.details.split(/(?=^\d+\.\s)/m).filter((s) => s.trim());

  return numbered
    .map((section) => {
      const lines = section.trim().split('\n');
      const title = lines[0].trim();
      const body = lines
        .slice(1)
        .map((l) => l.trim())
        .filter((l) => l)
        .map((l) => `<p>${escapeHtml(l)}</p>`)
        .join('\n');
      return `
        <div class="detail-section">
          <h3 class="collapsible" onclick="toggleSection(this)">${escapeHtml(title)}</h3>
          <div class="collapsible-content">${body}</div>
        </div>`;
    })
    .join('\n');
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * Generate self-contained HTML CR from raw CR text + brand profile.
 * Ported from Python html_template.py.
 */
export function generateHTML(crText: string, brand: BrandProfile): string {
  const parsed = parseCR(crText);
  const resumeHtml = buildResume(parsed);
  const detailHtml = buildDetail(parsed);

  return `<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Compte Rendu — ${parsed.date}</title>
<style>
  :root {
    --primary: ${brand.primary_color};
    --secondary: ${brand.secondary_color};
    --bg: ${brand.background_color};
    --text: ${brand.text_color};
    --surface: rgba(255,255,255,0.05);
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: ${brand.font_family};
    font-size: 1.05rem;
    line-height: 1.6;
    min-height: 100vh;
    position: relative;
    overflow-x: hidden;
  }
  /* Bokeh orbs */
  .bokeh { position: fixed; border-radius: 50%; filter: blur(80px); opacity: 0.12; pointer-events: none; z-index: 0; }
  .bokeh-1 { width: 400px; height: 400px; background: var(--primary); top: -100px; left: -100px; }
  .bokeh-2 { width: 350px; height: 350px; background: var(--secondary); bottom: -80px; right: -80px; }
  .bokeh-3 { width: 250px; height: 250px; background: var(--primary); top: 50%; left: 60%; }
  /* Film grain */
  .grain {
    position: fixed; inset: 0; z-index: 0; opacity: 0.03; pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  }
  /* Vignette */
  .vignette { position: fixed; inset: 0; z-index: 0; pointer-events: none; background: radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.6) 100%); }
  /* Main container */
  .container { position: relative; z-index: 1; max-width: 960px; margin: 0 auto; padding: 40px 24px; }
  /* Header */
  .header { text-align: center; margin-bottom: 40px; }
  .logo { max-height: 60px; margin-bottom: 16px; }
  .title { font-size: 1.8rem; font-weight: 700; background: linear-gradient(135deg, var(--primary), var(--secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
  .meta { color: #999; margin-top: 8px; font-size: 0.95rem; }
  /* Tabs */
  .tabs { display: flex; gap: 8px; margin-bottom: 24px; justify-content: center; }
  .tab-btn { padding: 10px 28px; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; background: var(--surface); color: var(--text); cursor: pointer; font-size: 1rem; transition: all 0.2s; }
  .tab-btn.active { background: linear-gradient(135deg, var(--primary), var(--secondary)); border-color: transparent; font-weight: 600; }
  .tab-content { display: none; }
  .tab-content.active { display: block; }
  /* Cards */
  .section { background: var(--surface); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 24px; margin-bottom: 20px; backdrop-filter: blur(12px); }
  .section h2 { font-size: 1.2rem; font-weight: 700; margin-bottom: 16px; background: linear-gradient(135deg, var(--primary), var(--secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
  .theme-card { padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
  .theme-card:last-child { border-bottom: none; }
  .bullet { color: var(--primary); margin-right: 8px; }
  .person-block { margin-bottom: 16px; }
  .person-name { font-weight: 700; color: var(--secondary); margin-bottom: 4px; }
  .person-block ol { padding-left: 24px; }
  .person-block li { margin-bottom: 4px; }
  .conclusion-box { padding: 16px; background: rgba(110,62,168,0.08); border-left: 3px solid var(--primary); border-radius: 0 8px 8px 0; }
  .arrow { color: var(--primary); font-weight: 700; margin-right: 8px; }
  /* Detail sections */
  .detail-section { margin-bottom: 16px; }
  .detail-section h3 { font-size: 1.1rem; font-weight: 600; cursor: pointer; padding: 12px 16px; background: var(--surface); border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); }
  .detail-section h3::before { content: '▸ '; color: var(--primary); }
  .detail-section h3.open::before { content: '▾ '; }
  .collapsible-content { padding: 12px 16px; display: none; }
  .collapsible-content.open { display: block; }
  .collapsible-content p { margin-bottom: 8px; }
  .muted { color: #666; font-style: italic; }
  /* Footer */
  .footer { text-align: center; color: #555; font-size: 0.85rem; margin-top: 40px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.06); }
  /* Print */
  @media print {
    body { background: #fff; color: #111; }
    .bokeh, .grain, .vignette { display: none; }
    .section { border-color: #ddd; background: #fafafa; }
    .tab-content { display: block !important; }
    .tabs { display: none; }
    .title, .section h2 { -webkit-text-fill-color: #333; color: #333; }
  }
</style>
</head>
<body>
<div class="bokeh bokeh-1"></div>
<div class="bokeh bokeh-2"></div>
<div class="bokeh bokeh-3"></div>
<div class="grain"></div>
<div class="vignette"></div>
<div class="container">
  <div class="header">
    ${brand.logo_b64 ? `<img src="${brand.logo_b64}" class="logo" alt="Logo">` : ''}
    <div class="title">Compte Rendu de Réunion</div>
    <div class="meta">${parsed.date}${parsed.duree ? ` — Durée : ${parsed.duree}` : ''}</div>
  </div>
  <div class="tabs">
    <button class="tab-btn active" onclick="switchTab('resume',this)">Résumé</button>
    <button class="tab-btn" onclick="switchTab('detail',this)">Détaillé</button>
  </div>
  <div id="tab-resume" class="tab-content active">
    ${resumeHtml}
  </div>
  <div id="tab-detail" class="tab-content">
    ${detailHtml}
  </div>
  <div class="footer">${brand.footer_text} — ${brand.company_name}</div>
</div>
<script>
function switchTab(name, btn) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  btn.classList.add('active');
}
function toggleSection(el) {
  el.classList.toggle('open');
  const content = el.nextElementSibling;
  content.classList.toggle('open');
}
</script>
</body>
</html>`;
}
