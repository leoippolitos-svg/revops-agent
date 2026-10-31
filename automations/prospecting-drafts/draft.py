"""Prospecting drafts: a first-touch message and a follow-up for the SDR, built on qualified evidence.

    python automations/prospecting-drafts/draft.py --leads automations/prospecting-drafts/examples/leads.json
    python automations/prospecting-drafts/draft.py --leads leads.json --write    # writes the drafts file
    python automations/prospecting-drafts/draft.py --leads leads.json --model    # the real model; needs ANTHROPIC_API_KEY

Spec: automations/prospecting-drafts/SPEC.md. Rules: context/rules/prospecting.md.
The guardrails are structural: only arguments whose evidence was found in the site
qualification ever reach the model, a lead with weak or unknown fit gets no draft and no
model call, and the reply is checked in code (length, arguments used, no price, discount,
guarantee, competitor, link, or number that is not in the input). Drafts are written to a
file for the SDR to review and send; nothing is ever sent.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "automations" / "_lib"))

from ai_step import AIStepError, model_available, run_ai_step  # noqa: E402

PROMPT = HERE / "prompts" / "draft-messages.md"
FORBIDDEN = re.compile(r"\b(price|pricing|discount|guarantee\w*|competitor\w*|cheaper|free trial)\b|https?://|www\.", re.I)
LIMITS = {"first_touch": 600, "follow_up": 400}


def load_arguments(context_dir: Path = ROOT / "context") -> list[dict]:
    """Each argument with its id, its sentence and the evidence it needs, from the rule document."""
    text = (context_dir / "rules" / "prospecting.md").read_text(encoding="utf-8")
    found = re.findall(r"- `(arg-[a-z-]+)`: (.+?) Needs: (.+?)\.\s*$", text, flags=re.MULTILINE)
    if not found:
        raise ValueError("prospecting.md no longer lists the eligible arguments")
    return [{"id": i, "sentence": s.strip(), "needs": n.strip()} for i, s, n in found]


def eligible(arguments: list[dict], qualification: dict) -> list[dict]:
    """Structural guardrail: an argument enters the prompt only if its evidence exists."""
    evidence = " ".join(qualification.get("evidence", [])).lower()
    keep = []
    for argument in arguments:
        need = argument["needs"].lower()
        if need == "technicians mentioned":
            ok = qualification.get("technicians_mentioned") is True
        else:
            word = re.search(r"evidence mentioning (.+)", need)
            ok = bool(word) and word.group(1) in evidence
        if ok:
            keep.append({"id": argument["id"], "sentence": argument["sentence"]})
    return keep


def validator(payload: dict):
    allowed_ids = {a["id"] for a in payload["eligible_arguments"]}
    input_numbers = set(re.findall(r"\d+", json.dumps(payload)))

    def validate(reply: dict) -> dict:
        if set(reply) != {"first_touch", "follow_up", "arguments_used"}:
            raise AIStepError("keys must be exactly first_touch, follow_up, arguments_used")
        for key, limit in LIMITS.items():
            if not isinstance(reply[key], str) or not reply[key].strip() or len(reply[key]) > limit:
                raise AIStepError(f"{key} is missing or longer than {limit} characters")
            if FORBIDDEN.search(reply[key]):
                raise AIStepError(f"{key} mentions a forbidden claim or a link")
            if set(re.findall(r"\d+", reply[key])) - input_numbers:
                raise AIStepError(f"{key} holds a number that is not in the input")
        used = reply["arguments_used"]
        if not isinstance(used, list) or not used or set(used) - allowed_ids:
            raise AIStepError("arguments_used must name only eligible arguments")
        return reply
    return validate


class DemoWriter:
    """Plays the model with no key: assembles the draft from the eligible arguments' own sentences."""

    def complete(self, model, system, messages, tools):
        p = json.loads(messages[0]["content"])
        args = p["eligible_arguments"]
        first = (f"Hi {p['first_name']}, I read about {p['company_name']}. {args[0]['sentence']} "
                 "Would a short call next week be useful?")
        follow = (f"Hi {p['first_name']}, a quick follow-up. "
                  + (args[1]["sentence"] if len(args) > 1 else "Happy to show how it would work for your team."))
        used = [args[0]["id"]] + ([args[1]["id"]] if len(args) > 1 else [])
        return {"text": json.dumps({"first_touch": first[:600], "follow_up": follow[:400], "arguments_used": used}),
                "tool_call": None, "usage": {}}


def draft(lead: dict, qualification: dict | None, arguments: list[dict], use_model: bool,
          log_path: Path | None = None) -> dict:
    base = {"lead_id": lead["lead_id"], "company_id": lead["company_id"]}
    if not qualification:
        return {**base, "outcome": "needs review", "why": "no site qualification for this company"}
    if qualification.get("fit") in ("weak", "unknown"):
        return {**base, "outcome": "no draft", "why": f"fit is {qualification.get('fit')}; no model call"}
    allowed = eligible(arguments, qualification)
    if not allowed:
        return {**base, "outcome": "needs review", "why": "no eligible argument has evidence"}
    payload = {"first_name": lead["first_name"], "job_title": lead["job_title"], "company_name": lead["company_name"],
               "qualification_summary": qualification.get("summary", ""), "eligible_arguments": allowed}
    try:
        step = run_ai_step("prospecting-drafts", PROMPT, payload, validator(payload),
                           demo_client=DemoWriter(), use_model=use_model, log_path=log_path)
    except AIStepError as error:
        return {**base, "outcome": "needs review", "why": str(error)}
    return {**base, "outcome": "drafted", **step["output"], "mode": step["mode"],
            "prompt_sha256": step["prompt_sha256"], "cost_usd": step["cost_usd"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draft prospecting messages for the SDR (dry run unless --write).")
    parser.add_argument("--leads", type=Path, required=True)
    parser.add_argument("--qualifications", type=Path, default=HERE / "examples" / "qualifications.json",
                        help="site qualification results, keyed by company id")
    parser.add_argument("--logs", type=Path, default=ROOT / "observability" / "logs")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--write", action="store_true", help="write the drafts file for the SDRs")
    parser.add_argument("--model", action="store_true", help="use the real model (needs ANTHROPIC_API_KEY)")
    args = parser.parse_args(argv)
    if args.model and not model_available():
        print("--model needs ANTHROPIC_API_KEY; run without it for the demo.", file=sys.stderr)
        return 1
    try:
        leads = json.loads(args.leads.read_text(encoding="utf-8"))
        qualifications = json.loads(args.qualifications.read_text(encoding="utf-8"))
        arguments = load_arguments()
        results = [draft(lead, qualifications.get(lead["company_id"]), arguments, args.model,
                         args.logs / "ai-steps.jsonl") for lead in leads]
    except (ValueError, OSError, KeyError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    print(json.dumps(results, indent=2))
    if args.write:
        args.logs.mkdir(parents=True, exist_ok=True)
        path = args.logs / f"prospecting-drafts-{args.date}.json"
        path.write_text(json.dumps(results, indent=2), encoding="utf-8")  # one file per day: a rerun overwrites it
        print(f"wrote {path}: drafts for the SDRs to review; nothing was sent")
    else:
        print("dry run: nothing written (use --write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
