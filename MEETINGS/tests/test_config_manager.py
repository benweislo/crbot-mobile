import json
from pathlib import Path
from app.config.manager import ConfigManager


def test_creates_default_config_on_first_load(tmp_path):
    mgr = ConfigManager(tmp_path)
    config = mgr.load()
    assert config["language"] == "fr"
    assert (tmp_path / "config.json").exists()


def test_saves_and_loads_custom_value(tmp_path):
    mgr = ConfigManager(tmp_path)
    config = mgr.load()
    config["language"] = "en"
    mgr.save(config)

    mgr2 = ConfigManager(tmp_path)
    loaded = mgr2.load()
    assert loaded["language"] == "en"


def test_loads_gladia_key_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GLADIA_API_KEY", "test-key-123")
    mgr = ConfigManager(tmp_path)
    config = mgr.load()
    assert config["gladia_api_key"] == "test-key-123"


def test_config_value_overrides_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GLADIA_API_KEY", "env-key")
    (tmp_path / "config.json").write_text(
        json.dumps({"gladia_api_key": "config-key"}), encoding="utf-8"
    )
    mgr = ConfigManager(tmp_path)
    config = mgr.load()
    assert config["gladia_api_key"] == "config-key"


def test_corrupted_config_resets_to_defaults(tmp_path):
    (tmp_path / "config.json").write_text("NOT JSON", encoding="utf-8")
    mgr = ConfigManager(tmp_path)
    config = mgr.load()
    assert config["language"] == "fr"


def test_history_empty_on_first_load(tmp_path):
    mgr = ConfigManager(tmp_path)
    history = mgr.load_history()
    assert history == {"processed": []}


def test_history_add_and_load(tmp_path):
    mgr = ConfigManager(tmp_path)
    mgr.add_to_history("test.mp3", "html/test.html")
    history = mgr.load_history()
    assert len(history["processed"]) == 1
    assert history["processed"][0]["file"] == "test.mp3"
    assert "processed_at" in history["processed"][0]


def test_is_processed(tmp_path):
    mgr = ConfigManager(tmp_path)
    assert not mgr.is_processed("test.mp3")
    mgr.add_to_history("test.mp3", "html/test.html")
    assert mgr.is_processed("test.mp3")
