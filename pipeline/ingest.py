"""Load the generator's daily snapshots into the bronze layer of the lakehouse.

Bronze is the raw mirror of each source: append-only, nothing cleaned. This is
the only code allowed to write to it (see docs/standards/data-modeling.md).

For every folder data/raw/as_of=YYYY-MM-DD/ that has not been loaded yet, each
CSV file is appended to a table named bronze.<source>_<object>, for example
data/raw/crm/deals.csv becomes bronze.crm_deals. Three columns are added:

    _loaded_at   when the batch was loaded
    _source      the source system folder (crm, marketing, billing, cs)
    _batch_id    the snapshot folder name, e.g. as_of=2026-01-02

Run from the repository root:
    python pipeline/ingest.py

Safe to run twice: a batch that is already in bronze is skipped. Each batch is
loaded in one transaction, so a failure leaves no half-loaded batch behind.
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path

import duckdb

# Bookkeeping table: one row per batch that finished loading. It lives in the
# same transaction as the data, so "in the log" always means "fully loaded".
LOG_TABLE = "bronze._ingestion_log"


def table_name(source: str, csv_path: Path) -> str:
    """crm + deals.csv -> bronze.crm_deals (naming rule: bronze.<source>_<object>)."""
    return f"bronze.{source}_{csv_path.stem}"


def batch_folders(raw_dir: Path) -> list[Path]:
    # Names sort by date because the date is written year-month-day.
    return sorted(p for p in raw_dir.glob("as_of=*") if p.is_dir())


def loaded_batches(con: duckdb.DuckDBPyConnection) -> set[str]:
    return {row[0] for row in con.execute(f"SELECT batch_id FROM {LOG_TABLE}").fetchall()}


def load_batch(con: duckdb.DuckDBPyConnection, folder: Path, loaded_at: datetime) -> int:
    """Append every CSV of one snapshot to bronze. Returns the number of rows loaded."""
    batch_id = folder.name
    total = 0
    for source_dir in sorted(p for p in folder.iterdir() if p.is_dir()):
        for csv_path in sorted(source_dir.glob("*.csv")):
            table = table_name(source_dir.name, csv_path)
            # Everything is read as text on purpose: bronze mirrors the source and
            # does not guess types. Typing is silver's job.
            select = (
                "SELECT *, ? AS _loaded_at, ? AS _source, ? AS _batch_id "
                "FROM read_csv(?, header = true, all_varchar = true)"
            )
            params = [loaded_at, source_dir.name, batch_id, str(csv_path)]
            exists = con.execute(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema = 'bronze' AND table_name = ?",
                [table.split(".")[1]],
            ).fetchone()[0]
            if exists:
                con.execute(f"INSERT INTO {table} {select}", params)
            else:
                con.execute(f"CREATE TABLE {table} AS {select}", params)
            total += con.execute(
                f"SELECT count(*) FROM {table} WHERE _batch_id = ?", [batch_id]
            ).fetchone()[0]
    return total


def ingest(raw_dir: Path, db_path: Path, loaded_at: datetime | None = None) -> list[str]:
    """Load every batch not yet in bronze, oldest first. Returns the batch ids loaded."""
    loaded_at = loaded_at or datetime.now(timezone.utc)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    try:
        con.execute("CREATE SCHEMA IF NOT EXISTS bronze")
        con.execute(
            f"CREATE TABLE IF NOT EXISTS {LOG_TABLE} "
            "(batch_id VARCHAR PRIMARY KEY, loaded_at TIMESTAMPTZ, row_count BIGINT)"
        )
        done = loaded_batches(con)
        newly_loaded = []
        for folder in batch_folders(raw_dir):
            if folder.name in done:
                continue
            # One transaction per batch: either all of its tables and its log row
            # are saved, or none are.
            con.execute("BEGIN TRANSACTION")
            try:
                rows = load_batch(con, folder, loaded_at)
                con.execute(f"INSERT INTO {LOG_TABLE} VALUES (?, ?, ?)", [folder.name, loaded_at, rows])
                con.execute("COMMIT")
            except Exception:
                con.execute("ROLLBACK")
                raise
            newly_loaded.append(folder.name)
        return newly_loaded
    finally:
        con.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Load generator snapshots into bronze.")
    parser.add_argument("--raw", type=Path, default=Path("data/raw"), help="folder with as_of=* snapshots")
    parser.add_argument("--db", type=Path, default=Path("data/lakehouse.duckdb"), help="DuckDB file")
    args = parser.parse_args()

    loaded = ingest(args.raw, args.db)
    if loaded:
        print(f"loaded {len(loaded)} batch(es): {loaded[0]} .. {loaded[-1]}")
    else:
        print("nothing new to load")


if __name__ == "__main__":
    main()
