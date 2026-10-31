"""Tests for agent/tools/get_map.py."""

import sys
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent" / "tools"))

from get_map import MAPS, UnknownMap, get_map  # noqa: E402


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "lake.duckdb"
    con = duckdb.connect(str(path))
    con.execute("CREATE SCHEMA gold")
    con.execute("CREATE TABLE gold.owner_directory (owner_id INT, full_name VARCHAR, team VARCHAR)")
    con.execute("INSERT INTO gold.owner_directory VALUES (9, 'Dana Cole', 'sales')")
    con.execute("CREATE TABLE gold.funnel_stage_monthly (month DATE, stage VARCHAR, stage_order INT)")
    con.execute("INSERT INTO gold.funnel_stage_monthly VALUES ('2025-12-01', 'discovery', 2), "
                "('2025-11-01', 'discovery', 2), ('2025-12-01', 'qualification', 1)")
    con.close()
    return path


def test_owners_resolve_names_from_gold(db):
    assert get_map("owners", db_path=db)["rows"] == [[9, "Dana Cole", "sales"]]


def test_funnel_stages_come_in_order_once_each(db):
    assert get_map("funnel_stages", db_path=db)["rows"] == [["qualification", 1], ["discovery", 2]]


def test_a_document_map_returns_one_section_of_the_document():
    out = get_map("teams")
    assert out["document"] == "entities" and "`customer_success`" in out["text"] and "## " not in out["text"]


@pytest.mark.parametrize("key", ["../../.env", "context/index.yaml", "owner", "SELECT 1", ""])
def test_any_other_key_is_refused_and_the_known_keys_are_listed(key):
    with pytest.raises(UnknownMap, match="Known maps: owners"):
        get_map(key)


def test_every_document_map_points_at_a_section_that_exists():
    for key, (_, kind, _) in MAPS.items():
        if kind == "section":
            assert get_map(key)["text"]
