"""Tests for tools/check_evals.py."""

import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_evals  # noqa: E402


def copy_repo(tmp_path: Path) -> Path:
    """A minimal copy with only what the check reads."""
    for rel in ("evals", "context/index.yaml", "agent/directives/routing.md"):
        src, dst = ROOT / rel, tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst) if src.is_dir() else shutil.copy(src, dst)
    return tmp_path


def test_the_real_repository_passes():
    assert check_evals.check(ROOT) == []


def test_unknown_intent_is_reported(tmp_path):
    root = copy_repo(tmp_path)
    path = root / "evals" / "router_cases.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["cases"][0]["intent"] = "made_up"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    errors = check_evals.check(root)
    assert any("unknown intent 'made_up'" in e for e in errors)


def test_unknown_document_and_too_few_cases_are_reported(tmp_path):
    root = copy_repo(tmp_path)
    path = root / "evals" / "retrieval_cases.yaml"
    path.write_text(yaml.safe_dump({"cases": [{"question": "q", "expected": "nope"}]}), encoding="utf-8")
    errors = check_evals.check(root)
    assert any("minimum is 40" in e for e in errors)
    assert any("unknown document 'nope'" in e for e in errors)
    assert any("no case covers the document 'mrr'" in e for e in errors)


def test_duplicated_question_is_reported(tmp_path):
    root = copy_repo(tmp_path)
    path = root / "evals" / "router_cases.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["cases"][1]["question"] = data["cases"][0]["question"]
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    assert any("duplicated question" in e for e in check_evals.check(root))
