"""
Build-breaking guard against accidentally committing real genetic data.

CLAUDE.md classifies any file outside `sample/` containing the pattern
`rs<digits>[,\\t]<chrom>[,\\t]<pos>[,\\t]<genotype>` as forbidden — that's
the canonical shape of a raw 23andMe/AncestryDNA/etc row. Real genotypes
must never reach version control; the consequences (PII exposure, GINA
implications, irreversibility once pushed) make this worse than any other
class of leak in this codebase.

This test enumerates every tracked file and scans for the pattern. If any
non-sample file matches, the build fails with the file path and line
number so the offending commit is obvious.

`sample/` is allowlisted because its files carry the
`# SYNTHETIC SAMPLE - NOT REAL GENETIC DATA` header (enforced by the
sample/README contract). This test file itself is allowlisted because it
literally contains the pattern as a regex string.
"""
import re
import subprocess
from pathlib import Path

import pytest


# The forbidden shape: rsID, chromosome, position, 1-2 base genotype.
# Separators are comma or tab — both formats are in the wild.
# Allowing whitespace flexibility in case someone exports with column
# alignment, but pinning to start-of-token to avoid matching docstrings
# that mention "rs1234 (something)".
_GENOTYPE_ROW_RE = re.compile(
    r"\brs[0-9]{2,9}[,\t][0-9XYMTxymt]{1,2}[,\t][0-9]{1,12}[,\t][ACGTacgt]{1,2}\b"
)

REPO_ROOT = Path(__file__).resolve().parent.parent

# Paths (relative to repo root) that are exempt from the scan.
# - sample/: synthetic test data, has the required SYNTHETIC header.
# - This very test file: contains the pattern as a regex string in source.
ALLOWLIST_PREFIXES = (
    "sample/",
    "tests/test_data_leak.py",
)

# Skip obvious binaries by extension — scanning them produces noise and
# false positives from accidental byte sequences. Real DNA exports are
# plain text (.txt/.csv/.tsv) or gzipped (we never commit .gz anyway).
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf",
    ".woff", ".woff2", ".ttf", ".otf",
    ".pyc", ".so", ".dylib", ".o", ".a",
    ".gz", ".zip", ".tar", ".bz2",
    ".db", ".sqlite", ".sqlite3",
}


def _tracked_files() -> list[Path]:
    """Return the list of files git considers tracked, relative to the repo
    root. Uses `git ls-files` so the scan exactly mirrors what would ship
    in a clone — untracked working-tree files (gitignored or not) are
    correctly skipped."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        pytest.skip(f"git ls-files unavailable (not a git checkout?): {e}")
    return [Path(line) for line in result.stdout.splitlines() if line.strip()]


def _is_allowlisted(rel_path: Path) -> bool:
    s = str(rel_path).replace("\\", "/")
    return any(s == p or s.startswith(p) for p in ALLOWLIST_PREFIXES)


def _scan_for_genotype_rows(abs_path: Path) -> list[tuple[int, str]]:
    """Return [(line_no, line_excerpt), ...] for every hit in the file.
    Empty list means clean."""
    if abs_path.suffix.lower() in BINARY_EXTENSIONS:
        return []
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
            hits = []
            for n, line in enumerate(f, start=1):
                if _GENOTYPE_ROW_RE.search(line):
                    hits.append((n, line.rstrip()[:160]))
                    if len(hits) >= 3:  # cap noise; first 3 are enough to act on
                        break
            return hits
    except OSError:
        return []


def test_no_tracked_file_contains_real_genotype_rows():
    """CI guard: any tracked file outside sample/ matching the rsID+geno
    row pattern is a privacy incident. Fail loudly with file+line so the
    offender can rotate the offending commit BEFORE pushing."""
    offenders: list[str] = []
    for rel in _tracked_files():
        if _is_allowlisted(rel):
            continue
        abs_path = REPO_ROOT / rel
        if not abs_path.exists():
            continue  # submodule, gitlink, etc.
        hits = _scan_for_genotype_rows(abs_path)
        for line_no, excerpt in hits:
            offenders.append(f"{rel}:{line_no}: {excerpt!r}")
    assert not offenders, (
        "Tracked files contain real genetic data (rsID+chrom+pos+genotype rows).\n"
        "This is a PRIVACY INCIDENT — do not push.\n"
        "If the rows are synthetic, move the file to sample/ and add the "
        "'# SYNTHETIC SAMPLE - NOT REAL GENETIC DATA' header.\n"
        "If a real export got committed by accident, rewrite history "
        "(git filter-repo) BEFORE the commit reaches origin, then rotate "
        "anything that touched the data path.\n\n"
        "Offenders:\n  " + "\n  ".join(offenders)
    )


def test_sample_files_carry_synthetic_header():
    """The allowlist for `sample/` is only safe as long as those files
    actually carry the synthetic-data header. If somebody drops a real
    export into sample/ to dodge the leak test, this catches it."""
    sample_dir = REPO_ROOT / "sample"
    if not sample_dir.exists():
        pytest.skip("sample/ directory missing")
    missing_header = []
    for csv_path in sample_dir.glob("*.csv"):
        text = csv_path.read_text(encoding="utf-8", errors="ignore")[:500]
        if "SYNTHETIC" not in text.upper():
            missing_header.append(str(csv_path.relative_to(REPO_ROOT)))
    assert not missing_header, (
        "Files in sample/ are exempt from the genotype-leak scan only "
        "because they're declared synthetic in their header. These files "
        "are missing the 'SYNTHETIC' marker — either add the header or "
        "move them out of sample/:\n  " + "\n  ".join(missing_header)
    )


def test_gitignore_still_excludes_user_data_directories():
    """Defense in depth: even if someone clears the leak test, the
    gitignore should keep raw user data from being added in the first
    place. Pin the rules we rely on."""
    gi = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    required = ["input/", "output/", "history/", ".genetics_consent"]
    missing = [r for r in required if r not in gi]
    assert not missing, (
        f".gitignore is missing entries that keep user genetic data out "
        f"of version control: {missing}"
    )
