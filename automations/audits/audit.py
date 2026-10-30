"""Weekly data-quality audit. Spec: automations/audits/SPEC.md.

Run from the repository root:
    python automations/audits/audit.py            # dry run: print the report
    python automations/audits/audit.py --write    # also write observability/logs/audit-<date>.md

It reads one gold table, read-only, and never changes any record.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import duckdb

# (label, column with the flagged count, column with the total)
FLAGS = [
    ("Possible duplicate companies", "possible_duplicate_companies", "companies"),
    ("Deals without a company", "deals_without_company", "deals"),
    ("Subscriptions without a deal", "subscriptions_without_deal", "subscriptions"),
    ("Closed won deals without a subscription", "closed_won_without_subscription", "closed_won_deals"),
]
# The counts are stored inside the report, so the next run can compare without a database.
COUNTS_LINE = re.compile(r"<!-- counts: (\{.*\}) -->")


def read_snapshot(db_path: Path) -> dict:
    """Return the single snapshot row as a dict. Raises RuntimeError with a clear message."""
    if not db_path.is_file():
        raise RuntimeError(f"lakehouse not found at {db_path}; build it with python tools/setup.py")
    # read_only=True: the connection itself cannot write, whatever this script does.
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        cursor = con.execute("SELECT * FROM gold.data_quality_snapshot")
        columns = [c[0] for c in cursor.description]
        rows = cursor.fetchall()
    except duckdb.Error as error:
        raise RuntimeError(f"cannot read gold.data_quality_snapshot: {error}") from error
    finally:
        con.close()
    if len(rows) != 1:
        raise RuntimeError(f"gold.data_quality_snapshot should have one row, it has {len(rows)}")
    return dict(zip(columns, rows[0]))


def previous_counts(logs: Path, as_of: str) -> dict | None:
    """Counts from the newest report dated before as_of, or None if there is none."""
    earlier = sorted(p for p in logs.glob("audit-*.md") if p.stem.removeprefix("audit-") < as_of)
    if not earlier:
        return None
    match = COUNTS_LINE.search(earlier[-1].read_text(encoding="utf-8"))
    return json.loads(match.group(1)) if match else None


def build_report(snapshot: dict, previous: dict | None) -> tuple[str, list[str]]:
    """Return the report text and the labels of the flags that rose since the last report."""
    as_of = str(snapshot["as_of"])
    raised = []
    lines = [f"# Data-quality audit, data as of {as_of}", "",
             "| Flag | Count | Of | Share | Change |", "|---|---|---|---|---|"]
    for label, column, total_column in FLAGS:
        count, total = snapshot[column], snapshot[total_column]
        share = f"{count / total:.1%}" if total else "n/a"
        if previous is None or column not in previous:
            change = "first report"
        else:
            delta = count - previous[column]
            change = f"{delta:+d}"
            if delta > 0:
                raised.append(label)
        lines.append(f"| {label} | {count} | {total} | {share} | {change} |")
    lines.append("")
    if raised:
        lines.append("**Attention, higher than the last report:** " + ", ".join(raised) + ".")
    else:
        lines.append("Nothing rose since the last report.")
    lines += ["",
              "Closed won deals without a subscription include deals won in the last two weeks, so a small number is normal.",
              "What each flag means and who fixes it: context/concepts/cross-cutting-rules.md.", "",
              "<!-- counts: " + json.dumps({column: snapshot[column] for _, column, _ in FLAGS}) + " -->", ""]
    return "\n".join(lines), raised


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Weekly data-quality audit (dry run unless --write).")
    parser.add_argument("--db", type=Path, default=Path("data/lakehouse.duckdb"), help="DuckDB file")
    parser.add_argument("--logs", type=Path, default=Path("observability/logs"), help="where reports go")
    parser.add_argument("--write", action="store_true", help="write the report file")
    args = parser.parse_args(argv)

    try:
        snapshot = read_snapshot(args.db)
    except RuntimeError as error:
        # Never report a failure as "no problems": say it and stop.
        print(f"ERROR {error}", file=sys.stderr)
        return 1

    report, _ = build_report(snapshot, previous_counts(args.logs, str(snapshot["as_of"])))
    print(report)
    if args.write:
        args.logs.mkdir(parents=True, exist_ok=True)
        # One file per data date: running twice overwrites it, so nothing is duplicated.
        path = args.logs / f"audit-{snapshot['as_of']}.md"
        path.write_text(report, encoding="utf-8", newline="\n")
        print(f"wrote {path}")
    else:
        print("dry run: nothing written (use --write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
