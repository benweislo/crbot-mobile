from app.config.defaults import DEFAULT_CONFIG, WSLO_THEME


def test_default_config_has_required_keys():
    required = [
        "audio_folder", "output_folder", "transcript_folder",
        "cr_folder", "language", "gladia_api_key", "system_prompt", "theme", "logo_path",
    ]
    for key in required:
        assert key in DEFAULT_CONFIG, f"Missing key: {key}"


def test_wslo_theme_has_all_colors():
    colors = [
        "primary", "secondary", "tertiary", "background",
        "surface", "surface_elevated", "text_primary", "text_secondary", "danger",
    ]
    for color in colors:
        assert color in WSLO_THEME, f"Missing color: {color}"
        assert WSLO_THEME[color].startswith("#"), f"{color} must be hex"


def test_default_config_audio_folder_points_to_meetings():
    assert "MEETINGS" in DEFAULT_CONFIG["audio_folder"]


def test_default_system_prompt_is_french_cr():
    prompt = DEFAULT_CONFIG["system_prompt"]
    assert "COMPTE RENDU" in prompt
    assert "THÈMES ABORDÉS" in prompt
    assert "ACTIONS" in prompt
    assert "TOUT EN DÉTAILS" in prompt
