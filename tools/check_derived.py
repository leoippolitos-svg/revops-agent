"""Warn when a short copy of a document no longer matches its source.

Run from the repository root:
    python tools/check_derived.py            # warns, exit code 0
    python tools/check_derived.py --strict   # exit code 1 if any copy is stale

Some files are condensed copies of a longer source, for example a one-page summary
of the security rules. The copy declares where it comes from in its front matter:

    derived_from: docs/standards/security.md
    source_sha256: <hash of the source when the copy was last updated>

If the source changes, the hash no longer matches and this script says which copy to
update. It warns instead of failing by default, as in the reference design: a source
can change in a way that does not touch the copy, and a person decides.
Line endings are normalised before hashing, so a Windows checkout and a Linux runner
agree on the same file.
"""

import hashlib
import sys
from pathlib import Path

import yaml

SEARCH = ("docs", "agent", "context", ".claude")


def source_hash(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    try:
        return yaml.safe_load(text.split("---", 2)[1]) or {}
    except yaml.YAMLError:
        return {}


def check(root: Path) -> list[str]:
    problems = []
    for folder in SEARCH:
        for path in sorted((root / folder).rglob("*.md")) if (root / folder).is_dir() else []:
            meta = front_matter(path)
            if "derived_from" not in meta:
                continue
            where = path.relative_to(root).as_posix()
            source = root / meta["derived_from"]
            if not source.is_file():
                problems.append(f"{where}: its source {meta['derived_from']} does not exist")
            elif meta.get("source_sha256") != source_hash(source):
                problems.append(f"{where}: {meta['derived_from']} changed since this copy was updated; "
                                f"update the copy and set source_sha256 to {source_hash(source)}")
    return problems


def main(argv: list[str] | None = None) -> int:
    strict = "--strict" in (argv if argv is not None else sys.argv[1:])
    problems = check(Path("."))
    for problem in problems:
        print(f"{'ERROR' if strict else 'WARNING'} {problem}")
    print(f"\nChecked derived copies: {len(problems)} stale.")
    return 1 if strict and problems else 0


if __name__ == "__main__":
    sys.exit(main())
