"""Onboarding auto-advance: move a subscription's milestone when the product reports the evidence.

    python automations/onboarding-advance/advance.py --events automations/onboarding-advance/examples/events.json
    python automations/onboarding-advance/advance.py --events events.json --write   # needs ONBOARDING_ADVANCE_ENABLED=true

Spec: automations/onboarding-advance/SPEC.md. Rules: context/rules/onboarding-milestones.md.
Which event moves which milestone is read from the context document at run time. A move
that does not fit the current milestone is never applied: it goes to the review list.
Every applied move is written to the movement log.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "automations" / "_lib"))

import movement_log  # noqa: E402
from controls import ControlsError, WriteControls  # noqa: E402

ORDER = ["not_started", "kickoff", "configured", "go_live"]


class AdvanceError(RuntimeError):
    """The run cannot continue and moves nothing."""


def load_rules(context_dir: Path = ROOT / "context") -> dict[str, tuple[str, str]]:
    """event -> (from milestone, to milestone), from the sentences of the context document."""
    flat = " ".join((context_dir / "rules" / "onboarding-milestones.md").read_text(encoding="utf-8").split())
    moves = re.findall(r"The product event `([a-z_]+)` moves a subscription from (\w+) to (\w+)\.", flat)
    if not moves:
        raise AdvanceError("onboarding-milestones.md no longer states which event moves which milestone")
    return {event: (start, end) for event, start, end in moves}


def read_progress(db_path: Path) -> dict[str, str]:
    if not db_path.is_file():
        raise AdvanceError(f"lakehouse not found at {db_path}")
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        rows = con.execute("SELECT subscription_id, current_milestone FROM gold.onboarding_progress").fetchall()
    except duckdb.Error as error:
        raise AdvanceError(f"cannot read gold.onboarding_progress: {error}") from None
    finally:
        con.close()
    return {str(s): m for s, m in rows}


def check_events(events) -> list[dict]:
    if not isinstance(events, list) or not all(isinstance(e, dict) for e in events):
        raise AdvanceError("the events file must be a list of events")
    ids = [e.get("event_id") for e in events]
    if not all(isinstance(i, str) and i for i in ids) or len(set(ids)) != len(ids):
        raise AdvanceError("every event needs a unique event_id, which is the idempotency key")
    return events


def decide(events: list[dict], progress: dict[str, str], rules: dict) -> list[dict]:
    """One decision per event, in order; a move counts for the next event of the same subscription."""
    current = dict(progress)
    decisions = []
    for event in events:
        sub = str(event.get("subscription_id"))
        rule = rules.get(event.get("event"))
        base = {"event_id": event["event_id"], "subscription_id": sub, "event": event.get("event"),
                "at": event.get("at") or "", "from": current.get(sub, "unknown")}
        if sub not in current:
            decisions.append({**base, "outcome": "needs review", "to": "-", "why": "unknown subscription"})
        elif rule is None:
            decisions.append({**base, "outcome": "needs review", "to": "-", "why": "event does not move a milestone"})
        elif current[sub] != rule[0]:
            decisions.append({**base, "outcome": "needs review", "to": "-",
                              "why": f"expected {rule[0]} before {rule[1]}; never skipped or moved back"})
        else:
            decisions.append({**base, "outcome": "advance", "to": rule[1], "why": f"product event {event['event']}"})
            current[sub] = rule[1]
    return decisions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Advance onboarding milestones (dry run unless --write).")
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--db", type=Path, default=ROOT / "data" / "lakehouse.duckdb")
    parser.add_argument("--logs", type=Path, default=ROOT / "observability" / "logs")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    try:
        controls = WriteControls("onboarding-advance", args.write)
        decisions = decide(check_events(json.loads(args.events.read_text(encoding="utf-8"))),
                           read_progress(args.db), load_rules())
    except (AdvanceError, ControlsError, ValueError, OSError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    for d in decisions:
        print(f"{d['event_id']}: {d['outcome']} subscription {d['subscription_id']} {d['from']} -> {d['to']} ({d['why']})")
    if controls.mode != "write":
        print(controls.describe())
        return 0
    path = args.logs / f"movements-{args.date}.md"
    moves = {d["event_id"]: d for d in decisions if d["outcome"] == "advance"}

    def entry(d):
        return {"key": d["event_id"], "when": d["at"], "who": "onboarding-advance", "record": f"subscription {d['subscription_id']}",
                "from": d["from"], "to": d["to"], "why": d["why"]}

    outcome = controls.apply(list(moves), lambda e: movement_log.record(path, [entry(moves[e])]),
                             lambda e: movement_log.contains(path, entry(moves[e])))
    review = [d for d in decisions if d["outcome"] != "advance"] + [
        {**moves[e], "why": reason} for e, reason in outcome.needs_review.items()]
    (args.logs / f"onboarding-review-{args.date}.md").write_text(
        "# Onboarding events for review\n\n" + "\n".join(f"- {d['event_id']}: subscription {d['subscription_id']}, {d['why']}" for d in review) + "\n",
        encoding="utf-8", newline="\n")
    print(f"{controls.describe()}\n{len(outcome.applied)} advanced, {len(review)} for review")
    return 0


if __name__ == "__main__":
    sys.exit(main())
