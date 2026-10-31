"""Tests for tools/check_context.py and pipeline/checks/daily_check.py."""

import sys
from pathlib import Path

import duckdb
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
# These are scripts, not installed packages, so we add their folders to the import path.
for folder in ("tools", "generator", "pipeline", "pipeline/checks"):
    sys.path.insert(0, str(ROOT / folder))

import check_context  # noqa: E402
import daily_check  # noqa: E402
import generate  # noqa: E402
import ingest  # noqa: E402


# --- check_context ---------------------------------------------------------------

def test_the_real_repository_passes():
    assert check_context.check(ROOT) == []


@pytest.fixture
def mini_repo(tmp_path):
    """A tiny repo with one gold model and one context document, all consistent."""
    models = tmp_path / "pipeline" / "dbt" / "models" / "gold"
    models.mkdir(parents=True)
    (models / "revenue_monthly.sql").write_text("select 1 as month", encoding="utf-8")
    schema = {"version": 2, "models": [{
        "name": "revenue_monthly", "description": "Revenue per month.",
        "columns": [{"name": "month", "description": "First day of the month."}],
    }]}
    (models / "schema.yml").write_text(yaml.safe_dump(schema), encoding="utf-8")

    concepts = tmp_path / "context" / "concepts"
    concepts.mkdir(parents=True)
    (concepts / "revenue.md").write_text(
        "---\nid: revenue\ntitle: Revenue\nowner_team: RevOps\nstatus: draft\n"
        "last_reviewed: 2026-10-29\nrelated: []\n---\n\n# Revenue\n\n"
        "## Definition\n\nRevenue is money in. It is counted per month.\n\n"
        "## Rules\n\n- Uses [[gold.revenue_monthly.month]] and [[gold.revenue_monthly]].\n\n"
        "## Gotchas\n\n- The last month is partial.\n\n"
        "## Team differences\n\nNone.\n\n"
        "## Examples\n\nJanuary revenue is the sum of January.\n", encoding="utf-8")
    index = {"concepts": [{"id": "revenue", "path": "concepts/revenue.md",
                           "summary": "Revenue", "status": "draft"}]}
    (tmp_path / "context" / "index.yaml").write_text(yaml.safe_dump(index), encoding="utf-8")
    return tmp_path


def test_a_consistent_mini_repo_passes(mini_repo):
    assert check_context.check(mini_repo) == []


def test_an_annotation_to_a_missing_column_fails(mini_repo):
    doc = mini_repo / "context" / "concepts" / "revenue.md"
    doc.write_text(doc.read_text(encoding="utf-8").replace("revenue_monthly.month", "revenue_monthly.day"),
                   encoding="utf-8")
    errors = check_context.check(mini_repo)
    assert any("gold.revenue_monthly.day" in e and "revenue.md" in e for e in errors)


def test_an_annotation_to_a_missing_concept_fails(mini_repo):
    doc = mini_repo / "context" / "concepts" / "revenue.md"
    doc.write_text(doc.read_text(encoding="utf-8") + "\nSee [[concept:nothing]].\n", encoding="utf-8")
    assert any("concept:nothing" in e for e in check_context.check(mini_repo))


def test_a_model_without_a_description_fails(mini_repo):
    path = mini_repo / "pipeline" / "dbt" / "models" / "gold" / "schema.yml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["models"][0]["description"] = ""
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    assert any("has no description" in e for e in check_context.check(mini_repo))


def test_a_column_without_a_description_fails(mini_repo):
    path = mini_repo / "pipeline" / "dbt" / "models" / "gold" / "schema.yml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    del data["models"][0]["columns"][0]["description"]
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    assert any("revenue_monthly.month has no description" in e for e in check_context.check(mini_repo))


def test_a_model_file_missing_from_the_catalog_fails(mini_repo):
    (mini_repo / "pipeline" / "dbt" / "models" / "gold" / "undocumented.sql").write_text("select 1", encoding="utf-8")
    assert any("undocumented.sql has no entry" in e for e in check_context.check(mini_repo))


