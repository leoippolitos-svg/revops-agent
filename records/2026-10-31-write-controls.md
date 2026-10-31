---
date: 2026-10-31
type: automation
pr: "#54"
author: Leonardo Ippolito
---

# Write controls for every automation that writes

## What was done
- `automations/_lib/controls.py`: dry run by default; a kill switch (`<NAME>_ENABLED=true`) without which `--write` becomes a shadow run; a cap per run read from the write-back rules; a circuit breaker after three consecutive failures; a read-back check after each write; and "needs review" for anything not written.
- Lead routing and closed-won provisioning now write one item at a time through the controls. Provisioning reports a deal with no company as "needs review" instead of "skipped", and never back-fills a deal won more than 60 days ago (a new rule in `closed-won-provisioning`, read at run time).
- `context/rules/writeback-rules.md` gained a cap-per-run column and the kill-switch rule. `tools/check_automations.py` now fails when code writes through `WriteControls` without a `RECURRING-AUTHORIZATION`, or when an authorization names a job no code runs.
- Both specs and the automation checklist in the security standard list the new controls. 12 tests added.

## Why
The original's writing jobs all had the same controls: idempotency, a cap, a kill switch, a shadow mode, a check after writing, a breaker and a review queue, and any failure was "needs review", never "skipped". Here only dry run and idempotency existed, written separately in each automation.

## Result or decision
- A local `--write` run now needs the kill switch, which is the point: turning an automation on is a deliberate act, and off is a variable, not a deploy.
- The Slack authorization waits for the Slack notifier, because the new check refuses an authorization no code uses.

## Rules and context changed
`writeback-rules` (cap column, kill switch), `closed-won-provisioning` (60-day cutoff).

## Follow-ups
The run catalog with job health, the Slack notifier, then the on-call agent.
