---
date: 2026-10-31
type: infra
pr: "#55"
author: Leonardo Ippolito
---

# Run catalog, job health and Slack alerts

## What was done
- `catalog/` holds one card per thing that runs (nine today: the audit, the collector, Slack alerts, lead routing, provisioning, funnel review, the snapshot page, the agent, the MCP server), with owner, trigger, where it lives, what it writes, whether it uses AI and where its status comes from. `docs/run-catalog.md` is generated from them.
- `tools/catalog.py`: `check` (every card valid, every scheduled workflow has a card, an active item has a status source), `page`, and `collect` (last run of each item from GitHub Actions or the log folder, status ok, failing, late, unknown or stopped, written to the job health file, with an alert per failing or late item).
- `.github/workflows/catalog-collect.yml` runs the collector at 08:00, 13:00 and 18:00 UTC with read-only permissions.
- `observability/notify.py`: Slack alerts built by code, one thread per item, through the write controls with the kill switch `SLACK_ALERTS_ENABLED`; simulated as `observability/logs/slack-<date>.md`; a real post needs the webhook secret and only goes to `hooks.slack.com`. ADR-0020. The weekly audit now alerts when a flag rises.
- `get_map("jobs")` lets the agent answer "did the jobs run yesterday?". The Slack connector moved from documented to simulated, and its write-back authorization is back with a cap of 30.

## Why
The original had a catalog of everything the team put to run, collected three times a day, a status page, and alerts in Slack with one thread per problem; it was the base of its on-call agent. Here nothing listed what runs or whether it ran.

## Result or decision
- Registering a card is a process rule (session closing), and the check enforces only what can be checked: a scheduled workflow with no card fails CI.
- No alert has reached Slack. The collector has not run on a schedule yet; it starts after this merge.

## Rules and context changed
`writeback-rules` (Slack row and authorization), connector registry (Slack simulated), AGENT.md (catalog path).

## Follow-ups
The on-call agent and the watchdog, built on the collector.
