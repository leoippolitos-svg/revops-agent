"""Weekly review queue of possible duplicate companies. It proposes; a person decides.

    python automations/duplicate-companies/duplicates.py           # dry run: print the queue
    python automations/duplicate-companies/duplicates.py --write   # also write the queue file

Spec: automations/duplicate-companies/SPEC.md. Standard: docs/standards/audits.md.
Merging companies cannot be undone, so nothing here merges. Each group of records that share
a name gets a proposal: keep the oldest record (it is likeliest to carry the history), and a
person approves or rejects each group, never in bulk.
"""

import argparse
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]


class DuplicatesError(RuntimeError):
    """The run cannot continue; nothing is reported as clean."""


def read_gold(db_path: Path) -> tuple[object, list[dict]]:
    if not db_path.is_file():
        raise DuplicatesError(f"lakehouse not found at {db_path}")
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        as_of = con.execute("SELECT as_of FROM gold.data_quality_snapshot").fetchone()[0]
        cursor = con.execute("SELECT * FROM gold.possible_duplicate_company ORDER BY name_key, created_at, company_id")
        columns = [c[0] for c in cursor.description]
        return as_of, [dict(zip(columns, r)) for r in cursor.fetchall()]
    except duckdb.Error as error:
        raise DuplicatesError(f"cannot read the gold tables: {error}") from None
    finally:
        con.close()


def groups(rows: list[dict]) -> list[dict]:
    """One proposal per name key: keep the oldest record, review the rest."""
    by_key: dict[str, list[dict]] = {}
    for row in rows:
        by_key.setdefault(row["name_key"], []).append(row)
    proposals = []
    for key, records in sorted(by_key.items()):
        keep = min(records, key=lambda r: (str(r["created_at"]), r["company_id"]))
        others = [r["company_id"] for r in records if r is not keep]
        proposals.append({"name": keep["name"], "keep": keep["company_id"], "review": others})
    return proposals


def build_report(as_of, proposals: list[dict]) -> str:
    lines = [f"# Possible duplicate companies, data as of {as_of}", "",
             "A review queue. Nothing was merged. A person approves or rejects each group; "
             "an approved merge is done in the CRM by hand, and the next run shows the group gone.", "",
             f"## Groups to review ({len(proposals)})", ""]
    if not proposals:
        lines.append("None.")
    else:
        lines += ["| Name | Keep (oldest record) | Review | Decision |", "|---|---|---|---|"]
        lines += [f"| {p['name']} | {p['keep']} | {', '.join(map(str, p['review']))} | pending |" for p in proposals]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Possible duplicate companies (dry run unless --write).")
    parser.add_argument("--db", type=Path, default=ROOT / "data" / "lakehouse.duckdb")
    parser.add_argument("--logs", type=Path, default=ROOT / "observability" / "logs")
    parser.add_argument("--write", action="store_true", help="write the review queue")
    args = parser.parse_args(argv)
    try:
        as_of, rows = read_gold(args.db)
    except DuplicatesError as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    report = build_report(as_of, groups(rows))
    print(report)
    if args.write:
        args.logs.mkdir(parents=True, exist_ok=True)
        path = args.logs / f"duplicate-companies-{as_of}.md"
        path.write_text(report, encoding="utf-8", newline="\n")  # one file per data date
        print(f"wrote {path}")
    else:
        print("dry run: nothing written (use --write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
