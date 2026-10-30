---
date: 2026-10-30
type: automation
pr: "#25"
author: Leonardo Ippolito
---

# Weekly data-quality audit as an automation

## What was done
Followed the `new-automation` flow. Wrote `automations/audits/SPEC.md` first, then `audit.py`, which reads `gold.data_quality_snapshot` through a read-only connection and writes `observability/logs/audit-<date>.md` only with `--write`. Added 6 tests, a scheduled workflow (`.github/workflows/weekly-audit.yml`, Mondays 07:00 UTC plus manual dispatch) that rebuilds the fictional lakehouse, runs the audit and keeps the report as an artifact, and ADR-0009. The `lakehouse` connector now lists `automations` as a consumer.

## Why
The weekly audit was listed as a skill idea. A skill does not run by itself, and the audit is deterministic counting. It belongs in an automation, with the agent's `data-discrepancy` skill left for explaining a result when asked.

## Result or decision
- The audit raises attention for a flag only when its count is higher than in the previous report. A steady or falling count is reported, not raised, and the first report raises nothing.
- Dry-run is the default. One file per data date, so a second run overwrites instead of duplicating.
- A missing database or table exits with code 1 and a message; it is never reported as "no problems".
- The effect is a local file and a workflow artifact. Nothing is sent to Slack or any other system, which matches the registry entry for Slack still being documented.
- The security checklist in the spec is ticked, with how each item was verified. Retry and rate-limit items are marked not applicable because the audit makes no network call.

## Rules and context changed
none

## Follow-ups
Verify the scheduled workflow with a manual dispatch after merge. Build a monthly version of the flag counts if the trend of the flags is needed. The other automations in `automations/README.md` are still planned.
