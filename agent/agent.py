"""The RevOps agent loop: route, call tools within a budget, answer, log.

    python agent/agent.py --plan "Why did conversion drop last month?"
    python agent/agent.py --ask "Why did conversion drop last month?"   # needs ANTHROPIC_API_KEY

The loop does not know which model it talks to. It needs an object with one method,
`complete(model, system, messages, tools)` (see ModelClient), so tests use a scripted
stand-in and the adapter in model_client.py plugs in without touching this file (ADR-0015,
ADR-0016). `--plan` calls nothing. `--ask` is the only path to a real model, and it stops
at once when no key is set. It has never been run with a key in this repository.

What holds regardless of the model:
- the only tools are the four read-only ones in TOOLS, and only those the intent allows;
- the call budget is counted here, not requested in a prompt;
- a request to change or send something is declined without a model call;
- the log keeps the intent, tier, tools, tokens and latency, and never a question or a row.
"""

import json
import re
import sys
import time
from pathlib import Path
from typing import Callable, Protocol

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))
sys.path.insert(0, str(ROOT / "agent" / "tools"))

from get_catalog import UnknownModel, get_catalog  # noqa: E402
from model_client import AnthropicClient, ModelError  # noqa: E402
from query_gold import QueryFailed, QueryRejected, query_gold  # noqa: E402
from router import route  # noqa: E402
from search_context import InvalidInput, search_context  # noqa: E402
from search_records import search_records  # noqa: E402

# Lookups are cheap and diagnoses are not (agent/directives/AGENT.md).
BUDGET = {"fast": 3, "standard": 8}
MAX_RESULT_CHARS = 20_000  # a tool result longer than this is cut, so one call cannot fill the context
DEFAULT_LOG = ROOT / "observability" / "logs" / "agent.jsonl"

DECLINE = ("I can only read and explain Fernway's revenue data, so I will not change, send or create "
           "anything. If you tell me what you want to achieve, I can recommend what to do and who can do it.")

# The one place that says which tools exist. Adding a key here is adding a tool (ADR-0006).
TOOLS: dict[str, Callable[..., dict]] = {
    "query_gold": query_gold,
    "search_context": search_context,
    "get_catalog": get_catalog,
    "search_records": search_records,
}
# What the model is told about each tool: the argument names it may use.
SPECS = {
    "query_gold": {"description": "Run one SELECT over a gold table. At most 200 rows.",
                   "arguments": {"sql": "string"}},
    "search_context": {"description": "Find the business definition of a concept.",
                       "arguments": {"question": "string", "k": "integer, optional, 1 to 5"}},
    "get_catalog": {"description": "Describe a table and its columns.",
                    "arguments": {"model": "string, such as gold.mrr_monthly"}},
    "search_records": {"description": "Find past work and what was concluded.",
                       "arguments": {"question": "string", "k": "integer, optional, 1 to 5"}},
}
# What a tool may raise on bad input. Anything else is a bug and is allowed to crash.
TOOL_ERRORS = (QueryRejected, QueryFailed, InvalidInput, UnknownModel)


class ModelClient(Protocol):
    def complete(self, model: str, system: str, messages: list[dict], tools: list[dict]) -> dict:
        """Return {"text": str | None, "tool_call": {"name", "input"} | None, "usage": {...}}."""


def model_ids() -> dict[str, str]:
    """Tier to model id, read from the one table that lists them."""
    text = (ROOT / "agent" / "tools" / "README.md").read_text(encoding="utf-8")
    return dict(re.findall(r"^\| `(fast|standard)` \| `([a-z0-9-]+)` \|", text, flags=re.MULTILINE))


def build_system_prompt(decision: dict) -> str:
    """Identity and protocol, the fallbacks, this intent's row, and the skill when there is one."""
    directives = ROOT / "agent" / "directives"
    parts = [(directives / "AGENT.md").read_text(encoding="utf-8"),
             (directives / "fallback.md").read_text(encoding="utf-8"),
             f"This question was routed as `{decision['intent']}` ({decision['reason']}). "
             f"Tools you may use: {', '.join(decision['tools']) or 'none'}."]
    if decision["skill"]:
        skill = (ROOT / "agent" / "skills" / decision["skill"] / "SKILL.md").read_text(encoding="utf-8")
        parts.append(skill.split("---", 2)[-1].strip())  # the steps, without the front matter
    return "\n\n".join(parts)


