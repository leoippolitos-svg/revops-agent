"""Tests for tools/check_context_ab.py."""

import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_context_ab  # noqa: E402


def copy_repo(tmp_path: Path) -> Path:
    for rel in ("evals/context_ab", "context/index.yaml"):
        src, dst = ROOT / rel, tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst) if src.is_dir() else shutil.copy(src, dst)
    return tmp_path


def edit_questions(root: Path, change) -> None:
    path = root / "evals" / "context_ab" / "questions.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    change(data["questions"])
    path.write_text(yaml.safe_dump(data), encoding="utf-8")


def test_the_real_design_passes():
    assert check_context_ab.check(ROOT) == []


def test_unknown_document_and_missing_trap_are_reported(tmp_path):
    root = copy_repo(tmp_path)

    def change(questions):
        questions[0]["context_doc"] = "nope"
        questions[1]["trap"] = ""

    edit_questions(root, change)
    errors = check_context_ab.check(root)
    assert any("unknown context_doc 'nope'" in e for e in errors)
    assert any("missing trap" in e for e in errors)


def test_thin_checklist_and_uncovered_document_are_reported(tmp_path):
    root = copy_repo(tmp_path)
    edit_questions(root, lambda qs: qs[0].update(must_include=["only one"]))
    assert any("needs at least 2 must_include" in e for e in check_context_ab.check(root))
    edit_questions(root, lambda qs: [q.update(context_doc="mrr") for q in qs])
    assert any("no question depends on the document 'mql'" in e for e in check_context_ab.check(root))


def test_results_never_claim_an_unmeasured_number(tmp_path):
    root = copy_repo(tmp_path)
    results = root / "evals" / "context_ab" / "results.md"
    results.write_text(
        "| Date | Model | Commit | Questions | Without context | With context | Status |\n"
        "|---|---|---|---|---|---|---|\n"
        "| none | n/a | n/a | 14 | 0.4 | 0.9 | not run |\n"
        "| 2026-11-01 | m | abc | 14 | 0.4 | 1.7 | done |\n",
        encoding="utf-8")
    errors = check_context_ab.check(root)
    assert any("a 'not run' row has a score" in e for e in errors)
    assert any("score '1.7' must be between 0 and 1" in e for e in errors)
