"""
Tests for src.local_ai.chat_about_analysis and its helpers.

The Ollama binary won't be installed in CI, so we mock the subprocess
layer (is_ollama_available + subprocess.run) and assert on the prompt
that *would* have been sent, plus the parsing of fake stdout/stderr.
"""
import subprocess
from unittest.mock import patch

import pytest

from src.local_ai import (
    _friendly_ollama_error,
    chat_about_analysis,
)


# ── _friendly_ollama_error ───────────────────────────────────────────────────

class TestFriendlyError:
    def test_model_not_pulled_uses_pull_hint(self):
        msg = _friendly_ollama_error(
            "Error: model 'llama3.1:8b' not found, try pulling it first",
            "llama3.1:8b",
        )
        assert "ollama pull llama3.1:8b" in msg

    def test_pulling_manifest_treated_as_missing_model(self):
        msg = _friendly_ollama_error("pulling manifest for model gemma2:9b", "gemma2:9b")
        assert "ollama pull gemma2:9b" in msg

    def test_connection_refused_points_at_daemon(self):
        msg = _friendly_ollama_error(
            "could not connect to ollama server: connection refused",
            "llama3.1:8b",
        )
        assert "ollama serve" in msg or "Ollama app" in msg

    def test_oom_suggests_smaller_model(self):
        msg = _friendly_ollama_error("CUDA out of memory", "llama3.1:70b")
        assert "gemma2:2b" in msg or "smaller" in msg.lower()

    def test_unknown_stderr_falls_back_to_raw(self):
        msg = _friendly_ollama_error("totally weird error nobody has seen", "x")
        assert "totally weird error" in msg

    def test_empty_stderr_returns_generic_message(self):
        msg = _friendly_ollama_error("", "x")
        assert msg  # non-empty
        assert "non-zero" in msg.lower() or "details" in msg.lower()


# ── chat_about_analysis ──────────────────────────────────────────────────────

def _fake_run(stdout: str = "", stderr: str = "", returncode: int = 0):
    """Build a mock CompletedProcess that subprocess.run would return."""
    return subprocess.CompletedProcess(
        args=["ollama", "run", "x"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


class TestChatAboutAnalysis:
    def test_returns_ok_with_model_reply(self):
        with patch("src.local_ai.is_ollama_available", return_value=True), \
             patch("src.local_ai.subprocess.run", return_value=_fake_run(stdout="Hello, here is the answer.")):
            ok, reply = chat_about_analysis(
                context="rs1234 (APOE): risk variant",
                history=[],
                question="What does this mean?",
                model="llama3.1:8b",
                language="en",
            )
        assert ok is True
        assert reply == "Hello, here is the answer."

    def test_returns_friendly_error_when_ollama_missing(self):
        with patch("src.local_ai.is_ollama_available", return_value=False):
            ok, reply = chat_about_analysis(
                context="ctx",
                history=[],
                question="hi",
            )
        assert ok is False
        assert "ollama" in reply.lower()

    def test_returns_friendly_error_when_model_not_pulled(self):
        with patch("src.local_ai.is_ollama_available", return_value=True), \
             patch("src.local_ai.subprocess.run", return_value=_fake_run(
                 returncode=1,
                 stderr="Error: model 'gemma2:9b' not found, try pulling it first",
             )):
            ok, reply = chat_about_analysis(
                context="ctx",
                history=[],
                question="hi",
                model="gemma2:9b",
            )
        assert ok is False
        assert "ollama pull gemma2:9b" in reply

    def test_returns_error_on_empty_stdout(self):
        with patch("src.local_ai.is_ollama_available", return_value=True), \
             patch("src.local_ai.subprocess.run", return_value=_fake_run(stdout="   ")):
            ok, reply = chat_about_analysis(
                context="ctx",
                history=[],
                question="hi",
            )
        assert ok is False
        assert "empty" in reply.lower()

    def test_returns_timeout_message(self):
        def _raise(*a, **kw):
            raise subprocess.TimeoutExpired(cmd="ollama", timeout=120)
        with patch("src.local_ai.is_ollama_available", return_value=True), \
             patch("src.local_ai.subprocess.run", side_effect=_raise):
            ok, reply = chat_about_analysis(
                context="ctx",
                history=[],
                question="hi",
            )
        assert ok is False
        assert "long" in reply.lower() or "timeout" in reply.lower() or "smaller" in reply.lower()

    def test_long_context_is_truncated_with_marker(self):
        """Contexts above MAX_CONTEXT_CHARS must be capped and announced."""
        long_context = "rs1\n" * 8000  # well over 20k chars
        captured = {}

        def _capture(args, **kw):
            captured["prompt"] = kw.get("input", "")
            return _fake_run(stdout="ok")

        with patch("src.local_ai.is_ollama_available", return_value=True), \
             patch("src.local_ai.subprocess.run", side_effect=_capture):
            chat_about_analysis(
                context=long_context,
                history=[],
                question="hi",
                language="en",
            )

        prompt = captured["prompt"]
        assert "analysis truncated" in prompt.lower()
        # The actual analysis content inside the markers must be bounded.
        between = prompt.split("USER'S ANALYSIS (read-only context) ----")[1]
        analysis_block = between.split("---- END OF ANALYSIS ----")[0]
        assert len(analysis_block) < 25000

    def test_prompt_includes_recent_history_only(self):
        """Only the last 8 turns should appear in the prompt."""
        captured = {}

        def _capture(args, **kw):
            captured["prompt"] = kw.get("input", "")
            return _fake_run(stdout="ok")

        # 12 turns: the first 4 must be dropped.
        history = [
            {"role": "user" if i % 2 == 0 else "assistant", "content": f"turn-{i}"}
            for i in range(12)
        ]

        with patch("src.local_ai.is_ollama_available", return_value=True), \
             patch("src.local_ai.subprocess.run", side_effect=_capture):
            chat_about_analysis(
                context="ctx",
                history=history,
                question="latest?",
                language="en",
            )

        prompt = captured["prompt"]
        # Earliest four should be gone
        assert "turn-0" not in prompt
        assert "turn-3" not in prompt
        # Most recent should be there
        assert "turn-11" in prompt
        assert "latest?" in prompt

    def test_language_picks_correct_system_prompt(self):
        captured = {}

        def _capture(args, **kw):
            captured["prompt"] = kw.get("input", "")
            return _fake_run(stdout="ok")

        with patch("src.local_ai.is_ollama_available", return_value=True), \
             patch("src.local_ai.subprocess.run", side_effect=_capture):
            chat_about_analysis(context="ctx", history=[], question="x", language="pt")
        assert "português" in captured["prompt"].lower() or "educador" in captured["prompt"].lower()

        with patch("src.local_ai.is_ollama_available", return_value=True), \
             patch("src.local_ai.subprocess.run", side_effect=_capture):
            chat_about_analysis(context="ctx", history=[], question="x", language="en")
        assert "educator" in captured["prompt"].lower()
