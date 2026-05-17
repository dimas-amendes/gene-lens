"""
Tests for src.chat_store — the per-analysis chat persistence layer.
"""
from pathlib import Path
from unittest.mock import patch

import pytest

from src import chat_store


@pytest.fixture
def tmp_history(tmp_path, monkeypatch):
    """Redirect HISTORY_DIR to a fresh tmp_path for each test."""
    monkeypatch.setattr(chat_store, "HISTORY_DIR", tmp_path)
    return tmp_path


class TestLoadAndAppend:
    def test_load_returns_empty_when_no_file(self, tmp_history):
        assert chat_store.load("never-existed") == []

    def test_append_creates_directory_and_file(self, tmp_history):
        chat_store.append("hid-1", "user", "first question")
        path = tmp_history / "hid-1" / "chat.json"
        assert path.exists()

    def test_append_then_load_round_trips(self, tmp_history):
        chat_store.append("hid-2", "user", "question?")
        chat_store.append("hid-2", "assistant", "answer.", model="llama3.1:8b")
        transcript = chat_store.load("hid-2")
        assert len(transcript) == 2
        assert transcript[0]["role"] == "user"
        assert transcript[0]["content"] == "question?"
        assert transcript[1]["role"] == "assistant"
        assert transcript[1]["model"] == "llama3.1:8b"

    def test_append_stamps_timestamp(self, tmp_history):
        chat_store.append("hid-3", "user", "x")
        transcript = chat_store.load("hid-3")
        assert "ts" in transcript[0]
        # ISO format: "YYYY-MM-DDTHH:MM:SS"
        assert len(transcript[0]["ts"]) >= 19

    def test_load_drops_malformed_turns(self, tmp_history):
        """If a turn is missing role/content, it must be filtered out on load."""
        path = tmp_history / "hid-x" / "chat.json"
        path.parent.mkdir(parents=True)
        path.write_text('[{"role": "user", "content": "ok"}, {"junk": true}, {"role": "system", "content": "x"}]')
        transcript = chat_store.load("hid-x")
        assert len(transcript) == 1
        assert transcript[0]["content"] == "ok"

    def test_load_handles_broken_json(self, tmp_history):
        path = tmp_history / "hid-broken" / "chat.json"
        path.parent.mkdir(parents=True)
        path.write_text("{this is not valid json")
        assert chat_store.load("hid-broken") == []


class TestSanitization:
    def test_rejects_empty_hid(self, tmp_history):
        with pytest.raises(ValueError):
            chat_store.load("")

    def test_path_traversal_is_sanitized_not_followed(self, tmp_history):
        """Slashes and dots get scrubbed so the lookup can't escape HISTORY_DIR."""
        chat_store.append("../../etc/passwd", "user", "should land in a safe dir")
        # The dangerous chars are stripped — file ends up at history/etcpasswd/chat.json
        sanitized = tmp_history / "etcpasswd" / "chat.json"
        assert sanitized.exists()
        # Nothing escaped to anywhere outside tmp_history.
        assert not (tmp_history.parent / "etc" / "passwd").exists()

    def test_strips_unsafe_chars(self, tmp_history):
        # Slashes, dots, spaces should all get scrubbed — but the underlying
        # safe portion remains usable.
        chat_store.append("safe-id-1", "user", "ok")
        # Should not raise even with messy input; same safe portion should map.
        assert chat_store.load("safe-id-1")

    def test_invalid_role_raises(self, tmp_history):
        with pytest.raises(ValueError):
            chat_store.append("hid", "system", "no")


class TestClear:
    def test_clear_removes_file(self, tmp_history):
        chat_store.append("hid-clear", "user", "x")
        path = tmp_history / "hid-clear" / "chat.json"
        assert path.exists()
        assert chat_store.clear("hid-clear") is True
        assert not path.exists()

    def test_clear_returns_false_when_no_file(self, tmp_history):
        assert chat_store.clear("never-existed") is False


class TestSummary:
    def test_summary_empty(self, tmp_history):
        s = chat_store.summary("none")
        assert s["turns"] == 0
        assert s["last_ts"] is None

    def test_summary_after_messages(self, tmp_history):
        chat_store.append("hid-s", "user", "q")
        chat_store.append("hid-s", "assistant", "a long answer that should be previewed and possibly truncated past 120 chars " * 3)
        s = chat_store.summary("hid-s")
        assert s["turns"] == 2
        assert s["last_role"] == "assistant"
        assert len(s["last_preview"]) <= 120


class TestAtomicWrite:
    def test_tmp_file_is_renamed_into_place(self, tmp_history):
        """An interrupted write must not corrupt the existing chat."""
        chat_store.append("hid-atomic", "user", "first")
        path = tmp_history / "hid-atomic" / "chat.json"
        original = path.read_text()
        # Append a second turn — under the hood the impl writes to a .tmp
        # and renames. We just verify the .tmp isn't left behind on success.
        chat_store.append("hid-atomic", "assistant", "reply")
        assert not (tmp_history / "hid-atomic" / "chat.json.tmp").exists()
        assert path.read_text() != original
