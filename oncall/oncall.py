"""The on-call agent's two steps without AI: list the problems, then execute what is allowed.

    python oncall/oncall.py problems --out oncall-run/        # step 1: no model
    python oncall/oncall.py execute --dir oncall-run/ [--write]  # step 3: no model

Step 2, between them, is the agent (oncall/prompt.md), run by the workflow only when a
problem exists, the kill switch ONCALL_AGENT_ENABLED is true and a key is set. A collection
with no problem never calls a model. ADR-0021.

The executor trusts nothing in the agent's report:
- the only action type is `rerun`, and only for a workflow whose card says `rerun_ok: true`
  (a job that reads or syncs idempotently); anything else is refused and needs review;
- reruns go through the write controls (`oncall-actions`: kill switch, cap, breaker);
- every item gets one message in its own Slack thread: the cause, what was done, the
  pull request, the human step.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "automations" / "_lib"))
sys.path.insert(0, str(ROOT / "observability"))

import catalog  # noqa: E402
from controls import ControlsError, WriteControls  # noqa: E402
from notify import send  # noqa: E402

HEALTH = ROOT / catalog.HEALTH_FILE
ALLOWED_ACTIONS = {"rerun"}
REPORT_FIELDS = ("id", "cause", "resolved", "what_i_did", "pr_url", "actions", "human_step")


def problems(health: dict, root: Path = ROOT) -> list[dict]:
    """Items of the last collection that are failing or late, each with its card."""
    cards = {c["id"]: c for c in catalog.load_cards(root)}
    found = []
    for item in health.get("items", []):
        if item.get("status") in ("failing", "late") and item["id"] in cards:
            card = {k: v for k, v in cards[item["id"]].items() if not k.startswith("_")}
            found.append({**item, "card": card})
    return found


def check_report(report, problem_ids: set[str]) -> tuple[list[dict], list[str]]:
    """Keep only well-formed entries for known problems; say what was dropped and why."""
    kept, dropped = [], []
    if not isinstance(report, list):
        return [], ["the report is not a list"]
    for entry in report:
        if not isinstance(entry, dict) or any(f not in entry for f in REPORT_FIELDS):
            dropped.append(f"malformed entry: {str(entry)[:80]}")
        elif entry["id"] not in problem_ids:
            dropped.append(f"{entry['id']}: not one of this run's problems")
        else:
            kept.append(entry)
    for missing in sorted(problem_ids - {e["id"] for e in kept}):
        kept.append({"id": missing, "cause": "the agent did not report on this item", "resolved": False,
                     "what_i_did": "", "pr_url": "", "actions": [], "human_step": "read the run log of this item"})
    return kept, dropped


def allowed_reruns(entry: dict, cards: dict) -> tuple[list[str], list[str]]:
    """The workflows this entry may rerun, and the refused actions with the reason."""
    ok, refused = [], []
    card = cards.get(entry["id"], {})
    for action in entry.get("actions") or []:
        kind = (action or {}).get("type")
        workflow = (action or {}).get("workflow")
        if kind not in ALLOWED_ACTIONS:
            refused.append(f"action {kind!r} is not on the closed list")
        elif not card.get("rerun_ok") or (card.get("status_source") or {}).get("workflow") != workflow:
            refused.append(f"rerun of {workflow!r} is not allowed for {entry['id']}")
        else:
            ok.append(workflow)
    return ok, refused


def gh_rerun(workflow: str) -> None:
    result = subprocess.run(["gh", "workflow", "run", workflow], capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip()[:200] or "gh workflow run failed")


def execute(report: list[dict], write: bool, root: Path = ROOT, runner=gh_rerun, notifier=send,
            env: dict | None = None) -> list[dict]:
    cards = {c["id"]: c for c in catalog.load_cards(root)}
    controls = WriteControls("oncall-actions", write, env=env)
    results = []
    for entry in report:
        reruns, refused = allowed_reruns(entry, cards)
        outcome = controls.apply(reruns, runner, lambda wf: True)
        lines = [f"Cause: {entry['cause']}"]
        if entry.get("what_i_did"):
            lines.append(f"Done: {entry['what_i_did']}")
        if entry.get("pr_url"):
            lines.append(f"Pull request: {entry['pr_url']}")
        lines += [f"Rerun requested: {wf}" for wf in outcome.applied]
        lines += [f"Needs review: {reason}" for reason in list(outcome.needs_review.values()) + refused]
        if controls.mode != "write" and reruns:
            lines.append(f"Rerun not run ({controls.mode}): {', '.join(reruns)}")
        if entry.get("human_step"):
            lines.append(f"Person: {entry['human_step']}")
        title = f"{entry['id']}: {'resolved' if entry.get('resolved') else 'needs attention'}"
        sent = notifier(entry["id"], title, lines, write, env=env) if env is not None else notifier(entry["id"], title, lines, write)
        results.append({"id": entry["id"], "reruns": outcome.applied, "refused": refused, "alert": sent["status"]})
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="On-call steps without AI.")
    parser.add_argument("step", choices=["problems", "execute"])
    parser.add_argument("--out", type=Path, default=Path("oncall-run"))
    parser.add_argument("--dir", type=Path, default=Path("oncall-run"))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.step == "problems":
            health = json.loads(HEALTH.read_text(encoding="utf-8")) if HEALTH.is_file() else {"items": []}
            found = problems(health)
            args.out.mkdir(parents=True, exist_ok=True)
            (args.out / "problems.json").write_text(json.dumps(found, indent=2), encoding="utf-8")
            print(f"{len(found)} problem(s)" + ("" if found else ": no model call needed"))
            return 0
        found = json.loads((args.dir / "problems.json").read_text(encoding="utf-8"))
        report_path = args.dir / "report.json"
        raw = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else []
        report, dropped = check_report(raw, {p["id"] for p in found})
        for reason in dropped:
            print(f"dropped from the report: {reason}")
        print(json.dumps(execute(report, args.write), indent=2))
        return 0
    except (ControlsError, ValueError, OSError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
