"""Rule-based router: one intent per question (agent/directives/routing.md).

    python agent/router.py "Why did conversion drop last month?"

Rules, not a model, for three reasons: it costs nothing per question, it answers the same
way every time, and a wrong route can be traced to one line below. The cost is that
unusual wording falls through to the default; evals/run_router.py measures how often.

The tools, tier and skill for each intent, and its profile (fixed documents and how many
context chunks), are read from routing.md, so that file stays the only place where they
are written down. Classification is a cascade that never fails: an optional model
classifier, then these rules, then the default, which runs on the standard tier because a
question no rule understands is the one that least deserves the weakest model. The step
that decided is returned as `via`.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Words that make a question about revenue at all. Without one, the question is not ours.
DOMAIN = re.compile(
    r"\b(mrr|arr|revenue|customers?|deals?|funnel|mqls?|leads?|stages?|conversion|churn\w*|"
    r"subscriptions?|pipeline|compan(?:y|ies)|accounts?|win|winning|proposals?|discovery|"
    r"negotiation|qualif\w+|invoices?|billing|reports?|catalog|flags?|sdr|sales|owners?|quota|"
    r"customer success|enterprise|marketing|onboarding|business)\b", re.I)

# Each rule is (intent, why, pattern), tried in this order: the first match wins. Writing
# and off-topic requests go first, so "send the report" is refused before it is a report.
RULES = [
    ("out_of_scope", "asks to change or send something", re.compile(
        r"\b(update|delete|remove|assign|reassign|send|email|post|merge|provision|"
        r"change the owner|set the owner|create an? (workspace|account|ticket|task|deal|lead))\b", re.I)),
    ("out_of_scope", "not about revenue", re.compile(
        r"\b(poem|joke|song|story|weather|restaurant|recipe|movie|football)\b", re.I)),
    ("report_request", "asks for a document", re.compile(
        r"\b(build|make|create|prepare|write|draft|generate|put together)\b.*"
        r"\b(report|summary|review|document|deck|one-pager|one-page)\b|\bhtml\b", re.I)),
    ("past_work_lookup", "asks about earlier work", re.compile(
        r"\bbefore\b|\bpreviously\b|\bearlier (work|analys)|\bever (studied|analy[sz]ed|looked)|"
        r"\banyone (looked|wrote|write|analy)|\bprevious (analysis|work)|\bwhat work was done|"
        r"\bwhat did we (decide|conclude)|\bpast (analys|work)", re.I)),
    ("data_quality", "two numbers or sources disagree", re.compile(
        r"don'?t|doesn'?t|\bdisagree|\bmismatch|\bmatch\b|\bdiffer(s|ent)?\b|\bduplicate|\bmissing\b|"
        r"\bno \w+ behind|\bbug\b|without any|\bwrong\b|\binconsisten", re.I)),
    ("definition_question", "asks what something means", re.compile(
        r"\bcounts? as\b|\bdefin|\bmean\b|\bmeans\b|\bcanonical\b|difference between|"
        r"\bwhen does .* enter\b|\bwhich (flag|status|statuses)\b", re.I)),
    ("funnel_diagnosis", "asks why a funnel number moved", re.compile(
        r"\b(why|what explains|what is behind|where is .* leak\w*|should we fix|slowing down|drop in)\b"
        r".*\b(conversion|funnel|stage|step|deals?|negotiation|proposal|discovery|closed won|win|winning|leak\w*)\b|"
        r"\bwhere is .* leak|\bwhich (stage|step)\b.*\b(fix|slow)", re.I)),
    ("trend_analysis", "asks how something moves over time", re.compile(
        r"\bhow (has|have)\b|\btrend\b|\bover the (last|past)\b|\bsince \w+|\bgoing up\b|\bgrowing\b|"
        r"\bimproving\b|\bgetting worse\b|\bmoved\b|\bplot\b|\bfaster\b|\bover time\b|"
        # "Why did churn go up" is a trend question, not a funnel one: no stage to blame.
        r"\bwhy\b.*\b(mrr|arr|churn\w*|revenue|customers?|mqls?)\b", re.I)),
    # A plain request for a number is a lookup by rule, so it stays on the fast tier; only a
    # question no rule understands falls to the default and its stronger model.
    ("metric_lookup", "asks for a number", re.compile(
        r"\bhow (many|much)\b|\bwhat (was|is|were|are) (the|our)\b|\btotal\b|\bnumber of\b|\bcount\b", re.I)),
]
DEFAULT = ("metric_lookup", "no rule matched, so it is read as a lookup, on the standard tier")


def load_routes(routing_md: Path | None = None) -> dict[str, dict]:
    """Tools, tier and skill per intent, read from the table in routing.md."""
    text = (routing_md or ROOT / "agent" / "directives" / "routing.md").read_text(encoding="utf-8")
    routes = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 5 and re.fullmatch(r"`[a-z_]+`", cells[0]):
            tools = [] if cells[2] == "none" else [t.strip() for t in cells[2].split(",")]
            routes[cells[0].strip("`")] = {
                "tools": tools, "tier": cells[3], "skill": None if cells[4] == "—" else cells[4]}
    return routes


def load_profiles(routing_md: Path | None = None) -> dict[str, dict]:
    """Fixed documents and context chunk budget per intent, from the profile table in routing.md."""
    text = (routing_md or ROOT / "agent" / "directives" / "routing.md").read_text(encoding="utf-8")
    profiles = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and re.fullmatch(r"`[a-z_]+`", cells[0]) and cells[2].isdigit():
            docs = [] if cells[1] == "—" else [d.strip() for d in cells[1].split(",")]
            profiles[cells[0].strip("`")] = {"fixed_docs": docs, "chunks": int(cells[2])}
    return profiles


def classify(question: str) -> tuple[str, str]:
    """The intent and the reason for it."""
    for intent, why, pattern in RULES:
        if pattern.search(question):
            return intent, why
    return DEFAULT


def route(question: str, routing_md: Path | None = None, classifier=None) -> dict:
    """Route a question. `classifier`, when given, is a callable that returns an intent id."""
    if not isinstance(question, str) or not question.strip():
        raise ValueError("The question must be a non-empty string.")
    routes = load_routes(routing_md)
    intent, why, via = None, None, None
    # A request to write or send is refused by rule before any model sees it.
    if classifier is not None and not RULES[0][2].search(question):
        try:
            guess = str(classifier(question)).strip().strip("`")
        except Exception:  # any failure falls through to the rules: classification never fails a question
            guess = None
        if guess in routes:
            intent, why, via = guess, "the classifier chose it", "model"
    if intent is None:
        intent, why = ("out_of_scope", "not about revenue")
        if DOMAIN.search(question) or any(p.search(question) for i, _, p in RULES[:2]):
            intent, why = classify(question)
        via = "default" if (intent, why) == DEFAULT else "rules"
    decision = {"intent": intent, "reason": why, "via": via, **routes[intent],
                **load_profiles(routing_md).get(intent, {"fixed_docs": [], "chunks": 0})}
    if via == "default":
        decision["tier"] = "standard"
    return decision


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print('usage: python agent/router.py "question"', file=sys.stderr)
        return 1
    print(json.dumps(route(argv[1]), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
