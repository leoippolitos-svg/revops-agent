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
        "Uses [[gold.revenue_monthly.month]] and [[gold.revenue_monthly]].\n", encoding="utf-8")
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
