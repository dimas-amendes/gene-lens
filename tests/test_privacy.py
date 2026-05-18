"""
Privacy guarantees of Gene Lens.

These tests defend the core promise of the product: while analysis is
happening, nothing reaches the network. Any future change that loosens
this protection must update or remove these tests deliberately.
"""
import socket
import threading
import time
import urllib.request
from pathlib import Path

import pytest

from src.privacy import (
    NetworkBlocker,
    sanitize_report_metadata,
    secure_delete,
)


class TestNetworkBlocker:
    def test_blocks_raw_socket_creation(self):
        with NetworkBlocker():
            with pytest.raises(ConnectionError):
                socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def test_blocks_dns_resolution(self):
        with NetworkBlocker():
            with pytest.raises(ConnectionError):
                socket.getaddrinfo("example.com", 80)

    def test_blocks_urllib_request(self):
        # urllib.request.urlopen goes through socket.socket eventually.
        with NetworkBlocker():
            with pytest.raises((ConnectionError, Exception)):
                urllib.request.urlopen("http://example.com", timeout=1)

    def test_restores_socket_after_exit(self):
        before = socket.socket
        with NetworkBlocker():
            assert socket.socket is not before
        assert socket.socket is before

    def test_restores_getaddrinfo_after_exit(self):
        before = socket.getaddrinfo
        with NetworkBlocker():
            assert socket.getaddrinfo is not before
        assert socket.getaddrinfo is before

    def test_restores_even_when_inner_block_raises(self):
        before = socket.socket
        with pytest.raises(RuntimeError):
            with NetworkBlocker():
                raise RuntimeError("simulated analysis failure")
        assert socket.socket is before, "socket must be restored even on exception"

    def test_nested_blockers(self):
        """A second nested blocker must not lose the original socket on exit."""
        before = socket.socket
        with NetworkBlocker():
            with NetworkBlocker():
                with pytest.raises(ConnectionError):
                    socket.socket()
            # Inner block exited; outer is still blocking.
            with pytest.raises(ConnectionError):
                socket.socket()
        assert socket.socket is before


class TestNetworkBlockerThreadIsolation:
    """Regression guard for the "loading page stuck on gray screen" bug.

    Original implementation patched socket.socket globally, so when the
    analysis thread entered NetworkBlocker the Flask main thread couldn't
    accept new client connections — every static asset request hung, the
    loading template never painted, and the timer was stuck at 00:00.

    The fix tracks which threads are inside a blocker and lets every other
    thread keep using the network normally.
    """

    def test_other_thread_can_still_open_sockets_during_blocker(self):
        results = {"error": None, "ok": False}

        def worker():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.close()
                results["ok"] = True
            except Exception as e:  # captures ConnectionError too
                results["error"] = e

        with NetworkBlocker():
            # Sanity: this thread IS blocked.
            with pytest.raises(ConnectionError):
                socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # But a sibling thread must remain unaffected.
            t = threading.Thread(target=worker)
            t.start()
            t.join(timeout=2.0)

        assert results["error"] is None, (
            f"sibling thread was wrongly blocked: {results['error']!r}. "
            "This is the bug that froze the loading page — do not regress."
        )
        assert results["ok"] is True

    def test_other_thread_dns_resolution_unaffected(self):
        results = {"ok": False, "error": None}

        def worker():
            try:
                # Loopback is always resolvable, doesn't need actual DNS.
                socket.getaddrinfo("127.0.0.1", 0)
                results["ok"] = True
            except Exception as e:
                results["error"] = e

        with NetworkBlocker():
            with pytest.raises(ConnectionError):
                socket.getaddrinfo("127.0.0.1", 0)
            t = threading.Thread(target=worker)
            t.start()
            t.join(timeout=2.0)

        assert results["ok"], f"sibling thread getaddrinfo wrongly blocked: {results['error']!r}"

    def test_concurrent_blockers_in_separate_threads_dont_unblock_each_other(self):
        """Two analysis threads can run with their own blockers. When one
        exits, the other must remain blocked — same lesson as nested blockers,
        but across threads."""
        thread_a_in_block = threading.Event()
        thread_a_can_exit = threading.Event()
        results = {"a_blocked": None, "b_blocked": None, "a_still_blocked_after_b": None}

        def thread_a():
            with NetworkBlocker():
                # While inside, our own socket call is blocked.
                try:
                    socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    results["a_blocked"] = False
                except ConnectionError:
                    results["a_blocked"] = True
                thread_a_in_block.set()
                # Wait for thread B to enter, run, and exit its blocker.
                thread_a_can_exit.wait(timeout=3.0)
                # After B exited, we must STILL be blocked.
                try:
                    socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    results["a_still_blocked_after_b"] = False
                except ConnectionError:
                    results["a_still_blocked_after_b"] = True

        def thread_b():
            thread_a_in_block.wait(timeout=3.0)
            with NetworkBlocker():
                try:
                    socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    results["b_blocked"] = False
                except ConnectionError:
                    results["b_blocked"] = True
            thread_a_can_exit.set()

        ta = threading.Thread(target=thread_a)
        tb = threading.Thread(target=thread_b)
        ta.start(); tb.start()
        ta.join(timeout=5.0); tb.join(timeout=5.0)

        assert results["a_blocked"] is True
        assert results["b_blocked"] is True
        assert results["a_still_blocked_after_b"] is True, (
            "Thread A was unblocked when Thread B exited its own blocker — "
            "blocker state is leaking across threads."
        )

    def test_main_thread_unblocked_after_worker_thread_blocker_finishes(self):
        """End-to-end version of the Flask scenario: a background worker
        enters a blocker, the main thread (us) keeps networking, and after
        the worker exits the global patches are torn down."""
        worker_done = threading.Event()

        def worker():
            with NetworkBlocker():
                # Hold the block for a moment so the main thread tries to
                # open a socket while the worker is inside.
                time.sleep(0.05)
            worker_done.set()

        before = socket.socket
        t = threading.Thread(target=worker)
        t.start()

        # While the worker is inside its blocker, main thread must still
        # be able to create sockets (this is what Flask needs).
        time.sleep(0.01)  # let worker enter
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.close()

        worker_done.wait(timeout=2.0)
        t.join(timeout=2.0)

        # All blockers exited → originals restored.
        assert socket.socket is before