def test_a_document_whose_id_does_not_match_its_file_fails(mini_repo):
    doc = mini_repo / "context" / "concepts" / "revenue.md"
    doc.write_text(doc.read_text(encoding="utf-8").replace("id: revenue", "id: other"), encoding="utf-8")
    assert any("must all be revenue" in e for e in check_context.check(mini_repo))


def rewrite_doc(repo, old, new):
    doc = repo / "context" / "concepts" / "revenue.md"
    text = doc.read_text(encoding="utf-8")
    assert old in text
    doc.write_text(text.replace(old, new), encoding="utf-8")


def test_a_missing_section_fails(mini_repo):
    rewrite_doc(mini_repo, "## Gotchas", "## Notes")
    assert any("missing the section 'Gotchas'" in e for e in check_context.check(mini_repo))


def test_an_empty_section_fails(mini_repo):
    rewrite_doc(mini_repo, "- The last month is partial.", "")
    assert any("section 'Gotchas' is empty" in e for e in check_context.check(mini_repo))


def test_a_definition_longer_than_three_sentences_fails(mini_repo):
    rewrite_doc(mini_repo, "It is counted per month.", "It is counted per month. It is in dollars. It is monthly.")
    assert any("the definition has 4 sentences" in e for e in check_context.check(mini_repo))


def test_dots_inside_an_annotation_do_not_count_as_sentences(mini_repo):
    rewrite_doc(mini_repo, "Revenue is money in.", "Revenue is [[gold.revenue_monthly.month]] money in.")
    assert check_context.check(mini_repo) == []


def test_a_code_block_fails(mini_repo):
    rewrite_doc(mini_repo, "None.", "```sql\nselect 1\n```")
    assert any("remove the code block" in e for e in check_context.check(mini_repo))


def test_missing_front_matter_fails(mini_repo):
    rewrite_doc(mini_repo, "owner_team: RevOps\n", "")
    assert any("front matter is missing owner_team" in e for e in check_context.check(mini_repo))


def add_area_doc(repo, body_sections=None, kind="area"):
    """Add one non-concept document to the mini repo and list it under "documents"."""
    names = body_sections or check_context.KIND_SECTIONS[kind]
    body = "".join(f"## {name}\n\nText about {name.lower()}, see [[concept:revenue]].\n\n" for name in names)
    folder = repo / "context" / "areas"
    folder.mkdir(exist_ok=True)
    (folder / "area-finance.md").write_text(
        "---\nid: area-finance\ntitle: Finance\nkind: area\nowner_team: RevOps\nstatus: draft\n"
        "last_reviewed: 2026-10-31\nrelated: [revenue]\n---\n\n# Finance\n\n" + body, encoding="utf-8")
    index_path = repo / "context" / "index.yaml"
    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    index["documents"] = [{"id": "area-finance", "kind": kind, "path": "areas/area-finance.md", "status": "draft"}]
    index_path.write_text(yaml.safe_dump(index), encoding="utf-8")


def test_a_complete_area_document_passes(mini_repo):
    add_area_doc(mini_repo)
    assert check_context.check(mini_repo) == []


def test_an_area_document_missing_a_section_of_its_kind_fails(mini_repo):
    add_area_doc(mini_repo, body_sections=[s for s in check_context.KIND_SECTIONS["area"] if s != "KPIs"])
    assert any("a area document needs the section 'KPIs'" in e for e in check_context.check(mini_repo))


def test_an_unknown_kind_fails(mini_repo):
    add_area_doc(mini_repo, kind="area")
    index_path = mini_repo / "context" / "index.yaml"
    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    index["documents"][0]["kind"] = "poem"
    index_path.write_text(yaml.safe_dump(index), encoding="utf-8")
    assert any("unknown kind 'poem'" in e for e in check_context.check(mini_repo))


