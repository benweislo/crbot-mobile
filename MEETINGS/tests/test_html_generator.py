from pathlib import Path
from app.pipeline.html_generator import HtmlGenerator
from app.config.defaults import WSLO_THEME

SAMPLE_CR = """============================================================
COMPTE RENDU DE RÉUNION
============================================================

  Date     : 20/03/2026
  Durée    : 01:30:00
  Fichiers : test_meeting.mp3

------------------------------------------------------------
THÈMES ABORDÉS
------------------------------------------------------------
  • Planning du projet
  • Budget trimestriel

------------------------------------------------------------
ACTIONS / PROCHAINES ÉTAPES
------------------------------------------------------------
  BEN :
  1. Finaliser le prototype
  ALI :
  2. Préparer la démo

------------------------------------------------------------
CONCLUSION DU MEETING
------------------------------------------------------------
  → Bonne avancée, prochaine réunion lundi

------------------------------------------------------------
TOUT EN DÉTAILS
------------------------------------------------------------
  ## 1. Planning du projet
  - Discussion sur le calendrier Q2
  - **Deadline** fixée au 15 avril

============================================================
FIN DU COMPTE RENDU
============================================================"""


def test_generates_html_file(tmp_path):
    gen = HtmlGenerator(theme=WSLO_THEME)
    output = tmp_path / "test.html"
    gen.generate(SAMPLE_CR, output)
    assert output.exists()
    html = output.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html
    assert "Planning du projet" in html
    assert "Budget trimestriel" in html


def test_html_contains_theme_colors(tmp_path):
    gen = HtmlGenerator(theme=WSLO_THEME)
    output = tmp_path / "test.html"
    gen.generate(SAMPLE_CR, output)
    html = output.read_text(encoding="utf-8")
    assert "#8B5CF6" in html
    assert "#2DD4BF" in html
    assert "#0B0F1A" in html


def test_html_contains_actions(tmp_path):
    gen = HtmlGenerator(theme=WSLO_THEME)
    output = tmp_path / "test.html"
    gen.generate(SAMPLE_CR, output)
    html = output.read_text(encoding="utf-8")
    assert "Finaliser le prototype" in html
    assert "Préparer la démo" in html


def test_html_contains_details_section(tmp_path):
    gen = HtmlGenerator(theme=WSLO_THEME)
    output = tmp_path / "test.html"
    gen.generate(SAMPLE_CR, output)
    html = output.read_text(encoding="utf-8")
    assert "Planning du projet" in html
    assert "Deadline" in html


def test_custom_theme_applied(tmp_path):
    custom = WSLO_THEME.copy()
    custom["primary"] = "#FF0000"
    gen = HtmlGenerator(theme=custom)
    output = tmp_path / "test.html"
    gen.generate(SAMPLE_CR, output)
    html = output.read_text(encoding="utf-8")
    assert "#FF0000" in html


def test_malformed_cr_fallback(tmp_path):
    gen = HtmlGenerator(theme=WSLO_THEME)
    output = tmp_path / "test.html"
    gen.generate("Just some random text\nNo structure here", output)
    assert output.exists()
    html = output.read_text(encoding="utf-8")
    assert "Just some random text" in html
