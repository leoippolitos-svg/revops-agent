"""Builds bronze from generated data, runs dbt on it and checks the silver layer."""

import sys
from pathlib import Path

import duckdb
import pytest
from dbt.adapters.factory import cleanup_connections, reset_adapters
from dbt.cli.main import dbtRunner

ROOT = Path(__file__).resolve().parents[1]
# Both are scripts, not installed packages, so we add their folders to the import path.
sys.path.insert(0, str(ROOT / "generator"))
sys.path.insert(0, str(ROOT / "pipeline"))

import generate  # noqa: E402
import ingest  # noqa: E402

DBT_DIR = ROOT / "pipeline" / "dbt"


@pytest.fixture(scope="module")
def lakehouse(tmp_path_factory, monkeypatch_module):
    """Initial load plus 10 days into bronze, then `dbt build` on top. Built once."""
    work = tmp_path_factory.mktemp("lakehouse")
    db_path = work / "lakehouse.duckdb"
    raw = work / "raw"
    generate.generate_days(seed=42, out_dir=raw, days=10)
    ingest.ingest(raw, db_path)

    monkeypatch_module.setenv("LAKEHOUSE_PATH", str(db_path))
    result = dbtRunner().invoke([
        "build", "--project-dir", str(DBT_DIR), "--profiles-dir", str(DBT_DIR),
        "--target-path", str(work / "target"), "--log-path", str(work / "logs"),
    ])
    # dbt runs inside this process and keeps its connection to the DuckDB file
    # open; DuckDB allows one configuration per file at a time, so we let go of
    # it before the tests open the file read-only.
    cleanup_connections()
    reset_adapters()
    return db_path, result


@pytest.fixture(scope="module")
def monkeypatch_module():
    # pytest's own monkeypatch lasts one test; this one lasts the whole module.
    with pytest.MonkeyPatch.context() as patch:
        yield patch


def query(db_path, sql):
    con = duckdb.connect(str(db_path))  # same configuration dbt used, see the fixture
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


def test_dbt_build_passes_every_model_and_every_test(lakehouse):
    _, result = lakehouse
    assert result.success, result.exception
    statuses = {str(r.status) for r in result.result}
    assert statuses <= {"success", "pass"}


def test_silver_has_one_row_per_entity(lakehouse):
    db, _ = lakehouse
    for table, key in [("company", "company_id"), ("deal", "deal_id"), ("invoice", "invoice_id"),
                       ("contact", "contact_id"), ("subscription", "subscription_id")]:
        total, distinct = query(db, f"SELECT count(*), count(DISTINCT {key}) FROM silver.{table}")[0]
        assert total == distinct > 0, table


def test_silver_keeps_the_same_entities_bronze_has(lakehouse):
    db, _ = lakehouse
    in_bronze = query(db, "SELECT count(DISTINCT deal_id) FROM bronze.crm_deals")[0][0]
    assert query(db, "SELECT count(*) FROM silver.deal")[0][0] == in_bronze


def test_silver_keeps_the_latest_version(lakehouse):
    db, _ = lakehouse
    # For every deal, the silver stage equals the stage in its most recent batch.
    wrong = query(db, """
        SELECT count(*) FROM silver.deal d
        JOIN (SELECT deal_id, arg_max(stage, _batch_id) AS stage FROM bronze.crm_deals GROUP BY deal_id) b
          ON b.deal_id = cast(d.deal_id AS varchar)
        WHERE b.stage <> d.stage""")[0][0]
    assert wrong == 0


def test_silver_columns_are_typed(lakehouse):
    db, _ = lakehouse
    types = {r[0]: r[1] for r in query(db, """
        SELECT column_name, data_type FROM information_schema.columns
        WHERE table_schema = 'silver' AND table_name = 'deal'""")}
    assert types["deal_id"] == "INTEGER" and types["amount_usd"] == "INTEGER"
    assert types["created_at"] == "DATE" and types["closed_at"] == "DATE"
    assert types["has_company"] == "BOOLEAN"


def test_data_quality_issues_are_flagged_not_hidden(lakehouse):
    db, _ = lakehouse
    # The generator plants these; silver must still show them, with a flag.
    assert query(db, "SELECT count(*) FROM silver.company WHERE is_possible_duplicate")[0][0] > 0
    assert query(db, "SELECT count(*) FROM silver.deal WHERE NOT has_company")[0][0] > 0
    assert query(db, "SELECT count(*) FROM silver.subscription WHERE NOT has_matching_deal")[0][0] > 0


def test_there_is_a_silver_schema_not_a_prefix(lakehouse):
    db, _ = lakehouse
    schemas = {r[0] for r in query(db, "SELECT schema_name FROM information_schema.schemata")}
    assert "silver" in schemas and "main_silver" not in schemas
