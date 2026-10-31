"""Tests for apps/agent-chat: the server's guards and the demo model. No model and no network."""

import importlib.util
import json
import sys
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "agent-chat"
sys.path.insert(0, str(APP))


def load(name):
    spec = importlib.util.spec_from_file_location(f"agent_chat_{name}", APP / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


server = load("server")
demo_model = load("demo_model")


@pytest.mark.parametrize("body, message", [
    (b"not json", "must be JSON"),
    (b'{"question": ""}', "non-empty"),
    (b'{"question": "x", "role": "admin"}', "exactly one field"),
    (json.dumps({"question": "x" * 501}).encode(), "longer than 500"),
    (b"x" * 5000, "too large"),
])
def test_bad_input_is_refused_before_the_agent(body, message):
    with pytest.raises(server.InvalidRequest, match=message):
        server.parse_question(body)


def test_only_this_pages_origin_may_call_the_api():
    assert server.allowed_origin(None, 8765) and server.allowed_origin("http://127.0.0.1:8765", 8765)
    assert not server.allowed_origin("https://evil.example", 8765)


def test_an_answer_carries_the_trace_and_says_it_is_a_demo(tmp_path):
    out = server.answer("What counts as an active customer?", log_path=tmp_path / "log.jsonl")
    assert out["mode"] == "demo" and out["answer"].startswith("Demo answer: no language model was called")
    assert out["route"]["intent"] == "definition_question" and out["tools_called"] == ["search_context"]
    assert [b["cached"] for b in out["prompt_blocks"]][:3] == [True, True, False]


def test_a_write_request_is_refused_without_a_model_call(tmp_path):
    out = server.answer("Update this deal to closed won", log_path=tmp_path / "log.jsonl")
    assert out["route"]["intent"] == "out_of_scope" and out["model_calls"] == [] and out["tools_called"] == []


def test_the_demo_model_picks_a_fixed_query_by_topic_and_only_offered_tools():
    pick = demo_model.DemoModel._pick_tool
    call = pick("metric_lookup", "How many MQLs last month?", {"query_gold", "search_context"})
    assert call["name"] == "query_gold" and "gold.mql_monthly" in call["input"]["sql"]
    assert pick("metric_lookup", "anything", {"search_context"})["name"] == "search_context"


def test_a_tool_error_is_reported_not_hidden():
    text = demo_model.DemoModel._answer("metric_lookup", [{"name": "query_gold", "is_error": True,
                                                           "content": json.dumps({"error": "lakehouse not found"})}])
    assert "failed: lakehouse not found" in text


@pytest.fixture
def running(tmp_path):
    server.Handler.log_path = tmp_path / "log.jsonl"
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()


def test_the_page_is_served_with_strict_security_headers(running):
    with urllib.request.urlopen(running + "/") as response:
        csp = response.headers["Content-Security-Policy"]
        assert "script-src 'self'" in csp and response.headers["X-Frame-Options"] == "DENY"
        assert b"<script src=\"/app.js\"></script>" in response.read()


def test_the_api_refuses_a_cross_site_request_and_a_wrong_content_type(running):
    def post(headers):
        request = urllib.request.Request(running + "/api/chat", data=b'{"question": "MRR"}', headers=headers)
        try:
            return urllib.request.urlopen(request).status
        except urllib.error.HTTPError as error:
            return error.code
    assert post({"Content-Type": "application/json", "Origin": "https://evil.example"}) == 403
    assert post({"Content-Type": "text/plain"}) == 415


def test_the_server_binds_to_localhost_only_and_never_puts_data_in_html():
    code = (APP / "server.py").read_text(encoding="utf-8")
    script = (APP / "app.js").read_text(encoding="utf-8")
    assert 'HOST = "127.0.0.1"' in code and "0.0.0.0" not in code
    assert "innerHTML" not in script.replace("never innerHTML", "")
