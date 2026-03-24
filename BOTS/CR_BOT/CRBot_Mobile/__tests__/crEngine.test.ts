import { parseCR, generateHTML } from '../src/services/crEngine';
import type { BrandProfile } from '../src/types';

const SAMPLE_CR = `
============================================================
COMPTE RENDU DE RÉUNION
============================================================

  Date     : 24 mars 2026
  Durée    : 1h15

------------------------------------------------------------
THÈMES ABORDÉS
------------------------------------------------------------
  • Avancement du projet mobile
  • Planning de la semaine prochaine
  • Questions techniques sur l'API

------------------------------------------------------------
ACTIONS / PROCHAINES ÉTAPES
------------------------------------------------------------
  **Ben:**
  1. Déployer le proxy sur le VPS
  2. Tester l'upload audio

  **Alice:**
  1. Préparer la démo client

------------------------------------------------------------
CONCLUSION DU MEETING
------------------------------------------------------------
  → Bonne avancée sur le projet. Prochaine réunion vendredi.

------------------------------------------------------------
TOUT EN DÉTAILS
------------------------------------------------------------
1. Avancement du projet mobile

Le développement de l'application mobile CR_BOT avance bien.
Les écrans principaux sont en place.

2. Planning de la semaine prochaine

La semaine prochaine sera focalisée sur les tests.
`;

const BRAND: BrandProfile = {
  company_name: 'CR_BOT',
  primary_color: '#6e3ea8',
  secondary_color: '#E93F7F',
  background_color: '#050505',
  text_color: '#E5E5E5',
  font_family: 'system-ui',
  footer_text: 'Compte rendu généré par CR_BOT',
  logo_b64: 'data:image/png;base64,iVBOR',
};

describe('parseCR', () => {
  test('extracts date and duration', () => {
    const parsed = parseCR(SAMPLE_CR);
    expect(parsed.date).toBe('24 mars 2026');
    expect(parsed.duree).toBe('1h15');
  });

  test('extracts themes as array', () => {
    const parsed = parseCR(SAMPLE_CR);
    expect(parsed.themes).toHaveLength(3);
    expect(parsed.themes[0]).toContain('Avancement du projet mobile');
    expect(parsed.themes[2]).toContain('Questions techniques');
  });

  test('extracts actions text with person names', () => {
    const parsed = parseCR(SAMPLE_CR);
    expect(parsed.actions).toContain('**Ben:**');
    expect(parsed.actions).toContain('Déployer le proxy');
    expect(parsed.actions).toContain('**Alice:**');
  });

  test('extracts conclusion', () => {
    const parsed = parseCR(SAMPLE_CR);
    expect(parsed.conclusion).toContain('Bonne avancée');
  });

  test('extracts detail sections', () => {
    const parsed = parseCR(SAMPLE_CR);
    expect(parsed.details).toContain('1. Avancement du projet mobile');
    expect(parsed.details).toContain('2. Planning de la semaine prochaine');
  });

  test('handles CR with missing sections gracefully', () => {
    const minimal = `
============================================================
COMPTE RENDU DE RÉUNION
============================================================

  Date     : 24 mars 2026
  Durée    : 30min

------------------------------------------------------------
THÈMES ABORDÉS
------------------------------------------------------------
  • Un seul thème

------------------------------------------------------------
CONCLUSION DU MEETING
------------------------------------------------------------
  → Réunion courte.
`;
    const parsed = parseCR(minimal);
    expect(parsed.date).toBe('24 mars 2026');
    expect(parsed.themes).toHaveLength(1);
    expect(parsed.actions).toBe('');
    expect(parsed.conclusion).toContain('Réunion courte');
    expect(parsed.details).toBe('');
  });
});

describe('generateHTML', () => {
  test('produces valid HTML with brand colors', () => {
    const html = generateHTML(SAMPLE_CR, BRAND);
    expect(html).toContain('<!DOCTYPE html>');
    expect(html).toContain('#6e3ea8'); // primary
    expect(html).toContain('#E93F7F'); // secondary
    expect(html).toContain('#050505'); // bg
  });

  test('embeds logo base64', () => {
    const html = generateHTML(SAMPLE_CR, BRAND);
    expect(html).toContain('data:image/png;base64,iVBOR');
  });

  test('contains resume and detail tabs', () => {
    const html = generateHTML(SAMPLE_CR, BRAND);
    expect(html).toContain('Résumé');
    expect(html).toContain('Détaillé');
    expect(html).toContain('tab-resume');
    expect(html).toContain('tab-detail');
  });

  test('contains collapsible section JavaScript', () => {
    const html = generateHTML(SAMPLE_CR, BRAND);
    expect(html).toContain('toggleSection');
  });
});
