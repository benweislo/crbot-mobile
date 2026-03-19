import pytest
from pathlib import Path

from app.branding.models import BrandProfile
from app.pipeline.html_generator import HtmlGenerator


SAMPLE_CR = """============================================================
COMPTE RENDU DE RÉUNION
============================================================

  Date     : 19/03/2026
  Durée    : 45 minutes

------------------------------------------------------------
THÈMES ABORDÉS
------------------------------------------------------------
  • Budget Q2
  • Recrutement développeur

------------------------------------------------------------
ACTIONS / PROCHAINES ÉTAPES
------------------------------------------------------------

  **Marie:**
  1. Envoyer le budget révisé avant vendredi

  **Jean-Pierre:**
  1. Publier l'offre d'emploi sur LinkedIn

------------------------------------------------------------
CONCLUSION DU MEETING
------------------------------------------------------------
  → Réunion productive, prochaine étape vendredi.

------------------------------------------------------------
TOUT EN DÉTAILS
------------------------------------------------------------

1. Budget Q2

Le budget a été revu à la hausse de 15% pour intégrer les coûts serveur.

2. Recrutement développeur

Jean-Pierre va publier une offre pour un dev Python senior.

============================================================
FIN DU COMPTE RENDU
============================================================"""


class TestHtmlGenerator:
    def test_generates_valid_html(self, sample_brand):
        profile = BrandProfile.from_dict(sample_brand)
        gen = HtmlGenerator(profile)
        html = gen.generate(SAMPLE_CR)
        assert "<!DOCTYPE html>" in html
        assert "Test Corp" in html

    def test_contains_brand_colors(self, sample_brand):
        profile = BrandProfile.from_dict(sample_brand)
        gen = HtmlGenerator(profile)
        html = gen.generate(SAMPLE_CR)
        assert "#2563EB" in html  # primary color

    def test_contains_themes(self, sample_brand):
        profile = BrandProfile.from_dict(sample_brand)
        gen = HtmlGenerator(profile)
        html = gen.generate(SAMPLE_CR)
        assert "Budget Q2" in html
        assert "Recrutement" in html

    def test_contains_actions(self, sample_brand):
        profile = BrandProfile.from_dict(sample_brand)
        gen = HtmlGenerator(profile)
        html = gen.generate(SAMPLE_CR)
        assert "Marie" in html
        assert "budget révisé" in html

    def test_has_tab_switching(self, sample_brand):
        profile = BrandProfile.from_dict(sample_brand)
        gen = HtmlGenerator(profile)
        html = gen.generate(SAMPLE_CR)
        assert "tab-resume" in html or "tab-summary" in html
        assert "tab-detail" in html

    def test_self_contained(self, sample_brand):
        profile = BrandProfile.from_dict(sample_brand)
        gen = HtmlGenerator(profile)
        html = gen.generate(SAMPLE_CR)
        # No external links
        assert "http://" not in html.replace("<!DOCTYPE html>", "")
        assert "https://" not in html

    def test_saves_to_file(self, sample_brand, tmp_dir):
        profile = BrandProfile.from_dict(sample_brand)
        gen = HtmlGenerator(profile)
        out = tmp_dir / "test_cr.html"
        gen.generate_to_file(SAMPLE_CR, out)
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
