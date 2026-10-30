---
date: 2026-10-30
type: infra
pr: "#19"
author: Leonardo Ippolito
---

# Connector registry check and MCP server contract

## What was done
Added `tools/check_connectors.py`, which validates `connectors/registry.yaml` against `docs/standards/connectors.md` and `docs/standards/security.md`, with 7 tests. Wired it into the pre-commit hook, CI `standards`, `make check` and `tools/setup.py`. Wrote ADR-0008 and the contract of the MCP server in `mcp_server/README.md`: four read-only tools, the security tests its code must pass, and its registry entry.

## Why
The registry rules were prose. A read-write connector marked live, a secret pasted into `auth`, or the agent consuming a write connector would have gone unnoticed. The MCP server is the third way gold is consumed and needed its limits written before any code.

## Result or decision
- The check enforces: required fields and unique ids, valid status and access, non-empty scopes, no secret-shaped `auth`, no live read-write connector, a note pointing to the ADR for every read-write connector, and no read-write connector consumed by `agent` or `mcp_server`.
- It found one real gap on its first run: the Slack entry was read-write with no ADR pointer. Its note now says an ADR is needed before going live.
- The MCP server is specified, not built. Its security tests are listed so the code is judged against them.

## Rules and context changed
none

## Follow-ups
MCP server code and its security tests. A gold model for data-quality flags, then the weekly audit skill and automation. Close Phase 4.
