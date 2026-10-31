"""The adapter that lets agent/agent.py talk to the Claude Messages API.

This is the structure only. Nothing in the repository calls it with a real key: the tests
give it a fake transport, and `python agent/agent.py --ask ...` stops with a clear message
when ANTHROPIC_API_KEY is not set (ADR-0016).

It has no dependency. The request is built by hand and sent with the standard library, so
adding it did not change requirements.txt. The loop in agent.py keeps its own message
format (see ModelClient there); this file translates it to the API format and back.
"""

import json
import os
import urllib.error
import urllib.request

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
KEY_VARIABLE = "ANTHROPIC_API_KEY"  # the name registered in connectors/registry.yaml
MAX_TOKENS = 1024
TIMEOUT_SECONDS = 60
MAX_ERROR_CHARS = 200  # an API error is shown short, so it can never fill a log or a screen


class ModelError(RuntimeError):
    """The model could not be reached or refused the request."""


class MissingKey(ModelError):
    """No API key was given and the environment variable is empty."""


def http_transport(url: str, headers: dict, body: bytes, timeout: int) -> tuple[int, bytes]:
    """The only function that touches the network. Tests replace it."""
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 (fixed https url)
            return response.status, response.read()
    except urllib.error.HTTPError as error:  # a 4xx or 5xx still carries a useful body
        return error.code, error.read()
    except (urllib.error.URLError, TimeoutError) as error:
        raise ModelError(f"Could not reach the model API: {type(error).__name__}") from None


def _input_schema(arguments: dict[str, str]) -> dict:
    """agent.SPECS describes arguments as 'integer, optional, 1 to 5'. The API wants JSON Schema."""
    properties, required = {}, []
    for name, text in arguments.items():
        kind = text.split(",")[0].strip()
        properties[name] = {"type": kind if kind in ("string", "integer") else "string", "description": text}
        if "optional" not in text:
            required.append(name)
    return {"type": "object", "properties": properties, "required": required}


def _to_api_messages(messages: list[dict]) -> list[dict]:
    """Our three roles become the API's two. A tool call and its result share an id by position."""
    converted, call_number = [], 0
    for message in messages:
        if message["role"] == "user":
            converted.append({"role": "user", "content": message["content"]})
        elif message["role"] == "assistant":
            call_number += 1
            call = message["tool_call"]
            converted.append({"role": "assistant", "content": [
                {"type": "tool_use", "id": f"toolu_{call_number}", "name": call["name"], "input": call.get("input") or {}}]})
        else:  # "tool": the result of the call just above
            converted.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": f"toolu_{call_number}", "content": message["content"]}]})
    return converted


class AnthropicClient:
    """Implements agent.ModelClient. One call to `complete` is one request to the API."""

    def __init__(self, api_key: str | None = None, transport=None, max_tokens: int = MAX_TOKENS):
        self._key = api_key or os.environ.get(KEY_VARIABLE)
        if not self._key:
            raise MissingKey(f"{KEY_VARIABLE} is not set. Export it in your shell; the repository never reads .env.")
        self._transport = transport or http_transport
        self._max_tokens = max_tokens

    def build_request(self, model: str, system: str, messages: list[dict], tools: list[dict]) -> dict:
        body = {"model": model, "max_tokens": self._max_tokens, "system": system,
                "messages": _to_api_messages(messages)}
        if tools:  # with the budget spent the loop sends none, and the model can only answer
            body["tools"] = [{"name": t["name"], "description": t["description"],
                              "input_schema": _input_schema(t["arguments"])} for t in tools]
            body["tool_choice"] = {"type": "auto", "disable_parallel_tool_use": True}  # the loop runs one call at a time
        return body

    def complete(self, model: str, system: str, messages: list[dict], tools: list[dict]) -> dict:
        headers = {"x-api-key": self._key, "anthropic-version": API_VERSION, "content-type": "application/json"}
        body = json.dumps(self.build_request(model, system, messages, tools)).encode("utf-8")
        status, raw = self._transport(API_URL, headers, body, TIMEOUT_SECONDS)
        try:
            data = json.loads(raw)
        except ValueError:
            raise ModelError(f"The model API returned a reply that is not JSON (status {status}).") from None
        if status != 200:
            detail = str((data.get("error") or {}).get("message", ""))[:MAX_ERROR_CHARS]
            raise ModelError(f"The model API refused the request (status {status}): {detail}")
        blocks = data.get("content") or []
        text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text") or None
        call = next(({"name": b["name"], "input": b.get("input") or {}} for b in blocks if b.get("type") == "tool_use"), None)
        return {"text": text, "tool_call": call, "usage": data.get("usage") or {}}
