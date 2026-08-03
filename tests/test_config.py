import pytest
from app.config import settings

def test_settings_defaults():
    # Check a few default values
    assert settings.WHISPER_MODEL == "base"
    assert "BGE" in settings.EMBEDDING_MODEL or "bge" in settings.EMBEDDING_MODEL

def test_settings_env_override(monkeypatch):
    # We test the class itself since the singleton 'settings' is already instantiated
    from app.config import Settings
    monkeypatch.setenv("WHISPER_MODEL", "medium")
    s = Settings()
    assert s.WHISPER_MODEL == "medium"
