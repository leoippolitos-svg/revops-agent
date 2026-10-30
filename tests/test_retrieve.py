"""Tests for agent/rag/retrieve.py and evals/run_retrieval.py."""

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent" / "rag"))
sys.path.insert(0, str(ROOT / "evals"))

import retrieve  # noqa: E402
import run_retrieval  # noqa: E402


def doc(doc_id: str, title: str, status: str, sections: dict[str, str]) -> str:
    body = "\n".join(f"## {name}\n\n{text}\n" for name, text in sections.items())
    return f"---\nid: {doc_id}\ntitle: {title}\nstatus: {status}\n---\n\n# {title}\n\n{body}"


@pytest.fixture
def context(tmp_path):
    """A tiny context folder: two documents, one draft, and one planned entry with no file."""
    (tmp_path / "concepts").mkdir()
    (tmp_path / "concepts" / "fruit.md").write_text(
        doc("fruit", "Fruit", "canonical", {"Rules": "Apples and pears are fruit.", "Gotchas": "Tomatoes are confusing."}),
        encoding="utf-8")
    (tmp_path / "concepts" / "cars.md").write_text(
        doc("cars", "Cars", "draft", {"Rules": "A car has four wheels and an engine."}), encoding="utf-8")
    index = {"concepts": [
        {"id": "fruit", "path": "concepts/fruit.md", "summary": "x", "status": "canonical"},
        {"id": "cars", "path": "concepts/cars.md", "summary": "x", "status": "draft"},
        {"id": "ghost", "path": "concepts/ghost.md", "summary": "x", "status": "planned"},
    ]}
    (tmp_path / "index.yaml").write_text(yaml.safe_dump(index), encoding="utf-8")
    return tmp_path


def test_tokenize_drops_stopwords_and_matches_plurals():
    assert retrieve.tokenize("How are the deals counted?") == ["deal", "counted"]
    assert retrieve.tokenize("companies") == ["company"]


def test_documents_are_split_by_section_heading(context):
    chunks = retrieve.load_chunks(context)
    assert [(c.doc_id, c.section) for c in chunks] == [("fruit", "Rules"), ("fruit", "Gotchas"), ("cars", "Rules")]


def test_the_best_section_comes_first_with_its_document_and_status(context):
    hits = retrieve.retrieve("how many wheels does a car have", k=2, context_dir=context)
    assert hits[0]["doc_id"] == "cars" and hits[0]["status"] == "draft"
    assert hits[0]["section"] == "Rules"


def test_a_planned_entry_with_no_file_is_skipped(context):
    assert all(c.doc_id != "ghost" for c in retrieve.load_chunks(context))


def test_k_limits_the_number_of_sections(context):
    assert len(retrieve.retrieve("fruit and cars", k=1, context_dir=context)) == 1


def test_a_question_that_matches_nothing_returns_nothing(context):
    assert retrieve.retrieve("zzz qqq", context_dir=context) == []


def test_k_below_one_is_an_error(context):
    with pytest.raises(ValueError):
        retrieve.retrieve("fruit", k=0, context_dir=context)


def test_the_same_question_always_gives_the_same_answer(context):
    first = retrieve.retrieve("apples pears", context_dir=context)
    assert first == retrieve.retrieve("apples pears", context_dir=context)


def test_ranked_documents_lists_each_document_once(context):
    assert retrieve.ranked_documents("fruit apples pears tomatoes", context) == ["fruit"]


def test_retrieval_meets_the_targets_on_the_real_corpus():
    cases = yaml.safe_load((ROOT / "evals" / "retrieval_cases.yaml").read_text(encoding="utf-8"))["cases"]
    hit, mrr, misses = run_retrieval.score(cases, ROOT / "context")
    assert hit >= run_retrieval.TARGET_HIT_AT_3, misses
    assert mrr >= run_retrieval.TARGET_MRR, misses
