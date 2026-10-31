"""Site qualification: read a company's website text and write a structured summary for the SDR.

    python automations/site-qualification/qualify.py --requests automations/site-qualification/examples/requests.json
    python automations/site-qualification/qualify.py --requests requests.json --write    # needs SITE_QUALIFICATION_ENABLED=true
    python automations/site-qualification/qualify.py --requests requests.json --model    # the real model; needs ANTHROPIC_API_KEY

Spec: automations/site-qualification/SPEC.md. Rules: context/rules/prospecting.md.
Guardrails in code, not in the prompt: contact details are removed before the text reaches
the model, the text is cut to a fixed length, the reply must be JSON with exactly the
expected keys, services must come from the allowed list, and every quote must appear word
for word in the text. A result that fails goes to review and is never written.
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
from controls import ControlsError, WriteControls  # noqa: E402

PROMPT = HERE / "prompts" / "qualify-site.md"
MAX_TEXT_CHARS = 6_000
FITS = {"strong", "partial", "weak", "unknown"}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\+?\d[\d ().-]{7,}\d")


def allowed_services(context_dir: Path = ROOT / "context") -> list[str]:
    flat = " ".join((context_dir / "rules" / "prospecting.md").read_text(encoding="utf-8").split())
    found = re.search(r"Service labels the qualification may use: ([^.]+)\.", flat)
    if not found:
        raise ValueError("prospecting.md no longer lists the service labels")
    return [s.strip() for s in found.group(1).split(",")]


def clean_text(text: str) -> str:
    """Structural guardrail: contact details never reach the model, and the text has a ceiling."""
    return PHONE.sub("[phone removed]", EMAIL.sub("[email removed]", text))[:MAX_TEXT_CHARS]


def validator(text: str, services: list[str]):
    def validate(reply: dict) -> dict:
        expected = {"fit", "technicians_mentioned", "services", "evidence", "summary"}
        if set(reply) != expected:
            raise AIStepError(f"keys must be exactly {sorted(expected)}")
        if reply["fit"] not in FITS or not isinstance(reply["technicians_mentioned"], bool):
            raise AIStepError("fit or technicians_mentioned has an invalid value")
        if not isinstance(reply["services"], list) or any(s not in services for s in reply["services"]):
            raise AIStepError("a service is not on the allowed list")
        quotes = reply["evidence"] if isinstance(reply["evidence"], list) else []
        if len(quotes) > 3 or any(not isinstance(q, str) or q not in text for q in quotes):
            raise AIStepError("a quote does not appear word for word in the website text")
        if not isinstance(reply["summary"], str) or len(reply["summary"]) > 300:
            raise AIStepError("the summary is missing or longer than 300 characters")
        return reply
    return validate


class DemoQualifier:
    """Plays the model with no key: finds the evidence by keyword, so the flow can be shown end to end."""

    def complete(self, model, system, messages, tools):
        payload = json.loads(messages[0]["content"])
        text, services = payload["website_text"], payload["allowed_services"]
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", text) if s.strip()]
        technicians = any(re.search(r"technician|engineer", s, re.I) for s in sentences)
        evidence = [s for s in sentences if re.search(r"technician|engineer|maintenance|work order|job", s, re.I)][:3]
        found = [s for s in services if s.lower() in text.lower()]
        fit = "strong" if technicians and found else "partial" if found or technicians else "weak" if len(text) > 80 else "unknown"
        summary = (f"{payload['company_name']}: {fit} fit. " + (f"Mentions {', '.join(found)}. " if found else "")
                   + ("Has field technicians." if technicians else "No field technicians mentioned."))[:300]
        reply = {"fit": fit, "technicians_mentioned": technicians, "services": found, "evidence": evidence, "summary": summary}
        return {"text": json.dumps(reply), "tool_call": None, "usage": {}}


def qualify(request: dict, sites_dir: Path, use_model: bool, log_path: Path | None = None) -> dict:
    text = clean_text((sites_dir / f"{request['company_id']}.txt").read_text(encoding="utf-8"))
    services = allowed_services()
    payload = {"company_name": request["company_name"], "allowed_services": services, "website_text": text}
    try:
        step = run_ai_step("site-qualification", PROMPT, payload, validator(text, services),
                           demo_client=DemoQualifier(), use_model=use_model, log_path=log_path)
    except AIStepError as error:
        return {"request_id": request["request_id"], "company_id": request["company_id"], "outcome": "needs review",
                "why": str(error)}
    return {"request_id": request["request_id"], "company_id": request["company_id"], "outcome": "qualified",
            **step["output"], "mode": step["mode"], "prompt_sha256": step["prompt_sha256"], "cost_usd": step["cost_usd"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Qualify companies from their website (dry run unless --write).")
    parser.add_argument("--requests", type=Path, required=True)
    parser.add_argument("--sites", type=Path, default=HERE / "examples" / "sites", help="folder of <company_id>.txt")
    parser.add_argument("--logs", type=Path, default=ROOT / "observability" / "logs")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--model", action="store_true", help="use the real model (needs ANTHROPIC_API_KEY)")
    args = parser.parse_args(argv)
    if args.model and not model_available():
        print("--model needs ANTHROPIC_API_KEY; run without it for the demo.", file=sys.stderr)
        return 1
    try:
        controls = WriteControls("site-qualification", args.write)
        requests = json.loads(args.requests.read_text(encoding="utf-8"))
        results = [qualify(r, args.sites, args.model, args.logs / "ai-steps.jsonl") for r in requests]
    except (ControlsError, ValueError, OSError, KeyError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    print(json.dumps(results, indent=2))
    if controls.mode != "write":
        print(controls.describe())
        return 0
    path = args.logs / f"site-qualification-{args.date}.json"
    done = {r["request_id"]: r for r in results if r["outcome"] == "qualified"}
    kept = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}

    def write_one(request_id):
        # The simulated CRM write: the summary into the qualification field, keyed by request id.
        kept[request_id] = done[request_id]
        path.write_text(json.dumps(kept, indent=2), encoding="utf-8")

    outcome = controls.apply(list(done), write_one, lambda rid: rid in json.loads(path.read_text(encoding="utf-8")))
    print(f"{controls.describe()}\n{len(outcome.applied)} written, "
          f"{len(outcome.needs_review) + len(results) - len(done)} need review")
    return 0


if __name__ == "__main__":
    sys.exit(main())
