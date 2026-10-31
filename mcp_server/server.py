"""A read-only MCP server over the gold layer, the catalog and the context documents.

    python mcp_server/server.py        # speaks MCP (JSON-RPC 2.0) on stdin and stdout

Contract: mcp_server/README.md. Decision: ADR-0008 and ADR-0017.

MCP is JSON-RPC with one message per line, so the protocol is written here with the
standard library instead of adding a package. Every tool delegates to code that already
has its own guards (agent/tools/), so this file only translates: it has no SQL checks of
its own and no way to write. It has never been connected to a real MCP client.
"""

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent" / "tools"))
sys.path.insert(0, str(ROOT / "tools"))

from build_catalog import load_models  # noqa: E402
from get_catalog import UnknownModel, get_catalog  # noqa: E402
from query_gold import QueryFailed, QueryRejected, query_gold  # noqa: E402

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "fernway-gold", "version": "0.1.0"}
MAX_LINE_CHARS = 100_000  # a longer request is refused unread, so one line cannot fill the memory

# What a tool may raise on bad input. Anything else is a bug and is allowed to crash.
TOOL_ERRORS = (QueryRejected, QueryFailed, UnknownModel, ValueError)

TOOLS = {
    "list_gold_tables": {"description": "List the gold tables with a one-line description.", "properties": {}},
    "describe_table": {"description": "Columns and descriptions of one gold table.",
                       "properties": {"table": "string"}},
    "get_context": {"description": "A business definition, by concept id, with its status.",
                    "properties": {"concept": "string"}},
    "query_gold": {"description": "Run one SELECT over gold tables. At most 200 rows.",
                   "properties": {"sql": "string"}},
}


def list_gold_tables(root: Path = ROOT) -> dict:
    return {"tables": [{"name": f"gold.{m['name']}", "description": " ".join(str(m["description"]).split())}
                       for m in load_models(root, "gold")]}


def describe_table(table: str, root: Path = ROOT) -> dict:
    if not isinstance(table, str) or not table.strip().lower().startswith("gold."):
        # The catalog also knows silver, but this server only offers gold.
        raise UnknownModel("Give a gold table name such as gold.mrr_monthly.")
    return get_catalog(table, root)


def get_context(concept: str, root: Path = ROOT) -> dict:
    """The id is looked up in the index and never turned into a path, so it cannot point elsewhere."""
    data = yaml.safe_load((root / "context" / "index.yaml").read_text(encoding="utf-8"))
    # Concepts and the other documents (company, areas, metrics, maps, rules) share one id space.
    index = data["concepts"] + data.get("documents", [])
    entry = next((c for c in index if c["id"] == concept), None) if isinstance(concept, str) else None
    if entry is None:
        raise ValueError(f"Unknown concept. Known: {', '.join(c['id'] for c in index)}.")
    if entry["status"] == "planned":
        return {"id": entry["id"], "status": "planned", "text": None}
    text = (root / "context" / entry["path"]).read_text(encoding="utf-8")
    return {"id": entry["id"], "status": entry["status"], "text": text}


def _run_tool(name: str, arguments: dict, db_path: Path | None) -> dict:
    if name == "list_gold_tables":
        return list_gold_tables()
    if name == "describe_table":
        return describe_table(arguments["table"])
    if name == "get_context":
        return get_context(arguments["concept"])
    return query_gold(arguments["sql"], db_path)


def _tool_list() -> list[dict]:
    return [{"name": name, "description": spec["description"],
             "inputSchema": {"type": "object", "properties": {k: {"type": t} for k, t in spec["properties"].items()},
                             "required": list(spec["properties"]), "additionalProperties": False}}
            for name, spec in TOOLS.items()]


def _error(request_id, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle(message, db_path: Path | None = None) -> dict | None:
    """One JSON-RPC message in, one reply out. A notification has no reply."""
    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" or not isinstance(message.get("method"), str):
        return _error(message.get("id") if isinstance(message, dict) else None, -32600, "Invalid request")
    method, request_id, params = message["method"], message.get("id"), message.get("params") or {}
    if "id" not in message:
        return None  # notifications such as notifications/initialized
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": request_id, "result": {
            "protocolVersion": PROTOCOL_VERSION, "capabilities": {"tools": {}}, "serverInfo": SERVER_INFO}}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": request_id, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": _tool_list()}}
    if method != "tools/call":
        return _error(request_id, -32601, f"Method not found: {method[:60]}")

    name, arguments = params.get("name"), params.get("arguments") or {}
    if name not in TOOLS:
        return _error(request_id, -32602, "Unknown tool")  # a tool that is not listed cannot be called
    if not isinstance(arguments, dict) or set(arguments) != set(TOOLS[name]["properties"]):
        expected = ", ".join(TOOLS[name]["properties"]) or "none"
        return _error(request_id, -32602, f"Arguments for {name} must be exactly: {expected}")
    try:
        result, failed = _run_tool(name, arguments, db_path), False
    except TOOL_ERRORS as error:
        result, failed = {"error": (str(error).splitlines() or [type(error).__name__])[0]}, True
    return {"jsonrpc": "2.0", "id": request_id, "result": {
        "content": [{"type": "text", "text": json.dumps(result, default=str)}], "isError": failed}}


def serve(lines, write, db_path: Path | None = None) -> None:
    for line in lines:
        if not line.strip():
            continue
        if len(line) > MAX_LINE_CHARS:
            reply = _error(None, -32600, "Request too long")
        else:
            try:
                reply = handle(json.loads(line), db_path)
            except ValueError:
                reply = _error(None, -32700, "Parse error")
        if reply is not None:
            write(json.dumps(reply) + "\n")


def main() -> int:
    serve(sys.stdin, lambda text: (sys.stdout.write(text), sys.stdout.flush()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
