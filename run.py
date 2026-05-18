#!/usr/bin/env python3
"""
Quick launcher — double-click or run `python run.py` to start the dashboard.

Flags:
  --debug           Enable Flask auto-reload on .py / template changes.
                    Also via GENE_LENS_DEBUG=1.
  --port PORT       Preferred port (default 5000). If the port is taken —
                    especially by macOS AirPlay Receiver, which squats on
                    5000 by default — we auto-bump to the next free port
                    and tell you in the banner.
                    Also via GENE_LENS_PORT=PORT.
  --no-auto-port    Disable auto-bump: fail fast if the chosen port is taken.
  --lang en|pt|pt-BR  Console/log language. Default en. UI language is
                    per-user via cookie.
"""
import argparse
import os
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dashboard import run_dashboard


def _print_preflight() -> None:
    from config import CLINVAR_TSV, PHARMGKB_ANNOTATIONS, PHARMGKB_ALLELES
    clinvar = CLINVAR_TSV.exists()
    pharm = PHARMGKB_ANNOTATIONS.exists() and PHARMGKB_ALLELES.exists()
    if clinvar and pharm:
        return
    print("─" * 60)
    if not clinvar:
        print("  ⚠  ClinVar database NOT FOUND — analyses will be empty")
        print("     Run: python main.py download")
    if not pharm:
        print("  ⚠  PharmGKB database NOT FOUND — no drug-gene findings")
        print("     See /settings for instructions")
    print("─" * 60)


def _port_squatter(port: int) -> str | None:
    """Return a short identifier of who's listening on 127.0.0.1:port, or
    None if the port is free.

    We do two checks because macOS AirPlay binds in a way that lets bind()
    succeed on a different address family while still intercepting traffic
    to 127.0.0.1 — so the bind-only test gives false negatives. Combining
    bind + a short HTTP probe catches both regular collisions and the
    AirPlay weirdness.
    """
    # Step 1: try to bind. If this fails, port is definitely occupied.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
            s.bind(("127.0.0.1", port))
    except OSError:
        # Step 2: who is it? Look at the Server header if any.
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/", method="GET")
            with urllib.request.urlopen(req, timeout=0.4) as resp:
                server = resp.headers.get("Server", "")
        except urllib.error.HTTPError as e:
            server = e.headers.get("Server", "") if e.headers else ""
        except Exception:
            server = ""
        if "AirTunes" in server or "airplay" in server.lower():
            return "macOS AirPlay Receiver"
        if server:
            return server
        return "another process"

    # Bind succeeded but AirPlay may still be intercepting via a different
    # address family — probe HTTP and look for the AirTunes signature.
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/", method="GET")
        with urllib.request.urlopen(req, timeout=0.4) as resp:
            server = resp.headers.get("Server", "")
            if "AirTunes" in server:
                return "macOS AirPlay Receiver"
    except urllib.error.HTTPError as e:
        server = e.headers.get("Server", "") if e.headers else ""
        if "AirTunes" in server:
            return "macOS AirPlay Receiver"
    except Exception:
        pass
    return None


def _pick_port(preferred: int, auto: bool = True) -> int:
    """Return a usable port, auto-bumping from `preferred` if it's taken.

    Probes preferred, then preferred+1, preferred+50, then a small fixed
    list of common dev fallbacks (8000, 8080). Bails after ~12 attempts
    so we never spin forever on a hostile system.
    """
    squatter = _port_squatter(preferred)
    if squatter is None:
        return preferred
    if not auto:
        print(f"  ⚠  Port {preferred} is taken by {squatter}.")
        print("     Re-run with --port <other> or drop --no-auto-port.")
        sys.exit(1)

    candidates = [preferred + 1, preferred + 50, 5050, 5500, 5555, 8000, 8080, 8888]
    seen = {preferred}
    for cand in candidates:
        if cand in seen or cand < 1024 or cand > 65535:
            continue
        seen.add(cand)
        if _port_squatter(cand) is None:
            print(f"  ⚠  Port {preferred} is taken by {squatter}. Using {cand} instead.")
            return cand
    # Last resort: ask the OS for any free port.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        fallback = s.getsockname()[1]
    print(f"  ⚠  Port {preferred} is taken by {squatter}. Using {fallback} instead.")
    return fallback


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gene Lens dashboard launcher")
    parser.add_argument("--debug", action="store_true",
                        default=os.environ.get("GENE_LENS_DEBUG") == "1",
                        help="Flask auto-reload on file changes")
    parser.add_argument("--port", type=int,
                        default=int(os.environ.get("GENE_LENS_PORT", "5000")),
                        help="Preferred port (default 5000; auto-bumps if taken)")
    parser.add_argument("--no-auto-port", action="store_true",
                        help="Don't auto-bump; fail if the port is taken")
    parser.add_argument("--lang", type=str, default="en",
                        choices=["en", "pt", "pt-BR"],
                        help="Console/log language (default en)")
    args = parser.parse_args()

    # In Flask debug mode, Werkzeug forks a child process for auto-reload.
    # The parent already chose a port and bound it briefly to probe — by the
    # time the child re-runs run.py, the parent's lingering socket would
    # show our own port as "taken" and we'd bump again. Skip the re-pick by
    # honoring GENE_LENS_RESOLVED_PORT, which the parent sets for us.
    resolved = os.environ.get("GENE_LENS_RESOLVED_PORT")
    if resolved:
        port = int(resolved)
    else:
        _print_preflight()
        port = _pick_port(args.port, auto=not args.no_auto_port)
        os.environ["GENE_LENS_RESOLVED_PORT"] = str(port)
    run_dashboard(port=port, debug=args.debug, lang=args.lang)
