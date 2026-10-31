"""Deactivation after churn: switch off a churned customer's workspace and mark the company inactive.

    python automations/churn-deactivation/deactivate.py --date 2026-01-18
    python automations/churn-deactivation/deactivate.py --date 2026-01-18 --write   # needs CHURN_DEACTIVATION_ENABLED=true

Spec: automations/churn-deactivation/SPEC.md. Rules: context/rules/churn-deactivation.md.
The grace period is read from the context document. A company with another active
subscription is never deactivated. Access is switched off, nothing is deleted, and every
change goes to the movement log. Simulated: the effect is a log line.
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "automations" / "_lib"))

import movement_log  # noqa: E402
from controls import ControlsError, WriteControls  # noqa: E402


class DeactivationError(RuntimeError):
    """The run cannot continue and deactivates nothing."""


def load_rules(context_dir: Path = ROOT / "context") -> dict:
    flat = " ".join((context_dir / "rules" / "churn-deactivation.md").read_text(encoding="utf-8").split())
    grace = re.search(r"deactivated (\d+) days after its subscription ended", flat)
    if not grace:
        raise DeactivationError("churn-deactivation.md no longer states the grace period")
    return {"grace_days": int(grace.group(1))}


def read_churned(db_path: Path) -> list[dict]:
    if not db_path.is_file():
        raise DeactivationError(f"lakehouse not found at {db_path}")
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        cursor = con.execute("SELECT subscription_id, company_id, ended_at, other_active_subscriptions "
                             "FROM gold.subscription_lifecycle WHERE ended_at IS NOT NULL ORDER BY subscription_id")
        columns = [c[0] for c in cursor.description]
        return [dict(zip(columns, r)) for r in cursor.fetchall()]
    except duckdb.Error as error:
        raise DeactivationError(f"cannot read gold.subscription_lifecycle: {error}") from None
    finally:
        con.close()


def decide(rows: list[dict], rules: dict, today: date) -> list[dict]:
    out = []
    for row in rows:
        waited = (today - row["ended_at"]).days
        base = {"subscription_id": row["subscription_id"], "company_id": row["company_id"], "ended_at": row["ended_at"]}
        if row["other_active_subscriptions"] > 0:
            out.append({**base, "outcome": "keep", "why": "the company has another active subscription"})
        elif waited < rules["grace_days"]:
            out.append({**base, "outcome": "wait", "why": f"{waited} of {rules['grace_days']} grace days"})
        else:
            out.append({**base, "outcome": "deactivate", "why": f"ended {waited} days ago, past the grace period"})
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deactivate churned workspaces (dry run unless --write).")
    parser.add_argument("--db", type=Path, default=ROOT / "data" / "lakehouse.duckdb")
    parser.add_argument("--logs", type=Path, default=ROOT / "observability" / "logs")
    parser.add_argument("--date", default=date.today().isoformat(), help="today")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    try:
        controls = WriteControls("churn-deactivation", args.write)
        decisions = decide(read_churned(args.db), load_rules(), date.fromisoformat(args.date))
    except (DeactivationError, ControlsError, ValueError, OSError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    for d in decisions:
        print(f"subscription {d['subscription_id']} (company {d['company_id']}): {d['outcome']}, {d['why']}")
    if controls.mode != "write":
        print(controls.describe())
        return 0
    path = args.logs / f"movements-{args.date}.md"
    todo = {str(d["subscription_id"]): d for d in decisions if d["outcome"] == "deactivate"}

    def entries(d):
        # Two changes, one per system, keyed so a rerun replaces them instead of adding.
        return [{"key": f"deactivate-{d['subscription_id']}", "when": args.date, "who": "churn-deactivation",
                 "record": f"workspace of subscription {d['subscription_id']}", "from": "active", "to": "deactivated",
                 "why": d["why"]},
                {"key": f"inactive-{d['company_id']}", "when": args.date, "who": "churn-deactivation",
                 "record": f"company {d['company_id']}", "from": "customer", "to": "inactive", "why": d["why"]}]

    outcome = controls.apply(list(todo), lambda s: movement_log.record(path, entries(todo[s])),
                             lambda s: all(movement_log.contains(path, e) for e in entries(todo[s])))
    print(f"{controls.describe()}\n{len(outcome.applied)} deactivated, {len(outcome.needs_review)} need review")
    for s, reason in outcome.needs_review.items():
        print(f"needs review: subscription {s}, {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
