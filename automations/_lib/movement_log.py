"""The movement log: one line per change an automation makes, shared by every automation.

Who changed it, what, from where, to where, why, and when. In the reference design this was a
sub-workflow every flow called, so every move could be audited and late moves chased by
owner. Here it is one function. Lines are keyed by an explicit id (the event id), so a rerun
replaces its own line instead of adding one.
"""

from pathlib import Path

HEADER = ["# Movement log", "", "| Key | When | Who | Record | From | To | Why |", "|---|---|---|---|---|---|---|"]


def line(entry: dict) -> str:
    return (f"| {entry['key']} | {entry['when']} | {entry['who']} | {entry['record']} | "
            f"{entry['from']} | {entry['to']} | {entry['why']} |")


def record(path: Path, entries: list[dict]) -> None:
    """Add or replace lines by key. The file is one per day, in the log folder."""
    lines = {}
    if path.is_file():
        for row in path.read_text(encoding="utf-8").splitlines()[len(HEADER):]:
            lines[row.split("|")[1].strip()] = row
    for entry in entries:
        lines[str(entry["key"])] = line(entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(HEADER + list(lines.values())) + "\n", encoding="utf-8", newline="\n")


def contains(path: Path, entry: dict) -> bool:
    return path.is_file() and line(entry) in path.read_text(encoding="utf-8")
