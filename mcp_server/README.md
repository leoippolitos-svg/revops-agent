# MCP server

A small MCP server that exposes the gold layer, the catalog and the context documents to any MCP client, read-only. Decision: [ADR-0008](../docs/adr/0008-mcp-server-exposes-gold-read-only.md). The guarantee does not depend on a prompt.

## Tools it offers

| Tool | Input | Returns |
|---|---|---|
| `list_gold_tables` | none | Gold table names with their one-line descriptions |
| `describe_table` | table name | Columns and descriptions, from the dbt `schema.yml` files |
| `get_context` | concept id | The context document as text, with its status |
| `query_gold` | one SELECT statement | Rows, at most 200 |

These match the agent tools in [agent/tools/README.md](../agent/tools/README.md) and follow the same hard rules: the lakehouse is opened read-only, only the `gold` schema can be read, one statement per call, anything that is not a SELECT is rejected before it reaches the database.

## Security tests the code must pass

- An `INSERT`, `UPDATE`, `DELETE`, `DROP`, `CREATE` or `ATTACH` is rejected.
- A query that names `silver` or `bronze` is rejected.
- Two statements joined by a semicolon are rejected.
- A result is cut at 200 rows and says it was cut.
- A table name that is not in the catalog is rejected, not looked up.

## Registry

Registered as the consumer `mcp_server` of the `lakehouse` connector in [connectors/registry.yaml](../connectors/registry.yaml). `tools/check_connectors.py` fails if it ever consumes a read-write connector.

## Status

Built: [server.py](server.py), run with `python mcp_server/server.py` (JSON-RPC on stdin and stdout, standard library only, ADR-0017). It imports the `query_gold` guard from [agent/tools/query_gold.py](../agent/tools/query_gold.py) instead of writing a second one (ADR-0013). The security tests above are in `tests/test_mcp_server.py`. No real MCP client has connected to it yet.
