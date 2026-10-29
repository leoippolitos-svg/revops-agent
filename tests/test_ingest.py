"""Tests for pipeline/ingest.py (raw snapshots -> bronze)."""

import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]
# Both are scripts, not installed packages, so we add their folders to the import path.
sys.path.insert(0, str(ROOT / "generator"))
sys.path.insert(0, str(ROOT / "pipeline"))

import generate  # noqa: E402
import ingest  # noqa: E402

LOADED_AT = datetime(2026, 1, 1, tzinfo=timezone.utc)


@pytest.fixture(scope="module")
def raw_dir(tmp_path_factory):
    """The initial load plus 30 days, enough for deals to change stage. Built once."""
    folder = tmp_path_factory.mktemp("raw")
    generate.generate_days(seed=42, out_dir=folder, days=30)
    return folder


@pytest.fixture(scope="module")
def loaded(raw_dir, tmp_path_factory):
    """Bronze loaded once, for the tests that only read it: (db path, batches loaded)."""
    db_path = tmp_path_factory.mktemp("lakehouse") / "lakehouse.duckdb"
    return db_path, ingest.ingest(raw_dir, db_path, LOADED_AT)


@pytest.fixture
def db(tmp_path):
    return tmp_path / "lakehouse.duckdb"


def query(db_path: Path, sql: str, params=None):
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        return con.execute(sql, params or []).fetchall()
    finally:
        con.close()


def test_every_batch_is_loaded_oldest_first(loaded):
    _, batches = loaded
    assert batches == sorted(batches) and len(batches) == 31
    assert batches[0] == f"as_of={generate.INITIAL_AS_OF.isoformat()}"


def test_tables_follow_the_bronze_naming_rule(loaded):
    db = loaded[0]
    names = {r[0] for r in query(db, "SELECT table_name FROM information_schema.tables "
                                     "WHERE table_schema = 'bronze'")}
    assert {"crm_companies", "crm_deals", "marketing_form_submissions",
            "billing_invoices", "cs_tickets"} <= names


def test_load_metadata_columns_are_filled(loaded):
    db = loaded[0]
    rows = query(db, "SELECT count(*), count(_loaded_at), count(_source), count(_batch_id), "
                     "min(_source), max(_source) FROM bronze.crm_deals")
    total, loaded_at, source, batch, low, high = rows[0]
    assert total == loaded_at == source == batch > 0
    assert low == high == "crm"


def test_each_batch_holds_exactly_the_rows_of_its_snapshot(raw_dir, loaded):
    db = loaded[0]
    for folder in ingest.batch_folders(raw_dir)[:3]:
        in_file = sum(1 for _ in (folder / "crm" / "deals.csv").open()) - 1  # minus header
        in_bronze = query(db, "SELECT count(*) FROM bronze.crm_deals WHERE _batch_id = ?",
                          [folder.name])[0][0]
        assert in_bronze == in_file


def test_bronze_stays_raw_everything_is_text(loaded):
    db = loaded[0]
    types = {r[0]: r[1] for r in query(
        db, "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_schema = 'bronze' AND table_name = 'crm_deals'")}
    assert types["amount_usd"] == "VARCHAR" and types["deal_id"] == "VARCHAR"


def test_running_twice_loads_nothing_new_and_adds_no_rows(tmp_path, db):
    raw = tmp_path / "raw"
    generate.generate_days(seed=42, out_dir=raw, days=2)
    ingest.ingest(raw, db, LOADED_AT)
    before = query(db, "SELECT count(*) FROM bronze.crm_deals")[0][0]
    assert ingest.ingest(raw, db, LOADED_AT) == []
    assert query(db, "SELECT count(*) FROM bronze.crm_deals")[0][0] == before


def test_a_new_day_loads_only_that_day(tmp_path, db):
    raw = tmp_path / "raw"
    generate.generate_days(seed=42, out_dir=raw, days=1)
    ingest.ingest(raw, db, LOADED_AT)
    generate.generate_days(seed=42, out_dir=raw, days=1)
    loaded = ingest.ingest(raw, db, LOADED_AT)
    assert loaded == ["as_of=2026-01-02"]


def test_bronze_keeps_every_version_of_a_deal(raw_dir, db):
    # A full export every day means a deal that changes stage appears with
    # different stages in different batches. Silver will pick the latest.
    ingest.ingest(raw_dir, db, LOADED_AT)
    changed = query(db, "SELECT count(*) FROM (SELECT deal_id FROM bronze.crm_deals "
                        "GROUP BY deal_id HAVING count(DISTINCT stage) > 1)")[0][0]
    assert changed > 0


def test_a_failing_batch_leaves_nothing_behind(tmp_path, db):
    raw = tmp_path / "raw"
    generate.generate_days(seed=42, out_dir=raw, days=2)
    ingest.ingest(raw, db, LOADED_AT)  # the three batches load fine
    good_rows = query(db, "SELECT count(*) FROM bronze.crm_deals")[0][0]

    generate.generate_days(seed=42, out_dir=raw, days=1)
    broken = raw / "as_of=2026-01-03"
    # The file that sorts last is loaded last, so the batch fails half way,
    # after other tables of the same batch were already written.
    (broken / "cs" / "tickets.csv").write_text("not,a,valid\n1,2\n", encoding="utf-8")
    with pytest.raises(Exception):
        ingest.ingest(raw, db, LOADED_AT)

    assert query(db, "SELECT count(*) FROM bronze.crm_deals")[0][0] == good_rows
    assert query(db, "SELECT count(*) FROM bronze._ingestion_log")[0][0] == 3

    # After the file is fixed, the same batch loads normally.
    shutil.copy(raw / "as_of=2026-01-02" / "cs" / "tickets.csv", broken / "cs" / "tickets.csv")
    assert ingest.ingest(raw, db, LOADED_AT) == ["as_of=2026-01-03"]
