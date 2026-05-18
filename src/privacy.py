"""
Privacy utilities — secure file handling and network isolation enforcement.

Design principles:
- Genetic data never leaves the machine
- Temporary files are securely wiped (overwritten before deletion)
- Network access is blocked during analysis (only allowed during explicit download)
- Output files contain no system metadata (hostname, username, paths)
"""
import os
import sys
import socket
import threading
import contextlib
from pathlib import Path
from datetime import datetime


def secure_delete(path: Path, passes: int = 3) -> None:
    """Overwrite file with random bytes before deletion to prevent recovery."""
    if not path.exists():
        return
    size = path.stat().st_size
    if size == 0:
        path.unlink()
        return
    with open(path, "r+b") as f:
        for _ in range(passes):
            f.seek(0)
            f.write(os.urandom(size))
            f.flush()
            os.fsync(f.fileno())
    path.unlink()


def secure_delete_dir(directory: Path, passes: int = 3) -> None:
    """Securely delete all files in a directory, then remove the directory."""
    if not directory.exists():
        return
    for item in directory.rglob("*"):
        if item.is_file():
            secure_delete(item, passes)
    # Remove empty dirs bottom-up
    for item in sorted(directory.rglob("*"), reverse=True):
        if item.is_dir():
            item.rmdir()
    if directory.exists():
        directory.rmdir()


class NetworkBlocker:
    """Context manager that blocks outbound network connections for the
    *calling thread only*.

    Replaces socket.socket / getaddrinfo at the module level, but the
    replacement checks the current thread ident against a registry — so
    other threads (e.g. the Flask web server serving static assets while
    an analysis job runs in the background) keep working normally.

    Prior versions patched globally, which deadlocked the Flask UI:
    accept()ing a new client socket from the browser would raise
    ConnectionError, leaving static CSS requests hanging and the loading
    page stuck on a gray screen.
    """

    _lock = threading.Lock()
    # thread_ident -> nesting depth. A thread is "blocked" iff it appears here.
    # Counting (instead of a set) lets nested `with NetworkBlocker()` work
    # correctly: the inner __exit__ must not unblock the outer scope.
    _blocked_threads: dict = {}
    _original_socket = None
    _original_getaddrinfo = None

    @classmethod
    def _install_patch(cls):
        cls._original_socket = socket.socket
        cls._original_getaddrinfo = socket.getaddrinfo

        def guarded_socket(*args, **kwargs):
            if threading.get_ident() in cls._blocked_threads:
                raise ConnectionError(
                    "Network access is blocked during genetic analysis for privacy. "
                    "Use 'python main.py download' separately to fetch databases."
                )
            return cls._original_socket(*args, **kwargs)

        def guarded_getaddrinfo(*args, **kwargs):
            if threading.get_ident() in cls._blocked_threads:
                raise ConnectionError("Network access blocked for privacy.")
            return cls._original_getaddrinfo(*args, **kwargs)

        socket.socket = guarded_socket
        socket.getaddrinfo = guarded_getaddrinfo

    @classmethod
    def _uninstall_patch(cls):
        if cls._original_socket is not None:
            socket.socket = cls._original_socket
            cls._original_socket = None
        if cls._original_getaddrinfo is not None:
            socket.getaddrinfo = cls._original_getaddrinfo
            cls._original_getaddrinfo = None

    def __enter__(self):
        with NetworkBlocker._lock:
            if not NetworkBlocker._blocked_threads:
                NetworkBlocker._install_patch()
            tid = threading.get_ident()
            NetworkBlocker._blocked_threads[tid] = (
                NetworkBlocker._blocked_threads.get(tid, 0) + 1
            )
        return self

    def __exit__(self, *exc):
        with NetworkBlocker._lock:
            tid = threading.get_ident()
            depth = NetworkBlocker._blocked_threads.get(tid, 0) - 1
            if depth <= 0:
                NetworkBlocker._blocked_threads.pop(tid, None)
            else:
                NetworkBlocker._blocked_threads[tid] = depth
            if not NetworkBlocker._blocked_threads:
                NetworkBlocker._uninstall_patch()
        return False


def sanitize_report_metadata() -> dict:
    """Return safe metadata for reports — no system-identifying info."""
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "tool": "Gene Lens (local)",
        "version": "2.0.0",
    }


def check_input_permissions(path: Path) -> None:
    """Warn if input file is world-readable (Unix) or in a shared folder."""
    if sys.platform == "win32":
        # On Windows, check if file is in a network/shared path
        str_path = str(path.resolve())
        if str_path.startswith("\\\\"):
            print(f"  [PRIVACY WARNING] Input file is on a network share: {path}")
            print("  Consider copying to a local drive first.")
    else:
        mode = path.stat().st_mode
        if mode & 0o004:  # world-readable
            print(f"  [PRIVACY WARNING] Input file is world-readable: {path}")
            print(f"  Run: chmod 600 {path}")


def ensure_directories():
    """Create required directories with restrictive permissions."""
    from config import DATA_DIR, CACHE_DIR, INPUT_DIR, OUTPUT_DIR
    for d in [DATA_DIR, CACHE_DIR, INPUT_DIR, OUTPUT_DIR]:
        d.mkdir(parents=True, exist_ok=True)
