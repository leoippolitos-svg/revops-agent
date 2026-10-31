"""Watchdog: when a scheduled job did not run, try to recover before alerting anyone.

    python oncall/watchdog.py [--write]

For every active card with an expected interval, it reads the last run. A job that is late
and whose card says `rerun_ok: true` is started again (`gh workflow run`), through the write
controls (`watchdog-recovery`: kill switch WATCHDOG_RECOVERY_ENABLED, set in CI from the repository
variable WATCHDOG_ENABLED; cap; breaker). A Slack alert
goes out only when recovery is not allowed or did not start. Silence means it was fine or
it recovered; an alert means a person is needed. ADR-0021.
"""

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "automations" / "_lib"))
sys.path.insert(0, str(ROOT / "observability"))
sys.path.insert(0, str(ROOT / "oncall"))

import catalog  # noqa: E402
from controls import ControlsError, WriteControls  # noqa: E402
from notify import send  # noqa: E402
from oncall import gh_rerun  # noqa: E402


def watch(write: bool, root: Path = ROOT, today: date | None = None, github=catalog.last_github_run,
          runner=gh_rerun, notifier=send, env: dict | None = None) -> list[dict]:
    today = today or datetime.now(timezone.utc).date()
    cards = {c["id"]: c for c in catalog.load_cards(root)}
    late = [h for h in catalog.collect(root, today, github)["items"]
            if h["status"] == "late" and cards[h["id"]]["situation"] == "active"]
    controls = WriteControls("watchdog-recovery", write, env=env)
    recoverable = {cards[h["id"]]["status_source"]["workflow"]: h for h in late if cards[h["id"]].get("rerun_ok")}
    outcome = controls.apply(list(recoverable), runner, lambda wf: True)
    results = []
    for item in late:
        workflow = cards[item["id"]]["status_source"].get("workflow")
        if workflow in outcome.applied:
            results.append({"id": item["id"], "action": "rerun started", "alert": None})
            continue
        reason = outcome.needs_review.get(workflow) or (
            f"recovery not run ({controls.mode})" if workflow in recoverable else "the card does not allow a rerun")
        lines = [item.get("detail", "late"), f"Recovery: {reason}"]
        kwargs = {"env": env} if env is not None else {}
        sent = notifier(item["id"], f"{item['id']} did not run and was not recovered", lines, write, **kwargs)
        results.append({"id": item["id"], "action": reason, "alert": sent["status"]})
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Recover late jobs, alert only when recovery fails.")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(watch(args.write), indent=2))
    except (ControlsError, OSError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
