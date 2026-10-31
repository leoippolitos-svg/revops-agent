"""Tests for onboarding-advance, churn-deactivation and deal-amount, on hand-built gold tables."""

import importlib.util
import json
from datetime import date
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(rel):
    spec = importlib.util.spec_from_file_location(Path(rel).stem + "_under_test", ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


advance = load("automations/onboarding-advance/advance.py")
deactivate = load("automations/churn-deactivation/deactivate.py")
recalculate = load("automations/deal-amount/recalculate.py")


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "lake.duckdb"
    con = duckdb.connect(str(path))
    con.execute("CREATE SCHEMA gold")
    con.execute("CREATE TABLE gold.onboarding_progress (subscription_id INT, current_milestone VARCHAR)")
    con.execute("INSERT INTO gold.onboarding_progress VALUES (1, 'kickoff'), (2, 'configured'), (3, 'kickoff')")
    con.execute("CREATE TABLE gold.subscription_lifecycle (subscription_id INT, company_id INT, ended_at DATE, "
                "other_active_subscriptions INT)")
    con.execute("INSERT INTO gold.subscription_lifecycle VALUES (10, 100, '2026-01-01', 0), "
                "(11, 101, '2026-01-15', 0), (12, 102, '2026-01-01', 1)")
    con.execute("CREATE TABLE gold.deal_amount (deal_id INT, stage VARCHAR, amount_usd INT)")
    con.execute("INSERT INTO gold.deal_amount VALUES (5, 'proposal', 12200), (36, 'closed_won', 9000)")
    con.close()
    return path


@pytest.fixture(autouse=True)
def switches(monkeypatch):
    monkeypatch.setenv("ONBOARDING_ADVANCE_ENABLED", "true")
    monkeypatch.setenv("CHURN_DEACTIVATION_ENABLED", "true")


def test_onboarding_rules_come_from_the_context_document():
    assert advance.load_rules() == {"workspace_configured": ("kickoff", "configured"),
                                    "first_job_completed": ("configured", "go_live")}


def test_onboarding_advances_only_in_order_and_counts_its_own_moves():
    events = [{"event_id": "a", "subscription_id": 1, "event": "workspace_configured"},
              {"event_id": "b", "subscription_id": 1, "event": "first_job_completed"},
              {"event_id": "c", "subscription_id": 3, "event": "first_job_completed"},
              {"event_id": "d", "subscription_id": 99, "event": "workspace_configured"}]
    out = {d["event_id"]: (d["outcome"], d["to"]) for d in
           advance.decide(events, {"1": "kickoff", "3": "kickoff"}, advance.load_rules())}
    assert out == {"a": ("advance", "configured"), "b": ("advance", "go_live"),
                   "c": ("needs review", "-"), "d": ("needs review", "-")}


def test_onboarding_write_logs_each_move_once(db, tmp_path):
    events = tmp_path / "e.json"
    events.write_text(json.dumps([{"event_id": "a", "subscription_id": 2, "event": "first_job_completed", "at": "2026-01-17"}]),
                      encoding="utf-8")
    args = ["--events", str(events), "--db", str(db), "--logs", str(tmp_path / "logs"), "--date", "2026-01-17", "--write"]
    assert advance.main(args) == 0 and advance.main(args) == 0
    log = (tmp_path / "logs" / "movements-2026-01-17.md").read_text(encoding="utf-8")
    assert log.count("| a |") == 1 and "configured | go_live" in log


def test_churn_waits_out_the_grace_period_and_keeps_companies_with_another_subscription(db):
    rules = deactivate.load_rules()
    out = {d["subscription_id"]: d["outcome"] for d in
           deactivate.decide(deactivate.read_churned(db), rules, date(2026, 1, 18))}
    assert rules == {"grace_days": 7} and out == {10: "deactivate", 11: "wait", 12: "keep"}


def test_churn_write_logs_workspace_and_company_and_needs_the_kill_switch(db, tmp_path, monkeypatch):
    args = ["--db", str(db), "--logs", str(tmp_path / "logs"), "--date", "2026-01-18", "--write"]
    monkeypatch.delenv("CHURN_DEACTIVATION_ENABLED")
    assert deactivate.main(args) == 0 and not (tmp_path / "logs").exists()  # shadow run
    monkeypatch.setenv("CHURN_DEACTIVATION_ENABLED", "true")
    deactivate.main(args)
    log = (tmp_path / "logs" / "movements-2026-01-18.md").read_text(encoding="utf-8")
    assert "deactivate-10" in log and "inactive-100" in log and "deactivate-12" not in log


def test_amount_proposals_name_their_approvers_and_never_touch_closed_deals(db):
    events = [{"event_id": "x", "deal_id": 5, "list_amount_usd": 14000, "discount_percent": 10},
              {"event_id": "y", "deal_id": 5, "list_amount_usd": 20000, "discount_percent": 30},
              {"event_id": "z", "deal_id": 36, "list_amount_usd": 9000, "discount_percent": 5}]
    out = {r["event_id"]: r for r in recalculate.propose(events, recalculate.read_deals(db), recalculate.load_rules())}
    assert out["x"]["outcome"] == "proposed" and out["x"]["net_usd"] == 12600 and "sales lead" not in out["x"]["why"]
    assert "Finance and the sales lead" in out["y"]["why"] and out["z"]["outcome"] == "no change"


@pytest.mark.parametrize("event", [{"deal_id": 5, "list_amount_usd": -1, "discount_percent": 10},
                                   {"deal_id": 5, "list_amount_usd": 100, "discount_percent": 100}])
def test_an_invalid_discount_event_stops_the_run(event):
    with pytest.raises(recalculate.AmountError):
        recalculate.check_events([event])


def test_the_amount_script_has_no_way_to_write_to_the_crm():
    code = (ROOT / "automations" / "deal-amount" / "recalculate.py").read_text(encoding="utf-8")
    assert "WriteControls" not in code and "read_only=True" in code
