---
date: 2026-10-30
type: infra
pr: "#20"
author: Leonardo Ippolito
---

# Close Phase 4: skills, connector registry and MCP server rules

## What was done
Marked Phase 4 as complete in the README roadmap, with its scope stated plainly: skills and rules, not a running MCP server.

## Why
The owner asked for organization and rules inside the repo, and for the skills missing from the process to be written in full. The roadmap should say what exists.

## Result or decision
Delivered in PRs #17 to #19:
- Five coding-agent skills: `new-analysis`, `new-automation`, `add-connector`, `fix-failing-data-check`, `run-evals`.
- Two business skills for the RevOps agent: `trend-analysis` and `data-discrepancy`, linked in `routing.md`.
- `tools/check_connectors.py`, which enforces the connector rules, and ADR-0008 with the MCP server contract.
- Every new skill has a trigger test in `evals/skills/`, and `tools/check_evals.py` now fails if a routed skill has no folder.

Not delivered, and not claimed: MCP server code, any model-scored skill triggering, and the weekly audit skill. The audit is blocked on a gold model that exposes the data-quality flags, because the agent cannot read silver.

## Rules and context changed
none

## Follow-ups
A gold data-quality model with its context document, then the audit skill and automation. The conversion gold model deferred from Phase 3. Build the agent, retrieval and MCP server against the written contracts.
