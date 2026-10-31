"""Check that every AI prompt in an automation is the one its spec says.

Run from the repository root:
    python tools/check_prompts.py

The repository is the source of truth of every prompt (docs/standards/prompt-patterns.md).
Each prompt file in automations/<name>/prompts/ must have its SHA-256 written in that
automation's SPEC.md, and each prompt in agent/prompts/ in docs/prompt-library.md,, in the form "prompt sha256: `<hash>`". Changing a prompt without
updating the spec fails here, so a result or an evaluation can always be tied to the exact
prompt that produced it. Line endings are normalised before hashing.
"""

import hashlib
import re
import sys
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")).hexdigest()


def check(root: Path) -> list[str]:
    errors = []
    # Automation prompts are recorded in their own spec; the agent's prompts in the prompt library.
    pairs = [(p, p.parents[1] / "SPEC.md") for p in sorted((root / "automations").glob("*/prompts/*.md"))]
    pairs += [(p, root / "docs" / "prompt-library.md") for p in sorted((root / "agent" / "prompts").glob("*.md"))]
    for prompt, spec in pairs:
        where = prompt.relative_to(root).as_posix()
        if not spec.is_file():
            errors.append(f"{where}: {spec.relative_to(root).as_posix()} does not exist")
            continue
        recorded = re.findall(rf"{re.escape(prompt.name)}`?, prompt sha256: `([0-9a-f]{{64}})`", spec.read_text(encoding="utf-8"))
        if not recorded:
            errors.append(f"{where}: SPEC.md does not record its hash; add \"{prompt.name}, prompt sha256: `{sha(prompt)}`\"")
        elif recorded[0] != sha(prompt):
            errors.append(f"{where}: the prompt changed; update its hash in SPEC.md to {sha(prompt)} and rerun its evaluation")
    return errors


def main() -> int:
    errors = check(Path("."))
    for error in errors:
        print(f"ERROR {error}")
    print(f"\nChecked automation prompts: {len(errors)} errors.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
