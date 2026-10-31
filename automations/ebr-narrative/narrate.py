"""Account review narrative: a short brief for the customer success manager before an executive review.

    python automations/ebr-narrative/narrate.py --companies 2 117
    python automations/ebr-narrative/narrate.py --companies 2 --write    # writes the briefs
    python automations/ebr-narrative/narrate.py --companies 2 --model    # the real model; needs ANTHROPIC_API_KEY

Spec: automations/ebr-narrative/SPEC.md. Rules: context/rules/proposal-rules.md.
The data pack is built by code from gold (health, onboarding, subscription). The model only
writes prose around it, and the code rejects any number or date that is not in the pack,
any "guaranteed", and anything past the length limits.
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

PROMPT = HERE / "prompts" / "ebr-narrative.md"
LIMITS = {"narrative": 1200, "next_step": 200}


def data_pack(db_path: Path, company_id: int) -> dict:
    """Everything the narrative may cite, from gold only."""
    if not db_path.is_file():
        raise ValueError(f"lakehouse not found at {db_path}")
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        health = con.execute("SELECT latest_score, latest_band, latest_scored_at FROM gold.account_health WHERE company_id = ?",
                             [company_id]).fetchone()
        subs = con.execute("SELECT s.subscription_id, s.status, s.started_at, s.ended_at, o.current_milestone, "
                           "o.kickoff_at, o.go_live_at FROM gold.subscription_lifecycle s "
                           "LEFT JOIN gold.onboarding_progress o USING (subscription_id) WHERE s.company_id = ? "
                           "ORDER BY s.started_at", [company_id]).fetchall()
    finally:
        con.close()
    return {
        "health": {"score": health[0], "band": health[1], "scored_on": str(health[2])} if health else None,
        "subscriptions": [{"status": s[1], "started_on": str(s[2]), "ended_on": str(s[3]) if s[3] else None,
                           "onboarding": s[4], "kickoff_on": str(s[5]) if s[5] else None,
                           "go_live_on": str(s[6]) if s[6] else None} for s in subs],
    }


def validator(payload: dict):
    # Numbers may come from the input only: the company name and the data pack.
    allowed = set(re.findall(r"\d+", json.dumps(payload)))

    def validate(reply: dict) -> dict:
        if set(reply) != set(LIMITS):
            raise AIStepError("keys must be exactly narrative and next_step")
        for key, limit in LIMITS.items():
            text = reply[key]
            if not isinstance(text, str) or not text.strip() or len(text) > limit:
                raise AIStepError(f"{key} is missing or longer than {limit} characters")
            if re.search(r"\bguarantee", text, re.I):
                raise AIStepError(f"{key} makes a guarantee")
            if set(re.findall(r"\d+", text)) - allowed:
                raise AIStepError(f"{key} holds a number or date that is not in the data pack")
        return reply
    return validate


class DemoNarrator:
    """Plays the model with no key: a templated narrative from the data pack, so the flow can be shown."""

    def complete(self, model, system, messages, tools):
        p = json.loads(messages[0]["content"])
        pack, name = p["data_pack"], p["company_name"]
        h = pack["health"]
        parts = [f"{name}: health score {h['score']} ({h['band']}) on {h['scored_on']}." if h else f"{name}: no health score yet."]
        for s in pack["subscriptions"]:
            if s["status"] == "churned":
                parts.append(f"A subscription started on {s['started_on']} ended on {s['ended_on']}.")
            else:
                parts.append(f"Active since {s['started_on']}; onboarding at {s['onboarding']}"
                             + (f", live since {s['go_live_on']}." if s["go_live_on"] else "."))
        step = ("Plan a recovery conversation before the review." if h and h["band"] == "red"
                else "Confirm the customer's goals for the next quarter in the review.")
        return {"text": json.dumps({"narrative": " ".join(parts)[:1200], "next_step": step}), "tool_call": None, "usage": {}}


def narrate(company_id: int, db_path: Path, use_model: bool, log_path: Path | None = None) -> dict:
    pack = data_pack(db_path, company_id)
    if not pack["subscriptions"]:
        return {"company_id": company_id, "outcome": "needs review", "why": "no subscription for this company"}
    payload = {"company_name": f"Company {company_id}", "data_pack": pack}
    try:
        step = run_ai_step("ebr-narrative", PROMPT, payload, validator(payload),
                           demo_client=DemoNarrator(), use_model=use_model, log_path=log_path)
    except AIStepError as error:
        return {"company_id": company_id, "outcome": "needs review", "why": str(error)}
    return {"company_id": company_id, "outcome": "written", **step["output"], "data_pack": pack,
            "mode": step["mode"], "prompt_sha256": step["prompt_sha256"], "cost_usd": step["cost_usd"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write account review briefs (dry run unless --write).")
    parser.add_argument("--companies", type=int, nargs="+", required=True)
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
        results = [narrate(c, args.db, args.model, args.logs / "ai-steps.jsonl") for c in args.companies]
    except (ValueError, OSError, duckdb.Error) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    print(json.dumps([{k: v for k, v in r.items() if k != "data_pack"} for r in results], indent=2))
    if args.write:
        args.logs.mkdir(parents=True, exist_ok=True)
        path = args.logs / f"ebr-briefs-{args.date}.json"
        path.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"wrote {path}")
    else:
        print("dry run: nothing written (use --write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
