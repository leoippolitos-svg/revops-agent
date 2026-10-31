"""Tests for tools/catalog.py, the run catalog and job health."""

import shutil
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import catalog  # noqa: E402


def test_the_real_catalog_passes_and_its_page_is_current():
    assert catalog.check(ROOT) == []
    assert (ROOT / "docs" / "run-catalog.md").read_text(encoding="utf-8").replace("\r\n", "\n") == catalog.render_page(ROOT)


def copy(tmp_path):
    shutil.copytree(ROOT / "catalog", tmp_path / "catalog")
    shutil.copytree(ROOT / ".github", tmp_path / ".github")
    for card in catalog.load_cards(ROOT):
        target = tmp_path / card["where"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()
    return tmp_path


def test_a_scheduled_workflow_without_a_card_is_reported(tmp_path):
    root = copy(tmp_path)
    (root / ".github" / "workflows" / "nightly.yml").write_text("on:\n  schedule:\n    - cron: '0 1 * * *'\n", encoding="utf-8")
    assert any("nightly.yml: runs on a schedule but has no card" in e for e in catalog.check(root))


def test_an_active_item_without_a_status_source_is_reported(tmp_path):
    root = copy(tmp_path)
    path = root / "catalog" / "revenue-snapshot.yml"
    card = yaml.safe_load(path.read_text(encoding="utf-8"))
    card["situation"] = "active"
    path.write_text(yaml.safe_dump(card), encoding="utf-8")
    assert any("an active item needs a status source" in e for e in catalog.check(root))


def card(**overrides):
    base = {"id": "x", "situation": "active",
            "status_source": {"type": "github_actions", "workflow": "x.yml", "expected_every_days": 1}}
    return {**base, **overrides}


def test_health_is_ok_failing_late_or_unknown():
    today = date(2026, 1, 10)
    ok = lambda wf: {"conclusion": "success", "createdAt": "2026-01-10T08:00:00Z"}
    failed = lambda wf: {"conclusion": "failure", "createdAt": "2026-01-10T08:00:00Z"}
    old = lambda wf: {"conclusion": "success", "createdAt": "2026-01-01T08:00:00Z"}
    none = lambda wf: None
    assert catalog.health(card(), ROOT, today, ok)["status"] == "ok"
    assert catalog.health(card(), ROOT, today, failed)["status"] == "failing"
    assert catalog.health(card(), ROOT, today, old)["status"] == "late"
    assert catalog.health(card(), ROOT, today, none)["status"] == "unknown"
    assert catalog.health(card(situation="stopped"), ROOT, today, failed)["status"] == "stopped"


def test_a_log_source_reads_the_date_of_the_newest_file(tmp_path):
    (tmp_path / "observability" / "logs").mkdir(parents=True)
    (tmp_path / "observability" / "logs" / "lead-routing-2026-01-09.md").write_text("x", encoding="utf-8")
    c = card(status_source={"type": "log", "pattern": "lead-routing-*.md"}, situation="manual")
    out = catalog.health(c, tmp_path, date(2026, 1, 10))
    assert out["status"] == "ok" and out["last_run"].startswith("2026-01-09")
