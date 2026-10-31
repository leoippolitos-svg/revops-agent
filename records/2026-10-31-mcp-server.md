---
date: 2026-10-31
type: app
pr: "#38"
author: Leonardo Ippolito
---

# The MCP server

## What was done
Built `mcp_server/server.py`, a read-only MCP server with the four tools in its contract: `list_gold_tables`, `describe_table`, `get_context` and `query_gold`. Added 35 tests, ADR-0017 and the README updates.

## Why
ADR-0008 and the contract existed, but there was no code, so "the same context serves any client" was only a sentence.

## Result or decision
- The protocol is written by hand on the standard library (ADR-0017): no dependency was added.
- The server has no guards of its own. `query_gold` reuses the guard from ADR-0013, `describe_table` accepts gold names only, and `get_context` finds the concept in the index and never builds a path from the id.
- Every security test in the contract is a test: writes, silver and bronze, two statements, the 200-row cut and a table that is not in the catalog. Others check that an unlisted tool and wrong arguments are refused, and that garbage and over-long lines do not stop the server.
- Not proven: no real MCP client has connected. Resources, prompts and progress messages are not offered.

## Rules and context changed
None.

## Follow-ups
Try it with a real MCP client. The micro-app and the three automations.
