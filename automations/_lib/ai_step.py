"""One AI step inside an automation: prompt from the repository, validated output, tokens and cost logged.

Every automation that uses a model calls run_ai_step. It does the parts that must be the
same everywhere, so no automation can skip them:

- the prompt is a file in the repository; its SHA-256 (line endings normalised) goes with
  every run, so a result can always be tied to the exact prompt that produced it;
- the model answers with one JSON object; the caller's validator checks it in code and
  anything that fails is "needs review", never written;
- tokens (input, output, cache) and the estimated cost are logged per run in
  observability/logs/ai-steps.jsonl, with the automation name and the prompt hash, and no
  input text, so the log holds no personal data;
- without a key, a scripted client given by the automation plays the model, and the log
  says the mode was "demo".

The model is called through the agent's adapter (agent/model_client.py), the same one the
agent uses; the cost uses the agent's price table, so an unknown price is null, never zero.
"""

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agent"))

LOG = ROOT / "observability" / "logs" / "ai-steps.jsonl"


class AIStepError(ValueError):
    """The model's output failed validation; nothing from it may be used."""


def prompt_hash(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")).hexdigest()


def parse_json(text: str | None) -> dict:
    """The first JSON object in the reply. A model sometimes wraps it in a code fence."""
    text = (text or "").strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise AIStepError("the reply holds no JSON object")
    try:
        data = json.loads(text[start:end + 1])
    except ValueError:
        raise AIStepError("the reply is not valid JSON") from None
    if not isinstance(data, dict):
        raise AIStepError("the reply is not a JSON object")
    return data


def run_ai_step(automation: str, prompt_path: Path, payload: dict, validate: Callable[[dict], dict],
                demo_client=None, use_model: bool = False, log_path: Path | None = None) -> dict:
    """Run one step and return {"output", "mode", "prompt_sha256", "usage", "cost_usd"}.

    `validate` receives the parsed reply and returns the clean output, or raises AIStepError.
    """
    import agent  # the price table and the model ids
    mode = "model" if use_model else "demo"
    if use_model:
        from model_client import AnthropicClient
        client = AnthropicClient()  # raises MissingKey when no key is set
    else:
        client = demo_client
    model = agent.model_ids()["fast"]
    started = time.perf_counter()
    reply = client.complete(model, prompt_path.read_text(encoding="utf-8"),
                            [{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}], [])
    usage = reply.get("usage") or {}
    tokens = {"input": usage.get("input_tokens", 0), "output": usage.get("output_tokens", 0),
              "cache_write": usage.get("cache_creation_input_tokens", 0),
              "cache_read": usage.get("cache_read_input_tokens", 0)}
    cost = agent.estimate_cost({model: tokens}) if any(tokens.values()) else 0.0
    record = {"automation": automation, "mode": mode, "model": model, "prompt_sha256": prompt_hash(prompt_path),
              **{f"{k}_tokens": v for k, v in tokens.items()}, "cost_usd": cost,
              "latency_ms": round((time.perf_counter() - started) * 1000)}
    try:
        output = validate(parse_json(reply.get("text")))
        record["valid"] = True
    except AIStepError as error:
        record["valid"], record["reason"] = False, str(error)
        raise
    finally:
        path = log_path or LOG
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
    return {"output": output, "mode": mode, "prompt_sha256": record["prompt_sha256"],
            "usage": tokens, "cost_usd": cost}


def model_available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))
