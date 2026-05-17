"""
Local persistence for AI chat sessions, keyed by analysis history id.

Conversations live alongside the rest of the user's analyses, under
history/<hid>/chat.json. The file lists messages in chronological order:

    [
      {"role": "user", "content": "...", "ts": "2026-05-17T20:00:00"},
      {"role": "assistant", "content": "...", "model": "llama3.1:8b", "ts": "..."},
      ...
    ]

Privacy contract:
    - File is gitignored via the existing history/ entry — nothing leaves disk.
    - Erasing the chat is a single unlink + best-effort overwrite (chat is
      not as sensitive as raw genome data but we still try not to leak it
      to a recoverable region).
    - No metadata about the user's environment is recorded.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

HISTORY_DIR = Path(__file__).resolve().parent.parent / "history"


def _chat_path(hid: str) -> Path:
    """Path to the chat file for an analysis. hid is sanitized to a safe filename."""
    safe = "".join(c for c in hid if c.isalnum() or c in ("_", "-"))[:128]
    if not safe:
        raise ValueError(f"invalid analysis id: {hid!r}")
    return HISTORY_DIR / safe / "chat.json"


def load(hid: str) -> list[dict]:
    """Return the chat transcript for an analysis, or [] if none exists."""
    path = _chat_path(hid)
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    return [t for t in data if isinstance(t, dict) and t.get("role") in ("user", "assistant")]


def append(hid: str, role: str, content: str, *, model: Optional[str] = None) -> None:
    """Append a single turn to the chat transcript. Creates the file if missing."""
    if role not in ("user", "assistant"):
        raise ValueError(f"role must be 'user' or 'assistant', got {role!r}")

    path = _chat_path(hid)
    path.parent.mkdir(parents=True, exist_ok=True)
    transcript = load(hid)

    turn = {
        "role": role,
        "content": content,
        "ts": datetime.now().isoformat(timespec="seconds"),
    }
    if model:
        turn["model"] = model
    transcript.append(turn)

    # Atomic write: write tmp + rename so a crash mid-write doesn't truncate
    # the existing chat. The temp file lives in the same directory so the
    # rename is on the same filesystem.
    tmp = path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def clear(hid: str) -> bool:
    """Delete the chat transcript for an analysis. Returns True if a file was removed."""
    path = _chat_path(hid)
    if not path.exists():
        return False
    # Best-effort overwrite before unlink — chat may quote findings, so treat
    # it with the same care as the rest of the analysis output.
    try:
        size = path.stat().st_size
        with path.open("r+b") as f:
            f.write(os.urandom(min(size, 1024 * 64)))
            f.flush()
            os.fsync(f.fileno())
    except OSError:
        pass
    path.unlink()
    return True


def summary(hid: str) -> dict:
    """Lightweight metadata for the chat list view."""
    transcript = load(hid)
    if not transcript:
        return {"turns": 0, "last_ts": None}
    last = transcript[-1]
    return {
        "turns": len(transcript),
        "last_ts": last.get("ts"),
        "last_role": last.get("role"),
        "last_preview": (last.get("content") or "")[:120],
    }
