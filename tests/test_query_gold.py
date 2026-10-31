"""Security and behaviour tests for agent/tools/query_gold.py (ADR-0013).

The database here is built by hand, with a secret-looking table in silver and bronze, so
a leak from either layer would show up as a value in a result.
"""

import sys
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent" / "tools"))

import query_gold as qg  # noqa: E402
from query_gold import QueryFailed, QueryRejected, query_gold  # noqa: E402


@pytest.fixture(scope="module")
def db(tmp_path_factory):
    path = tmp_path_factory.mktemp("lake") / "lakehouse.duckdb"
    con = duckdb.connect(str(path))
    con.execute("""
        CREATE SCHEMA bronze; CREATE SCHEMA silver; CREATE SCHEMA gold;
        CREATE TABLE bronze.raw_contact (email VARCHAR);
        INSERT INTO bronze.raw_contact VALUES ('bronze-secret');
        CREATE TABLE silver.customer (name VARCHAR);
        INSERT INTO silver.customer VALUES ('silver-secret');
        CREATE TABLE gold.mrr_monthly (month DATE, mrr_usd DECIMAL(12, 2));
        INSERT INTO gold.mrr_monthly VALUES ('2025-01-01', 1000.50), ('2025-02-01', 1200.00);
        CREATE TABLE gold.big AS SELECT range AS n FROM range(2000);
    """)
    con.close()
    return path


def rows(db, sql):
    return query_gold(sql, db)["rows"]


# --- what a good query gets back -------------------------------------------------------

def test_a_gold_select_returns_columns_and_rows(db):
    result = query_gold("SELECT month, mrr_usd FROM mrr_monthly ORDER BY month", db)
    assert result["columns"] == ["month", "mrr_usd"]
    # Dates and decimals become text or floats so the rows can go to the model as JSON.
    assert result["rows"] == [["2025-01-01", 1000.5], ["2025-02-01", 1200.0]]
    assert result["row_count"] == 2 and result["truncated"] is False


def test_the_schema_can_be_written_out_and_a_trailing_semicolon_is_fine(db):
    assert rows(db, "SELECT count(*) FROM gold.mrr_monthly;") == [[2]]


def test_ctes_subqueries_and_joins_over_gold_work(db):
    sql = """
        WITH recent AS (SELECT * FROM mrr_monthly WHERE month >= '2025-02-01')
        SELECT (SELECT count(*) FROM recent), a.month
        FROM mrr_monthly a JOIN recent r ON a.month = r.month
    """
    assert rows(db, sql) == [[1, "2025-02-01"]]


def test_a_cte_may_reuse_a_name_that_exists_only_outside_gold(db):
    # The name is defined by the query itself, so nothing from silver is read.
    assert rows(db, "WITH customer AS (SELECT 1 AS x) SELECT x FROM customer") == [[1]]


# --- statements that are not a single SELECT ------------------------------------------

@pytest.mark.parametrize("sql", [
    "INSERT INTO mrr_monthly VALUES ('2025-03-01', 1)",
    "UPDATE mrr_monthly SET mrr_usd = 0",
    "DELETE FROM mrr_monthly",
    "DROP TABLE mrr_monthly",
    "CREATE TABLE gold.x (a INT)",
    "CREATE TABLE x AS SELECT * FROM mrr_monthly",
    "ALTER TABLE mrr_monthly ADD COLUMN x INT",
    "ATTACH 'other.duckdb' AS other",
    "COPY mrr_monthly TO 'out.csv'",
    "INSTALL httpfs",
    "SET enable_external_access = true",
    "PRAGMA database_list",
    "EXPORT DATABASE 'out'",
    "USE silver",
    "CALL pragma_version()",
])
def test_anything_that_is_not_a_select_is_rejected(db, sql):
    with pytest.raises(QueryRejected):
        query_gold(sql, db)


def test_two_statements_joined_by_a_semicolon_are_rejected(db):
    with pytest.raises(QueryRejected, match="exactly one"):
        query_gold("SELECT 1; DROP TABLE mrr_monthly", db)
    with pytest.raises(QueryRejected, match="exactly one"):
        query_gold("SELECT 1; SELECT 2", db)


@pytest.mark.parametrize("sql", ["", "   ", "-- only a comment", "SELEC nonsense FROM"])
def test_empty_and_unparseable_input_is_rejected(db, sql):
    with pytest.raises(QueryRejected):
        query_gold(sql, db)


# --- schemas and tables outside gold ---------------------------------------------------

@pytest.mark.parametrize("sql", [
    "SELECT * FROM silver.customer",
    "SELECT * FROM bronze.raw_contact",
    'SELECT * FROM "silver"."customer"',
    "SELECT * FROM SILVER.customer",
    "SELECT * FROM lakehouse.silver.customer",
    "SELECT * FROM mrr_monthly WHERE month IN (SELECT 1 FROM silver.customer)",
    "WITH c AS (SELECT * FROM silver.customer) SELECT * FROM c",
    "SELECT * FROM mrr_monthly a JOIN bronze.raw_contact b ON true",
    "SELECT * FROM information_schema.tables",
    "SELECT * FROM duckdb_tables",
    "SELECT * FROM other_db.gold.mrr_monthly",
])
def test_reading_outside_gold_is_rejected(db, sql):
    with pytest.raises(QueryRejected):
        query_gold(sql, db)


