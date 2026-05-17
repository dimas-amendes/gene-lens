"""
Privacy guarantees of Gene Lens.

These tests defend the core promise of the product: while analysis is
happening, nothing reaches the network. Any future change that loosens
this protection must update or remove these tests deliberately.
"""
import socket
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
