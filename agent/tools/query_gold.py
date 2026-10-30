"""query_gold: the agent's only door to the lakehouse (ADR-0006, ADR-0013).

    python agent/tools/query_gold.py "select * from mrr_monthly order by month desc limit 3"

Two layers, so that no single mistake opens the database:
1. The query is parsed by DuckDB itself and may only be one SELECT over gold tables.
2. The connection is read-only, cannot touch files and has a time and memory limit.
"""

import json
import os
import sys
import threading
from decimal import Decimal
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
MAX_ROWS = 200
TIMEOUT_SECONDS = 10
MEMORY_LIMIT = "512MB"


class QueryRejected(ValueError):
    """The guard refused the query before it reached the data."""


class QueryFailed(RuntimeError):
    """The query was allowed but did not run (bad column, timeout)."""


def default_db_path() -> Path:
    # dbt needs an absolute path, but here a relative one is fine: it is only opened.
    return Path(os.environ.get("LAKEHOUSE_PATH") or ROOT / "data" / "lakehouse.duckdb")


def _connect(db_path: Path) -> duckdb.DuckDBPyConnection:
    """Open the lakehouse so that even a query that slipped past the parser cannot do harm."""
    if not Path(db_path).is_file():
        raise QueryFailed("The lakehouse file was not found. Build it first.")
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        con.execute("USE gold")  # unqualified names now mean gold
    except duckdb.Error as error:
        con.close()
        raise QueryFailed("The lakehouse has no gold schema.") from error
    con.execute("SET enable_external_access = false")  # no files, no network, no extensions
    con.execute(f"SET memory_limit = '{MEMORY_LIMIT}'")
    con.execute("SET lock_configuration = true")  # the query cannot undo the settings above
    return con


def _walk(node, tables: list, cte_names: set) -> None:
    """Collect every table the parsed query reads. Table functions are refused outright."""
    if isinstance(node, dict):
        kind = node.get("type")
        if kind == "TABLE_FUNCTION":
            raise QueryRejected("Table functions are not allowed. Read gold tables only.")
        if kind == "BASE_TABLE":
            tables.append((node["catalog_name"].lower(), node["schema_name"].lower(), node["table_name"].lower()))
        if "cte_map" in node:
            cte_names.update(entry["key"].lower() for entry in node["cte_map"]["map"])
        for value in node.values():
            _walk(value, tables, cte_names)
    elif isinstance(node, list):
        for item in node:
            _walk(item, tables, cte_names)


def _check(con: duckdb.DuckDBPyConnection, sql: str) -> None:
    if not sql.strip():
        raise QueryRejected("The query is empty.")
    try:
        statements = con.extract_statements(sql)
    except duckdb.Error as error:
        raise QueryRejected("The query could not be parsed.") from error
    if len(statements) != 1:
        raise QueryRejected("Send exactly one statement per call.")
    if statements[0].type != duckdb.StatementType.SELECT:
        raise QueryRejected("Only SELECT statements are allowed.")

    tree = json.loads(con.execute("SELECT json_serialize_sql(?)", [sql]).fetchone()[0])
    if tree.get("error"):  # DuckDB refuses to serialize anything that is not a plain SELECT
        raise QueryRejected("Only SELECT statements are allowed.")

    tables, cte_names = [], set()
    _walk(tree, tables, cte_names)
    in_gold = {
        name.lower() for (name,) in con.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'gold'").fetchall()
    }
    current_catalog = con.execute("SELECT current_database()").fetchone()[0].lower()
    for catalog, schema, table in tables:
        if catalog not in ("", current_catalog) or schema not in ("", "gold"):
            raise QueryRejected("Only the gold schema can be read.")
        if schema == "" and catalog == "" and table in cte_names:
            continue  # a name the query defined itself with WITH
        if table not in in_gold:
            raise QueryRejected(f"'{table}' is not a gold table.")


def _plain(value):
    # Rows go to a language model as JSON, so dates and decimals become text.
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return float(value) if isinstance(value, Decimal) else str(value)


def query_gold(sql: str, db_path: Path | None = None) -> dict:
    """Run one SELECT over gold. Returns columns, rows (at most 200) and whether they were cut."""
    con = _connect(db_path or default_db_path())
    timer = threading.Timer(TIMEOUT_SECONDS, con.interrupt)
    try:
        _check(con, sql)
        timer.start()
        cursor = con.execute(sql)
        fetched = cursor.fetchmany(MAX_ROWS + 1)  # one extra row tells us the result was cut
        return {
            "columns": [column[0] for column in cursor.description],
            "rows": [[_plain(v) for v in row] for row in fetched[:MAX_ROWS]],
            "row_count": min(len(fetched), MAX_ROWS),
            "truncated": len(fetched) > MAX_ROWS,
        }
    except duckdb.InterruptException as error:
        raise QueryFailed(f"The query took longer than {TIMEOUT_SECONDS} seconds.") from error
    except duckdb.Error as error:
        # The first line only: the rest of a DuckDB error echoes the query and internals.
        raise QueryFailed(str(error).splitlines()[0]) from error
    finally:
        timer.cancel()
        con.close()


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print('usage: python agent/tools/query_gold.py "select ..."', file=sys.stderr)
        return 1
    try:
        print(json.dumps(query_gold(argv[1]), indent=2))
    except (QueryRejected, QueryFailed) as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
