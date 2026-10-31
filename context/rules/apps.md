---
id: apps
title: Internal apps and what they compute
kind: inventory
owner_team: RevOps
status: canonical
last_reviewed: 2026-10-31
related: [report-revenue-snapshot]
---

# Internal apps and what they compute

## Purpose

Every internal app RevOps runs, what it computes and where its data lives, so the agent explains an app's number instead of recomputing it differently. The agent reads it when a question names an app or a number seen in one. It does not hold the app's rules in full; each app has a spec in `apps/<name>/SPEC.md`. RevOps owns it and adds a row in the same pull request that creates or retires an app.

## Items

| App | What it shows | Data it reads | Writes | Spec |
|---|---|---|---|---|
| agent-chat | a local chat with the agent and, under each answer, how it got there (route, documents, prompt blocks, tools) | gold through the agent's read-only tools, and the context documents | nothing | [apps/agent-chat/SPEC.md](../../apps/agent-chat/SPEC.md) |
| revenue-snapshot | MRR, customers, funnel entries and MQLs by month, each with its definition | four gold tables, read-only | nothing | [apps/revenue-snapshot/SPEC.md](../../apps/revenue-snapshot/SPEC.md) |

How each number is computed: [[doc:report-revenue-snapshot]].

## Rules for the agent

- Explain an app's number with the app's definition, then answer with gold if the person needs another cut.
- If an app and a gold query disagree, report both, with their data dates, and do not pick one silently.
- An app never writes data; if someone says an app changed a record, the record was changed elsewhere.
