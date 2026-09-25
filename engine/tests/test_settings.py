from pathlib import Path

from crossmith.settings import Settings


def test_settings_roundtrip(tmp_path: Path):
    config_file = tmp_path / "config.toml"
    settings = Settings(theme="dark", ai_assist_enabled=True)
    settings.save(config_file)

    loaded = Settings.load(config_file)
    assert loaded.theme == "dark"
    assert loaded.ai_assist_enabled is True


def test_settings_defaults_when_missing(tmp_path: Path):
    missing = tmp_path / "does-not-exist.toml"
    settings = Settings.load(missing)
    assert settings.theme == "system"
    assert settings.telemetry_enabled is False
    assert settings.default_packaging_backend == "nuitka"


def test_settings_endpoint_roundtrip(client, tmp_path, monkeypatch):
    monkeypatch.setattr("crossmith.settings.CONFIG_FILE", tmp_path / "config.toml")

    response = client.put("/settings", json={"theme": "dark", "ai_assist_enabled": True})
    assert response.status_code == 200
    assert response.json()["theme"] == "dark"

    response = client.get("/settings")
    assert response.json()["theme"] == "dark"
    assert response.json()["ai_assist_enabled"] is True
