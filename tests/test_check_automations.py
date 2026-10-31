"""Tests for tools/check_automations.py."""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_automations  # noqa: E402


def copy_repo(tmp_path: Path) -> Path:
    for rel in ("automations/funnel-review", "automations/audits", "pipeline/dbt/models/gold/schema.yml"):
        src, dst = ROOT / rel, tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst) if src.is_dir() else shutil.copy(src, dst)
    return tmp_path


def spec_path(root: Path, name: str = "funnel-review") -> Path:
    return root / "automations" / name / "SPEC.md"


def edit(root: Path, old: str, new: str, name: str = "funnel-review") -> None:
    path = spec_path(root, name)
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_the_real_automations_pass():
    assert check_automations.check(ROOT) == []


def test_missing_spec_is_reported(tmp_path):
    root = copy_repo(tmp_path)
    spec_path(root).unlink()
    assert any("missing SPEC.md" in e for e in check_automations.check(root))


def test_missing_section_is_reported(tmp_path):
    root = copy_repo(tmp_path)
    edit(root, "## Failure behavior", "## What if it fails")
    assert any("missing the section 'Failure behavior'" in e for e in check_automations.check(root))


def test_ticked_item_on_an_unbuilt_automation_is_reported(tmp_path):
    root = copy_repo(tmp_path)
    edit(root, "Status: built", "Status: specified, not built")  # the real spec is built and fully ticked
    assert any("ticked but the automation is not built" in e for e in check_automations.check(root))


def test_built_automation_with_unticked_item_is_reported(tmp_path):
    root = copy_repo(tmp_path)
    edit(root, "- [x] Idempotent", "- [ ] Idempotent", name="audits")
    assert any("built but a checklist item is not ticked" in e for e in check_automations.check(root))


def test_reading_silver_or_a_missing_gold_table_is_reported(tmp_path):
    root = copy_repo(tmp_path)
    edit(root, "- `gold.funnel_stage_monthly`", "- `silver.deal`\n- `gold.ghost_table`")
    errors = check_automations.check(root)
    assert any("automations read gold only" in e for e in errors)
    assert any("not a gold model" in e for e in errors)


def test_must_never_has_to_forbid_writes(tmp_path):
    root = copy_repo(tmp_path)
    edit(root, "- Write to any data source", "- Do something else")
    assert any("must forbid writing" in e for e in check_automations.check(root))
