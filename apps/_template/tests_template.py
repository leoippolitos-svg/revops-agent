"""Template for an app's tests. Copy to tests/test_<app_name>.py and point APP at the new app.

Kept here, not in tests/, so it does not run as part of the suite until it is copied.
"""

import importlib.util
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "apps" / "<app-name>" / "app.py"


def load_app():
    spec = importlib.util.spec_from_file_location("app_under_test", APP)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_db(path: Path, rows) -> Path:
    con = duckdb.connect(str(path))
    con.execute("CREATE SCHEMA gold")
    con.execute("CREATE TABLE gold.mrr_monthly (month DATE, ending_mrr_usd INT)")
    for row in rows:
        con.execute("INSERT INTO gold.mrr_monthly VALUES (?, ?)", list(row))
    con.close()
    return path


def test_main_path(tmp_path):
    page = load_app().render(make_db(tmp_path / "l.duckdb", [("2025-12-01", 100)]))
    assert "2025-12" in page


def test_empty_result_says_so_and_never_shows_a_zero(tmp_path):
    assert "no data for this period" in load_app().render(make_db(tmp_path / "l.duckdb", []))


def test_the_page_has_no_form_and_no_script(tmp_path):
    page = load_app().render(make_db(tmp_path / "l.duckdb", [("2025-12-01", 100)])).lower()
    assert "<form" not in page and "<script" not in page and "<input" not in page
