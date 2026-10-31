"""Lead routing. Spec: automations/lead-routing/SPEC.md. Rules: context/concepts/lead-routing.md.

Run from the repository root:
    python automations/lead-routing/route.py --leads leads.json            # dry run: print the plan
    python automations/lead-routing/route.py --leads leads.json --write    # also write the log file

`leads.json` is a list of lead events: {"lead_id", "company_id", "segment", "owner_id"}, where
owner_id is the company's current owner, if any. In this repository the CRM write is simulated:
the "assignment" is one line in observability/logs/lead-routing-<date>.md (ADR-0010).

The rules are read from the context document every run, so the limits and the segment-to-team
map change there and never here. The only database access is one read-only query on gold.
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

from controls import ControlsError, WriteControls  # noqa: E402
HEADER = ["# Lead routing", "", "| Lead | Outcome | Owner | Previous owner | Rule |", "|---|---|---|---|---|"]
# The context document spells segments the way people say them. The data spells them like this.
SEGMENT_WORDS = {"small business": "smb", "mid market": "mid_market", "enterprise": "enterprise"}


class RoutingError(RuntimeError):
    """The run cannot continue and assigns nothing."""


def load_rules(context_dir: Path = ROOT / "context") -> dict:
    """Capacity limits and the segment-to-team map, read from the context document's own sentences."""
    text = (context_dir / "concepts" / "lead-routing.md").read_text(encoding="utf-8")
    flat = " ".join(text.split())
    limits = re.search(r"(\d+) for the sales team and (\d+) for the enterprise team", flat)
    if not limits:
        raise RoutingError("lead-routing.md no longer states the capacity limits in the expected words")
    team_of = {}
    for subject, team in re.findall(r"([A-Z][^.]*?) (?:goes|go) to the (\w+) team\.", flat):
        for words, segment in SEGMENT_WORDS.items():
            if words in subject.lower():
                team_of[segment] = team
    if set(team_of) != set(SEGMENT_WORDS.values()):
        raise RoutingError("lead-routing.md no longer states which team each segment goes to in the expected words")
    tolerance = re.search(r"at most (\d+)% over the limit", flat)
    if not tolerance:
        raise RoutingError("lead-routing.md no longer states the continuity tolerance in the expected words")
    return {"limit": {"sales": int(limits.group(1)), "enterprise": int(limits.group(2))}, "team_of": team_of,
            "tolerance_percent": int(tolerance.group(1))}


def read_workload(db_path: Path) -> dict[str, dict]:
    """owner_id to {team, open_deals}. Stops when the table is missing or empty: nothing is assigned on a guess."""
    if not db_path.is_file():
        raise RoutingError(f"lakehouse not found at {db_path}; build it with python tools/setup.py")
    con = duckdb.connect(str(db_path), read_only=True)  # the connection itself cannot write
    try:
        rows = con.execute("SELECT owner_id, team, open_deals FROM gold.owner_workload").fetchall()
    except duckdb.Error as error:
        raise RoutingError(f"cannot read gold.owner_workload: {error}") from error
    finally:
        con.close()
    if not rows:
        raise RoutingError("gold.owner_workload is empty")
    return {str(o): {"team": t, "open_deals": int(n)} for o, t, n in rows}


def check_leads(leads) -> list[dict]:
    if not isinstance(leads, list) or not all(isinstance(lead, dict) for lead in leads):
        raise RoutingError("the leads file must be a list of lead events")
    ids = [lead.get("lead_id") for lead in leads]
    if not all(isinstance(i, str) and i.strip() for i in ids):
        raise RoutingError("every lead needs a lead_id, which is the idempotency key")
    if len(set(ids)) != len(ids):
        raise RoutingError("a lead_id appears twice in the same run")
    return leads


