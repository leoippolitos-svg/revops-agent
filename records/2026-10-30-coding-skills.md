---
date: 2026-10-30
type: process
pr: "#17"
author: Leonardo Ippolito
---

# Five missing skills for the coding agent

## What was done
Reviewed the repository's workflows against the skills that existed (`context-docs`, `create-skill`, `medallion-modeling`, `new-micro-app`, `open-pr`, `pr-review`) and found five repeated workflows with no skill. Wrote each in full, with steps, an example, troubleshooting and a "Never" list: `new-analysis`, `new-automation`, `add-connector`, `fix-failing-data-check` and `run-evals`. Each has a trigger test in `evals/skills/`.

## Why
The folders `analyses/`, `automations/` and `connectors/`, the daily check and the eval sets all had rules in standards but no workflow an agent could follow. Without one, each task would be done differently.

## Result or decision
- Each skill points to the standard that holds the rule and adds only the workflow, so rules live in one place.
- `run-evals` says an unmeasured set is "not measured", never a number, matching how Phase 3 was closed.
- Skill trigger tests are written but only checked for shape: no model has scored whether the descriptions trigger correctly.

## Rules and context changed
none

## Follow-ups
Business skills for the RevOps agent (data discrepancies, trends, weekly audit), then the connector registry and the MCP server rules.
