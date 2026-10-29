"""Block real company terms from entering the repository (rule zero).

The list of forbidden terms is NOT stored in the repo, because publishing it
would itself be a leak. It comes from one of two places:

  1. Locally: a file named `.leak-terms` at the repo root (gitignored),
     one term per line. Lines starting with '#' are ignored.
  2. In CI: the GitHub secret LEAK_TERMS, one term per line or comma-separated.

Run from the repository root:
    python tools/check_leaks.py

Exits with code 1 if any term is found. It prints only the file and line,
never the term, so the CI log does not leak it either.
"""

import os
import sys
import unicodedata
from pathlib import Path

TERMS_FILE = Path(".leak-terms")

# Folders that are not ours to scan (dependencies, build output, git internals).
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", "target", "dbt_packages"}

# Only scan text files; binary files (images, the DuckDB file) are skipped.
TEXT_SUFFIXES = {
    ".md", ".py", ".sql", ".yaml", ".yml", ".json", ".toml", ".txt",
    ".csv", ".html", ".css", ".js", ".ts", ".example", "",
}


def normalize(text: str) -> str:
    """Lowercase and strip accents, so 'Ação' and 'acao' match the same term."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def load_terms() -> list[str]:
    raw = os.environ.get("LEAK_TERMS", "")
    if TERMS_FILE.is_file():
        raw += "\n" + TERMS_FILE.read_text(encoding="utf-8")
    terms = []
    for line in raw.replace(",", "\n").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            terms.append(normalize(line))
    return terms


def files_to_scan():
    for path in Path(".").rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        # The terms file itself obviously contains the terms.
        if path == TERMS_FILE or not path.is_file():
            continue
        if path.suffix in TEXT_SUFFIXES:
            yield path


def main() -> int:
    terms = load_terms()
    if not terms:
        # Without a list we cannot check anything. Warn, but do not block,
        # so people who clone the repo can still run the other checks.
        print("WARN  no leak terms configured (.leak-terms or LEAK_TERMS); skipping")
        return 0

    hits = []
    for path in files_to_scan():
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue  # not really a text file
        for number, line in enumerate(lines, start=1):
            clean = normalize(line)
            if any(term in clean for term in terms):
                hits.append(f"{path}:{number}")

    for hit in hits:
        print(f"ERROR forbidden term found at {hit}")
    print(f"\nScanned with {len(terms)} terms: {len(hits)} hits.")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
