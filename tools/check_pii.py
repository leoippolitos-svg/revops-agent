"""Find personal data in tracked files: e-mail addresses and phone numbers that are not fictional.

Run from the repository root:
    python tools/check_pii.py

Rule zero keeps real data out; this is the second net for the kind of value that slips in
by copy and paste. Allowed: addresses at example.com (the generator uses it), placeholders
such as <email>, and git attribution addresses. It prints the file and line only, never the
value, the same as the leak check.

It does not cover names: every person in this repository is fictional by rule, and a name
list would flag the generator's word lists.
"""

import re
import subprocess
import sys
from pathlib import Path

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}")
PHONE = re.compile(r"(?<![\w.])\+?\d{1,3}[ .-]?\(?\d{2,4}\)?[ .-]\d{3,5}[ .-]\d{3,5}(?![\w.])")
ALLOWED_EMAIL = re.compile(r"@(example\.com|anthropic\.com|users\.noreply\.github\.com)$", re.I)
IPV4 = re.compile(r"\d{1,3}(\.\d{1,3}){3}")
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".duckdb", ".ico", ".pdf"}


def tracked_files(root: Path) -> list[Path]:
    out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True)
    return [root / line for line in out.stdout.splitlines() if line]


def scan_text(text: str) -> list[int]:
    lines = []
    for number, line in enumerate(text.splitlines(), start=1):
        emails = [m.group(0) for m in EMAIL.finditer(line) if not ALLOWED_EMAIL.search(m.group(0))]
        # A dotted IP address has the shape of a phone number; it is not personal data.
        phones = [m.group(0) for m in PHONE.finditer(line) if not IPV4.fullmatch(m.group(0).strip())]
        if emails or phones:
            lines.append(number)
    return lines


def check(root: Path) -> list[str]:
    problems = []
    for path in tracked_files(root):
        if path.suffix.lower() in SKIP_SUFFIXES or not path.is_file() or path.name == "check_pii.py":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for number in scan_text(text):
            problems.append(f"{path.relative_to(root).as_posix()}:{number}")
    return problems


def main() -> int:
    problems = check(Path("."))
    for where in problems:
        print(f"ERROR possible personal data at {where}")
    print(f"\nScanned tracked files for personal data: {len(problems)} hits.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
