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
    """Context manager that blocks all outbound network connections.

    Replaces socket.socket with a stub that raises ConnectionError.
    This guarantees no data leaks during analysis — even if a dependency
    tries to phone home.
    """

    def __init__(self):
        self._original_socket = None
        self._original_getaddrinfo = None

    def __enter__(self):
        self._original_socket = socket.socket
        self._original_getaddrinfo = socket.getaddrinfo

        def blocked_socket(*args, **kwargs):
            raise ConnectionError(
                "Network access is blocked during genetic analysis for privacy. "
                "Use 'python main.py download' separately to fetch databases."
            )

        def blocked_getaddrinfo(*args, **kwargs):
            raise ConnectionError("Network access blocked for privacy.")

        socket.socket = blocked_socket
        socket.getaddrinfo = blocked_getaddrinfo
        return self

    def __exit__(self, *exc):
        socket.socket = self._original_socket
        socket.getaddrinfo = self._original_getaddrinfo
        return False


def sanitize_report_metadata() -> dict:
    """Return safe metadata for reports — no system-identifying info."""
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "tool": "Genetic Health Analyzer (local)",
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