def _decide(lead: dict, workload: dict, open_deals: dict, rules: dict) -> tuple[str | None, str]:
    """The owner chosen (or None) and the rule that decided it."""
    if not lead.get("company_id"):
        return None, "no company; listed for cleanup"
    team = rules["team_of"].get(str(lead.get("segment") or "").strip().lower())
    if team is None:
        return None, "no segment or an unknown segment; listed for cleanup"
    limit = rules["limit"][team]
    current = lead.get("owner_id")
    if current in workload and workload[current]["team"] == team:
        # Account continuity comes first, and may pass the limit by the tolerance in the document
        # (rounded down, in whole deals). Beyond that it is a case for a person, not a hand-over to someone else.
        ceiling = limit * (100 + rules["tolerance_percent"]) // 100
        if open_deals[current] >= ceiling:
            return None, f"account owner is at the {team} ceiling of {ceiling}; a person decides"
        over = " (over the limit, within the tolerance)" if open_deals[current] >= limit else ""
        return current, "account continuity" + over
    # Fewest open deals, and a tie goes to the lowest owner_id so the same input gives the same answer.
    room = sorted((open_deals[o], o) for o, info in workload.items() if info["team"] == team and open_deals[o] < limit)
    if not room:
        return None, f"every {team} owner is at the limit of {limit}; shortage reported"
    return room[0][1], "fewest open deals"


def route(leads: list[dict], workload: dict[str, dict], rules: dict) -> list[dict]:
    """One decision per lead, in order. Each assignment counts for the next lead, so a batch is fair."""
    open_deals = {owner: info["open_deals"] for owner, info in workload.items()}
    decisions = []
    for lead in leads:
        owner, rule = _decide(lead, workload, open_deals, rules)
        if owner is not None:
            open_deals[owner] += 1
        decisions.append({"lead_id": lead["lead_id"], "outcome": "assigned" if owner else "not routed",
                          "owner_id": owner or "-", "previous_owner": lead.get("owner_id") or "none", "rule": rule})
    return decisions


def _line(d: dict) -> str:
    return f"| {d['lead_id']} | {d['outcome']} | {d['owner_id']} | {d['previous_owner']} | {d['rule']} |"


def write_log(path: Path, decisions: list[dict]) -> None:
    """One line per lead. A lead that is already in the file has its line replaced, so a second run adds nothing."""
    lines = {}
    if path.is_file():
        for row in path.read_text(encoding="utf-8").splitlines()[len(HEADER):]:
            lines[row.split("|")[1].strip()] = row
    for d in decisions:
        lines[d["lead_id"]] = _line(d)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(HEADER + list(lines.values())) + "\n", encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Route new leads (dry run unless --write).")
    parser.add_argument("--leads", type=Path, required=True, help="JSON file with the lead events")
    parser.add_argument("--db", type=Path, default=ROOT / "data" / "lakehouse.duckdb", help="DuckDB file")
    parser.add_argument("--logs", type=Path, default=ROOT / "observability" / "logs", help="where the log goes")
    parser.add_argument("--date", default=date.today().isoformat(), help="date in the log file name")
    parser.add_argument("--write", action="store_true", help="write the log file")
    args = parser.parse_args(argv)

    try:
        controls = WriteControls("lead-routing", args.write)
        leads = check_leads(json.loads(args.leads.read_text(encoding="utf-8")))
        decisions = route(leads, read_workload(args.db), load_rules())
    except (RoutingError, ControlsError, ValueError, OSError) as error:
        # Never report a failure as "all routed": say it and stop with nothing assigned.
        print(f"ERROR {error}", file=sys.stderr)
        return 1

    print("\n".join(HEADER + [_line(d) for d in decisions]))
    unrouted = sum(d["outcome"] == "not routed" for d in decisions)
    print(f"\n{len(decisions) - unrouted} assigned, {unrouted} not routed.")
    if controls.mode != "write":
        print(controls.describe())
        return 0
    path = args.logs / f"lead-routing-{args.date}.md"
    # Leads that were not routed are a review list, a report and not a CRM write.
    write_log(path, [d for d in decisions if d["outcome"] != "assigned"])
    # Each assignment is the simulated CRM write, so it goes through the controls one by one.
    assigned = {d["lead_id"]: d for d in decisions if d["outcome"] == "assigned"}
    outcome = controls.apply(list(assigned), write_one=lambda lead: write_log(path, [assigned[lead]]),
                             read_back=lambda lead: _line(assigned[lead]) in path.read_text(encoding="utf-8"))
    for lead, reason in outcome.needs_review.items():
        write_log(path, [{**assigned[lead], "outcome": "needs review", "owner_id": "-", "rule": reason}])
    print(f"{controls.describe()}\nwrote {path}: {len(outcome.applied)} assigned, "
          f"{len(outcome.needs_review)} need review")
    return 0


if __name__ == "__main__":
    sys.exit(main())
