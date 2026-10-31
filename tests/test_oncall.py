"""Tests for oncall/oncall.py and oncall/watchdog.py. Nothing calls gh, a model or Slack."""

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "oncall"))

import oncall  # noqa: E402
import watchdog  # noqa: E402

ON = {"ONCALL_ACTIONS_ENABLED": "true", "WATCHDOG_RECOVERY_ENABLED": "true"}


def captured():
    sent = []

    def notifier(item, title, lines, write, **kwargs):
        sent.append({"item": item, "title": title, "lines": lines})
        return {"status": "sent"}
    return sent, notifier


def entry(**overrides):
    base = {"id": "weekly-audit", "cause": "timeout reading the lakehouse", "resolved": True, "what_i_did": "",
            "pr_url": "", "actions": [{"type": "rerun", "workflow": "weekly-audit.yml"}], "human_step": ""}
    return {**base, **overrides}


def test_problems_lists_only_failing_or_late_items_with_their_card():
    health = {"items": [{"id": "weekly-audit", "status": "failing"}, {"id": "watchdog", "status": "ok"},
                        {"id": "not-a-card", "status": "failing"}]}
    found = oncall.problems(health)
    assert [p["id"] for p in found] == ["weekly-audit"] and found[0]["card"]["rerun_ok"] is True


def test_the_report_is_checked_and_a_silent_item_still_gets_a_line():
    report, dropped = oncall.check_report([entry(), {"id": "x"}, entry(id="ghost")], {"weekly-audit", "oncall"})
    assert [e["id"] for e in report] == ["weekly-audit", "oncall"]
    assert any("malformed" in d for d in dropped) and any("ghost" in d for d in dropped)


def test_only_a_rerun_of_the_items_own_rerun_ok_workflow_is_allowed():
    cards = {c["id"]: c for c in oncall.catalog.load_cards()}
    ok, refused = oncall.allowed_reruns(entry(actions=[
        {"type": "rerun", "workflow": "weekly-audit.yml"}, {"type": "rerun", "workflow": "ci.yml"},
        {"type": "delete_branch", "workflow": "x"}]), cards)
    assert ok == ["weekly-audit.yml"] and len(refused) == 2
    _, refused = oncall.allowed_reruns(entry(id="revenue-snapshot"), cards)
    assert refused  # the card has no rerun_ok


def test_execute_runs_allowed_reruns_and_posts_one_message_per_item():
    runs, (sent, notifier) = [], captured()
    out = oncall.execute([entry(pr_url="https://example.com/pr/1")], write=True, runner=runs.append,
                         notifier=notifier, env=ON)
    assert runs == ["weekly-audit.yml"] and out[0]["reruns"] == ["weekly-audit.yml"]
    assert len(sent) == 1 and any("Pull request" in line for line in sent[0]["lines"])


def test_without_the_kill_switch_nothing_is_rerun_and_the_message_says_so():
    runs, (sent, notifier) = [], captured()
    oncall.execute([entry()], write=True, runner=runs.append, notifier=notifier, env={})
    assert runs == [] and any("not run (shadow)" in line for line in sent[0]["lines"])


def late(workflow):
    return {"conclusion": "success", "createdAt": "2025-12-01T07:00:00Z"}


def test_watchdog_recovers_a_late_rerun_ok_job_without_alerting():
    runs, (sent, notifier) = [], captured()
    out = watchdog.watch(True, today=date(2026, 1, 10), github=late, runner=runs.append, notifier=notifier, env=ON)
    recovered = {r["id"] for r in out if r["action"] == "rerun started"}
    assert "weekly-audit" in recovered and "weekly-audit.yml" in runs
    assert "weekly-audit" not in {s["item"] for s in sent}


def test_watchdog_alerts_when_a_late_job_cannot_be_recovered():
    runs, (sent, notifier) = [], captured()
    watchdog.watch(True, today=date(2026, 1, 10), github=late, runner=runs.append, notifier=notifier, env=ON)
    assert "oncall" in {s["item"] for s in sent}  # active and late, but its card has no rerun_ok
