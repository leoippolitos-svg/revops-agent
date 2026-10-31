"""Closed won provisioning. Spec: automations/closed-won-provisioning/SPEC.md.
Rules: context/concepts/closed-won-provisioning.md.

Run from the repository root:
    python automations/closed-won-provisioning/provision.py --deals deals.json            # dry run
    python automations/closed-won-provisioning/provision.py --deals deals.json --write    # write the log

`deals.json` is one deal event or a list of them:
    {"deal_id", "stage", "company_id", "company_is_possible_duplicate", "has_subscription", "closed_won_at"}
`closed_won_at` (YYYY-MM-DD) is optional and only used to flag a missing subscription after two weeks.

In this repository the product call is simulated: a "requested" outcome is one line in
observability/logs/provisioning-<date>.md (ADR-0011). Nothing is sent to the customer, no plan or
price is set, and the only database access is one read-only query on a gold snapshot.
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
HEADER = ["# Closed won provisioning", "", "| Deal | Outcome | Reason |", "|---|---|---|"]
NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4}


class ProvisioningError(RuntimeError):
    """The run cannot continue and requests nothing."""


def load_rules(context_dir: Path = ROOT / "context") -> dict:
    """The two-week wait and the one milestone requested, read from the context document's sentences."""
    flat = " ".join((context_dir / "concepts" / "closed-won-provisioning.md").read_text(encoding="utf-8").split())
    wait = re.search(r"starts within (\w+) weeks of the win", flat)
    milestone = re.search(r"Provisioning only requests the (\w+)\.", flat)
    cutoff = re.search(r"A deal won more than (\d+) days ago is never provisioned automatically", flat)
    if not wait or wait.group(1) not in NUMBER_WORDS or not milestone or not cutoff:
        raise ProvisioningError("closed-won-provisioning.md no longer states the wait, the milestone or the "
                                "cutoff in the expected words")
    return {"wait_days": NUMBER_WORDS[wait.group(1)] * 7, "milestone": milestone.group(1),
            "cutoff_days": int(cutoff.group(1))}


def read_backlog(db_path: Path) -> int | None:
    """Size of the closed won backlog without a subscription, or None when it cannot be read.
    A missing snapshot does not stop the run: the deal can still be handled, and the report says so."""
    if not db_path.is_file():
        return None
    con = duckdb.connect(str(db_path), read_only=True)  # the connection itself cannot write
    try:
        row = con.execute("SELECT closed_won_without_subscription FROM gold.data_quality_snapshot").fetchone()
    except duckdb.Error:
        return None
    finally:
        con.close()
    return int(row[0]) if row else None


def check_deals(deals) -> list[dict]:
    deals = [deals] if isinstance(deals, dict) else deals
    if not isinstance(deals, list) or not all(isinstance(d, dict) for d in deals):
        raise ProvisioningError("the deals file must be one deal event or a list of them")
    ids = [d.get("deal_id") for d in deals]
    if not all(isinstance(i, str) and i.strip() for i in ids):
        raise ProvisioningError("every deal event needs a deal_id, which is the idempotency key")
    if len(set(ids)) != len(ids):
        raise ProvisioningError("a deal_id appears twice in the same run")
    return deals


def decide(deal: dict, rules: dict, today: date) -> tuple[str, str]:
    """The outcome (requested, skipped, held or needs review) and the reason, in the order the document lists them.

    "skipped" is only for a deal the rules say needs nothing; a deal that cannot be handled
    is "needs review", so it is an alert and not silence (writeback-rules)."""
    if deal.get("stage") != "closed_won":
        return "skipped", "not in closed_won"
    if not deal.get("company_id"):
        return "needs review", "no company; listed for the owner to fix"
    if deal.get("company_is_possible_duplicate"):
        return "held", "company is a possible duplicate; a person confirms it first"
    if deal.get("has_subscription"):
        return "skipped", "already has a subscription"
    reason = f"{rules['milestone']} requested"
    won = deal.get("closed_won_at")
    if won:
        try:
            waited = (today - date.fromisoformat(won)).days
        except (TypeError, ValueError):
            raise ProvisioningError(f"closed_won_at of {deal['deal_id']} must be a date like 2026-01-09") from None
        if waited > rules["cutoff_days"]:
            return "needs review", f"won more than {rules['cutoff_days']} days ago; never back-filled automatically"
        if waited > rules["wait_days"]:
            reason += f"; no subscription after {rules['wait_days']} days, listed for Finance"
    return "requested", reason


def run(deals: list[dict], rules: dict, today: date) -> list[dict]:
    return [{"deal_id": d["deal_id"], **dict(zip(("outcome", "reason"), decide(d, rules, today)))} for d in deals]


def _line(d: dict) -> str:
    return f"| {d['deal_id']} | {d['outcome']} | {d['reason']} |"


def write_log(path: Path, results: list[dict]) -> None:
    """One line per deal. A deal already in the file has its line replaced, so a second run adds nothing."""
    lines = {}
    if path.is_file():
        for row in path.read_text(encoding="utf-8").splitlines()[len(HEADER):]:
            lines[row.split("|")[1].strip()] = row
    for r in results:
        lines[r["deal_id"]] = _line(r)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(HEADER + list(lines.values())) + "\n", encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Provision closed won deals (dry run unless --write).")
    parser.add_argument("--deals", type=Path, required=True, help="JSON file with the deal event(s)")
    parser.add_argument("--db", type=Path, default=ROOT / "data" / "lakehouse.duckdb", help="DuckDB file")
    parser.add_argument("--logs", type=Path, default=ROOT / "observability" / "logs", help="where the log goes")
    parser.add_argument("--date", default=date.today().isoformat(), help="today, also used in the log file name")
    parser.add_argument("--write", action="store_true", help="write the log file")
    args = parser.parse_args(argv)

    try:
        controls = WriteControls("closed-won-provisioning", args.write)
        today = date.fromisoformat(args.date)
        deals = check_deals(json.loads(args.deals.read_text(encoding="utf-8")))
        results = run(deals, load_rules(), today)
    except (ProvisioningError, ControlsError, ValueError, OSError) as error:
        # Never report a failure as "provisioned": say it and stop with nothing requested.
        print(f"ERROR {error}", file=sys.stderr)
        return 1

    print("\n".join(HEADER + [_line(r) for r in results]))
    counts = {o: sum(r["outcome"] == o for r in results) for o in ("requested", "skipped", "held", "needs review")}
    print(f"\n{counts['requested']} requested, {counts['skipped']} skipped, {counts['held']} held, "
          f"{counts['needs review']} need review.")
    backlog = read_backlog(args.db)
    print("Closed won backlog without a subscription: " + (str(backlog) if backlog is not None else "unavailable") + ".")
    if controls.mode != "write":
        print(controls.describe())
        return 0
    path = args.logs / f"provisioning-{args.date}.md"
    write_log(path, [r for r in results if r["outcome"] != "requested"])  # a report, not a product write
    requested = {r["deal_id"]: r for r in results if r["outcome"] == "requested"}
    outcome = controls.apply(list(requested), write_one=lambda deal: write_log(path, [requested[deal]]),
                             read_back=lambda deal: _line(requested[deal]) in path.read_text(encoding="utf-8"))
    for deal, reason in outcome.needs_review.items():
        write_log(path, [{**requested[deal], "outcome": "needs review", "reason": reason}])
    print(f"{controls.describe()}\nwrote {path}: {len(outcome.applied)} requested, "
          f"{len(outcome.needs_review)} need review")
    return 0


if __name__ == "__main__":
    sys.exit(main())
