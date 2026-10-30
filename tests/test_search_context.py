"""Tests for agent/tools/search_context.py."""

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent" / "tools"))

import search_context as sc  # noqa: E402
from search_context import InvalidInput, search_context  # noqa: E402


def write_doc(path: Path, doc_id: str, status: str, text: str) -> None:
    path.write_text(
        f"---\nid: {doc_id}\ntitle: {doc_id.title()}\nstatus: {status}\n---\n\n# {doc_id}\n\n## Rules\n\n{text}\n",
        encoding="utf-8")


@pytest.fixture
def context(tmp_path):
    folder = tmp_path / "context"
    (folder / "concepts").mkdir(parents=True)
    write_doc(folder / "concepts" / "fruit.md", "fruit", "canonical", "Apples and pears are fruit.")
    write_doc(folder / "concepts" / "cars.md", "cars", "draft", "A car has four wheels.")
    write_doc(folder / "concepts" / "fax.md", "fax", "deprecated", "A fax machine sends pages by phone line.")
    index = {"concepts": [
        {"id": i, "path": f"concepts/{i}.md", "summary": "x", "status": s}
        for i, s in (("fruit", "canonical"), ("cars", "draft"), ("fax", "deprecated"))
    ]}
    (folder / "index.yaml").write_text(yaml.safe_dump(index), encoding="utf-8")
    return folder


def test_a_hit_has_document_status_section_text_and_score(context):
    out = search_context("what are apples", context_dir=context)
    assert out["count"] == 1
    hit = out["results"][0]
    assert (hit["doc_id"], hit["status"], hit["section"]) == ("fruit", "canonical", "Rules")
    assert "Apples" in hit["text"] and hit["score"] > 0
    assert "warning" not in hit  # a canonical document needs no caveat


def test_draft_and_deprecated_sections_carry_a_warning(context):
    draft = search_context("how many wheels on a car", context_dir=context)["results"][0]
    assert draft["status"] == "draft" and "draft" in draft["warning"]
    old = search_context("fax machine phone line", context_dir=context)["results"][0]
    assert old["status"] == "deprecated" and "deprecated" in old["warning"]


def test_k_limits_the_results(context):
    assert search_context("fruit car fax", k=1, context_dir=context)["count"] == 1


def test_no_match_is_an_empty_list_not_an_error(context):
    assert search_context("zzz qqq", context_dir=context) == {"results": [], "count": 0}


@pytest.mark.parametrize("question", ["", "   ", None, 42, ["apples"]])
def test_a_missing_or_wrong_type_of_question_is_rejected(context, question):
    with pytest.raises(InvalidInput):
        search_context(question, context_dir=context)


def test_a_very_long_question_is_rejected(context):
    with pytest.raises(InvalidInput, match="longer"):
        search_context("apples " * 100, context_dir=context)


@pytest.mark.parametrize("k", [0, -1, sc.MAX_K + 1, 2.5, "3", True, None])
def test_k_must_be_a_whole_number_in_range(context, k):
    with pytest.raises(InvalidInput):
        search_context("apples", k=k, context_dir=context)


def test_an_index_entry_pointing_outside_the_context_folder_is_an_error(context, tmp_path):
    write_doc(tmp_path / "outside.md", "outside", "canonical", "Secret text outside the folder.")
    index = {"concepts": [{"id": "outside", "path": "../outside.md", "summary": "x", "status": "canonical"}]}
    (context / "index.yaml").write_text(yaml.safe_dump(index), encoding="utf-8")
    with pytest.raises(ValueError, match="outside the context folder"):
        search_context("secret text", context_dir=context)


def test_the_real_corpus_answers_a_real_question():
    out = search_context("Are trial accounts counted as customers?")
    assert out["results"][0]["doc_id"] == "active-customer"
