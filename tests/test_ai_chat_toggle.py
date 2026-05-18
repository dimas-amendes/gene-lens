"""
The AI chat is opt-in: even with Ollama installed locally, the feature must
stay off until the user explicitly enables it on /settings. These tests pin
that contract end-to-end (preferences module + Flask routes).
"""
import json
from pathlib import Path

import pytest

from src import preferences


@pytest.fixture(autouse=True)
def isolated_prefs(tmp_path, monkeypatch):
    """Redirect preferences storage to a temp file per test."""
    fake = tmp_path / "prefs.json"
    monkeypatch.setattr(preferences, "PREFS_FILE", fake)
    yield fake


def test_default_is_disabled():
    assert preferences.is_ai_chat_enabled() is False


def test_set_then_get_round_trips(isolated_prefs):
    preferences.set_ai_chat_enabled(True)
    assert preferences.is_ai_chat_enabled() is True
    assert isolated_prefs.exists()
    saved = json.loads(isolated_prefs.read_text())
    assert saved["ai_chat_enabled"] is True


def test_can_be_toggled_off_again():
    preferences.set_ai_chat_enabled(True)
    preferences.set_ai_chat_enabled(False)
    assert preferences.is_ai_chat_enabled() is False


def test_corrupt_prefs_file_falls_back_to_default(isolated_prefs):
    isolated_prefs.write_text("{not valid json")
    assert preferences.is_ai_chat_enabled() is False


def test_unknown_keys_are_ignored(isolated_prefs):
    isolated_prefs.write_text(json.dumps({"ai_chat_enabled": True, "evil": "x"}))
    assert preferences.is_ai_chat_enabled() is True


# --- Flask route integration ---------------------------------------------------

@pytest.fixture
def client(monkeypatch, tmp_path):
    # Force prefs into a temp file BEFORE importing dashboard so the route
    # closures pick up the patched module attribute on every call.
    fake = tmp_path / "prefs.json"
    monkeypatch.setattr(preferences, "PREFS_FILE", fake)
    import dashboard
    dashboard.app.config["TESTING"] = True
    return dashboard.app.test_client()


def _local_post(client, path, **kwargs):
    # The global CSRF hook requires same-origin headers for POSTs.
    headers = {"Origin": "http://127.0.0.1:5000"}
    return client.post(path, headers=headers, **kwargs)


def test_chat_ask_returns_403_when_disabled(client):
    resp = _local_post(
        client,
        "/api/chat/ask",
        json={"question": "what does this mean?"},
    )
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "ai_chat_disabled"


def test_toggle_route_refuses_to_enable_without_ollama(client, monkeypatch):
    import dashboard  # noqa: F401  (ensures app is registered)
    from src import local_ai
    monkeypatch.setattr(local_ai, "is_ollama_available", lambda: False)

    resp = _local_post(client, "/settings/ai-toggle")
    # Redirect back to /settings, but pref stays off.
    assert resp.status_code in (302, 303)
    assert preferences.is_ai_chat_enabled() is False


def test_toggle_route_enables_when_ollama_present(client, monkeypatch):
    from src import local_ai
    monkeypatch.setattr(local_ai, "is_ollama_available", lambda: True)

    resp = _local_post(client, "/settings/ai-toggle")
    assert resp.status_code in (302, 303)
    assert preferences.is_ai_chat_enabled() is True


def test_toggle_route_can_disable_even_without_ollama(client, monkeypatch):
    """Once enabled, the user must always be able to turn it back off — even
    if they later uninstalled Ollama. Otherwise the pref could get stuck on."""
    preferences.set_ai_chat_enabled(True)
    from src import local_ai
    monkeypatch.setattr(local_ai, "is_ollama_available", lambda: False)

    resp = _local_post(client, "/settings/ai-toggle")
    assert resp.status_code in (302, 303)
    assert preferences.is_ai_chat_enabled() is False
