"""Tests for tools/check_apps.py."""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_apps  # noqa: E402


def copy_repo(tmp_path: Path) -> Path:
    for rel in ("apps/revenue-snapshot", "pipeline/dbt/models/gold/schema.yml"):
        src, dst = ROOT / rel, tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst) if src.is_dir() else shutil.copy(src, dst)
    return tmp_path


def spec_path(root: Path) -> Path:
    return root / "apps" / "revenue-snapshot" / "SPEC.md"


def edit(root: Path, old: str, new: str) -> None:
    path = spec_path(root)
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_the_real_apps_pass():
    assert check_apps.check(ROOT) == []


def test_missing_spec_is_reported(tmp_path):
    root = copy_repo(tmp_path)
    spec_path(root).unlink()
    assert any("missing SPEC.md" in e for e in check_apps.check(root))


def test_missing_section_is_reported(tmp_path):
    root = copy_repo(tmp_path)
    edit(root, "## Screens", "## Pages")
    assert any("missing the section 'Screens'" in e for e in check_apps.check(root))


def test_ticked_item_on_an_unbuilt_app_is_reported(tmp_path):
    root = copy_repo(tmp_path)
    edit(root, "- [ ] Dependencies pinned", "- [x] Dependencies pinned")
    assert any("ticked but the app is not built" in e for e in check_apps.check(root))


def test_built_app_with_unticked_item_is_reported(tmp_path):
    root = copy_repo(tmp_path)
    edit(root, "Status: specified, not built", "Status: built")
    assert any("built but a checklist item is not ticked" in e for e in check_apps.check(root))


def test_reading_silver_or_a_missing_gold_table_is_reported(tmp_path):
    root = copy_repo(tmp_path)
    edit(root, "- `gold.mrr_monthly`", "- `silver.deal`\n- `gold.ghost_table`")
    errors = check_apps.check(root)
    assert any("apps read gold only" in e for e in errors)
    assert any("not a gold model" in e for e in errors)


def test_must_never_has_to_forbid_writes(tmp_path):
    root = copy_repo(tmp_path)
    edit(root, "- Write to any data source", "- Do something else")
    assert any("must forbid writing" in e for e in check_apps.check(root))
