"""Tests for agent/rag/corpus.py, agent/rag/ingest.py and the category search."""

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent" / "rag"))
sys.path.insert(0, str(ROOT / "agent" / "tools"))

import corpus  # noqa: E402

# Loaded by path: the pipeline has its own module called "ingest", and the test run imports both.
_spec = importlib.util.spec_from_file_location("rag_ingest", ROOT / "agent" / "rag" / "ingest.py")
ingest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ingest)
from search_context import InvalidInput, search_context  # noqa: E402


def test_every_category_has_files_and_concepts_are_the_default_domain():
    by_category = {}
    for source in corpus.sources():
        by_category.setdefault(source.category, set()).add(source.doc_id)
    assert set(by_category) == set(corpus.CATEGORIES)
    assert "mql" in by_category["domain"] and "area-sales" in by_category["reference"]
    assert "project-funnel-review" in by_category["incidents"]


def test_a_long_section_is_cut_at_paragraphs_never_inside_a_heading():
    text = "---\ntitle: T\n---\n\n## Big\n\n" + "\n\n".join("word " * 100 for _ in range(10)) + "\n\n## Small\n\nshort\n"
    pieces = corpus.chunks_of(text)
    assert len([p for p in pieces if p[1] == "Big"]) > 1 and all(len(p[2]) <= corpus.MAX_CHUNK_CHARS + 600 for p in pieces)
    assert pieces[-1] == ("T", "Small", "short")


def test_the_hash_ignores_line_endings(tmp_path):
    (tmp_path / "a.md").write_bytes(b"line\nnext\n")
    (tmp_path / "b.md").write_bytes(b"line\r\nnext\r\n")
    assert corpus.file_hash(tmp_path / "a.md") == corpus.file_hash(tmp_path / "b.md")


@pytest.fixture
def repo(tmp_path):
    shutil.copytree(ROOT / "context", tmp_path / "context")
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    (tmp_path / "docs" / "adr" / "0001-x.md").write_text("# ADR-0001: X\n\n## Decision\nUse x.\n", encoding="utf-8")
    return tmp_path


def test_ingest_only_reprocesses_what_changed_and_removes_what_left(repo):
    index = repo / "data" / "rag-index.json"
    first = ingest.ingest(repo, index)
    assert first["added"] and not first["unchanged"]
    adr = repo / "docs" / "adr" / "0001-x.md"
    adr.write_text(adr.read_text(encoding="utf-8") + "More.\n", encoding="utf-8")
    second = ingest.ingest(repo, index)
    assert second["changed"] == ["docs/adr/0001-x.md"] and not second["added"]
    adr.unlink()
    assert ingest.ingest(repo, index)["removed"] == ["docs/adr/0001-x.md"]
    assert ingest.is_current(repo, index)


def test_search_by_category_and_an_unknown_category_is_refused():
    out = search_context("why does the funnel review never state a cause", k=2, category="incidents")
    assert out["results"][0]["category"] == "incidents"
    with pytest.raises(InvalidInput, match="category must be one of"):
        search_context("anything", category="everything")