def test_a_doc_annotation_must_resolve(mini_repo):
    add_area_doc(mini_repo)
    rewrite_doc(mini_repo, "None.", "See [[doc:area-finance]] and [[doc:area-nowhere]].")
    errors = check_context.check(mini_repo)
    assert any("doc:area-nowhere" in e for e in errors) and not any("doc:area-finance" in e for e in errors)


def test_only_map_documents_may_hold_a_code_block(mini_repo):
    add_area_doc(mini_repo)
    doc = mini_repo / "context" / "areas" / "area-finance.md"
    doc.write_text(doc.read_text(encoding="utf-8") + "```sql\nselect 1\n```\n", encoding="utf-8")
    assert any("may hold a code block" in e for e in check_context.check(mini_repo))


# --- daily_check -----------------------------------------------------------------


def load_days(tmp_path, days):
    raw = tmp_path / "raw"
    generate.generate_days(seed=42, out_dir=raw, days=days)
    db = tmp_path / "lakehouse.duckdb"
    ingest.ingest(raw, db)
    return raw, db


def test_a_normal_day_has_no_errors(tmp_path):
    _, db = load_days(tmp_path, 2)
    assert [f for f in daily_check.compare(db) if f[0] == "ERROR"] == []


def test_fewer_than_two_batches_gives_nothing_to_compare(tmp_path):
    raw = tmp_path / "raw"
    generate.generate_days(seed=42, out_dir=raw, days=0)
    db = tmp_path / "lakehouse.duckdb"
    ingest.ingest(raw, db)
    assert daily_check.compare(db) == []


def test_lost_rows_are_an_error(tmp_path):
    raw, db = load_days(tmp_path, 1)
    # Tomorrow's export is missing rows the source had yesterday.
    generate.generate_days(seed=42, out_dir=raw, days=1)
    deals = raw / "as_of=2026-01-02" / "crm" / "deals.csv"
    lines = deals.read_text(encoding="utf-8").splitlines()
    deals.write_text("\n".join(lines[:-10]) + "\n", encoding="utf-8")
    ingest.ingest(raw, db)
    errors = [m for level, m in daily_check.compare(db) if level == "ERROR"]
    assert any("bronze.crm_deals lost rows" in m for m in errors)


def test_a_missing_table_is_an_error(tmp_path):
    raw, db = load_days(tmp_path, 1)
    generate.generate_days(seed=42, out_dir=raw, days=1)
    (raw / "as_of=2026-01-02" / "cs" / "tickets.csv").unlink()
    ingest.ingest(raw, db)
    errors = [m for level, m in daily_check.compare(db) if level == "ERROR"]
    assert any("bronze.cs_tickets is missing" in m for m in errors)


def test_a_big_jump_is_a_warning_not_an_error(tmp_path):
    raw, db = load_days(tmp_path, 1)
    # Double yesterday's invoices: a swing, not a loss.
    generate.generate_days(seed=42, out_dir=raw, days=1)
    invoices = raw / "as_of=2026-01-02" / "billing" / "invoices.csv"
    lines = invoices.read_text(encoding="utf-8").splitlines()
    extra = [line.replace(line.split(",")[0], str(9000 + i), 1) for i, line in enumerate(lines[1:], start=1)]
    invoices.write_text("\n".join(lines + extra) + "\n", encoding="utf-8")
    ingest.ingest(raw, db)
    findings = daily_check.compare(db)
    assert any(level == "WARN" and "bronze.billing_invoices grew" in m for level, m in findings)
    assert not any(level == "ERROR" for level, _ in findings)


def test_the_command_line_exit_code_follows_the_errors(tmp_path, monkeypatch):
    raw, db = load_days(tmp_path, 1)
    monkeypatch.setattr(sys, "argv", ["daily_check.py", "--db", str(db)])
    assert daily_check.main() == 0
    generate.generate_days(seed=42, out_dir=raw, days=1)
    (raw / "as_of=2026-01-02" / "cs" / "tickets.csv").unlink()
    ingest.ingest(raw, db)
    assert daily_check.main() == 1
