"""
Tests for src.local_ai.chat_about_analysis and its helpers.

The Ollama daemon won't be running in CI, so we mock the network layer
(urllib.request.urlopen for the blocking HTTP path, subprocess.Popen for
the streaming CLI path) and assert on the request body that *would* have
been sent, plus parsing of fake responses.
"""
import io
import json
import subprocess
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from src.local_ai import (
    _build_chat_messages,
    _friendly_ollama_error,
    chat_about_analysis,
    chat_about_analysis_stream,
    estimate_prompt_tokens,
    estimate_tokens,
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


# ── _build_chat_messages (pure helper, no I/O) ───────────────────────────────

class TestBuildChatMessages:
    """The HTTP /api/chat endpoint takes a `messages` array. This helper is
    the single source of truth for that array — system prompt + bounded
    context + capped history + user question. Locking the contract here is
    cheaper and more precise than asserting through the network mock."""

    def test_starts_with_a_single_system_message(self):
        msgs = _build_chat_messages("rs1 (APOE): risk", [], "what?", "en")
        assert msgs[0]["role"] == "system"
        # Exactly one system message — duplicate system roles confuse models.
        assert sum(1 for m in msgs if m["role"] == "system") == 1

    def test_ends_with_the_current_user_question(self):
        msgs = _build_chat_messages("ctx", [], "is this risky?", "en")
        assert msgs[-1] == {"role": "user", "content": "is this risky?"}

    def test_strips_whitespace_from_question(self):
        msgs = _build_chat_messages("ctx", [], "   what now?  \n", "en")
        assert msgs[-1]["content"] == "what now?"

    def test_system_message_wraps_context_in_explicit_markers(self):
        """Without explicit markers around the analysis, the model can confuse
        user text with analysis data — a small jailbreak vector."""
        msgs = _build_chat_messages("rs1234 = APOE risk variant", [], "x", "en")
        sys = msgs[0]["content"]
        assert "---- USER'S ANALYSIS (read-only context) ----" in sys
        assert "---- END OF ANALYSIS ----" in sys
        assert "rs1234 = APOE risk variant" in sys

    def test_english_language_uses_english_system_prompt(self):
        from src.local_ai import SYSTEM_PROMPT_EN
        sys_msg = _build_chat_messages("ctx", [], "x", "en")[0]["content"]
        assert sys_msg.startswith(SYSTEM_PROMPT_EN[:80])

    def test_portuguese_language_uses_portuguese_system_prompt(self):
        from src.local_ai import SYSTEM_PROMPT_PT
        sys_msg = _build_chat_messages("ctx", [], "x", "pt")[0]["content"]
        assert sys_msg.startswith(SYSTEM_PROMPT_PT[:80])

    def test_unknown_language_falls_back_to_english(self):
        """The Flask layer always passes en/pt, but a typo shouldn't crash."""
        from src.local_ai import SYSTEM_PROMPT_EN
        sys_msg = _build_chat_messages("ctx", [], "x", "xx")[0]["content"]
        assert sys_msg.startswith(SYSTEM_PROMPT_EN[:80])

    def test_history_is_capped_to_last_8_turns(self):
        history = [
            {"role": "user" if i % 2 == 0 else "assistant", "content": f"turn-{i}"}
            for i in range(12)
        ]
        msgs = _build_chat_messages("ctx", history, "latest", "en")
        # 1 system + up to 8 history + 1 user question = 10 max
        assert len(msgs) <= 10
        contents = [m["content"] for m in msgs]
        # Oldest four dropped, most recent kept. Exact-match check (substring
        # would alias "turn-1" with "turn-11").
        for i in range(4):
            assert f"turn-{i}" not in contents, f"turn-{i} should have been dropped"
        assert "turn-11" in contents

    def test_history_roles_map_to_user_and_assistant_only(self):
        """Any non-'user' role coming from the frontend (e.g. a stray
        'system') must be normalized to 'assistant' so we don't ship a
        rogue second system message."""
        history = [
            {"role": "user", "content": "hi"},
            {"role": "system", "content": "leak attempt"},  # adversarial
            {"role": "assistant", "content": "hello"},
        ]
        msgs = _build_chat_messages("ctx", history, "ok", "en")
        # Only the first message has role=system.
        non_first_system = [m for m in msgs[1:] if m["role"] == "system"]
        assert non_first_system == []
        # And the rogue content still appears, just under 'assistant'.
        assert any(m["role"] == "assistant" and "leak attempt" in m["content"] for m in msgs)

    def test_empty_or_blank_history_turns_are_skipped(self):
        history = [
            {"role": "user", "content": ""},
            {"role": "user", "content": "   "},
            {"role": "assistant", "content": None},
            {"role": "user", "content": "real question"},
        ]
        msgs = _build_chat_messages("ctx", history, "q", "en")
        history_msgs = [m for m in msgs if m["role"] in ("user", "assistant")]
        # 1 real history turn + 1 final question = 2
        assert len(history_msgs) == 2
        assert history_msgs[0]["content"] == "real question"

    def test_long_context_is_truncated_with_marker(self):
        long_ctx = "rs1234\n" * 8000  # well over 20k chars
        msgs = _build_chat_messages(long_ctx, [], "hi", "en")
        sys = msgs[0]["content"]
        assert "analysis truncated" in sys.lower()
        # Hard cap: 20k char ctx + system prompt + framing ≈ well under 25k.
        between = sys.split("---- USER'S ANALYSIS (read-only context) ----")[1]
        block = between.split("---- END OF ANALYSIS ----")[0]
        assert len(block) < 25000

    def test_empty_context_does_not_crash(self):
        msgs = _build_chat_messages("", [], "hi", "en")
        assert msgs[-1]["content"] == "hi"
        assert msgs[0]["role"] == "system"

    def test_none_context_does_not_crash(self):
        msgs = _build_chat_messages(None, [], "hi", "en")
        assert msgs[0]["role"] == "system"

    def test_messages_are_json_serializable(self):
        """This array goes straight into urllib as JSON body — anything
        non-serializable would explode at request time, not test time."""
        msgs = _build_chat_messages(
            "ctx with ünicôde 🧬",
            [{"role": "user", "content": "test"}],
            "what about ácido?",
            "pt",
        )
        # Should not raise.
        encoded = json.dumps({"messages": msgs}, ensure_ascii=False)
        assert "🧬" in encoded
        assert "ácido" in encoded


# ── chat_about_analysis (HTTP path) ──────────────────────────────────────────

def _fake_http_response(payload: dict, status: int = 200):
    """Mock the context-manager response object urllib.request.urlopen returns."""
    body = json.dumps(payload).encode("utf-8")
    resp = MagicMock()
    resp.read.return_value = body
    resp.__enter__.return_value = resp
    resp.__exit__.return_value = False
    resp.status = status
    return resp


class TestChatAboutAnalysis:
    """HTTP path: chat_about_analysis posts JSON to /api/chat on the local
    Ollama daemon. We mock urllib.request.urlopen and assert on the
    request that *would* have gone out."""

    def test_returns_ok_with_model_reply(self):
        resp = _fake_http_response({
            "message": {"role": "assistant", "content": "Hello, here is the answer."},
            "done": True,
        })
        with patch("urllib.request.urlopen", return_value=resp):
            ok, reply = chat_about_analysis(
                context="rs1234 (APOE): risk variant",
                history=[],
                question="What does this mean?",
                model="llama3.1:8b",
                language="en",
            )
        assert ok is True
        assert reply == "Hello, here is the answer."

    def test_friendly_error_on_connection_refused(self):
        """Daemon not running → urllib raises URLError. Must produce the
        'start ollama serve' friendly hint, not a stack trace."""
        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("connection refused"),
        ):
            ok, reply = chat_about_analysis(context="ctx", history=[], question="hi")
        assert ok is False
        assert "ollama serve" in reply.lower() or "ollama app" in reply.lower()

    def test_friendly_error_when_model_not_pulled(self):
        """Daemon answers with 404 and stderr-style body — we surface the
        'ollama pull <model>' instruction."""
        err = urllib.error.HTTPError(
            url="http://127.0.0.1:11434/api/chat",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=io.BytesIO(b"model 'gemma2:9b' not found, try pulling it first"),
        )
        with patch("urllib.request.urlopen", side_effect=err):
            ok, reply = chat_about_analysis(
                context="ctx", history=[], question="hi", model="gemma2:9b",
            )
        assert ok is False
        assert "ollama pull gemma2:9b" in reply

    def test_returns_error_on_empty_reply(self):
        resp = _fake_http_response({
            "message": {"role": "assistant", "content": "   "},
            "done": True,
        })
        with patch("urllib.request.urlopen", return_value=resp):
            ok, reply = chat_about_analysis(context="ctx", history=[], question="hi")
        assert ok is False
        assert "empty" in reply.lower()

    def test_request_targets_local_ollama_loopback(self):
        """Privacy guarantee: the request must go to 127.0.0.1:11434, never
        an external host. This is what makes the AI chat 'local-only'."""
        resp = _fake_http_response({"message": {"content": "ok"}, "done": True})
        captured = {}

        def _capture(req, timeout=None):
            captured["url"] = req.full_url
            captured["body"] = req.data
            return resp

        with patch("urllib.request.urlopen", side_effect=_capture):
            chat_about_analysis(context="ctx", history=[], question="hi")

        assert captured["url"].startswith("http://127.0.0.1:11434/"), (
            f"AI chat must hit local Ollama only, got {captured['url']!r}"
        )

    def test_request_body_includes_messages_and_options(self):
        resp = _fake_http_response({"message": {"content": "ok"}, "done": True})
        captured = {}

        def _capture(req, timeout=None):
            captured["body"] = json.loads(req.data.decode("utf-8"))
            return resp

        with patch("urllib.request.urlopen", side_effect=_capture):
            chat_about_analysis(
                context="rs1=APOE", history=[], question="explain?", model="llama3.1:8b",
            )

        body = captured["body"]
        assert body["model"] == "llama3.1:8b"
        assert body["stream"] is False
        assert isinstance(body["messages"], list)
        assert body["messages"][-1] == {"role": "user", "content": "explain?"}
        # num_predict / num_ctx must be pinned so PT replies don't get cut.
        assert body["options"]["num_predict"] >= 1024
        assert body["options"]["num_ctx"] >= 4096


