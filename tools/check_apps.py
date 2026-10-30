"""Check that every micro-app in apps/ follows the spec-first flow.

Run from the repository root:
    python tools/check_apps.py

For each folder in apps/ (the _template is skipped), it exits with code 1 if:

  1. SPEC.md is missing, or lacks a section of the template.
  2. The spec says it is built ("Status: built") but a checklist item is
     unticked, or it says it is not built but an item is ticked. A ticked box
     must mean the work was done.
  3. "Must never" does not forbid writing to a data source.
  4. "Data read" names a table that is not a gold model, or a gold table that
     does not exist.
"""

import re
import sys
from pathlib import Path

import yaml

REQUIRED_SECTIONS = ("Problem", "Users", "Screens", "Data read", "Must never", "Security checklist")
CHECKBOX = re.compile(r"^- \[( |x)\] ", re.MULTILINE)
TABLE = re.compile(r"`((?:gold|silver|bronze)\.[a-z_]+)`")


def gold_tables(root: Path) -> set[str]:
    schema = root / "pipeline" / "dbt" / "models" / "gold" / "schema.yml"
    models = (yaml.safe_load(schema.read_text(encoding="utf-8")) or {}).get("models", [])
    return {f"gold.{m['name']}" for m in models}


def sections(text: str) -> dict[str, str]:
    found, current = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            found[current] = ""
        elif current is not None:
            found[current] += line + "\n"
    return found


def check_app(root: Path, folder: Path, gold: set[str]) -> list[str]:
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
        errors.append(f"{where}: the app is built but a checklist item is not ticked")
    if not built and "x" in ticks:
        errors.append(f"{where}: a checklist item is ticked but the app is not built")

    if "write" not in found.get("Must never", "").lower():
        errors.append(f"{where}: 'Must never' must forbid writing to a data source")

    for table in TABLE.findall(found.get("Data read", "")):
        if not table.startswith("gold."):
            errors.append(f"{where}: reads {table}; apps read gold only")
        elif table not in gold:
            errors.append(f"{where}: reads {table}, which is not a gold model")
    return errors


def check(root: Path) -> list[str]:
    gold = gold_tables(root)
    folders = sorted(p for p in (root / "apps").iterdir() if p.is_dir() and not p.name.startswith("_"))
    errors = []
    for folder in folders:
        errors += check_app(root, folder, gold)
    return errors


def main() -> int:
    errors = check(Path("."))
    for error in errors:
        print(f"ERROR {error}")
    print(f"\nChecked the micro-apps: {len(errors)} errors.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
