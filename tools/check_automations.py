"""Check that every automation in automations/ follows the spec-first flow.

Run from the repository root:
    python tools/check_automations.py

For each folder in automations/ it exits with code 1 if:

  1. SPEC.md is missing, or lacks a section of the new-automation skill.
  2. The spec says it is built ("Status: built") but a checklist item is
     unticked, or it says it is not built but an item is ticked. A ticked box
     must mean the work was done.
  3. "Must never" does not forbid writing to a data source.
  4. "Inputs" names a table that is not a gold model, or a gold table that
     does not exist.
  5. Code that writes through WriteControls("<name>") has no
     RECURRING-AUTHORIZATION for that name in context/rules/writeback-rules.md,
     or an authorization names an automation that no code uses. Writing is
     allowed only where the write-back rules say so, and an authorization for a
     job that no longer exists must be removed.

It reuses the helpers of tools/check_apps.py, because the rules are the same.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_apps import CHECKBOX, TABLE, gold_tables, sections  # noqa: E402

REQUIRED_SECTIONS = ("Trigger", "Inputs", "Rules", "Effects", "Failure behavior", "Must never", "Security checklist")


def check_automation(root: Path, folder: Path, gold: set[str]) -> list[str]:
    spec = folder / "SPEC.md"
    where = spec.relative_to(root).as_posix()
    if not spec.is_file():
        return [f"{folder.relative_to(root).as_posix()}: missing SPEC.md"]
    text = spec.read_text(encoding="utf-8")
    found = sections(text)
    errors = [f"{where}: missing the section '{s}'" for s in REQUIRED_SECTIONS if s not in found]

    ticks = CHECKBOX.findall(found.get("Security checklist", ""))
    built = re.search(r"^Status:\s*built\b", text, flags=re.MULTILINE | re.IGNORECASE) is not None
    if "Security checklist" in found and not ticks:
        errors.append(f"{where}: the security checklist has no items")
    if built and " " in ticks:
        errors.append(f"{where}: the automation is built but a checklist item is not ticked")
    if not built and "x" in ticks:
        errors.append(f"{where}: a checklist item is ticked but the automation is not built")

    if "write" not in found.get("Must never", "").lower():
        errors.append(f"{where}: 'Must never' must forbid writing to a data source")

    for table in TABLE.findall(found.get("Inputs", "")):
        if not table.startswith("gold."):
            errors.append(f"{where}: reads {table}; automations read gold only")
        elif table not in gold:
            errors.append(f"{where}: reads {table}, which is not a gold model")
    return errors


WRITER = re.compile(r"WriteControls\(\s*\"([a-z-]+)\"")
MARKER = re.compile(r"RECURRING-AUTHORIZATION: ([a-z-]+)\.")
# Names authorised in the rules but written by code outside automations/ (tools/, scripts).
SEARCH = ("automations", "tools", "observability", "oncall")


def writeback_errors(root: Path) -> list[str]:
    rules = root / "context" / "rules" / "writeback-rules.md"
    authorised = set(MARKER.findall(rules.read_text(encoding="utf-8"))) if rules.is_file() else set()
    writers = {}
    for folder in SEARCH:
        for path in sorted((root / folder).rglob("*.py")) if (root / folder).is_dir() else []:
            if path.name == "controls.py":
                continue
            for name in WRITER.findall(path.read_text(encoding="utf-8")):
                writers.setdefault(name, path.relative_to(root).as_posix())
    errors = [f"{where}: writes as {name!r}, but writeback-rules.md has no RECURRING-AUTHORIZATION for it"
              for name, where in sorted(writers.items()) if name not in authorised]
    errors += [f"context/rules/writeback-rules.md: authorises {name!r}, which no code writes as; remove it"
               for name in sorted(authorised - set(writers))]
    return errors


def check(root: Path) -> list[str]:
    gold = gold_tables(root)
    folders = sorted(p for p in (root / "automations").iterdir() if p.is_dir() and not p.name.startswith("_"))
    errors = []
    for folder in folders:
        errors += check_automation(root, folder, gold)
    return errors + writeback_errors(root)


def main() -> int:
    errors = check(Path("."))
    for error in errors:
        print(f"ERROR {error}")
    print(f"\nChecked the automations: {len(errors)} errors.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