# ── chat_about_analysis_stream ──────────────────────────────────────────────

class _FakePopen:
    """Minimal subprocess.Popen substitute that yields a scripted stdout."""
    def __init__(self, chunks=("Hello ", "world", ""), stderr="", returncode=0):
        self._chunks = list(chunks)
        self._stderr_text = stderr
        self.returncode = returncode
        self.stdin = _FakeStdin()
        self.stdout = self  # we'll implement read() ourselves
        self.stderr = _FakeStderr(stderr)
        self.wait_called = False

    def read(self, n=64):
        if not self._chunks:
            return ""
        return self._chunks.pop(0)

    def wait(self, timeout=None):
        self.wait_called = True
        return self.returncode


class _FakeStdin:
    def write(self, data): pass
    def close(self): pass


class _FakeStderr:
    def __init__(self, text): self._text = text
    def read(self): return self._text


class TestChatStream:
    def test_yields_chunks_in_order(self):
        fake = _FakePopen(chunks=("Hello, ", "this is ", "the answer.", ""))
        with patch("src.local_ai.is_ollama_available", return_value=True), \
             patch("src.local_ai.subprocess.Popen", return_value=fake):
            chunks = list(chat_about_analysis_stream(
                context="ctx", history=[], question="hi", model="llama3.1:8b", language="en",
            ))
        # All chunks should be strings (no error sentinel since returncode=0)
        assert all(isinstance(c, str) for c in chunks)
        assert "".join(chunks) == "Hello, this is the answer."

    def test_yields_error_sentinel_when_ollama_missing(self):
        with patch("src.local_ai.is_ollama_available", return_value=False):
            chunks = list(chat_about_analysis_stream(
                context="ctx", history=[], question="hi",
            ))
        assert len(chunks) == 1
        assert isinstance(chunks[0], dict)
        assert chunks[0]["event"] == "error"

    def test_yields_error_when_binary_not_found(self):
        with patch("src.local_ai.is_ollama_available", return_value=True), \
             patch("src.local_ai.subprocess.Popen", side_effect=FileNotFoundError):
            chunks = list(chat_about_analysis_stream(
                context="ctx", history=[], question="hi",
            ))
        assert chunks[0]["event"] == "error"
        assert "ollama" in chunks[0]["message"].lower()

    def test_yields_error_appended_after_text_on_nonzero_exit(self):
        """If model errors out mid-stream we still surface a diagnostic."""
        fake = _FakePopen(
            chunks=("partial reply", ""),
            stderr="Error: model 'llama3.1:8b' not found",
            returncode=1,
        )
        with patch("src.local_ai.is_ollama_available", return_value=True), \
             patch("src.local_ai.subprocess.Popen", return_value=fake):
            chunks = list(chat_about_analysis_stream(
                context="ctx", history=[], question="hi", model="llama3.1:8b",
            ))
        assert chunks[0] == "partial reply"
        # Last item is the error sentinel
        assert isinstance(chunks[-1], dict)
        assert chunks[-1]["event"] == "error"
        assert "ollama pull" in chunks[-1]["message"]

    def test_yields_error_when_no_text_produced(self):
        fake = _FakePopen(chunks=("",), returncode=0)
        with patch("src.local_ai.is_ollama_available", return_value=True), \
             patch("src.local_ai.subprocess.Popen", return_value=fake):
            chunks = list(chat_about_analysis_stream(
                context="ctx", history=[], question="hi",
            ))
        assert len(chunks) == 1
        assert chunks[0]["event"] == "error"
        assert "empty" in chunks[0]["message"].lower()


