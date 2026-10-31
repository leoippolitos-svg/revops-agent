"""Deal amount recalculation: when a discount changes, propose the new net amount for approval.

    python automations/deal-amount/recalculate.py --events automations/deal-amount/examples/events.json
    python automations/deal-amount/recalculate.py --events events.json --write   # writes the proposals file

Spec: automations/deal-amount/SPEC.md. Rules: context/rules/deal-discount.md.
The amount is a sensitive field, so this automation never writes it: it writes proposals,
each approved item by item by Finance (and by the sales lead above the discount limit).
The limit and the tolerance are read from the context document at run time.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
OPEN_STAGES = ("qualification", "discovery", "proposal", "negotiation")


class AmountError(RuntimeError):
    """The run cannot continue and proposes nothing."""


def load_rules(context_dir: Path = ROOT / "context") -> dict:
    flat = " ".join((context_dir / "rules" / "deal-discount.md").read_text(encoding="utf-8").split())
    tolerance = re.search(r"A difference under (\d+) dollars? is not a change", flat)
    limit = re.search(r"A discount above (\d+) percent also needs the approval of the sales lead", flat)
    if not tolerance or not limit:
        raise AmountError("deal-discount.md no longer states the tolerance or the discount limit")
    return {"tolerance_usd": int(tolerance.group(1)), "discount_limit": int(limit.group(1))}


def read_deals(db_path: Path) -> dict[str, dict]:
    if not db_path.is_file():
        raise AmountError(f"lakehouse not found at {db_path}")
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        rows = con.execute("SELECT deal_id, stage, amount_usd FROM gold.deal_amount").fetchall()
    except duckdb.Error as error:
        raise AmountError(f"cannot read gold.deal_amount: {error}") from None
    finally:
        con.close()
    return {str(d): {"stage": s, "amount_usd": a} for d, s, a in rows}


def check_events(events) -> list[dict]:
    if not isinstance(events, list) or not all(isinstance(e, dict) for e in events):
        raise AmountError("the events file must be a list of discount changes")
    for event in events:
        if not isinstance(event.get("list_amount_usd"), (int, float)) or event["list_amount_usd"] <= 0:
            raise AmountError(f"event {event.get('event_id')}: list_amount_usd must be a positive number")
        if not isinstance(event.get("discount_percent"), (int, float)) or not 0 <= event["discount_percent"] < 100:
            raise AmountError(f"event {event.get('event_id')}: discount_percent must be from 0 to under 100")
    return events


def propose(events: list[dict], deals: dict, rules: dict) -> list[dict]:
    out = []
    for event in events:
        deal = deals.get(str(event.get("deal_id")))
        net = round(event["list_amount_usd"] * (1 - event["discount_percent"] / 100))
        base = {"event_id": event.get("event_id"), "deal_id": event.get("deal_id"), "net_usd": net}
        if deal is None:
            out.append({**base, "outcome": "needs review", "why": "unknown deal"})
        elif deal["stage"] not in OPEN_STAGES:
            out.append({**base, "outcome": "no change", "why": f"deal is {deal['stage']}; a closed amount is history"})
        elif abs((deal["amount_usd"] or 0) - net) < rules["tolerance_usd"]:
            out.append({**base, "outcome": "no change", "why": "the amount already matches"})
        else:
            approvers = "Finance" + (" and the sales lead" if event["discount_percent"] > rules["discount_limit"] else "")
            out.append({**base, "outcome": "proposed", "current_usd": deal["amount_usd"],
                        "why": f"{event['discount_percent']}% off {event['list_amount_usd']:,}; approve: {approvers}"})
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Propose deal amounts after a discount change (dry run unless --write).")
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--db", type=Path, default=ROOT / "data" / "lakehouse.duckdb")
    parser.add_argument("--logs", type=Path, default=ROOT / "observability" / "logs")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--write", action="store_true", help="write the proposals file")
    args = parser.parse_args(argv)
    try:
        results = propose(check_events(json.loads(args.events.read_text(encoding="utf-8"))),
                          read_deals(args.db), load_rules())
    except (AmountError, ValueError, OSError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    lines = ["# Deal amount proposals", "", "Status of each line: proposed, waiting for approval item by item. "
             "Nothing was written to the CRM.", "", "| Event | Deal | Outcome | Current | Proposed | Why |", "|---|---|---|---|---|---|"]
    lines += [f"| {r['event_id']} | {r['deal_id']} | {r['outcome']} | {r.get('current_usd', '-')} | {r['net_usd']} | {r['why']} |"
              for r in results]
    report = "\n".join(lines) + "\n"
    print(report)
    if args.write:
        args.logs.mkdir(parents=True, exist_ok=True)
        path = args.logs / f"amount-proposals-{args.date}.md"
        path.write_text(report, encoding="utf-8", newline="\n")  # one file per day: a rerun overwrites it
        print(f"wrote {path}")
    else:
        print("dry run: nothing written (use --write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
