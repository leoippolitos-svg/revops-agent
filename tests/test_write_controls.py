"""Tests for automations/_lib/controls.py and how the writing automations use it."""

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automations" / "_lib"))

from controls import ControlsError, WriteControls, writeback_cap  # noqa: E402


def controls(write=True, enabled=True, cap=10, breaker=3):
    env = {"DEMO_ENABLED": "true"} if enabled else {}
    return WriteControls("demo", write, env=env, cap=cap, breaker_limit=breaker)


def test_without_write_it_is_a_dry_run_and_writes_nothing():
    c = controls(write=False)
    assert c.mode == "dry run" and c.apply(["a"], lambda i: 1 / 0, lambda i: True).applied == []


def test_write_without_the_kill_switch_is_a_shadow_run():
    written = []
    c = controls(enabled=False)
    out = c.apply(["a", "b"], written.append, lambda i: True)
    assert c.mode == "shadow" and written == [] and out.applied == [] and "DEMO_ENABLED" in c.describe()


def test_the_cap_stops_writes_and_the_rest_needs_review():
    written = []
    out = controls(cap=2).apply(["a", "b", "c"], written.append, lambda i: True)
    assert written == ["a", "b"] and out.needs_review == {"c": "over the cap of 2 writes per run"}


def test_three_failures_in_a_row_open_the_breaker_and_nothing_more_is_tried():
    tried = []

    def failing(item):
        tried.append(item)
        raise RuntimeError("api down")
    out = controls(breaker=3).apply(["a", "b", "c", "d", "e"], failing, lambda i: True)
    assert tried == ["a", "b", "c"] and out.breaker_open
    assert out.needs_review["d"].startswith("not attempted") and out.needs_review["a"] == "write failed: api down"


def test_a_success_resets_the_failure_count():
    def flaky(item):
        if item in ("a", "b", "d", "e"):
            raise RuntimeError("x")
    out = controls(breaker=3).apply(["a", "b", "c", "d", "e", "f"], flaky, lambda i: True)
    assert not out.breaker_open and out.applied == ["c", "f"]


def test_a_write_that_cannot_be_read_back_needs_review():
    out = controls().apply(["a", "b"], lambda i: None, lambda i: i == "a")
    assert out.applied == ["a"] and "check after writing" in out.needs_review["b"]


def test_the_cap_and_the_authorisation_come_from_the_write_back_rules():
    assert writeback_cap("lead-routing") == 50 and writeback_cap("closed-won-provisioning") == 20


def test_an_automation_without_authorisation_cannot_write():
    with pytest.raises(ControlsError, match="no RECURRING-AUTHORIZATION"):
        writeback_cap("mass-update")


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_lead_routing_with_write_but_no_kill_switch_writes_nothing(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("LEAD_ROUTING_ENABLED", raising=False)
    route = load(ROOT / "automations" / "lead-routing" / "route.py")
    leads = tmp_path / "leads.json"
    leads.write_text(json.dumps([{"lead_id": "L1", "company_id": "C1", "segment": "smb"}]), encoding="utf-8")
    monkeypatch.setattr(route, "read_workload", lambda db: {"6": {"team": "sales", "open_deals": 0}})
    assert route.main(["--leads", str(leads), "--logs", str(tmp_path / "logs"), "--write"]) == 0
    assert "shadow run" in capsys.readouterr().out and not (tmp_path / "logs").exists()


def test_a_deal_won_long_ago_is_never_back_filled():
    provision = load(ROOT / "automations" / "closed-won-provisioning" / "provision.py")
    from datetime import date
    deal = {"deal_id": "D1", "stage": "closed_won", "company_id": "C1", "closed_won_at": "2025-10-01"}
    outcome, reason = provision.decide(deal, provision.load_rules(), date(2026, 1, 9))
    assert outcome == "needs review" and "never back-filled" in reason
