# ADR-0008: The MCP server exposes gold, read-only

- Status: accepted
- Date: 2026-10-30

## Context
Other tools and agents should be able to ask the lakehouse questions. An MCP server is the standard way to offer that. Whatever it offers, it offers to clients this repo does not control.

## Decision
The MCP server exposes the `gold` schema and the catalog, nothing else, and only for reading. Its contract is in `mcp_server/README.md`. The guarantees are mechanical: the database file is opened read-only, only SELECT statements on `gold` are accepted, and the server's registry entry is `read` so `tools/check_connectors.py` fails if it is ever listed as a consumer of a read-write connector. Context documents are served as text so a client gets the meaning with the numbers.

## Alternatives considered
- **Expose silver as well**: more freedom for analysts, but silver is not stable and carries unreviewed flags.
- **No MCP, agent only**: smaller, but gives up the portfolio point that the same context serves any client.

## Consequences
Clients see one stable, documented layer. Anything that needs silver or a write goes through a PR instead. The server is specified here; its code is a later change and must pass the security tests listed in the contract.
