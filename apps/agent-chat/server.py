"""Agent chat: a local web chat that shows the RevOps agent working, step by step.

    python apps/agent-chat/server.py            # http://127.0.0.1:8765, demo mode, no key
    python apps/agent-chat/server.py --model    # the real model, only if ANTHROPIC_API_KEY is set

Spec: apps/agent-chat/SPEC.md. Decision: ADR-0023.
It runs the real agent loop (router, category profile, four prompt blocks, budget, the five
read-only tools on the local lakehouse) and returns, next to the answer, the trace of how it
got there. In demo mode a scripted model (demo_model.py) plays the model's part, so the page
works with no key and says so on every answer.

Why it is safe to run: it listens on 127.0.0.1 only, so nobody outside this machine reaches
it; it accepts one JSON field, validated on the server; it refuses requests from other web
pages (Origin check); it serves no third-party script (a strict Content-Security-Policy);
and nothing it calls can write.
"""

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "agent"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "automations" / "_lib"))

import agent  # noqa: E402
from ai_step import AIStepError, run_ai_step  # noqa: E402
from demo_model import DemoModel  # noqa: E402

TITLE_PROMPT = ROOT / "agent" / "prompts" / "conversation-title.md"


class DemoTitler:
    """Plays the model with no key: the first words of the question become the title."""

    def complete(self, model, system, messages, tools):
        question = json.loads(messages[0]["content"])["question"]
        words = question.rstrip("?!. ").split()
        return {"text": json.dumps({"title": " ".join(words[:7])[:60]}), "tool_call": None, "usage": {}}


def title_for(question: str, use_model: bool, log_path: Path | None = None) -> str:
    """A short title for the thread, from the cheapest model; a bad reply falls back to the question."""
    def validate(reply):
        title = reply.get("title") if set(reply) == {"title"} else None
        if not isinstance(title, str) or not title.strip() or len(title) > 60:
            raise AIStepError("the title is missing or longer than 60 characters")
        return reply
    try:
        step = run_ai_step("conversation-title", TITLE_PROMPT, {"question": question}, validate,
                           demo_client=DemoTitler(), use_model=use_model,
                           log_path=(log_path.parent / "ai-steps.jsonl") if log_path else None)
        return step["output"]["title"]
    except AIStepError:
        return question[:60]

HOST = "127.0.0.1"
MAX_BODY_BYTES = 4_096
MAX_QUESTION_CHARS = 500
STATIC = {"/": ("page.html", "text/html; charset=utf-8"),
          "/app.js": ("app.js", "text/javascript; charset=utf-8"),
          "/app.css": ("app.css", "text/css; charset=utf-8")}
SECURITY_HEADERS = {
    "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; "
                               "frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}


class InvalidRequest(ValueError):
    """The request was refused before it reached the agent."""


def parse_question(body: bytes) -> str:
    """The one input, checked on the server: a JSON object with a short, non-empty question."""
    if len(body) > MAX_BODY_BYTES:
        raise InvalidRequest("the request is too large")
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        raise InvalidRequest("the request must be JSON") from None
    if not isinstance(data, dict) or set(data) != {"question"}:
        raise InvalidRequest('send exactly one field: {"question": "..."}')
    question = data["question"]
    if not isinstance(question, str) or not question.strip():
        raise InvalidRequest("the question must be a non-empty text")
    if len(question) > MAX_QUESTION_CHARS:
        raise InvalidRequest(f"the question is longer than {MAX_QUESTION_CHARS} characters")
    return question.strip()


def answer(question: str, use_model: bool = False, log_path: Path | None = None) -> dict:
    """Run the agent and return the answer with the trace the page shows."""
    plan = agent.plan(question)
    client = DemoModel()
    if use_model:
        from model_client import AnthropicClient  # raises MissingKey when no key is set
        client = AnthropicClient()
    outcome = agent.run_agent(question, client, log_path=log_path)
    steps = client.calls if isinstance(client, DemoModel) else []
    return {
        "mode": "model" if use_model else "demo",
        "title": title_for(question, use_model, log_path),
        "answer": outcome["answer"],
        "route": {k: plan[k] for k in ("intent", "via", "reason", "tier", "model", "budget", "tools", "fixed_docs", "skill")},
        "prompt_blocks": plan["system_blocks"],
        "tools_called": outcome["tools_called"],
        "budget_exhausted": outcome["budget_exhausted"],
        "model_calls": steps,
    }


def allowed_origin(origin: str | None, port: int) -> bool:
    """A browser sends Origin on a cross-site POST; only this page's own origin may call the API."""
    return origin is None or origin in (f"http://{HOST}:{port}", f"http://localhost:{port}")


class Handler(BaseHTTPRequestHandler):
    use_model = False
    log_path = None

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for name, value in SECURITY_HEADERS.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, data: dict) -> None:
        self._send(status, json.dumps(data, default=str).encode("utf-8"), "application/json")

    def do_GET(self):  # noqa: N802 (the name is set by BaseHTTPRequestHandler)
        if self.path == "/api/health":
            return self._json(200, {"ok": True, "mode": "model" if self.use_model else "demo"})
        if self.path in STATIC:
            name, content_type = STATIC[self.path]
            return self._send(200, (HERE / name).read_bytes(), content_type)
        return self._json(404, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        if self.path != "/api/chat":
            return self._json(404, {"error": "not found"})
        if not allowed_origin(self.headers.get("Origin"), self.server.server_address[1]):
            return self._json(403, {"error": "requests from other pages are refused"})
        if (self.headers.get("Content-Type") or "").split(";")[0].strip() != "application/json":
            return self._json(415, {"error": "the request must be JSON"})
        try:
            length = int(self.headers.get("Content-Length") or 0)
            question = parse_question(self.rfile.read(min(length, MAX_BODY_BYTES + 1)))
            return self._json(200, answer(question, self.use_model, self.log_path))
        except InvalidRequest as error:
            return self._json(400, {"error": str(error)})
        except Exception as error:  # full detail on the console, a generic message on the page
            print(f"ERROR {type(error).__name__}: {error}", file=sys.stderr)
            return self._json(500, {"error": "the agent could not answer; see the server console"})

    def log_message(self, fmt, *args):  # the default prints every request; questions stay out of logs
        pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local chat that shows the RevOps agent working.")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--model", action="store_true", help="use the real model (needs ANTHROPIC_API_KEY)")
    args = parser.parse_args(argv)
    if args.model and not os.environ.get("ANTHROPIC_API_KEY"):
        print("--model needs ANTHROPIC_API_KEY in the environment; run without it for the demo.", file=sys.stderr)
        return 1
    Handler.use_model = args.model
    server = ThreadingHTTPServer((HOST, args.port), Handler)  # 127.0.0.1 only: never reachable from outside
    print(f"Agent chat on http://{HOST}:{args.port} ({'model' if args.model else 'demo, no key'}). Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
