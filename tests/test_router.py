"""Tests for agent/router.py and evals/run_router.py."""

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))
sys.path.insert(0, str(ROOT / "evals"))

import router  # noqa: E402
import run_router  # noqa: E402
from router import route  # noqa: E402


def test_every_intent_in_routing_md_has_tools_a_tier_and_a_skill_field():
    routes = router.load_routes()
    assert set(routes) == {"metric_lookup", "trend_analysis", "funnel_diagnosis", "definition_question",
                           "data_quality", "past_work_lookup", "report_request", "out_of_scope"}
    assert routes["funnel_diagnosis"] == {
        "tools": ["search_context", "query_gold", "search_records", "get_map"], "tier": "standard", "skill": "funnel-diagnosis"}
    assert routes["metric_lookup"]["skill"] is None
    assert routes["out_of_scope"]["tools"] == []


def test_a_route_carries_the_tools_tier_and_skill_of_its_intent():
    out = route("Why did conversion drop last month?")
    assert out["intent"] == "funnel_diagnosis" and out["tier"] == "standard"
    assert out["skill"] == "funnel-diagnosis" and "search_records" in out["tools"]
    assert out["reason"]


def test_the_tools_come_from_routing_md_not_from_the_code(tmp_path):
    changed = tmp_path / "routing.md"
    text = (ROOT / "agent" / "directives" / "routing.md").read_text(encoding="utf-8")
    changed.write_text(text.replace("| search_context | fast | — |", "| search_context, get_catalog | fast | — |"), encoding="utf-8")
    assert route("What counts as an active customer?", changed)["tools"] == ["search_context", "get_catalog"]


@pytest.mark.parametrize("question, intent", [
    ("Update this deal to closed won", "out_of_scope"),
    ("Send the report to the sales team", "out_of_scope"),    # refused before it is a report
    ("Write me a poem about revenue", "out_of_scope"),       # mentions revenue, still off topic
    ("What is the capital of France?", "out_of_scope"),      # no revenue word at all
    ("Create a workspace for the deal we just closed", "out_of_scope"),
    ("Write a monthly revenue report", "report_request"),
    ("Did we analyze churn in enterprise before?", "past_work_lookup"),
    ("Why does MRR differ from the invoices total?", "data_quality"),
    ("What is the difference between new and expansion MRR?", "definition_question"),
    ("Why did conversion drop last month?", "funnel_diagnosis"),
    ("Why did churn go up in Q3?", "trend_analysis"),
    ("How has MRR moved this year?", "trend_analysis"),
    ("How many MQLs did we get in September?", "metric_lookup"),
])
def test_questions_reach_the_intent_the_rules_promise(question, intent):
    assert route(question)["intent"] == intent


def test_an_unclear_question_about_revenue_falls_to_the_default_on_the_standard_tier():
    out = route("MQLs from webinars")
    assert (out["intent"], out["via"], out["tier"]) == ("metric_lookup", "default", "standard")


def test_a_plain_request_for_a_number_is_a_lookup_by_rule_on_the_fast_tier():
    out = route("How many MQLs did we get in September?")
    assert (out["intent"], out["via"], out["tier"]) == ("metric_lookup", "rules", "fast")


def test_a_valid_classifier_answer_wins_and_is_logged_as_model():
    out = route("MQLs from webinars", classifier=lambda q: "trend_analysis")
    assert (out["intent"], out["via"]) == ("trend_analysis", "model")


@pytest.mark.parametrize("answer", ["not_an_intent", None, RuntimeError("down")])
def test_a_bad_or_failing_classifier_falls_back_to_the_rules(answer):
    def classifier(question):
        if isinstance(answer, Exception):
            raise answer
        return answer
    out = route("Why did conversion drop last month?", classifier=classifier)
    assert (out["intent"], out["via"]) == ("funnel_diagnosis", "rules")


def test_a_write_request_never_reaches_the_classifier():
    def classifier(question):
        raise AssertionError("the classifier must not see a write request")
    assert route("Update this deal to closed won", classifier=classifier)["intent"] == "out_of_scope"


def test_every_intent_has_a_profile_with_fixed_documents_and_a_chunk_budget():
    from router import load_profiles, load_routes
    assert set(load_profiles()) == set(load_routes())
    assert route("Why did conversion drop last month?")["fixed_docs"][0] == "funnel-stages"


@pytest.mark.parametrize("question", ["", "   ", None, 5])
def test_an_empty_or_non_text_question_is_an_error(question):
    with pytest.raises(ValueError):
        route(question)


def test_the_same_question_always_gets_the_same_route():
    assert route("Where is the funnel leaking?") == route("Where is the funnel leaking?")


@pytest.mark.parametrize("name", run_router.FILES)
def test_the_router_meets_the_accuracy_target_on_each_case_file(name):
    cases = yaml.safe_load((ROOT / "evals" / name).read_text(encoding="utf-8"))["cases"]
    accuracy, misses = run_router.score(cases)
    assert accuracy >= run_router.TARGET_ACCURACY, misses
