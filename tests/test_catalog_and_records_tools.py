"""Tests for get_catalog, search_records and agent/rag/record_search.py."""

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent" / "tools"))
sys.path.insert(0, str(ROOT / "agent" / "rag"))

import record_search  # noqa: E402
import search_records as sr  # noqa: E402
from get_catalog import UnknownModel, get_catalog  # noqa: E402
from search_context import InvalidInput  # noqa: E402


# --- get_catalog ----------------------------------------------------------------------

def test_a_model_comes_back_with_description_columns_and_context_documents():
    out = get_catalog("gold.mrr_monthly")
    assert out["model"] == "gold.mrr_monthly" and out["layer"] == "gold"
    assert out["description"] and "\n" not in out["description"]
    assert "month" in [c["name"] for c in out["columns"]]
    assert all(c["description"] for c in out["columns"])
    assert "mrr" in out["context_documents"]


def test_a_bare_name_means_the_gold_model():
    assert get_catalog("mrr_monthly")["model"] == "gold.mrr_monthly"
    assert get_catalog("  GOLD.MRR_MONTHLY ")["model"] == "gold.mrr_monthly"


def test_a_silver_model_can_be_described_too():
    assert get_catalog("silver.deal")["layer"] == "silver"


def test_every_model_in_the_schema_files_can_be_fetched():
    for layer in ("gold", "silver"):
        schema = yaml.safe_load((ROOT / "pipeline" / "dbt" / "models" / layer / "schema.yml").read_text(encoding="utf-8"))
        for model in schema["models"]:
            assert get_catalog(f"{layer}.{model['name']}")["columns"]


@pytest.mark.parametrize("name", ["gold.nothing", "bronze.crm_deal", "mrr_monthly; DROP TABLE x", "../gold", "", "  ", None, 7])
def test_an_unknown_name_is_rejected_not_looked_up(name):
    with pytest.raises(UnknownModel):
        get_catalog(name)


def test_the_rejection_lists_the_gold_models_so_the_agent_can_retry():
    with pytest.raises(UnknownModel, match="gold.mrr_monthly"):
        get_catalog("gold.nothing")


def test_get_catalog_never_opens_the_database(monkeypatch):
    # A catalog answer must work with no lakehouse at all, so duckdb must not be touched.
    import duckdb
    monkeypatch.setattr(duckdb, "connect", lambda *a, **k: pytest.fail("the database was opened"))
    assert get_catalog("gold.mrr_monthly")["columns"]


def test_a_copy_of_the_repository_is_read_from_its_own_schema_files(tmp_path):
    for layer, name in (("gold", "thing"), ("silver", "other")):
        folder = tmp_path / "pipeline" / "dbt" / "models" / layer
        folder.mkdir(parents=True)
        (folder / "schema.yml").write_text(yaml.safe_dump({"models": [
            {"name": name, "description": "A  tiny\nmodel.", "columns": [{"name": "id", "description": "Key."}]}]}),
            encoding="utf-8")
    (tmp_path / "context" / "concepts").mkdir(parents=True)
    out = get_catalog("thing", root=tmp_path)
    assert out["description"] == "A tiny model." and out["context_documents"] == []


# --- search_records --------------------------------------------------------------------

def write_record(folder: Path, name: str, title: str, conclusion: str, extra: str = "") -> None:
    (folder / f"{name}.md").write_text(
        f"---\ndate: 2026-01-0{len(name) % 9 + 1}\ntype: data\npr: \"#9\"\nauthor: x\n---\n\n# {title}\n\n"
        f"## What was done\n{extra or 'Did the work.'}\n\n## Result or decision\n{conclusion}\n", encoding="utf-8")


@pytest.fixture
def records(tmp_path):
    write_record(tmp_path, "2026-01-01-apples", "Apple counting", "Apples are counted by the crate.")
    write_record(tmp_path, "2026-01-02-pears", "Pear weighing", "Pears are weighed on Fridays.")
    (tmp_path / "README.md").write_text("# Records\n\nApples and pears.\n", encoding="utf-8")
    (tmp_path / "_template.md").write_text("---\ndate: x\n---\n\n# Title\n\n## Result or decision\nApples.\n", encoding="utf-8")
    return tmp_path


def test_a_record_comes_back_with_title_date_type_pr_and_conclusion(records):
    hit = sr.search_records("how are apples counted", records_dir=records)["results"][0]
    assert hit["record"] == "2026-01-01-apples" and hit["title"] == "Apple counting"
    assert hit["conclusion"] == "Apples are counted by the crate."
    assert (hit["type"], hit["pr"]) == ("data", "#9") and hit["date"].startswith("2026-01")


def test_the_readme_and_the_template_are_not_records(records):
    ids = [c.doc_id for c, _ in record_search.load_records(records)]
    assert ids == ["2026-01-01-apples", "2026-01-02-pears"]


def test_k_limits_and_no_match_is_empty(records):
    assert sr.search_records("apples pears", k=1, records_dir=records)["count"] == 1
    assert sr.search_records("zzz qqq", records_dir=records) == {"results": [], "count": 0}


@pytest.mark.parametrize("question, k", [("", 3), ("  ", 3), (None, 3), ("x " * 300, 3), ("apples", 0), ("apples", 6), ("apples", True)])
def test_search_records_uses_the_same_input_rules_as_search_context(records, question, k):
    with pytest.raises(InvalidInput):
        sr.search_records(question, k, records_dir=records)


def test_every_real_record_has_a_title_a_date_and_a_conclusion():
    loaded = record_search.load_records(ROOT / "records")
    assert len(loaded) >= 30
    for chunk, info in loaded:
        assert info["title"] and info["date"] and info["conclusion"], chunk.doc_id


# Ten questions I wrote after reading the records, not an eval set with an independent author.
REAL_CASES = [
    ("How do we calculate win rate by cohort?", "gold-funnel-conversion"),
    ("Why is the weekly audit scheduled and what does it check?", "weekly-audit"),
    ("What happens when a deal is closed won and needs a workspace?", "closed-won-provisioning-spec"),
    ("How is lead routing capacity decided?", "lead-routing-spec"),
    ("Was a context A/B test designed?", "context-ab"),
    ("What did the data quality snapshot find?", "gold-data-quality"),
    ("How were skills for coding tasks written?", "coding-skills"),
    ("Which BM25 scores did retrieval reach?", "search-context-retrieval"),
    ("How does query_gold stop writes?", "query-gold"),
    ("How was the generator for billing built?", "generator-billing-cs"),
]


def test_the_right_record_is_in_the_top_three_for_most_real_questions():
    hits = sum(
        any(expected in r["record"] for r in sr.search_records(question)["results"])
        for question, expected in REAL_CASES)
    assert hits / len(REAL_CASES) >= 0.9
