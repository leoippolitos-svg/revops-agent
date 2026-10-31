"""Tests for apps/revenue-snapshot/snapshot.py, against a hand-built gold schema."""

import os
import re
import sys
import time
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "revenue-snapshot"))

import snapshot  # noqa: E402

GOLD = """
CREATE SCHEMA gold; CREATE SCHEMA silver;
CREATE TABLE silver.customer (name VARCHAR); INSERT INTO silver.customer VALUES ('silver-secret');
CREATE TABLE gold.mrr_monthly (month DATE, starting_mrr_usd DECIMAL(12,2), new_mrr_usd DECIMAL(12,2),
    churned_mrr_usd DECIMAL(12,2), ending_mrr_usd DECIMAL(12,2));
INSERT INTO gold.mrr_monthly VALUES ('2025-01-01', 0, 1000, 0, 1000), ('2025-02-01', 1000, 400, 100, 1300),
    ('2025-03-01', 1300, 50, 0, 1350);
CREATE TABLE gold.active_customer_monthly (month DATE, active_customers INT, active_subscriptions INT);
INSERT INTO gold.active_customer_monthly VALUES ('2025-01-01', 3, 4), ('2025-02-01', 5, 7);
CREATE TABLE gold.funnel_stage_monthly (month_stage_key VARCHAR, month DATE, stage VARCHAR, stage_order INT,
    deals_entered INT, amount_usd_entered DECIMAL(12,2));
INSERT INTO gold.funnel_stage_monthly VALUES ('a', '2025-02-01', 'Qualified', 1, 11, 0), ('b', '2025-02-01', 'Proposal', 2, 6, 0),
    ('c', '2025-03-01', 'Qualified', 1, 99, 0);
CREATE TABLE gold.mql_monthly (month DATE, form_submissions INT, marketing_mqls INT, sales_mqls INT, conflicting_flags INT);
INSERT INTO gold.mql_monthly VALUES ('2025-01-01', 50, 12, 12, 0), ('2025-02-01', 60, 20, 17, 3);
"""


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "lakehouse.duckdb"
    con = duckdb.connect(str(path))
    con.execute(GOLD)
    con.close()
    return path


def page(db, **kwargs):
    return snapshot.render(db, **kwargs)


# --- what the page shows -----------------------------------------------------------------

def test_the_page_has_the_four_blocks_and_a_definition_link_under_each(db):
    out = page(db)
    for title in ("MRR", "Customers", "Funnel", "MQLs"):
        assert f"<h2>{title}</h2>" in out
    for doc in ("mrr", "active-customer", "funnel-stages", "mql"):
        assert f"context/concepts/{doc}.md" in out
    assert snapshot.definition("mrr").startswith("Monthly recurring revenue")


def test_the_newest_month_is_labelled_partial_and_the_headline_uses_the_month_before(db):
    out = page(db)
    assert "2025-03 (partial)" in out and "Data through 2025-03" in out
    assert "Latest full month 2025-02: new $400, churned $100." in out


def test_customers_are_two_separate_columns(db):
    out = page(db)
    assert "<th>Active customers</th>" in out and "<th>Active subscriptions</th>" in out


def test_the_funnel_shows_the_latest_full_month_in_stage_order(db):
    out = page(db)
    assert out.index("Qualified") < out.index("Proposal") and ">11<" in out and ">99<" not in out


def test_the_sales_mql_count_is_never_shown_or_added(db):
    out = page(db)
    assert "Sales agrees" in out and "Sales counts differently" in out
    assert ">17<" not in out and ">37<" not in out and ">32<" not in out  # Sales' count, and two sums


def test_an_empty_table_says_so_and_never_shows_zero(db):
    con = duckdb.connect(str(db))
    con.execute("DELETE FROM gold.active_customer_monthly")
    con.close()
    out = page(db)
    assert "no data for this period" in out and "<td>0</td>" not in out


# --- failure behaviour -------------------------------------------------------------------

def test_a_missing_lakehouse_shows_a_banner_and_no_path(tmp_path, capsys):
    missing = tmp_path / "secret-folder" / "lake.duckdb"
    out = page(missing)
    assert "Gold is not available" in out and "secret-folder" not in out and "lake.duckdb" not in out
    assert "secret-folder" not in capsys.readouterr().err


def test_data_older_than_two_days_gets_a_banner_and_still_shows_the_data(db):
    old = time.time() - 5 * 86400
    os.utime(db, (old, old))
    out = page(db)
    assert "5 days old" in out and "$1,300" in out


def test_fresh_data_has_no_banner(db):
    assert "class='banner'" not in page(db)


def test_a_table_missing_from_gold_shows_the_banner_not_a_stack_trace(tmp_path):
    path = tmp_path / "lake.duckdb"
    con = duckdb.connect(str(path))
    con.execute("CREATE SCHEMA gold; CREATE TABLE gold.other (a INT)")
    con.close()
    out = page(path)
    assert "Gold is not available" in out and "Catalog" not in out and "Traceback" not in out


# --- what the page must never do ---------------------------------------------------------

def test_the_page_has_no_inputs_no_script_and_no_form(db):
    out = page(db).lower()
    assert not re.search(r"<(form|input|script|textarea|button|select)", out)


def test_values_from_the_data_are_escaped(db):
    con = duckdb.connect(str(db))
    con.execute("UPDATE gold.funnel_stage_monthly SET stage = '<script>alert(1)</script>' WHERE stage = 'Proposal'")
    con.close()
    out = page(db)
    assert "<script>" not in out and "&lt;script&gt;" in out


def test_silver_is_never_read_and_no_value_from_it_reaches_the_page(db):
    assert "silver-secret" not in page(db)
    assert all("silver" not in sql and "bronze" not in sql for sql in snapshot.QUERIES.values())


def test_every_query_reads_only_the_gold_tables_the_spec_lists():
    spec = (ROOT / "apps" / "revenue-snapshot" / "SPEC.md").read_text(encoding="utf-8")
    listed = set(re.findall(r"`(gold\.[a-z_]+)`", spec.split("## Data read")[1].split("##")[0]))
    used = {t for sql in snapshot.QUERIES.values() for t in re.findall(r"gold\.[a-z_]+", sql)}
    assert used == listed


def test_the_colors_come_from_the_design_tokens(db):
    assert snapshot.TOKENS["color"]["primary"] in page(db)


def test_the_command_line_writes_the_file(db, tmp_path, monkeypatch):
    monkeypatch.setenv("LAKEHOUSE_PATH", str(db))
    out = tmp_path / "page.html"
    assert snapshot.main(["--out", str(out)]) == 0
    assert "<h1>Revenue snapshot</h1>" in out.read_text(encoding="utf-8")


def test_the_real_gold_tables_have_the_columns_the_queries_use():
    import yaml
    models = {m["name"]: {c["name"] for c in m["columns"]} for m in yaml.safe_load(
        (ROOT / "pipeline" / "dbt" / "models" / "gold" / "schema.yml").read_text(encoding="utf-8"))["models"]}
    for sql in snapshot.QUERIES.values():
        table = re.search(r"FROM gold\.([a-z_]+)", sql).group(1)
        columns = re.search(r"SELECT (.+?) FROM", sql).group(1).split(", ")
        assert set(columns) <= models[table], (table, columns)
