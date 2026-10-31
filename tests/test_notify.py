"""Tests for observability/notify.py. Nothing is ever posted: no webhook is set."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "observability"))

import notify  # noqa: E402

ON = {"SLACK_ALERTS_ENABLED": "true"}


def test_the_message_is_built_from_a_template():
    message = notify.build_message("weekly-audit", "Flags rose", ["Deals without a company: 6"], None)
    assert message["text"] == "*Flags rose* (weekly-audit)\n- Deals without a company: 6"


def test_dry_run_and_shadow_write_nothing(tmp_path):
    assert notify.send("a", "t", ["l"], write=False, logs=tmp_path, env=ON)["status"] == "dry run"
    assert notify.send("a", "t", ["l"], write=True, logs=tmp_path, env={})["status"] == "shadow"
    assert not list(tmp_path.iterdir())


def test_the_first_alert_opens_a_thread_and_the_next_replies_in_it(tmp_path):
    first = notify.send("weekly-audit", "Flags rose", ["a"], write=True, logs=tmp_path, env=ON, today="2026-01-12")
    second = notify.send("weekly-audit", "Running again", ["b"], write=True, logs=tmp_path, env=ON, today="2026-01-12")
    channel = (tmp_path / "slack-2026-01-12.md").read_text(encoding="utf-8")
    assert first["status"] == "sent" and second["thread"] == first["thread"]
    assert "new thread" in channel and f"reply in {first['thread']}" in channel


def test_a_webhook_on_another_host_is_refused_and_needs_review(tmp_path):
    env = {**ON, "SLACK_WEBHOOK_URL": "https://example.com/steal"}
    result = notify.send("a", "t", ["l"], write=True, logs=tmp_path, env=env)
    assert result["status"].startswith("needs review") and "allowlist" in result["status"]


def test_a_webhook_post_only_goes_to_slack(monkeypatch):
    with pytest.raises(ValueError, match="allowlist"):
        notify._post("http://169.254.169.254/latest", "x")