class TestSanitizeMetadata:
    def test_no_system_identifying_info(self):
        meta = sanitize_report_metadata()
        # These keys leak the operator's identity / machine and must never appear.
        forbidden = {"hostname", "username", "user", "uid", "home", "path", "cwd"}
        assert forbidden.isdisjoint(meta.keys())

    def test_contains_required_fields(self):
        meta = sanitize_report_metadata()
        assert "generated_at" in meta
        assert "tool" in meta
        assert "version" in meta
        assert "gene lens" in meta["tool"].lower()


class TestSecureDelete:
    def test_removes_existing_file(self, tmp_path: Path):
        target = tmp_path / "secret.bin"
        target.write_bytes(b"sensitive payload")
        secure_delete(target, passes=1)
        assert not target.exists()

    def test_handles_empty_file(self, tmp_path: Path):
        target = tmp_path / "empty.bin"
        target.touch()
        secure_delete(target, passes=1)
        assert not target.exists()

    def test_handles_missing_file(self, tmp_path: Path):
        target = tmp_path / "never_existed.bin"
        # Must not raise on missing path.
        secure_delete(target, passes=1)
        assert not target.exists()

    def test_overwrites_before_delete(self, tmp_path: Path):
        """The bytes on disk should differ from the original before unlink."""
        target = tmp_path / "wipe.bin"
        payload = b"A" * 4096
        target.write_bytes(payload)

        # We can't observe the intermediate state directly without race conditions,
        # but we can confirm secure_delete writes random bytes by mocking the unlink
        # step. Patch Path.unlink to inspect contents right before deletion.
        observed = {}
        original_unlink = Path.unlink

        def _capture_then_unlink(self, *args, **kwargs):
            if self == target:
                observed["bytes"] = self.read_bytes()
            return original_unlink(self, *args, **kwargs)

        Path.unlink = _capture_then_unlink
        try:
            secure_delete(target, passes=1)
        finally:
            Path.unlink = original_unlink

        assert "bytes" in observed
        assert observed["bytes"] != payload, "file must be overwritten before unlink"


class TestDeleteHistoryCascade:
    """Deleting a history entry must ALSO wipe the raw-DNA input file the
    entry was generated from. Otherwise the user thinks they removed their
    analysis but their genotype file is still on disk — a serious privacy
    regression in a "100% offline" product."""

    def _setup(self, tmp_path: Path, monkeypatch):
        import dashboard
        hist = tmp_path / "history"
        inp = tmp_path / "input"
        hist.mkdir()
        inp.mkdir()
        monkeypatch.setattr(dashboard, "HISTORY_DIR", hist)
        monkeypatch.setattr(dashboard, "INPUT_DIR", inp)
        return dashboard, hist, inp

    def test_deletes_linked_input_csv(self, tmp_path: Path, monkeypatch):
        import json
        dashboard, hist, inp = self._setup(tmp_path, monkeypatch)

        csv = inp / "user_dna.csv"
        csv.write_text("RSID,CHROMOSOME,POSITION,RESULT\nrs1,1,100,AA\n")
        hid = "20260518_141016_Sample"
        (hist / f"{hid}.json").write_text(json.dumps({
            "id": hid,
            "genome_info": {"filename": "user_dna.csv"},
        }))

        dashboard._delete_history(hid)

        assert not (hist / f"{hid}.json").exists(), "history JSON should be wiped"
        assert not csv.exists(), "linked input CSV should be wiped"

    def test_missing_input_does_not_crash(self, tmp_path: Path, monkeypatch):
        """Already-deleted or never-existed input file must not abort the
        history wipe — the JSON should still go."""
        import json
        dashboard, hist, inp = self._setup(tmp_path, monkeypatch)

        hid = "20260101_000000_ghost"
        (hist / f"{hid}.json").write_text(json.dumps({
            "id": hid,
            "genome_info": {"filename": "no_such_file.csv"},
        }))

        dashboard._delete_history(hid)
        assert not (hist / f"{hid}.json").exists()

    def test_rejects_path_traversal_in_filename(self, tmp_path: Path, monkeypatch):
        """A malformed history JSON with `../` in filename must NOT escape
        INPUT_DIR. The JSON itself still gets wiped."""
        import json
        dashboard, hist, inp = self._setup(tmp_path, monkeypatch)

        outside = tmp_path / "outside_secret.txt"
        outside.write_text("must not be touched")

        hid = "20260101_000001_evil"
        (hist / f"{hid}.json").write_text(json.dumps({
            "id": hid,
            "genome_info": {"filename": "../outside_secret.txt"},
        }))

        dashboard._delete_history(hid)
        assert outside.exists(), "path-traversal target must not be deleted"
        assert outside.read_text() == "must not be touched"
        assert not (hist / f"{hid}.json").exists()
