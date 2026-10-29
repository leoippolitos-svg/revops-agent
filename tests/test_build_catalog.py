"""Tests for tools/build_catalog.py (the rendered data catalog)."""

import re
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
# The tool is a script, not an installed package, so we add its folder to the import path.
sys.path.insert(0, str(ROOT / "tools"))

import build_catalog  # noqa: E402


def test_the_committed_catalog_is_up_to_date():
    assert (ROOT / "docs" / "catalog.md").read_text(encoding="utf-8") == build_catalog.render(ROOT)


def test_every_model_and_column_of_the_real_project_is_in_the_page():
    page = build_catalog.render(ROOT)
    for layer in ("gold", "silver"):
        for model in build_catalog.load_models(ROOT, layer):
            assert f"### `{layer}.{model['name']}`" in page
            for column in model["columns"]:
                assert f"| `{column['name']}` |" in page


def test_every_context_link_in_the_page_points_at_a_real_document():
    page = build_catalog.render(ROOT)
    links = set(re.findall(r"\]\((\.\./context/[^)]+)\)", page))
    assert links
    for link in links:
        assert (ROOT / "docs" / link).resolve().is_file(), link


@pytest.fixture
def mini_repo(tmp_path):
    for layer in ("gold", "silver"):
        folder = tmp_path / "pipeline" / "dbt" / "models" / layer
        folder.mkdir(parents=True)
        models = [{"name": f"{layer}_table", "description": "A table.",
                   "columns": [{"name": "key", "description": "Joined with a bar, like a|b."}]}]
        (folder / "schema.yml").write_text(yaml.safe_dump({"version": 2, "models": models}), encoding="utf-8")
    concepts = tmp_path / "context" / "concepts"
    concepts.mkdir(parents=True)
    (concepts / "thing.md").write_text(
        "---\nid: thing\ntitle: The thing\n---\n\n## Rules\n\n- Uses [[gold.gold_table.key]].\n", encoding="utf-8")
    return tmp_path


def test_a_model_lists_the_documents_that_use_it(mini_repo):
    page = build_catalog.render(mini_repo)
    assert "**Context:** [The thing](../context/concepts/thing.md)" in page


def test_a_model_no_document_uses_has_no_context_line(mini_repo):
    page = build_catalog.render(mini_repo)
    silver_section = page.split("### `silver.silver_table`")[1]
    assert "**Context:**" not in silver_section


def test_pipes_in_a_description_do_not_break_the_table(mini_repo):
    assert "Joined with a bar, like a\\|b." in build_catalog.render(mini_repo)


def test_gold_comes_before_silver(mini_repo):
    page = build_catalog.render(mini_repo)
    assert page.index("## Gold") < page.index("## Silver")


def test_check_fails_when_the_page_is_stale_and_passes_after_a_rebuild(mini_repo, monkeypatch):
    monkeypatch.chdir(mini_repo)
    (mini_repo / "docs").mkdir()
    assert build_catalog.main(["--check"]) == 1          # no page yet
    assert build_catalog.main([]) == 0                    # build it
    assert build_catalog.main(["--check"]) == 0
    schema = mini_repo / "pipeline" / "dbt" / "models" / "gold" / "schema.yml"
    schema.write_text(schema.read_text(encoding="utf-8").replace("A table.", "A changed table."), encoding="utf-8")
    assert build_catalog.main(["--check"]) == 1           # the description changed, the page did not
