from app.ui.theme import build_stylesheet
from app.config.defaults import WSLO_THEME


def test_stylesheet_contains_background_color():
    qss = build_stylesheet(WSLO_THEME)
    assert "#0B0F1A" in qss


def test_stylesheet_contains_primary_color():
    qss = build_stylesheet(WSLO_THEME)
    assert "#8B5CF6" in qss


def test_stylesheet_has_button_styles():
    qss = build_stylesheet(WSLO_THEME)
    assert "QPushButton" in qss


def test_stylesheet_has_list_styles():
    qss = build_stylesheet(WSLO_THEME)
    assert "QListWidget" in qss


def test_custom_theme_applied():
    custom = WSLO_THEME.copy()
    custom["primary"] = "#FF0000"
    qss = build_stylesheet(custom)
    assert "#FF0000" in qss
