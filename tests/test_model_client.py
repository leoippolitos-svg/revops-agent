"""Tests for agent/model_client.py, with a fake transport. No network and no key are used."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))

import agent  # noqa: E402
import model_client  # noqa: E402
from model_client import AnthropicClient, MissingKey, ModelError  # noqa: E402

FAKE_KEY = "test-key-not-real"


class FakeTransport:
    """Records the request and plays back one reply."""

    def __init__(self, status=200, body=None):
        self.status, self.body, self.requests = status, body if body is not None else {"content": []}, []

    def __call__(self, url, headers, body, timeout):
        self.requests.append({"url": url, "headers": headers, "body": json.loads(body), "timeout": timeout})
        raw = self.body if isinstance(self.body, bytes) else json.dumps(self.body).encode()
        return self.status, raw


def client(**kwargs):
    transport = kwargs.pop("transport", None) or FakeTransport()
    return AnthropicClient(api_key=FAKE_KEY, transport=transport, **kwargs), transport


SPECS = [{"name": n, **agent.SPECS[n]} for n in ("search_context", "get_catalog")]


# --- the key -----------------------------------------------------------------------------

def test_no_key_stops_before_anything_is_sent(monkeypatch):
    monkeypatch.delenv(model_client.KEY_VARIABLE, raising=False)
    with pytest.raises(MissingKey, match="never reads .env"):
        AnthropicClient()


def test_the_key_can_come_from_the_environment(monkeypatch):
    monkeypatch.setenv(model_client.KEY_VARIABLE, FAKE_KEY)
    assert AnthropicClient(transport=FakeTransport())._key == FAKE_KEY


def test_the_variable_name_is_the_one_in_the_connector_registry():
    registry = (ROOT / "connectors" / "registry.yaml").read_text(encoding="utf-8")
    assert f"{model_client.KEY_VARIABLE} in .env" in registry


# --- the request -------------------------------------------------------------------------

def test_the_request_goes_to_the_messages_api_with_the_key_in_a_header_only():
    c, transport = client()
    c.complete("claude-haiku-5-5", "system text", [{"role": "user", "content": "hi"}], [])
    (sent,) = transport.requests
    assert sent["url"] == "https://api.anthropic.com/v1/messages" and sent["timeout"] == 60
    assert sent["headers"]["x-api-key"] == FAKE_KEY and sent["headers"]["anthropic-version"] == "2023-06-01"
    assert FAKE_KEY not in json.dumps(sent["body"])
    assert sent["body"]["model"] == "claude-haiku-5-5" and sent["body"]["system"] == "system text"
    assert sent["body"]["messages"] == [{"role": "user", "content": "hi"}]


def test_with_no_tools_the_request_has_no_tools_so_the_model_can_only_answer():
    c, transport = client()
    c.complete("m", "s", [{"role": "user", "content": "hi"}], [])
    assert "tools" not in transport.requests[0]["body"] and "tool_choice" not in transport.requests[0]["body"]


def test_tool_specs_become_json_schema_and_optional_arguments_are_not_required():
    c, transport = client()
    c.complete("m", "s", [{"role": "user", "content": "hi"}], SPECS)
    body = transport.requests[0]["body"]
    by_name = {t["name"]: t["input_schema"] for t in body["tools"]}
    assert by_name["search_context"]["required"] == ["question"]
    assert by_name["search_context"]["properties"]["k"]["type"] == "integer"
    assert by_name["get_catalog"]["required"] == ["model"]
    assert body["tool_choice"]["disable_parallel_tool_use"] is True


def test_a_tool_call_and_its_result_share_an_id_in_the_api_format():
    c, transport = client()
    messages = [{"role": "user", "content": "q"},
                {"role": "assistant", "tool_call": {"name": "search_context", "input": {"question": "x"}}},
                {"role": "tool", "name": "search_context", "content": '{"ok": true}'},
                {"role": "assistant", "tool_call": {"name": "get_catalog", "input": {"model": "gold.t"}}},
                {"role": "tool", "name": "get_catalog", "content": "{}"}]
    c.complete("m", "s", messages, SPECS)
    sent = transport.requests[0]["body"]["messages"]
    assert [m["role"] for m in sent] == ["user", "assistant", "user", "assistant", "user"]
    assert sent[1]["content"][0]["id"] == sent[2]["content"][0]["tool_use_id"] == "toolu_1"
    assert sent[3]["content"][0]["id"] == sent[4]["content"][0]["tool_use_id"] == "toolu_2"
    assert sent[2]["content"][0]["content"] == '{"ok": true}'


# --- the reply ---------------------------------------------------------------------------

def test_a_text_reply_becomes_text_and_usage():
    body = {"content": [{"type": "text", "text": "Hello "}, {"type": "text", "text": "there"}],
            "usage": {"input_tokens": 12, "output_tokens": 3}}
    c, _ = client(transport=FakeTransport(body=body))
    assert c.complete("m", "s", [{"role": "user", "content": "q"}], []) == {
        "text": "Hello there", "tool_call": None, "usage": {"input_tokens": 12, "output_tokens": 3}}


def test_a_tool_use_block_becomes_a_tool_call():
    body = {"content": [{"type": "text", "text": "Let me look."},
                        {"type": "tool_use", "id": "toolu_x", "name": "search_context", "input": {"question": "mql"}}]}
    c, _ = client(transport=FakeTransport(body=body))
    reply = c.complete("m", "s", [{"role": "user", "content": "q"}], SPECS)
    assert reply["tool_call"] == {"name": "search_context", "input": {"question": "mql"}}


def test_an_empty_reply_has_no_text_and_no_call():
    c, _ = client()
    reply = c.complete("m", "s", [{"role": "user", "content": "q"}], [])
    assert reply["text"] is None and reply["tool_call"] is None


# --- failures ----------------------------------------------------------------------------

def test_an_api_error_is_raised_short_and_without_the_key():
    body = {"error": {"type": "invalid_request_error", "message": "x" * 500}}
    c, _ = client(transport=FakeTransport(status=400, body=body))
    with pytest.raises(ModelError) as error:
        c.complete("m", "s", [{"role": "user", "content": "q"}], [])
    assert "status 400" in str(error.value) and len(str(error.value)) < 300 and FAKE_KEY not in str(error.value)


def test_a_reply_that_is_not_json_is_an_error():
    c, _ = client(transport=FakeTransport(status=502, body=b"<html>bad gateway</html>"))
    with pytest.raises(ModelError, match="not JSON"):
        c.complete("m", "s", [{"role": "user", "content": "q"}], [])


def test_the_default_transport_turns_a_network_failure_into_a_model_error(monkeypatch):
    def fail(*args, **kwargs):
        raise model_client.urllib.error.URLError("no network")
    monkeypatch.setattr(model_client.urllib.request, "urlopen", fail)
    with pytest.raises(ModelError, match="Could not reach"):
        model_client.http_transport(model_client.API_URL, {}, b"{}", 1)


# --- inside the loop ---------------------------------------------------------------------

def test_the_adapter_runs_the_whole_loop_against_a_fake_api(tmp_path):
    replies = [{"content": [{"type": "tool_use", "id": "t", "name": "search_context",
                             "input": {"question": "active customer"}}], "usage": {"input_tokens": 50, "output_tokens": 5}},
               {"content": [{"type": "text", "text": "An active customer is..."}], "usage": {"input_tokens": 80, "output_tokens": 9}}]

    class Sequence(FakeTransport):
        def __call__(self, *args):
            self.body = replies[len(self.requests)]
            return super().__call__(*args)

    c, transport = client(transport=Sequence())
    out = agent.run_agent("What counts as an active customer?", c, None, tmp_path / "log.jsonl")
    assert out["answer"] == "An active customer is..." and out["tools_called"] == ["search_context"]
    assert transport.requests[0]["body"]["model"] == "claude-haiku-5-5"
    assert transport.requests[1]["body"]["messages"][-1]["content"][0]["type"] == "tool_result"
    assert json.loads((tmp_path / "log.jsonl").read_text(encoding="utf-8"))["input_tokens"] == 130


# --- the command line --------------------------------------------------------------------

def test_ask_without_a_key_exits_with_a_message_and_calls_nothing(monkeypatch, capsys):
    monkeypatch.delenv(model_client.KEY_VARIABLE, raising=False)
    assert agent.main(["agent.py", "--ask", "What counts as an active customer?"]) == 1
    assert "is not set" in capsys.readouterr().err
