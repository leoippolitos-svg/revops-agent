"""Scan the lines added by a push for things that look like secrets.

    python tools/push_scan.py                 # the lines added by the last commit
    python tools/push_scan.py --range A..B    # the lines added between two commits

A cheap second net for a push to main that did not go through the AI review: it reads only
the added lines of the diff, looks for well-known credential shapes, and exits 1 if any is
found. It prints the file and the kind of secret, never the value. The full secret scan
(gitleaks) still runs on every pull request; this one is fast and has no dependency.
"""

import argparse
import re
import subprocess
import sys

PATTERNS = {
    "private key block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "Slack token": re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"),
    "Slack webhook": re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/]{20,}"),
    "Anthropic key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
    "connection string with a password": re.compile(r"\b[a-z]+://[^\s:/@]+:[^\s@/]{6,}@[^\s/]+"),
}


def added_lines(diff: str) -> list[tuple[str, str]]:
    """(file, line) for every line the diff adds."""
    current, found = None, []
    for line in diff.splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else line[4:]
        elif line.startswith("+") and not line.startswith("+++") and current:
            found.append((current, line[1:]))
    return found


def scan(diff: str) -> list[str]:
    hits = []
    for path, line in added_lines(diff):
        for kind, pattern in PATTERNS.items():
            if pattern.search(line):
                hits.append(f"{path}: looks like a {kind}")
    return hits


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan the lines added by a push for secrets.")
    parser.add_argument("--range", default="HEAD~1..HEAD")
    args = parser.parse_args(argv)
    diff = subprocess.run(["git", "diff", "--unified=0", args.range], capture_output=True, text=True, encoding="utf-8").stdout
    hits = scan(diff)
    for hit in hits:
        print(f"ERROR {hit}")
    print(f"\nScanned the added lines of {args.range}: {len(hits)} possible secret(s).")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
