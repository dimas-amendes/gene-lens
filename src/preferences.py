"""User preferences persisted to ~/.gene_lens_prefs.json.

Tiny key/value store for optional features the user has explicitly opted into.
Nothing sensitive lives here — just booleans that gate local-only behaviour.
"""
from __future__ import annotations

import json
from pathlib import Path

PREFS_FILE = Path.home() / ".gene_lens_prefs.json"

_DEFAULTS = {
    "ai_chat_enabled": False,
}


def _load() -> dict:
    if not PREFS_FILE.exists():
        return dict(_DEFAULTS)
    try:
        data = json.loads(PREFS_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return dict(_DEFAULTS)
        merged = dict(_DEFAULTS)
        merged.update({k: v for k, v in data.items() if k in _DEFAULTS})
        return merged
    except (OSError, json.JSONDecodeError):
        return dict(_DEFAULTS)


def _save(data: dict) -> None:
    PREFS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def is_ai_chat_enabled() -> bool:
    return bool(_load().get("ai_chat_enabled", False))


def set_ai_chat_enabled(enabled: bool) -> bool:
    data = _load()
    data["ai_chat_enabled"] = bool(enabled)
    _save(data)
    return data["ai_chat_enabled"]
