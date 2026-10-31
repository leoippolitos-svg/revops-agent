---
date: 2026-10-31
type: process
pr: "#61"
author: Leonardo Ippolito
---

# Parity check with the original agent, and the README

## What was done
- Checked every item of the parity list taken from the original agent's documentation against the repository, and fixed two claims that were not true: the query history said the agent loop writes it (it does not, by design), and the benchmarks folder implied a job updates it (none does).
- ADR-0022 records why the web chat app is not built: it needs a host and a key, and its hard parts (sign-in, allowlist, row-level security) cannot be shown without them.
- `README.md` now describes the whole system: context by area, the prompt and profile mechanisms, the write controls, audits, the run catalog, alerts, on-call and verification, with current numbers (521 tests, 11 gold models, 34 context documents, 22 decisions) and a status table that says what has never run.
- `BACKLOG.md` and the agent project digest were updated.

## Why
The owner asked for the original agent to be the rule, with nothing forgotten, and for the README to explain the system to anyone arriving from a portfolio link.

## Result or decision
Recreated: the knowledge structure by area, the reading order, the agent's prompt and routing mechanisms, the closed map tool, cost per answer, write-back rules with recurring authorizations and controls, the run catalog with health and Slack, the on-call agent and watchdog, verification, audits, the categorised corpus with incremental reingest, session closing, memory, projects, the app standard, the security rules, the team process and the lessons.
Not recreated, on purpose: the web chat (ADR-0022), the CRM mirror and the flows of the original's specific tools, its business-specific directives and reports, and archives of cancelled tools.

## Rules and context changed
None.

## Follow-ups
In `BACKLOG.md`.
