"""Weekly reconciliation of won deals (CRM) against subscriptions (billing).

    python automations/reconciliation/reconcile.py              # dry run: print the report
    python automations/reconciliation/reconcile.py --write      # also write the report and alert

Spec: automations/reconciliation/SPEC.md. Standard: docs/standards/audits.md.
It reads one gold list matched on the deal id the subscription carries, sorts every record
into a divergence, a pending item or a known case, names who corrects it, and proposes the
correction. It never corrects anything. The tolerance and the wait are read from the context
documents at run time, so changing a rule never needs a code change.
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "observability"))

NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4}
# Who corrects each class: the team that owns the source to be corrected (cross-cutting-rules).
OWNER = {"amount differs": "Finance (billing is the source of truth for revenue)",
         "won without subscription": "Finance, with Customer Success for the kickoff",
         "subscription without deal": "Sales, to create or link the deal in the CRM"}


class ReconciliationError(RuntimeError):
    """The run cannot continue; nothing is reported as reconciled."""


def load_rules(context_dir: Path = ROOT / "context") -> dict:
    flat_rules = " ".join((context_dir / "concepts" / "cross-cutting-rules.md").read_text(encoding="utf-8").split())
    flat_prov = " ".join((context_dir / "concepts" / "closed-won-provisioning.md").read_text(encoding="utf-8").split())
    tolerance = re.search(r"divided by 12, within (\d+) dollars? a month", flat_rules)
    wait = re.search(r"starts within (\w+) weeks of the win", flat_prov)
    if not tolerance or not wait or wait.group(1) not in NUMBER_WORDS:
        raise ReconciliationError("the context documents no longer state the tolerance or the wait in the expected words")
    return {"tolerance_usd": int(tolerance.group(1)), "wait_days": NUMBER_WORDS[wait.group(1)] * 7}


def read_gold(db_path: Path) -> tuple[date, list[dict]]:
    if not db_path.is_file():
        raise ReconciliationError(f"lakehouse not found at {db_path}")
    con = duckdb.connect(str(db_path), read_only=True)  # the connection itself cannot write
    try:
        as_of = con.execute("SELECT as_of FROM gold.data_quality_snapshot").fetchone()[0]
        cursor = con.execute("SELECT * FROM gold.deal_subscription_reconciliation ORDER BY deal_id")
        columns = [c[0] for c in cursor.description]
        rows = [dict(zip(columns, r)) for r in cursor.fetchall()]
    except duckdb.Error as error:
        raise ReconciliationError(f"cannot read the gold tables: {error}") from None
    finally:
        con.close()
    return as_of, rows


def classify(row: dict, rules: dict, as_of: date) -> tuple[str, str, str] | None:
    """(destination, class, proposal) for a record, or None when it matches. One class per record, in order."""
    status = row["match_status"]
    if status == "subscription_without_deal":
        # Billing wins: the revenue counts. Documented in cross-cutting-rules, so a known case.
        return "known case", "subscription without deal", f"link subscription {row['subscription_id']} to a deal in the CRM"
    if status == "won_without_subscription":
        waited = (as_of - row["closed_at"]).days if row["closed_at"] else None
        if waited is not None and waited <= rules["wait_days"]:
            return "pending", "won without subscription", f"expected within {rules['wait_days']} days of the win ({waited} so far)"
        return "divergence", "won without subscription", f"start the subscription for deal {row['deal_id']}, or reopen the deal"
    gap = row["monthly_gap_usd"] or 0
    if abs(gap) > rules["tolerance_usd"]:
        return "divergence", "amount differs", f"align deal {row['deal_id']}: monthly gap of {gap:+,.2f} dollars"
    return None


def build_report(as_of: date, rows: list[dict], rules: dict) -> tuple[str, list[dict]]:
    found = []
    for row in rows:
        result = classify(row, rules, as_of)
        if result:
            destination, kind, proposal = result
            found.append({"deal_id": row["deal_id"], "destination": destination, "class": kind,
                          "owner": OWNER[kind], "proposal": proposal})
    matched = sum(r["match_status"] == "matched" for r in rows)
    lines = [f"# Reconciliation of won deals and subscriptions, data as of {as_of}", "",
             f"Scope: every closed won deal and every subscription. Join key: the deal id the subscription carries. "
             f"Coverage: {matched} of {len(rows)} records matched. Tolerance: {rules['tolerance_usd']} dollar a month. "
             f"Wait for a subscription: {rules['wait_days']} days.", ""]
    for destination in ("divergence", "pending", "known case"):
        items = [f for f in found if f["destination"] == destination]
        lines += [f"## {destination.capitalize()} ({len(items)})", ""]
        if items:
            lines += ["| Deal | Class | Owner | Proposal |", "|---|---|---|---|"]
            lines += [f"| {f['deal_id']} | {f['class']} | {f['owner']} | {f['proposal']} |" for f in items]
        else:
            lines.append("None.")
        lines.append("")
    lines.append("This is a proposal. Nothing was corrected; each item is fixed by its owner, and the next run shows whether it left the list.")
    return "\n".join(lines) + "\n", found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reconcile won deals and subscriptions (dry run unless --write).")
    parser.add_argument("--db", type=Path, default=ROOT / "data" / "lakehouse.duckdb")
    parser.add_argument("--logs", type=Path, default=ROOT / "observability" / "logs")
    parser.add_argument("--write", action="store_true", help="write the report and send the alert")
    args = parser.parse_args(argv)
    try:
        rules = load_rules()
        as_of, rows = read_gold(args.db)
    except ReconciliationError as error:
        print(f"ERROR {error}", file=sys.stderr)  # never "all reconciled" after a failure
        return 1
    report, found = build_report(as_of, rows, rules)
    print(report)
    if not args.write:
        print("dry run: nothing written (use --write)")
        return 0
    args.logs.mkdir(parents=True, exist_ok=True)
    path = args.logs / f"reconciliation-{as_of}.md"
    path.write_text(report, encoding="utf-8", newline="\n")  # one file per data date: a rerun overwrites it
    print(f"wrote {path}")
    divergences = [f for f in found if f["destination"] == "divergence"]
    if divergences:
        from notify import send
        lines = [f"{f['deal_id']}: {f['class']}, owner {f['owner'].split(' (')[0]}" for f in divergences[:5]]
        result = send("reconciliation", f"{len(divergences)} deal(s) do not match billing (data as of {as_of})",
                      lines, write=True, logs=args.logs)
        print(f"alert: {result['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
