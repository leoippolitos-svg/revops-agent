"""The run catalog: one card for everything that runs, and the health of each.

Run from the repository root:
    python tools/catalog.py check            # validate every card, find scheduled workflows with no card
    python tools/catalog.py page [--check]   # write docs/run-catalog.md from the cards (or check it is current)
    python tools/catalog.py collect [--write] [--notify]
        # read the last run of each card, write observability/logs/job-health.json,
        # and with --notify send one Slack alert per item that is failing or late

A card (catalog/<id>.yml) says what the thing is, who owns it, what starts it, where it
lives, what it writes, whether it uses AI, and where its status comes from. Creating,
changing or stopping something that runs is not finished until its card is (context
document `session-closing`). A stopped item keeps its card with situation "stopped": the
history of what ran is part of the catalog.

Health is runtime data, so it lives in the gitignored log folder. The agent reads it with
get_map("jobs") to answer "did the jobs run yesterday?".
"""

import json
import re
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("id", "name", "kind", "owner", "purpose", "trigger", "where", "writes", "ai", "status_source", "situation")
KINDS = {"automation", "agent", "app", "job", "server"}
SITUATIONS = {"active", "manual", "stopped"}  # active runs on its own; manual runs when a person runs it
SOURCES = {"github_actions", "log", "none"}
HEALTH_FILE = Path("observability") / "logs" / "job-health.json"
PAGE = Path("docs") / "run-catalog.md"


def load_cards(root: Path = ROOT) -> list[dict]:
    return [dict(yaml.safe_load(p.read_text(encoding="utf-8")) or {}, _file=p.stem)
            for p in sorted((root / "catalog").glob("*.yml"))]


def check(root: Path = ROOT) -> list[str]:
    errors, seen = [], set()
    for card in load_cards(root):
        where = f"catalog/{card['_file']}.yml"
        missing = [k for k in REQUIRED if k not in card]
        if missing:
            errors.append(f"{where}: missing {', '.join(missing)}")
            continue
        if card["id"] != card["_file"]:
            errors.append(f"{where}: id must match the file name")
        if card["kind"] not in KINDS:
            errors.append(f"{where}: kind must be one of {sorted(KINDS)}")
        if card["situation"] not in SITUATIONS:
            errors.append(f"{where}: situation must be one of {sorted(SITUATIONS)}")
        source = card["status_source"] or {}
        if source.get("type") not in SOURCES:
            errors.append(f"{where}: status_source type must be one of {sorted(SOURCES)}")
        if source.get("type") == "github_actions" and not (root / ".github" / "workflows" / str(source.get("workflow"))).is_file():
            errors.append(f"{where}: workflow {source.get('workflow')} does not exist")
        if card["situation"] == "active" and source.get("type") == "none":
            errors.append(f"{where}: an active item needs a status source, or nobody sees it break")
        if not (root / str(card["where"])).exists():
            errors.append(f"{where}: where points at {card['where']}, which does not exist")
        seen.add(str(source.get("workflow")))
    # A scheduled workflow is something that runs on its own, so it needs a card.
    for workflow in sorted((root / ".github" / "workflows").glob("*.yml")):
        if re.search(r"^\s*schedule:", workflow.read_text(encoding="utf-8"), flags=re.MULTILINE) and workflow.name not in seen:
            errors.append(f".github/workflows/{workflow.name}: runs on a schedule but has no card in catalog/")
    return errors


def render_page(root: Path = ROOT) -> str:
    lines = ["# Run catalog", "",
             "Everything that runs, generated from `catalog/*.yml` by `python tools/catalog.py page`. "
             "Do not edit by hand. Live health is in `observability/logs/job-health.json`, written by the "
             "collector, and the agent reads it with `get_map(\"jobs\")`.", "",
             "| Item | Kind | Situation | Owner | Trigger | Writes | AI | Status from |",
             "|---|---|---|---|---|---|---|---|"]
    for card in load_cards(root):
        source = card["status_source"] or {}
        origin = source.get("workflow") or source.get("pattern") or "none"
        lines.append(f"| [{card['name']}](../catalog/{card['id']}.yml) | {card['kind']} | {card['situation']} | "
                     f"{card['owner']} | {card['trigger']} | {card['writes']} | {card['ai']} | {origin} |")
    return "\n".join(lines) + "\n"


