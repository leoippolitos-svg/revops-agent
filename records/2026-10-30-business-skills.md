---
date: 2026-10-30
type: process
pr: "#18"
author: Leonardo Ippolito
---

# Business skills for the RevOps agent: trend analysis and data discrepancy

## What was done
Compared the eight routing intents with the business skills available. Two intents that need a repeatable method had none: `trend_analysis` and `data_quality`. Wrote `trend-analysis` and `data-discrepancy` in full, each with steps, an example, troubleshooting and a trigger test, and linked them in `agent/directives/routing.md`. `tools/check_evals.py` now fails when a skill named in the routing table has no folder in `agent/skills/` (1 new test).

## Why
Funnel diagnosis and reports had skills, but "how has this moved?" and "why do these numbers differ?" are the questions most likely to produce a confident wrong answer: a partial month compared with a full one, or two definitions mistaken for a bug.

## Result or decision
- `trend-analysis` makes the comparison fair first: no partial month, MRR identity checked, missing funnel rows read as zero, and no "season" claim with fewer than six full months.
- `data-discrepancy` checks causes in a fixed order (definitions, dates, source of truth, flags, grain) and states which number to use for which decision. It reads gold only; when the cause needs silver rows it says so and hands over instead of guessing.
- The examples use illustrative figures and say so.
- A weekly audit skill was considered and left out: the duplicate, missing-company and missing-deal flags live in silver, which the agent cannot read. It needs a gold audit model first.

## Rules and context changed
none

## Follow-ups
A gold model exposing the data-quality flags, then a weekly audit skill and automation. Connector registry and MCP server rules.
