"""Tests for the proposal generator, the account review narrative, the chat title and chunk summaries."""

import importlib.util
import json
import sys
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automations" / "_lib"))


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generate = load("automations/proposal-generator/generate.py", "proposal_generate")
narrate = load("automations/ebr-narrative/narrate.py", "ebr_narrate")
server = load("apps/agent-chat/server.py", "chat_server_titles")
ingest = load("agent/rag/ingest.py", "rag_ingest_summaries")
EXAMPLES = ROOT / "automations" / "proposal-generator" / "examples"


class Fixed:
    def __init__(self, reply):
        self.reply = reply

    def complete(self, model, system, messages, tools):
        return {"text": json.dumps(self.reply), "tool_call": None, "usage": {}}


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "lake.duckdb"
    con = duckdb.connect(str(path))
    con.execute("CREATE SCHEMA gold")
    con.execute("CREATE TABLE gold.deal_amount (deal_id INT, amount_usd INT)")
    con.execute("INSERT INTO gold.deal_amount VALUES (5, 12200)")
    con.execute("CREATE TABLE gold.account_health (company_id INT, latest_score INT, latest_band VARCHAR, latest_scored_at DATE)")
    con.execute("INSERT INTO gold.account_health VALUES (2, 38, 'red', '2025-12-04')")
    con.execute("CREATE TABLE gold.subscription_lifecycle (subscription_id INT, company_id INT, status VARCHAR, started_at DATE, ended_at DATE)")
    con.execute("INSERT INTO gold.subscription_lifecycle VALUES (1, 2, 'churned', '2025-08-06', '2025-12-22')")
    con.execute("CREATE TABLE gold.onboarding_progress (subscription_id INT, current_milestone VARCHAR, kickoff_at DATE, go_live_at DATE)")
    con.execute("INSERT INTO gold.onboarding_progress VALUES (1, 'go_live', '2025-08-10', '2025-09-20')")
    con.close()
    return path


REQUEST = {"request_id": "p1", "deal_id": 5, "company_name": "N", "notes_file": "meeting-D5.txt"}


def test_plans_follow_the_technician_rule():
    rules = generate.load_rules()
    assert [generate.plan_for(n, rules) for n in (8, 42, 140, None)] == ["starter", "growth", "scale", None]


def test_the_demo_proposal_is_assembled_from_checked_facts_and_the_deal_amount(db, tmp_path):
    out = generate.generate(REQUEST, EXAMPLES, db, False, tmp_path / "l")
    assert out["outcome"] == "drafted" and out["plan"] == "growth"
    assert "$12,200" in out["proposal"] and "2026-03-15" in out["proposal"] and "Nothing was sent" in out["proposal"]


@pytest.mark.parametrize("bad", [
    {"technicians": 500, "pain_points": [], "current_tool": None, "decision_date": None, "evidence": []},
    {"technicians": 42, "pain_points": ["world peace"], "current_tool": None, "decision_date": None, "evidence": []},
    {"technicians": 42, "pain_points": [], "current_tool": None, "decision_date": "2030-01-01", "evidence": []},
])
def test_a_fact_not_in_the_note_sends_the_proposal_to_review(db, tmp_path, monkeypatch, bad):
    monkeypatch.setattr(generate, "DemoExtractor", lambda: Fixed(bad))
    assert generate.generate(REQUEST, EXAMPLES, db, False, tmp_path / "l")["outcome"] == "needs review"


def test_the_narrative_uses_only_numbers_from_the_data_pack(db, tmp_path):
    out = narrate.narrate(2, db, False, tmp_path / "l")
    assert out["outcome"] == "written" and "38" in out["narrative"] and "recovery" in out["next_step"]


@pytest.mark.parametrize("narrative", ["Health is 99 and rising.", "We guarantee renewal."])
def test_a_narrative_with_a_new_number_or_a_guarantee_is_rejected(db, tmp_path, monkeypatch, narrative):
    monkeypatch.setattr(narrate, "DemoNarrator", lambda: Fixed({"narrative": narrative, "next_step": "Call them."}))
    assert narrate.narrate(2, db, False, tmp_path / "l")["outcome"] == "needs review"


def test_the_chat_title_is_short_and_falls_back_to_the_question(tmp_path, monkeypatch):
    assert server.title_for("How many MQLs did we get in September last year?", False, tmp_path / "x.jsonl") == \
        "How many MQLs did we get in"
    monkeypatch.setattr(server, "DemoTitler", lambda: Fixed({"title": "x" * 99}))
    assert server.title_for("short question", False, tmp_path / "x.jsonl") == "short question"


def test_chunk_summaries_are_one_short_line_and_only_on_request(tmp_path):
    summary = ingest.summarise("mql", "Definition", "An MQL is a lead Marketing flags. More text follows.")
    assert summary == "An MQL is a lead Marketing flags" and len(summary) <= 160
