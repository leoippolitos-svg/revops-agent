"""Run query.sql against the local lakehouse, read-only, and print each result.

    python analyses/2026-01-new-mrr-december/run.py > analyses/2026-01-new-mrr-december/output.txt

The path is absolute on purpose: a relative path would resolve from the current folder.
"""

import re
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent
LAKEHOUSE = HERE.parents[1] / "data" / "lakehouse.duckdb"

con = duckdb.connect(str(LAKEHOUSE), read_only=True)  # read-only: this script cannot change data
sql = (HERE / "query.sql").read_text(encoding="utf-8")

# Each query starts with a "-- name:" line; split on it so every result has a title.
for block in re.split(r"^-- name: ", sql, flags=re.M)[1:]:
    name, _, body = block.partition("\n")
    cursor = con.execute(body)
    columns = [d[0] for d in cursor.description]
    print(f"## {name}")
    print(" | ".join(columns))
    for row in cursor.fetchall():
        print(" | ".join(str(v) for v in row))
    print()