# ── token estimates ─────────────────────────────────────────────────────────

class TestTokenEstimates:
    def test_empty_text_is_zero_tokens(self):
        assert estimate_tokens("") == 0

    def test_short_text_is_at_least_one_token(self):
        assert estimate_tokens("hi") >= 1

    def test_estimate_scales_roughly_linear(self):
        small = estimate_tokens("x" * 100)
        big = estimate_tokens("x" * 10000)
        # 100x more chars should produce ~100x more tokens (within rounding).
        assert 80 <= big / small <= 120

    def test_prompt_breakdown_includes_all_sections(self):
        b = estimate_prompt_tokens(
            context="rs1 finding " * 50,
            history=[{"role": "user", "content": "earlier"}],
            question="What about rs1?",
            language="en",
        )
        assert {"system", "context", "history", "question", "total"} <= set(b.keys())
        assert b["total"] >= b["context"] + b["question"]
        assert b["context"] > 0
        assert b["system"] > 0

    def test_history_estimate_only_counts_last_eight(self):
        many = [{"role": "user", "content": "x" * 10000} for _ in range(20)]
        b = estimate_prompt_tokens(context="", history=many, question="", language="en")
        # last 8 turns of 10k chars each ≈ 8 * 2500 = 20k tokens
        assert b["history"] < 25000  # should never count all 20 turns
