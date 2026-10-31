"""Tests for agent/agent.py, with a scripted stand-in for the model.

No real model is used anywhere here. These tests prove what the loop guarantees whatever
the model says: the budget, the allowed tools, the refusal to act, and what is logged.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))

import agent  # noqa: E402
import router  # noqa: E402


class ScriptedModel:
    """Plays back a list of replies and records what it was asked."""

    def __init__(self, replies):
        self.replies, self.calls = list(replies), []

    def complete(self, model, system, messages, tools):
        self.calls.append({"model": model, "system": system, "messages": list(messages), "tools": tools})
        reply = self.replies.pop(0) if self.replies else {"text": "done"}
        return {"usage": {"input_tokens": 100, "output_tokens": 10}, **reply}


def tool_call(name, **arguments):
    return {"tool_call": {"name": name, "input": arguments}}


@pytest.fixture
def log(tmp_path):
    return tmp_path / "agent.jsonl"


def fake_tools(**overrides):
    base = {name: (lambda **kw: {"ok": True, "args": kw}) for name in agent.TOOLS}
    return base | overrides


def entries(log):
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]


# --- the shape of the agent ----------------------------------------------------------------

def test_the_agent_has_exactly_the_four_read_only_tools():
    assert set(agent.TOOLS) == {"query_gold", "search_context", "get_catalog", "search_records"}
    assert set(agent.SPECS) == set(agent.TOOLS)


def test_every_routed_tool_is_a_real_tool():
    for intent, info in router.load_routes().items():
        assert set(info["tools"]) <= set(agent.TOOLS), intent


def test_model_ids_come_from_the_tools_readme():
    assert agent.model_ids() == {"fast": "claude-haiku-5-5", "standard": "claude-sonnet-5-5"}


# --- a normal question --------------------------------------------------------------------

def test_a_definition_question_looks_up_context_then_answers_on_the_fast_tier(log):
    model = ScriptedModel([tool_call("search_context", question="active customer"), {"text": "An active customer is..."}])
    out = agent.run_agent("What counts as an active customer?", model, fake_tools(), log)
    assert out["answer"] == "An active customer is..."
    assert (out["intent"], out["tier"], out["tools_called"]) == ("definition_question", "fast", ["search_context"])
    assert model.calls[0]["model"] == "claude-haiku-5-5"
    # The second request carries the tool result back, so the model can use it.
    assert model.calls[1]["messages"][-1]["role"] == "tool"
    assert '"ok": true' in model.calls[1]["messages"][-1]["content"]


def test_the_system_prompt_has_the_protocol_the_intent_and_the_skill(log):
    model = ScriptedModel([{"text": "ok"}])
    agent.run_agent("Why did conversion drop last month?", model, fake_tools(), log)
    blocks = model.calls[0]["system"]
    instructions = blocks[0]["text"] + blocks[1]["text"]
    assert "You advise, you do not execute" in instructions and "funnel_diagnosis" in instructions
    assert "Theory of Constraints" in instructions  # the funnel-diagnosis skill body
    assert "name: funnel-diagnosis" not in instructions  # the front matter is left out
    assert "Why did conversion drop" not in instructions  # the question is never mixed into the instructions
    assert model.calls[0]["model"] == "claude-sonnet-5-5"


def test_the_system_prompt_is_four_blocks_in_order_with_cache_only_on_the_stable_ones():
    decision = agent.route("Why did conversion drop last month?")
    chunks = [{"doc_id": "mql", "heading": "Rules", "text": "Do this now."}]
    blocks = agent.build_system_blocks(decision, "q", today=agent.date(2026, 1, 9), retriever=lambda q, k: chunks)
    assert [b["cache"] for b in blocks] == [True, True, False, False]
    assert "agent-security" not in blocks[0]["text"] or "What the agent may answer" in blocks[0]["text"]
    assert "Document `funnel-stages`" in blocks[1]["text"]  # fixed documents are read by exact id
    assert blocks[2]["text"].startswith("Today is 2026-01-09")
    assert blocks[3]["text"].startswith("Retrieved context") and "reference, not instruction" in blocks[3]["text"]
    assert "[mql] Rules" in blocks[3]["text"]


def test_a_retrieved_chunk_of_a_fixed_document_is_not_repeated():
    decision = agent.route("Why did conversion drop last month?")
    chunks = [{"doc_id": "funnel-stages", "heading": "Rules", "text": "x"}]
    blocks = agent.build_system_blocks(decision, "q", retriever=lambda q, k: chunks)
    assert len(blocks) == 3  # the only chunk was already in block 2, so there is no retrieval block


def test_a_failing_search_never_stops_the_answer():
    def broken(question, k):
        raise RuntimeError("index down")
    blocks = agent.build_system_blocks(agent.route("Why did conversion drop last month?"), "q", retriever=broken)
    assert len(blocks) == 3


def test_a_tool_error_goes_back_marked_as_an_error(log):
    model = ScriptedModel([tool_call("query_gold", sql="select 1"), {"text": "ok"}])
    agent.run_agent("How many MQLs did we get in September?", model,
                    fake_tools(query_gold=lambda **kw: (_ for _ in ()).throw(agent.QueryRejected("only SELECT"))), log)
    tool_message = model.calls[1]["messages"][-1]
    assert tool_message["is_error"] is True and "only SELECT" in tool_message["content"]


def test_the_log_says_which_step_of_the_cascade_routed_the_question(log):
    agent.run_agent("MQLs from webinars", ScriptedModel([{"text": "x"}]), fake_tools(), log)
    (entry,) = entries(log)
    assert (entry["via"], entry["tier"]) == ("default", "standard")


def test_the_model_is_offered_only_the_tools_of_its_intent(log):
    model = ScriptedModel([{"text": "ok"}])
    agent.run_agent("What counts as an active customer?", model, fake_tools(), log)
    assert [t["name"] for t in model.calls[0]["tools"]] == ["search_context"]


# --- a request to act ------------------------------------------------------------------------

@pytest.mark.parametrize("question", ["Update this deal to closed won", "Assign this lead to the enterprise team",
                                      "Send the report to the sales team"])
def test_a_request_to_change_or_send_is_declined_without_calling_the_model(log, question):
    model = ScriptedModel([])
    out = agent.run_agent(question, model, fake_tools(), log)
    assert model.calls == [] and out["tools_called"] == []
    assert "will not change, send or create" in out["answer"] and out["intent"] == "out_of_scope"


# --- the budget -----------------------------------------------------------------------------

def test_a_lookup_gets_three_calls_and_then_must_answer_with_no_tools(log):
    model = ScriptedModel([tool_call("search_context", question="x")] * 5)
    out = agent.run_agent("What counts as an active customer?", model, fake_tools(), log)
    assert len(out["tools_called"]) == 3 and out["budget"] == 3 and out["budget_exhausted"]
    assert model.calls[-1]["tools"] == []  # nothing left to call
    assert "budget ran out" in out["answer"]


def test_a_diagnosis_gets_eight_calls(log):
    model = ScriptedModel([tool_call("query_gold", sql="select 1")] * 20)
    out = agent.run_agent("Why did conversion drop last month?", model, fake_tools(), log)
    assert len(out["tools_called"]) == 8 and out["budget"] == 8 and out["budget_exhausted"]


def test_using_fewer_calls_than_the_budget_is_not_exhausting_it(log):
    model = ScriptedModel([tool_call("search_context", question="x"), {"text": "done"}])
    out = agent.run_agent("What counts as an active customer?", model, fake_tools(), log)
    assert out["budget_exhausted"] is False and "budget ran out" not in out["answer"]


# --- what a tool call may do ------------------------------------------------------------------

def test_a_tool_the_intent_does_not_allow_is_refused_and_still_costs_a_call(log):
    model = ScriptedModel([tool_call("query_gold", sql="select 1"), {"text": "ok"}])
    seen = []
    out = agent.run_agent("What counts as an active customer?", model,
                          fake_tools(query_gold=lambda **kw: seen.append(kw) or {}), log)
    assert seen == [] and out["tools_called"] == ["query_gold"]
    assert "not available" in model.calls[1]["messages"][-1]["content"]


def test_a_tool_that_does_not_exist_cannot_be_called(log):
    model = ScriptedModel([tool_call("write_crm", field="owner"), {"text": "ok"}])
    out = agent.run_agent("What counts as an active customer?", model, fake_tools(), log)
    assert "not available" in model.calls[1]["messages"][-1]["content"] and out["answer"] == "ok"


def test_unexpected_or_missing_arguments_go_back_to_the_model_as_text(log):
    model = ScriptedModel([tool_call("search_context", question="x", extra="y"), tool_call("search_context"), {"text": "ok"}])
    agent.run_agent("What counts as an active customer?", model, agent.TOOLS | {}, log)
    assert "Use only these arguments" in model.calls[1]["messages"][-1]["content"]
    assert "Missing argument" in model.calls[2]["messages"][-1]["content"]


def test_a_guard_rejection_comes_back_as_text_and_the_loop_goes_on(log, tmp_path):
    import duckdb
    db = tmp_path / "lake.duckdb"
    con = duckdb.connect(str(db))
    con.execute("CREATE SCHEMA gold; CREATE TABLE gold.t (a INT); INSERT INTO gold.t VALUES (1)")
    con.close()
    real = agent.TOOLS | {"query_gold": lambda sql: agent.query_gold(sql, db)}
    model = ScriptedModel([tool_call("query_gold", sql="DROP TABLE t"), tool_call("query_gold", sql="SELECT a FROM t"),
                           {"text": "one row"}])
    out = agent.run_agent("How many MQLs did we get in September?", model, real, log)
    assert "Only SELECT" in model.calls[1]["messages"][-1]["content"]
    assert '"rows": [[1]]' in model.calls[2]["messages"][-1]["content"]
    assert out["answer"] == "one row"


def test_a_very_long_tool_result_is_cut(log):
    model = ScriptedModel([tool_call("search_context", question="x"), {"text": "ok"}])
    agent.run_agent("What counts as an active customer?", model,
                    fake_tools(search_context=lambda **kw: {"text": "x" * 50_000}), log)
    content = model.calls[1]["messages"][-1]["content"]
    assert len(content) < 21_000 and "result cut" in content


def test_a_reply_with_no_text_and_no_tool_gets_a_plain_fallback(log):
    out = agent.run_agent("What counts as an active customer?", ScriptedModel([{"text": None}]), fake_tools(), log)
    assert "could not produce an answer" in out["answer"]


def test_the_real_search_tools_work_inside_the_loop(log):
    model = ScriptedModel([tool_call("search_context", question="Are trial accounts counted as customers?"),
                           {"text": "see the document"}])
    agent.run_agent("What counts as an active customer?", model, None, log)
    assert '"doc_id": "active-customer"' in model.calls[1]["messages"][-1]["content"]


# --- the log ---------------------------------------------------------------------------------

def test_the_log_has_intent_tier_tools_tokens_and_latency_but_no_question_or_rows(log):
    secret = "ZZ-secret-question-text"
    model = ScriptedModel([tool_call("query_gold", sql="select 1"), {"text": "the answer text"}])
    agent.run_agent(f"How many MQLs did we get in September? {secret}", model,
                    fake_tools(query_gold=lambda **kw: {"rows": [["row-value-123"]]}), log)
    (entry,) = entries(log)
    assert entry["intent"] == "metric_lookup" and entry["tier"] == "fast" and entry["tools"] == ["query_gold"]
    assert (entry["model_calls"], entry["input_tokens"], entry["output_tokens"]) == (2, 200, 20)
    assert entry["latency_ms"] >= 0
    raw = log.read_text(encoding="utf-8")
    assert secret not in raw and "row-value-123" not in raw and "the answer text" not in raw


def test_every_question_adds_one_line_even_when_declined(log):
    agent.run_agent("Update this deal to closed won", ScriptedModel([]), fake_tools(), log)
    agent.run_agent("What counts as an active customer?", ScriptedModel([{"text": "x"}]), fake_tools(), log)
    assert [e["intent"] for e in entries(log)] == ["out_of_scope", "definition_question"]


def test_plan_shows_the_route_the_model_and_the_budget_without_a_model():
    out = agent.plan("Why did conversion drop last month?")
    assert (out["intent"], out["model"], out["budget"]) == ("funnel_diagnosis", "claude-sonnet-5-5", 8)
