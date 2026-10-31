"""Tests for the AI step, site qualification and prospecting drafts. No model is called."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automations" / "_lib"))
sys.path.insert(0, str(ROOT / "tools"))

import ai_step  # noqa: E402
import check_prompts  # noqa: E402


def load(rel):
    spec = importlib.util.spec_from_file_location(Path(rel).stem + "_ai_test", ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


qualify = load("automations/site-qualification/qualify.py")
draft = load("automations/prospecting-drafts/draft.py")
SITES = ROOT / "automations" / "site-qualification" / "examples" / "sites"


class Fixed:
    """A stand-in model that returns a fixed reply, to test what the code does with bad output."""

    def __init__(self, reply, usage=None):
        self.reply, self.usage = reply, usage or {}

    def complete(self, model, system, messages, tools):
        self.seen = messages[0]["content"]
        return {"text": json.dumps(self.reply) if isinstance(self.reply, dict) else self.reply,
                "tool_call": None, "usage": self.usage}


def test_every_run_logs_tokens_cost_and_prompt_hash_but_no_input(tmp_path):
    log = tmp_path / "ai.jsonl"
    result = ai_step.run_ai_step("demo", qualify.PROMPT, {"secret": "do-not-log"}, lambda r: r,
                                 demo_client=Fixed({"a": 1}, {"input_tokens": 100, "output_tokens": 20}), log_path=log)
    (record,) = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert record["prompt_sha256"] == ai_step.prompt_hash(qualify.PROMPT) and record["input_tokens"] == 100
    assert record["cost_usd"] is None  # the price table is empty: unknown, never zero
    assert "do-not-log" not in log.read_text(encoding="utf-8") and result["mode"] == "demo"


def test_contact_details_are_removed_before_the_model_sees_the_text():
    cleaned = qualify.clean_text("Write to ops" + "@" + "example.com or call +44 20 " + "7946 0958 today")
    assert "example.com" not in cleaned and "7946" not in cleaned and "[email removed]" in cleaned


def test_a_quote_not_in_the_site_sends_the_result_to_review(tmp_path, monkeypatch):
    bad = {"fit": "strong", "technicians_mentioned": True, "services": ["HVAC maintenance"],
           "evidence": ["We have 5,000 technicians"], "summary": "x"}
    monkeypatch.setattr(qualify, "DemoQualifier", lambda: Fixed(bad))
    out = qualify.qualify({"request_id": "r", "company_id": "C-101", "company_name": "N"}, SITES, False, tmp_path / "l")
    assert out["outcome"] == "needs review" and "word for word" in out["why"]


def test_a_service_off_the_allowed_list_is_refused(tmp_path, monkeypatch):
    bad = {"fit": "strong", "technicians_mentioned": True, "services": ["rocket repair"], "evidence": [], "summary": "x"}
    monkeypatch.setattr(qualify, "DemoQualifier", lambda: Fixed(bad))
    out = qualify.qualify({"request_id": "r", "company_id": "C-101", "company_name": "N"}, SITES, False, tmp_path / "l")
    assert out["outcome"] == "needs review"


def test_the_demo_qualifies_a_field_service_company_as_strong_and_a_studio_as_weak(tmp_path):
    strong = qualify.qualify({"request_id": "a", "company_id": "C-101", "company_name": "N"}, SITES, False, tmp_path / "l")
    weak = qualify.qualify({"request_id": "b", "company_id": "C-102", "company_name": "L"}, SITES, False, tmp_path / "l")
    assert (strong["fit"], weak["fit"]) == ("strong", "weak") and strong["technicians_mentioned"]


QUAL = {"fit": "strong", "technicians_mentioned": True, "summary": "s",
        "evidence": ["We are moving from paper job sheets to digital work orders."]}
LEAD = {"lead_id": "L1", "company_id": "C-101", "company_name": "N", "first_name": "Morgan", "job_title": "Head"}


def test_only_arguments_with_evidence_are_eligible():
    ids = [a["id"] for a in draft.eligible(draft.load_arguments(), QUAL)]
    assert ids == ["arg-paper-to-digital", "arg-scheduling-scale"]


def test_a_weak_fit_lead_gets_no_draft_and_no_model_call(tmp_path, monkeypatch):
    def explode():
        raise AssertionError("the model must not be called")
    monkeypatch.setattr(draft, "DemoWriter", explode)
    out = draft.draft(LEAD, {**QUAL, "fit": "weak"}, draft.load_arguments(), False, tmp_path / "l")
    assert out["outcome"] == "no draft"


@pytest.mark.parametrize("first_touch, reason", [
    ("Hi Morgan, we can offer a 20% discount.", "forbidden"),
    ("Hi Morgan, see https://example.com", "forbidden"),
    ("Hi Morgan, 300 customers love us.", "number"),
])
def test_drafts_with_forbidden_claims_links_or_new_numbers_are_rejected(tmp_path, monkeypatch, first_touch, reason):
    reply = {"first_touch": first_touch, "follow_up": "Hi again.", "arguments_used": ["arg-paper-to-digital"]}
    monkeypatch.setattr(draft, "DemoWriter", lambda: Fixed(reply))
    out = draft.draft(LEAD, QUAL, draft.load_arguments(), False, tmp_path / "l")
    assert out["outcome"] == "needs review" and reason in out["why"]


def test_a_draft_using_an_ineligible_argument_is_rejected(tmp_path, monkeypatch):
    reply = {"first_touch": "Hi Morgan.", "follow_up": "Hi.", "arguments_used": ["arg-emergency-dispatch"]}
    monkeypatch.setattr(draft, "DemoWriter", lambda: Fixed(reply))
    assert draft.draft(LEAD, QUAL, draft.load_arguments(), False, tmp_path / "l")["outcome"] == "needs review"


def test_the_demo_draft_is_valid_and_uses_eligible_arguments(tmp_path):
    out = draft.draft(LEAD, QUAL, draft.load_arguments(), False, tmp_path / "l")
    assert out["outcome"] == "drafted" and out["first_touch"].startswith("Hi Morgan")


def test_every_prompt_hash_is_recorded_in_its_spec_and_a_change_is_caught(tmp_path):
    assert check_prompts.check(ROOT) == []
    folder = tmp_path / "automations" / "x"
    (folder / "prompts").mkdir(parents=True)
    (folder / "prompts" / "p.md").write_text("new prompt", encoding="utf-8")
    (folder / "SPEC.md").write_text("Prompt: `prompts/p.md`, prompt sha256: `" + "0" * 64 + "`", encoding="utf-8")
    assert any("the prompt changed" in e for e in check_prompts.check(tmp_path))
