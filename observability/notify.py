"""Slack alerts, built by code and simulated until a webhook exists (ADR-0020).

    python observability/notify.py --item weekly-audit --title "Audit raised a flag" --line "Deals without a company: 6" --write

The text of every message is built here from fixed templates, never by a model, so an
alert says exactly what the data says. One thread per item: the first alert for an item
opens it, and everything after (a new cause, "running again") is a reply in that thread.

Where a message goes:
- dry run (default): printed, nothing kept;
- --write without the kill switch SLACK_ALERTS_ENABLED=true: shadow run, printed only;
- --write with the kill switch: appended to observability/logs/slack-<date>.md, the simulated
  channel, and, only if SLACK_WEBHOOK_URL is also set, posted to that webhook. The webhook
  host must be hooks.slack.com: a server-side request goes only to an allowlisted host.
Nothing in this repository sets SLACK_WEBHOOK_URL; it has never posted to Slack.
"""

import argparse
import json
import os
import sys
import urllib.request
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automations" / "_lib"))

from controls import ControlsError, WriteControls  # noqa: E402

LOGS = ROOT / "observability" / "logs"
ALLOWED_HOSTS = {"hooks.slack.com"}
WEBHOOK_VARIABLE = "SLACK_WEBHOOK_URL"


def build_message(item: str, title: str, lines: list[str], thread: str | None) -> dict:
    """The whole message, from a fixed template. `thread` is the item's thread, or None for a new one."""
    body = "\n".join(f"- {line}" for line in lines)
    return {"item": item, "thread": thread, "text": f"*{title}* ({item})\n{body}".rstrip()}


def _threads(logs: Path) -> dict:
    path = logs / "slack-threads.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def _post(url: str, text: str) -> None:
    if urlparse(url).hostname not in ALLOWED_HOSTS:
        raise ValueError("the Slack webhook host is not on the allowlist")
    request = urllib.request.Request(url, data=json.dumps({"text": text}).encode("utf-8"),
                                     headers={"content-type": "application/json"})
    with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310 (host checked above)
        if response.status != 200:
            raise RuntimeError(f"Slack answered {response.status}")


def send(item: str, title: str, lines: list[str], write: bool, logs: Path = LOGS,
         env: dict | None = None, today: str | None = None) -> dict:
    """Send one alert through the write controls. Returns the message and what happened to it."""
    env = os.environ if env is None else env
    controls = WriteControls("slack-alerts", write, env=env)
    threads = _threads(logs)
    message = build_message(item, title, lines, threads.get(item))
    if controls.mode != "write":
        return {**message, "status": controls.mode}
    channel = logs / f"slack-{today or date.today().isoformat()}.md"

    def write_one(_):
        logs.mkdir(parents=True, exist_ok=True)
        thread = message["thread"] or f"thread-{item}-{len(threads) + 1}"
        prefix = f"reply in {thread}" if message["thread"] else f"new thread {thread}"
        with channel.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(f"\n## {prefix}\n\n{message['text']}\n")
        threads[item] = thread
        (logs / "slack-threads.json").write_text(json.dumps(threads, indent=2), encoding="utf-8")
        if env.get(WEBHOOK_VARIABLE):
            _post(env[WEBHOOK_VARIABLE], message["text"])

    outcome = controls.apply([item], write_one, lambda _: message["text"] in channel.read_text(encoding="utf-8"))
    status = "sent" if outcome.applied else f"needs review: {outcome.needs_review.get(item)}"
    return {**message, "thread": threads.get(item), "status": status}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Send one Slack alert (dry run unless --write).")
    parser.add_argument("--item", required=True, help="catalog id of the thing the alert is about")
    parser.add_argument("--title", required=True)
    parser.add_argument("--line", action="append", default=[], help="one line of the message; repeat")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = send(args.item, args.title, args.line, args.write)
    except (ControlsError, ValueError, OSError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0 if not result["status"].startswith("needs review") else 1


if __name__ == "__main__":
    sys.exit(main())
