---
date: 2026-10-31
type: process
pr: "#43"
author: Leonardo Ippolito
---

# Final status of the repository

## What was done
Rewrote the status paragraph of the README so it says what exists and what has never been measured, in one place.

## Why
The paragraph had grown one clause at a time over eight pull requests and still opened with "Phases 3 to 6 are written as rules, specs and eval cases", which was no longer true.

## Result or decision
- Built and tested: pipeline, retrieval, four agent tools, router, agent loop, model adapter, MCP server, revenue-snapshot page, four automations.
- Never run against anything real: a model, an API key, an MCP client, a browser, a CRM or a product.
- Never measured: answer quality, the context A/B comparison and the skill triggers.
- Open questions for the owner, each in its own record: continuity versus capacity in lead routing, and the funnel-review thresholds and owner teams.

## Rules and context changed
None.

## Follow-ups
Run the agent once with a real key, then the first scored evals. Ask someone else to write router and retrieval questions.
