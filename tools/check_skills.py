"""Check that every skill in the repo follows docs/standards/skills.md.

Run from the repository root:
    python tools/check_skills.py

Exits with code 1 if any rule is broken, so CI fails the pull request.
"""

import re
import sys
from pathlib import Path

import yaml  # reads the YAML frontmatter at the top of each SKILL.md

# The two places skills can live (see docs/standards/skills.md).
SKILL_ROOTS = [Path(".claude/skills"), Path("agent/skills")]

# kebab-case: lowercase words joined by single hyphens, e.g. "funnel-diagnosis".
KEBAB_CASE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

MAX_DESCRIPTION = 1024
RESERVED_WORDS = ("claude", "anthropic")


def read_frontmatter(skill_file: Path) -> dict | None:
    """Return the YAML block between the first two '---' lines, or None if missing."""
    text = skill_file.read_text(encoding="utf-8")
    # The file must start with '---', then the YAML, then another '---'.
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    return yaml.safe_load(match.group(1)) or {}


def check_skill(folder: Path) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for one skill folder."""
    errors, warnings = [], []
    name = folder.name

    if not KEBAB_CASE.match(name):
        errors.append(f"{folder}: folder name must be kebab-case")
    if any(word in name for word in RESERVED_WORDS):
        errors.append(f"{folder}: name must not contain 'claude' or 'anthropic'")

    # The file name is case-sensitive: SKILL.md, nothing else.
    skill_file = folder / "SKILL.md"
    if not skill_file.is_file():
        errors.append(f"{folder}: missing SKILL.md (exact name)")
        return errors, warnings

    if (folder / "README.md").exists():
        errors.append(f"{folder}: no README.md inside a skill; use SKILL.md or references/")

    meta = read_frontmatter(skill_file)
    if meta is None:
        errors.append(f"{skill_file}: missing YAML frontmatter between '---' lines")
        return errors, warnings

    if meta.get("name") != name:
        errors.append(f"{skill_file}: 'name' must equal the folder name '{name}'")

    description = str(meta.get("description", "")).strip()
    if not description:
        errors.append(f"{skill_file}: 'description' is required")
    else:
        if len(description) > MAX_DESCRIPTION:
            errors.append(f"{skill_file}: description longer than {MAX_DESCRIPTION} characters")
        if "<" in description or ">" in description:
            errors.append(f"{skill_file}: description must not contain '<' or '>'")
        # A good description says when to use the skill, not only what it does.
        if "use when" not in description.lower():
            warnings.append(f"{skill_file}: description should say 'Use when ...'")

    # Trigger tests: required for business skills, recommended for coding skills.
    trigger_test = Path("evals/skills") / f"{name}.yaml"
    if not trigger_test.is_file():
        message = f"{folder}: no trigger test at {trigger_test}"
        if folder.parent == Path("agent/skills"):
            errors.append(message)
        else:
            warnings.append(message)

    return errors, warnings


def main() -> int:
    all_errors, all_warnings = [], []
    found = 0

    for root in SKILL_ROOTS:
        if not root.is_dir():
            continue
        for folder in sorted(p for p in root.iterdir() if p.is_dir()):
            found += 1
            errors, warnings = check_skill(folder)
            all_errors += errors
            all_warnings += warnings

    for w in all_warnings:
        print(f"WARN  {w}")
    for e in all_errors:
        print(f"ERROR {e}")

    print(f"\nChecked {found} skills: {len(all_errors)} errors, {len(all_warnings)} warnings.")
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
