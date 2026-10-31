---
date: 2026-10-31
type: process
pr: "#67"
author: Leonardo Ippolito
---

# Replication guide, environment setup with the MCP credential pattern, and a worked example automation

## What was done
- `docs/replication-guide.md`: how to stand this agent up in a real company: the idea, the reference stack, nine phases in order from process to writes, what is essential and what can wait, the pitfalls that cost time, and the checklist before the first business user.
- `docs/standards/environment-setup.md`: the pieces that make agents work here from the first session, the setup steps, the rules for MCP credentials, and what belongs in a request versus the repository.
- `mcp.template.json` with `${env:NAME}` placeholders only, and `tools/mcp_env_wrapper.py`, which starts an MCP server with the names it needs from a local `.env`, as a list of arguments with no shell, printing no value. 5 tests, all with temporary files.
- `automations/_examples/multi-year-contract-split/`: the original's multi-year contract split documented to the full standard (problem, why, gains, diagram, rules, guards) as a worked example, not built.

## Why
The dossier had a replication guide, a starter kit with priorities per file, an environment setup and a credential wrapper for MCP servers; none of it was here. The owner asked for the contract split as an example only, because it is too specific to build on Fernway.

## Result or decision
- The wrapper reads `.env` at run time for an MCP client; no agent reads `.env`, and the tests never touch the real one.
- The example is skipped by the automation checks and says it is not built.

## Rules and context changed
None. Standards: environment setup; `CLAUDE.md` links it.

## Follow-ups
RevOps methodologies as reference and skills, gold models for the missing metrics, the proposal and EBR apps with AI, the security review pipeline.
