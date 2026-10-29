"""Compare today's bronze batch with yesterday's and flag what looks wrong.

Run from the repository root, after ingestion:
    python pipeline/checks/daily_check.py

Every daily export is a full copy of each source table, so from one day to the
next a table can only keep its rows or gain some. The checks:

  ERROR  a table has fewer rows today than yesterday (rows disappeared)
  ERROR  a table is missing from today's batch
  WARN   a table grew by more than MAX_DAILY_GROWTH in one day (unusual swing)

Exit code 1 when there is any ERROR, so a scheduler or CI can alert on it.
"""

import argparse
import sys
from pathlib import Path

import duckdb

# Typical daily growth is a few percent. More than this is worth a look.
MAX_DAILY_GROWTH = 0.20
# Tiny tables (a dozen campaigns) swing by whole percents with one new row, so
# the growth warning only applies from this size.
MIN_ROWS_FOR_GROWTH_CHECK = 100


def batch_counts(con: duckdb.DuckDBPyConnection, table: str) -> dict[str, int]:
    rows = con.execute(f"SELECT _batch_id, count(*) FROM bronze.{table} GROUP BY _batch_id").fetchall()
    return dict(rows)


def compare(db_path: Path) -> list[tuple[str, str]]:
    """Return findings as (level, message). Empty when there are fewer than two batches."""
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        batches = [r[0] for r in con.execute(
            "SELECT batch_id FROM bronze._ingestion_log ORDER BY batch_id").fetchall()]
        if len(batches) < 2:
            return []
        yesterday, today = batches[-2], batches[-1]
        tables = [r[0] for r in con.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'bronze' AND table_name NOT LIKE '\\_%' ESCAPE '\\' "
            "ORDER BY table_name").fetchall()]

        findings = []
        for table in tables:
            counts = batch_counts(con, table)
            before, after = counts.get(yesterday, 0), counts.get(today)
            if after is None:
                findings.append(("ERROR", f"bronze.{table} is missing from batch {today}"))
            elif after < before:
                findings.append(("ERROR", f"bronze.{table} lost rows: {before} in {yesterday}, {after} in {today}"))
            elif before >= MIN_ROWS_FOR_GROWTH_CHECK and (after - before) / before > MAX_DAILY_GROWTH:
                findings.append(("WARN", f"bronze.{table} grew {(after - before) / before:.0%} in one day "
                                         f"({before} to {after})"))
        return findings
    finally:
        con.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare today's bronze batch with yesterday's.")
    parser.add_argument("--db", type=Path, default=Path("data/lakehouse.duckdb"), help="DuckDB file")
    args = parser.parse_args()

    findings = compare(args.db)
    for level, message in findings:
        print(f"{level:5} {message}")
    errors = sum(1 for level, _ in findings if level == "ERROR")
    print(f"\nDaily check: {errors} errors, {len(findings) - errors} warnings.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
