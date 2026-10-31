# ADR-0017: The MCP server speaks the protocol by hand and delegates every guard

- Status: accepted
- Date: 2026-10-31

## Context
ADR-0008 decided what the MCP server exposes. Building it needs an MCP library, which is a new dependency, or the protocol written directly. MCP over stdio is JSON-RPC 2.0 with one message per line, and the server needs only four methods: `initialize`, `ping`, `tools/list` and `tools/call`.

## Decision
`mcp_server/server.py` implements those methods with the standard library, so `requirements.txt` does not change. It has no SQL checks of its own: `query_gold` calls the guard from ADR-0013, `describe_table` calls `get_catalog` and refuses anything outside gold, and `get_context` looks the concept id up in `context/index.yaml` and never builds a path from it. A tool that is not listed cannot be called, and the arguments must be exactly those the tool declares.

## Alternatives considered
- **The official MCP package**: handles more of the protocol, but adds a dependency and a version to keep current, for four tools.
- **Writing a second SQL guard for the server**: would let the two drift apart, which is what ADR-0013 was written to avoid.

## Consequences
The server is tested by calling its handler and by running it as a process, but it has never been connected to a real MCP client, so a client that expects a method this server omits (resources, prompts, progress) will not work. If more of the protocol is needed, switching to the package is a new ADR.