def test_a_bare_name_that_only_exists_in_silver_is_not_looked_up(db):
    # `customer` exists in silver. It must not be found by falling back to another schema.
    with pytest.raises(QueryRejected, match="not a gold table"):
        query_gold("SELECT * FROM customer", db)


def test_a_table_that_does_not_exist_is_rejected_not_searched_for(db):
    with pytest.raises(QueryRejected, match="not a gold table"):
        query_gold("SELECT * FROM nothing_here", db)


@pytest.mark.parametrize("sql", [
    "SELECT * FROM read_csv('data.csv')",
    "SELECT * FROM read_parquet('data.parquet')",
    "SELECT * FROM glob('*')",
    "SELECT * FROM range(10)",
    "SELECT * FROM duckdb_tables()",
    "SELECT * FROM mrr_monthly, read_text('secret.txt')",
])
def test_table_functions_are_rejected(db, sql):
    with pytest.raises(QueryRejected, match="Table functions"):
        query_gold(sql, db)


# --- the connection holds even if the parser were fooled ------------------------------

def test_the_connection_is_read_only_whatever_the_parser_says(db):
    con = qg._connect(db)
    try:
        with pytest.raises(duckdb.Error):
            con.execute("INSERT INTO gold.mrr_monthly VALUES ('2025-03-01', 1)")
        with pytest.raises(duckdb.Error):
            con.execute("CREATE TABLE gold.x (a INT)")
    finally:
        con.close()


def test_the_connection_cannot_read_files_and_its_settings_are_locked(db, tmp_path):
    (tmp_path / "secret.csv").write_text("a\n1\n", encoding="utf-8")
    con = qg._connect(db)
    try:
        with pytest.raises(duckdb.Error):
            con.execute(f"SELECT * FROM read_csv('{(tmp_path / 'secret.csv').as_posix()}')")
        with pytest.raises(duckdb.Error):
            con.execute("SET enable_external_access = true")
        with pytest.raises(duckdb.Error):
            con.execute("SET memory_limit = '64GB'")
    finally:
        con.close()


def test_unqualified_names_resolve_to_gold_on_the_connection(db):
    con = qg._connect(db)
    try:
        assert con.execute("SELECT current_schema()").fetchone() == ("gold",)
    finally:
        con.close()


def test_a_missing_lakehouse_or_gold_schema_is_a_clear_failure(tmp_path):
    with pytest.raises(QueryFailed, match="not found"):
        query_gold("SELECT 1", tmp_path / "missing.duckdb")
    empty = tmp_path / "empty.duckdb"
    duckdb.connect(str(empty)).close()
    with pytest.raises(QueryFailed, match="no gold schema"):
        query_gold("SELECT 1", empty)


# --- limits ----------------------------------------------------------------------------

def test_a_big_result_is_cut_at_200_rows_and_says_so(db):
    result = query_gold("SELECT * FROM big", db)
    assert result["row_count"] == 200 and len(result["rows"]) == 200
    assert result["truncated"] is True


def test_a_cut_result_says_the_real_total_so_the_sample_is_never_reported_as_the_count(db):
    full = rows(db, "SELECT count(*) AS n FROM big")[0][0]
    result = query_gold("SELECT * FROM big;", db)
    assert result["total_rows"] == full > 200
    assert query_gold("SELECT * FROM big LIMIT 5", db)["total_rows"] == 5


def test_a_result_of_exactly_200_rows_is_not_marked_as_cut(db):
    result = query_gold("SELECT * FROM big LIMIT 200", db)
    assert result["row_count"] == 200 and result["truncated"] is False


def test_a_slow_query_is_stopped_at_the_time_limit(db, monkeypatch):
    monkeypatch.setattr(qg, "TIMEOUT_SECONDS", 0.5)
    # 2000^4 combinations: it would run for hours if nothing stopped it.
    with pytest.raises(QueryFailed, match="longer than"):
        query_gold("SELECT count(*) FROM big a, big b, big c, big d WHERE (a.n * b.n + c.n * d.n) % 99991 = 99990", db)


def test_a_database_error_is_shortened_to_one_line(db):
    with pytest.raises(QueryFailed) as caught:
        query_gold("SELECT no_such_column FROM mrr_monthly", db)
    assert "\n" not in str(caught.value)


def test_the_file_is_unchanged_after_all_the_attacks(db):
    con = duckdb.connect(str(db), read_only=True)
    try:
        assert con.execute("SELECT count(*) FROM gold.mrr_monthly").fetchone() == (2,)
        assert con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'x'").fetchone() == (0,)
    finally:
        con.close()
