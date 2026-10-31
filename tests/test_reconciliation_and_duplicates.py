"""Tests for the reconciliation audit and the duplicate-companies queue, on hand-built gold tables."""

import importlib.util
from datetime import date
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(rel):
    spec = importlib.util.spec_from_file_location(Path(rel).stem, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


reconcile = load("automations/reconciliation/reconcile.py")
duplicates = load("automations/duplicate-companies/duplicates.py")
AS_OF = date(2026, 1, 15)


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "lake.duckdb"
    con = duckdb.connect(str(path))
    con.execute("CREATE SCHEMA gold")
    con.execute("CREATE TABLE gold.data_quality_snapshot (as_of DATE)")
    con.execute("INSERT INTO gold.data_quality_snapshot VALUES (?)", [AS_OF])
    con.execute("CREATE TABLE gold.deal_subscription_reconciliation (deal_id INT, subscription_id INT, company_id INT, "
                "owner_id INT, closed_at DATE, started_at DATE, deal_amount_usd INT, subscription_mrr_usd INT, "
                "match_status VARCHAR, monthly_gap_usd DOUBLE)")
    rows = [(1, 11, 1, 6, "2025-11-01", "2025-11-05", 12000, 1000, "matched", 0.0),
            (2, 12, 2, 6, "2025-11-01", "2025-11-05", 24000, 1500, "matched", 500.0),
            (3, None, 3, 7, "2026-01-12", None, 6000, None, "won_without_subscription", None),
            (4, None, 4, 7, "2025-10-19", None, 6000, None, "won_without_subscription", None),
            (900, 13, 5, None, None, "2025-12-01", None, 800, "subscription_without_deal", None)]
    for row in rows:
        con.execute("INSERT INTO gold.deal_subscription_reconciliation VALUES (?,?,?,?,?,?,?,?,?,?)", list(row))
    con.execute("CREATE TABLE gold.possible_duplicate_company (company_id INT, name VARCHAR, name_key VARCHAR, "
                "records_with_name INT, owner_id INT, created_at DATE)")
    for row in [(122, "Clearwater Maintenance", "clearwater maintenance", 2, 6, "2025-01-10"),
                (303, "clearwater maintenance ", "clearwater maintenance", 2, 7, "2025-06-01")]:
        con.execute("INSERT INTO gold.possible_duplicate_company VALUES (?,?,?,?,?,?)", list(row))
    con.close()
    return path


def test_the_rules_are_read_from_the_context_documents():
    assert reconcile.load_rules() == {"tolerance_usd": 1, "wait_days": 14}


def test_every_record_lands_in_one_destination_with_an_owner(db):
    as_of, rows = reconcile.read_gold(db)
    _, found = reconcile.build_report(as_of, rows, reconcile.load_rules())
    by_deal = {f["deal_id"]: (f["destination"], f["class"]) for f in found}
    assert by_deal == {2: ("divergence", "amount differs"), 3: ("pending", "won without subscription"),
                       4: ("divergence", "won without subscription"), 900: ("known case", "subscription without deal")}
    assert all(f["owner"] for f in found)


def test_the_report_states_scope_coverage_and_says_it_corrected_nothing(db):
    as_of, rows = reconcile.read_gold(db)
    report, _ = reconcile.build_report(as_of, rows, reconcile.load_rules())
    assert "Coverage: 2 of 5 records matched" in report and "Nothing was corrected" in report


def test_dry_run_writes_nothing_and_write_makes_one_file_per_data_date(db, tmp_path, monkeypatch):
    monkeypatch.delenv("SLACK_ALERTS_ENABLED", raising=False)
    logs = tmp_path / "logs"
    assert reconcile.main(["--db", str(db), "--logs", str(logs)]) == 0 and not logs.exists()
    reconcile.main(["--db", str(db), "--logs", str(logs), "--write"])
    reconcile.main(["--db", str(db), "--logs", str(logs), "--write"])
    assert [p.name for p in logs.glob("reconciliation-*.md")] == ["reconciliation-2026-01-15.md"]


def test_a_missing_lakehouse_stops_the_run(tmp_path):
    assert reconcile.main(["--db", str(tmp_path / "none.duckdb")]) == 1


def test_duplicates_propose_keeping_the_oldest_record_and_merge_nothing(db):
    as_of, rows = duplicates.read_gold(db)
    proposals = duplicates.groups(rows)
    assert proposals == [{"name": "Clearwater Maintenance", "keep": 122, "review": [303]}]
    assert "Nothing was merged" in duplicates.build_report(as_of, proposals)


def test_neither_script_has_a_way_to_write_to_a_source():
    for rel in ("automations/reconciliation/reconcile.py", "automations/duplicate-companies/duplicates.py"):
        code = (ROOT / rel).read_text(encoding="utf-8").lower()
        assert "read_only=true" in code and not any(w in code for w in ("insert into", "update ", "delete from", "merge into"))