def _call_tool(name: str, arguments, allowed: list[str], tools: dict[str, Callable]) -> dict:
    """Run one tool call. A refusal or a tool error goes back to the model as text, not as a crash."""
    if name not in allowed:
        return {"error": f"The tool '{name}' is not available for this question. Available: {', '.join(allowed)}."}
    if not isinstance(arguments, dict) or not set(arguments) <= set(SPECS[name]["arguments"]):
        return {"error": f"Use only these arguments for {name}: {', '.join(SPECS[name]['arguments'])}."}
    try:
        return tools[name](**arguments)
    except TOOL_ERRORS as error:
        return {"error": str(error)}
    except TypeError:  # a missing argument
        return {"error": f"Missing argument for {name}: {', '.join(SPECS[name]['arguments'])}."}


def _serialize(result: dict) -> str:
    text = json.dumps(result, default=str)
    return text if len(text) <= MAX_RESULT_CHARS else text[:MAX_RESULT_CHARS] + ' ... [result cut: ask for fewer rows]'


def _log(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


def run_agent(question: str, client: ModelClient, tools: dict[str, Callable] | None = None,
              log_path: Path | None = None) -> dict:
    """Answer one question. Returns the answer and how it was reached."""
    started = time.perf_counter()
    decision = route(question)
    tools = tools or TOOLS
    log_path = log_path or DEFAULT_LOG
    tier, called, tokens = decision["tier"], [], {"input": 0, "output": 0}
    budget, exhausted, answer, model_calls = BUDGET[tier], False, None, 0

    if decision["intent"] == "out_of_scope":
        answer = DECLINE  # nothing to look up, so there is nothing to spend a model call on
    else:
        model = model_ids()[tier]
        system = build_system_prompt(decision)
        specs = [{"name": n, **SPECS[n]} for n in decision["tools"]]
        messages = [{"role": "user", "content": question}]
        while answer is None:
            exhausted = len(called) >= budget
            # With the budget spent the model gets no tools, so the only thing it can do is answer.
            reply = client.complete(model, system, messages, [] if exhausted else specs)
            model_calls += 1
            usage = reply.get("usage") or {}
            tokens["input"] += usage.get("input_tokens", 0)
            tokens["output"] += usage.get("output_tokens", 0)
            call = reply.get("tool_call")
            if call and not exhausted:
                called.append(call["name"])
                result = _call_tool(call["name"], call.get("input"), decision["tools"], tools)
                messages += [{"role": "assistant", "tool_call": call},
                             {"role": "tool", "name": call["name"], "content": _serialize(result)}]
            else:
                answer = reply.get("text") or "I could not produce an answer from what I found."
                if exhausted and call:  # it wanted more tools than the budget allows
                    answer += " (The tool budget ran out before I could check everything.)"

    outcome = {
        "answer": answer, "intent": decision["intent"], "tier": tier, "tools_called": called,
        "budget": budget, "budget_exhausted": exhausted,
    }
    _log(log_path, {
        "intent": outcome["intent"], "tier": tier, "tools": called, "model_calls": model_calls,
        "budget_exhausted": exhausted, "input_tokens": tokens["input"], "output_tokens": tokens["output"],
        "latency_ms": round((time.perf_counter() - started) * 1000),
    })
    return outcome


def plan(question: str) -> dict:
    """What the loop would do for a question, without calling any model."""
    decision = route(question)
    return {**decision, "model": model_ids()[decision["tier"]], "budget": BUDGET[decision["tier"]],
            "system_prompt_chars": len(build_system_prompt(decision))}


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[1] not in ("--plan", "--ask"):
        print('usage: python agent/agent.py --plan|--ask "question"', file=sys.stderr)
        return 1
    if argv[1] == "--plan":
        print(json.dumps(plan(argv[2]), indent=2))
        return 0
    try:
        outcome = run_agent(argv[2], AnthropicClient())  # raises MissingKey before any network use
    except ModelError as error:
        print(error, file=sys.stderr)
        return 1
    print(outcome["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
