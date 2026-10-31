"""Tests for mcp_server/server.py, including the security tests in mcp_server/README.md."""

import json
import os
import subprocess
import sys
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mcp_server"))

import server  # noqa: E402


@pytest.fixture(scope="module")
def db(tmp_path_factory):
    path = tmp_path_factory.mktemp("lake") / "lakehouse.duckdb"
    con = duckdb.connect(str(path))
    con.execute("""
        CREATE SCHEMA silver; CREATE SCHEMA gold;
        CREATE TABLE silver.customer (name VARCHAR); INSERT INTO silver.customer VALUES ('silver-secret');
        CREATE TABLE gold.t (a INT); INSERT INTO gold.t VALUES (1);
        CREATE TABLE gold.big AS SELECT range AS n FROM range(2000);
    """)
    con.close()
    return path


def call(db, name, **arguments):
    reply = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                           "params": {"name": name, "arguments": arguments}}, db)
    if "error" in reply:
        return reply
    return {"isError": reply["result"]["isError"], "data": json.loads(reply["result"]["content"][0]["text"])}


# --- the protocol ------------------------------------------------------------------------

def test_initialize_names_the_server_and_offers_tools():
    reply = server.handle({"jsonrpc": "2.0", "id": 7, "method": "initialize", "params": {}})
    assert reply["id"] == 7 and reply["result"]["serverInfo"]["name"] == "fernway-gold"
    assert "tools" in reply["result"]["capabilities"]


def test_the_server_offers_exactly_the_four_tools_in_its_contract():
    names = [t["name"] for t in server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]]
    assert names == ["list_gold_tables", "describe_table", "get_context", "query_gold"]
    readme = (ROOT / "mcp_server" / "README.md").read_text(encoding="utf-8")
    assert all(f"`{n}`" in readme for n in names)


def test_a_notification_gets_no_reply():
    assert server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


@pytest.mark.parametrize("message", [[], "x", {"id": 1, "method": "ping"}, {"jsonrpc": "2.0", "id": 1}])
def test_a_malformed_request_is_an_invalid_request(message):
    assert server.handle(message)["error"]["code"] == -32600


def test_an_unknown_method_is_not_found():
    assert server.handle({"jsonrpc": "2.0", "id": 1, "method": "resources/list"})["error"]["code"] == -32601


def test_an_unlisted_tool_cannot_be_called():
    assert call(None, "write_crm", field="owner")["error"]["message"] == "Unknown tool"


@pytest.mark.parametrize("arguments", [{}, {"sql": "select 1", "extra": 1}, {"other": 1}])
def test_wrong_arguments_are_refused(db, arguments):
    assert call(db, "query_gold", **arguments)["error"]["code"] == -32602


# --- query_gold: the security tests in the contract --------------------------------------

@pytest.mark.parametrize("sql", ["INSERT INTO gold.t VALUES (2)", "UPDATE gold.t SET a = 2", "DELETE FROM gold.t",
                                 "DROP TABLE gold.t", "CREATE TABLE gold.x (a INT)", "ATTACH 'x.db' AS x"])
def test_a_statement_that_writes_is_rejected_and_nothing_changes(db, sql):
    assert call(db, "query_gold", sql=sql)["isError"] is True
    assert call(db, "query_gold", sql="select count(*) from gold.t")["data"]["rows"] == [[1]]


@pytest.mark.parametrize("sql", ["select * from silver.customer", "select * from bronze.raw_contact"])
def test_a_query_on_silver_or_bronze_is_rejected(db, sql):
    out = call(db, "query_gold", sql=sql)
    assert out["isError"] is True and "silver-secret" not in json.dumps(out)


def test_two_statements_are_rejected(db):
    assert call(db, "query_gold", sql="select 1; select 2")["isError"] is True


def test_a_result_is_cut_at_200_rows_and_says_so(db):
    data = call(db, "query_gold", sql="select n from gold.big")["data"]
    assert data["row_count"] == 200 and data["truncated"] is True


# --- the catalog and the context ---------------------------------------------------------

def test_the_gold_tables_are_listed_with_descriptions():
    tables = call(None, "list_gold_tables")["data"]["tables"]
    assert "gold.mrr_monthly" in [t["name"] for t in tables] and all(t["description"] for t in tables)


def test_a_gold_table_is_described_with_its_columns():
    data = call(None, "describe_table", table="gold.mrr_monthly")["data"]
    assert data["layer"] == "gold" and data["columns"]


@pytest.mark.parametrize("table", ["silver.deal", "gold.nope", "../secrets", ""])
def test_a_table_that_is_not_in_gold_is_rejected_not_looked_up(table):
    assert call(None, "describe_table", table=table)["isError"] is True


def test_a_context_document_is_served_with_its_status():
    data = call(None, "get_context", concept="active-customer")["data"]
    assert data["status"] == "canonical" and "Active customer" in data["text"]


@pytest.mark.parametrize("concept", ["../README", "nope", "", None])
def test_a_concept_id_is_never_turned_into_a_path(concept):
    assert call(None, "get_context", concept=concept)["isError"] is True


# --- over stdio --------------------------------------------------------------------------

def test_serve_answers_line_by_line_and_survives_garbage():
    out = []
    lines = ['{"jsonrpc": "2.0", "id": 1, "method": "ping"}\n', "not json\n", "\n", "x" * 200_000 + "\n"]
    server.serve(lines, out.append)
    replies = [json.loads(o) for o in out]
    assert replies[0] == {"jsonrpc": "2.0", "id": 1, "result": {}}
    assert [r["error"]["code"] for r in replies[1:]] == [-32700, -32600]


def test_the_script_runs_as_a_process_on_stdin_and_stdout():
    request = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}) + "\n"
    done = subprocess.run([sys.executable, str(ROOT / "mcp_server" / "server.py")], input=request,
                          capture_output=True, text=True, timeout=60, env={**os.environ, "PYTHONUTF8": "1"})
    assert len(json.loads(done.stdout)["result"]["tools"]) == 4
