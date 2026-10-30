"""Tests for automations/audits/audit.py. They use a tiny hand-made database, not dbt."""

import sys
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automations" / "audits"))

import audit  # noqa: E402


def make_db(path: Path, as_of="2026-01-09", **counts) -> Path:
    row = {"as_of": as_of, "companies": 100, "possible_duplicate_companies": 4, "deals": 200,
           "deals_without_company": 6, "subscriptions": 80, "subscriptions_without_deal": 2,
           "closed_won_deals": 90, "closed_won_without_subscription": 5, **counts}
    con = duckdb.connect(str(path))
    con.execute("CREATE SCHEMA gold")
    con.execute("CREATE TABLE gold.data_quality_snapshot (as_of DATE, companies INTEGER, "
                "possible_duplicate_companies INTEGER, deals INTEGER, deals_without_company INTEGER, "
                "subscriptions INTEGER, subscriptions_without_deal INTEGER, closed_won_deals INTEGER, "
                "closed_won_without_subscription INTEGER)")
    con.execute("INSERT INTO gold.data_quality_snapshot VALUES (?,?,?,?,?,?,?,?,?)", list(row.values()))
    con.close()
    return path


def run(db, logs, *extra):
    return audit.main(["--db", str(db), "--logs", str(logs), *extra])


def test_dry_run_prints_and_writes_nothing(tmp_path, capsys):
    db = make_db(tmp_path / "l.duckdb")
    logs = tmp_path / "logs"
    assert run(db, logs) == 0
    assert "Possible duplicate companies" in capsys.readouterr().out
    assert not logs.exists()


def test_write_creates_one_file_and_a_second_run_does_not_duplicate_it(tmp_path):
    db = make_db(tmp_path / "l.duckdb")
    logs = tmp_path / "logs"
    run(db, logs, "--write")
    run(db, logs, "--write")
    assert [p.name for p in logs.iterdir()] == ["audit-2026-01-09.md"]


def test_first_report_raises_nothing(tmp_path, capsys):
    db = make_db(tmp_path / "l.duckdb")
    run(db, tmp_path / "logs")
    out = capsys.readouterr().out
    assert "first report" in out and "Nothing rose" in out


def test_a_rising_flag_is_raised_and_a_steady_one_is_not(tmp_path, capsys):
    logs = tmp_path / "logs"
    run(make_db(tmp_path / "a.duckdb", as_of="2026-01-02"), logs, "--write")
    capsys.readouterr()
    run(make_db(tmp_path / "b.duckdb", as_of="2026-01-09", deals_without_company=9), logs)
    out = capsys.readouterr().out
    assert "Attention, higher than the last report:** Deals without a company." in out
    assert "| Possible duplicate companies | 4 | 100 | 4.0% | +0 |" in out


def test_a_missing_database_or_table_is_an_error_not_a_clean_report(tmp_path, capsys):
    assert run(tmp_path / "nope.duckdb", tmp_path / "logs", "--write") == 1
    assert not (tmp_path / "logs").exists()
    empty = tmp_path / "empty.duckdb"
    duckdb.connect(str(empty)).close()
    assert run(empty, tmp_path / "logs") == 1
    assert "ERROR" in capsys.readouterr().err


def test_the_audit_cannot_write_to_the_database(tmp_path):
    db = make_db(tmp_path / "l.duckdb")
    con = duckdb.connect(str(db), read_only=True)
    with pytest.raises(duckdb.Error):
        con.execute("DELETE FROM gold.data_quality_snapshot")
    con.close()