def last_github_run(workflow: str) -> dict | None:
    """The newest run of a workflow, through the gh CLI and the token of the run. None when unavailable."""
    try:
        out = subprocess.run(["gh", "run", "list", "--workflow", workflow, "--limit", "1",
                              "--json", "conclusion,status,createdAt"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    runs = json.loads(out.stdout or "[]") if out.returncode == 0 else []
    return runs[0] if runs else None


def last_log(root: Path, pattern: str) -> dict | None:
    files = sorted((root / "observability" / "logs").glob(pattern))
    if not files:
        return None
    day = re.search(r"(\d{4}-\d{2}-\d{2})", files[-1].name)
    return {"conclusion": "success", "createdAt": f"{day.group(1)}T00:00:00Z" if day else None}


def health(card: dict, root: Path, today: date, github=last_github_run) -> dict:
    """ok, failing, late or unknown, with the evidence. A manual item with no run is unknown, not failing."""
    source = card["status_source"] or {}
    run = None
    if source.get("type") == "github_actions":
        run = github(source["workflow"])
    elif source.get("type") == "log":
        run = last_log(root, source["pattern"])
    record = {"id": card["id"], "situation": card["situation"], "last_run": (run or {}).get("createdAt")}
    if card["situation"] == "stopped":
        return {**record, "status": "stopped"}
    if not run:
        return {**record, "status": "unknown", "detail": "no run found"}
    if run.get("conclusion") not in ("success", None) or run.get("status") == "failure":
        return {**record, "status": "failing", "detail": f"last run concluded {run.get('conclusion')}"}
    every = source.get("expected_every_days")
    if every and record["last_run"]:
        age = (today - datetime.fromisoformat(record["last_run"].replace("Z", "+00:00")).date()).days
        if age > every:
            return {**record, "status": "late", "detail": f"last run {age} days ago, expected every {every}"}
    return {**record, "status": "ok"}


def collect(root: Path = ROOT, today: date | None = None, github=last_github_run) -> dict:
    today = today or datetime.now(timezone.utc).date()
    return {"collected_at": today.isoformat(), "items": [health(c, root, today, github) for c in load_cards(root)]}


def main(argv: list[str]) -> int:
    command = argv[1] if len(argv) > 1 else ""
    root = Path(".")
    if command == "check":
        errors = check(root)
        for error in errors:
            print(f"ERROR {error}")
        print(f"\nChecked the run catalog: {len(errors)} errors.")
        return 1 if errors else 0
    if command == "page":
        page = render_page(root)
        if "--check" in argv:
            current = (root / PAGE).read_text(encoding="utf-8") if (root / PAGE).is_file() else ""
            if current.replace("\r\n", "\n") != page:
                print(f"{PAGE} is out of date: run python tools/catalog.py page")
                return 1
            print(f"{PAGE} is up to date.")
            return 0
        (root / PAGE).write_text(page, encoding="utf-8", newline="\n")
        print(f"wrote {PAGE}")
        return 0
    if command == "collect":
        report = collect(root)
        print(json.dumps(report, indent=2))
        if "--write" in argv:
            (root / HEALTH_FILE).parent.mkdir(parents=True, exist_ok=True)
            (root / HEALTH_FILE).write_text(json.dumps(report, indent=2), encoding="utf-8")
        if "--notify" in argv:
            sys.path.insert(0, str(ROOT / "observability"))
            from notify import send
            for item in report["items"]:
                if item["status"] in ("failing", "late"):
                    send(item["id"], f"{item['id']} is {item['status']}", [item.get("detail", "")], "--write" in argv)
        return 0
    print("usage: python tools/catalog.py check | page [--check] | collect [--write] [--notify]", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
