"""Proposal generator: turn a meeting note and the deal into a proposal draft for the seller.

    python automations/proposal-generator/generate.py --requests automations/proposal-generator/examples/requests.json
    python automations/proposal-generator/generate.py --requests requests.json --write   # writes the drafts
    python automations/proposal-generator/generate.py --requests requests.json --model   # the real model; needs ANTHROPIC_API_KEY

Spec: automations/proposal-generator/SPEC.md. Rules: context/rules/proposal-rules.md.
Two steps. The AI step only extracts facts from the meeting note into a fixed shape, and the
code checks them: every number and quote must appear in the note, pain points must be on
the allowed list. The proposal is then assembled by code from those facts, the plan rule
and the deal's amount in gold, so the model never writes a price or a promise.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "automations" / "_lib"))

from ai_step import AIStepError, model_available, run_ai_step  # noqa: E402

PROMPT = HERE / "prompts" / "extract-meeting-fields.md"
RULES = ROOT / "context" / "rules" / "proposal-rules.md"


def load_rules(path: Path = RULES) -> dict:
    flat = " ".join(path.read_text(encoding="utf-8").split())
    plans = re.findall(r"(starter|growth|scale) (up to|above) (\d+) technicians", flat)
    pains = re.search(r"Pain points a proposal may address: ([^.]+)\.", flat)
    if len(plans) != 3 or not pains:
        raise ValueError("proposal-rules.md no longer states the plans or the pain points")
    return {"plans": [(name, kind, int(n)) for name, kind, n in plans],
            "pain_points": [p.strip() for p in pains.group(1).split(",")]}


def plan_for(technicians: int | None, rules: dict) -> str | None:
    if technicians is None:
        return None
    for name, kind, limit in rules["plans"]:
        if kind == "up to" and technicians <= limit:
            return name
    return next(name for name, kind, _ in rules["plans"] if kind == "above")


def validator(note: str, pains: list[str]):
    def validate(reply: dict) -> dict:
        expected = {"technicians", "pain_points", "current_tool", "decision_date", "evidence"}
        if set(reply) != expected:
            raise AIStepError(f"keys must be exactly {sorted(expected)}")
        tech = reply["technicians"]
        if tech is not None and (not isinstance(tech, int) or str(tech) not in note):
            raise AIStepError("the number of technicians is not in the note")
        if not isinstance(reply["pain_points"], list) or any(p not in pains for p in reply["pain_points"]):
            raise AIStepError("a pain point is not on the allowed list")
        if reply["decision_date"] is not None and reply["decision_date"] not in note:
            raise AIStepError("the decision date is not in the note")
        if any(not isinstance(q, str) or q not in note for q in reply["evidence"] or []):
            raise AIStepError("a quote does not appear word for word in the note")
        return reply
    return validate


class DemoExtractor:
    """Plays the model with no key: finds the facts by pattern, so the flow can be shown end to end."""

    KEYWORDS = {"paper job sheets": "paper", "manual scheduling": "spreadsheet", "slow emergency dispatch": "emergency",
                "missed planned maintenance": "planned maintenance", "no visibility of technician location": "where technicians"}

    def complete(self, model, system, messages, tools):
        payload = json.loads(messages[0]["content"])
        note = payload["note"]
        tech = re.search(r"(\d+) (?:field )?technicians", note)
        date_found = re.search(r"\d{4}-\d{2}-\d{2}", note)
        pains = [p for p in payload["allowed_pain_points"] if self.KEYWORDS.get(p, p) in note.lower()]
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", note) if s.strip()]
        reply = {"technicians": int(tech.group(1)) if tech else None, "pain_points": pains,
                 "current_tool": "paper and spreadsheets" if "spreadsheet" in note.lower() else None,
                 "decision_date": date_found.group(0) if date_found else None,
                 "evidence": [s for s in sentences if re.search(r"technician|paper|emergency|decide", s, re.I)][:3]}
        return {"text": json.dumps(reply), "tool_call": None, "usage": {}}


def deal_amount(db_path: Path, deal_id) -> int | None:
    if not db_path.is_file():
        raise ValueError(f"lakehouse not found at {db_path}")
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        row = con.execute("SELECT amount_usd FROM gold.deal_amount WHERE deal_id = ?", [deal_id]).fetchone()
    finally:
        con.close()
    return row[0] if row else None


def assemble(request: dict, facts: dict, plan: str | None, amount: int | None) -> str:
    """The proposal is written by code from validated facts: no price or promise from a model."""
    pains = "\n".join(f"- {p.capitalize()}" for p in facts["pain_points"]) or "- To confirm with the customer"
    lines = [f"# Proposal draft: {request['company_name']}", "",
             "Draft for the seller to review. Nothing was sent.", "",
             "## What we heard", pains, "",
             "## Recommended plan",
             f"{plan.capitalize()}, for {facts['technicians']} field technicians." if plan else "To confirm: the number of technicians is not in the note.", "",
             "## Commercial terms",
             f"Yearly amount as recorded on the deal: ${amount:,}." if amount else "No amount recorded on the deal yet.", "",
             "## Next step",
             f"Decision expected by {facts['decision_date']}." if facts["decision_date"] else "Agree a decision date with the customer.", "",
             "## Evidence from the meeting note"] + [f"> {q}" for q in facts["evidence"]]
    return "\n".join(lines) + "\n"


def generate(request: dict, examples: Path, db_path: Path, use_model: bool, log_path: Path | None = None) -> dict:
    rules = load_rules()
    note = (examples / request["notes_file"]).read_text(encoding="utf-8")
    payload = {"allowed_pain_points": rules["pain_points"], "note": note}
    try:
        step = run_ai_step("proposal-generator", PROMPT, payload, validator(note, rules["pain_points"]),
                           demo_client=DemoExtractor(), use_model=use_model, log_path=log_path)
    except AIStepError as error:
        return {"request_id": request["request_id"], "outcome": "needs review", "why": str(error)}
    facts = step["output"]
    plan = plan_for(facts["technicians"], rules)
    return {"request_id": request["request_id"], "outcome": "drafted", "plan": plan, "facts": facts,
            "proposal": assemble(request, facts, plan, deal_amount(db_path, request["deal_id"])),
            "mode": step["mode"], "prompt_sha256": step["prompt_sha256"], "cost_usd": step["cost_usd"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate proposal drafts (dry run unless --write).")
    parser.add_argument("--requests", type=Path, required=True)
    parser.add_argument("--examples", type=Path, default=HERE / "examples", help="folder of meeting notes")
    parser.add_argument("--db", type=Path, default=ROOT / "data" / "lakehouse.duckdb")
    parser.add_argument("--logs", type=Path, default=ROOT / "observability" / "logs")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--model", action="store_true")
    args = parser.parse_args(argv)
    if args.model and not model_available():
        print("--model needs ANTHROPIC_API_KEY; run without it for the demo.", file=sys.stderr)
        return 1
    try:
        requests = json.loads(args.requests.read_text(encoding="utf-8"))
        results = [generate(r, args.examples, args.db, args.model, args.logs / "ai-steps.jsonl") for r in requests]
    except (ValueError, OSError, KeyError, duckdb.Error) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    for r in results:
        print(r.get("proposal") or f"{r['request_id']}: {r['outcome']}, {r['why']}")
    if args.write:
        args.logs.mkdir(parents=True, exist_ok=True)
        path = args.logs / f"proposals-{args.date}.json"
        path.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"wrote {path}: drafts for the sellers; nothing was sent")
    else:
        print("dry run: nothing written (use --write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
