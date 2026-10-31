"""Tests for tools/check_derived.py."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_derived  # noqa: E402


def make(tmp_path: Path, source_text: str, recorded: str | None = None) -> Path:
    (tmp_path / "docs").mkdir()
    source = tmp_path / "docs" / "long.md"
    source.write_text(source_text, encoding="utf-8")
    digest = recorded or check_derived.source_hash(source)
    (tmp_path / "docs" / "short.md").write_text(
        f"---\nderived_from: docs/long.md\nsource_sha256: {digest}\n---\n\n# Short\n", encoding="utf-8")
    return tmp_path


def test_the_real_copies_are_current():
    assert check_derived.check(ROOT) == []


def test_a_matching_copy_passes(tmp_path):
    assert check_derived.check(make(tmp_path, "# Long\n")) == []


def test_a_changed_source_is_reported(tmp_path):
    root = make(tmp_path, "# Long\n")
    (root / "docs" / "long.md").write_text("# Long, edited\n", encoding="utf-8")
    assert any("changed since this copy" in p for p in check_derived.check(root))


def test_line_endings_do_not_count_as_a_change(tmp_path):
    root = make(tmp_path, "# Long\nline\n")
    (root / "docs" / "long.md").write_bytes(b"# Long\r\nline\r\n")
    assert check_derived.check(root) == []


def test_it_warns_by_default_and_fails_only_when_strict(tmp_path, monkeypatch):
    root = make(tmp_path, "# Long\n", recorded="0" * 64)
    monkeypatch.chdir(root)
    assert check_derived.main([]) == 0 and check_derived.main(["--strict"]) == 1
