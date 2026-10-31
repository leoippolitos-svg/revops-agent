---
date: 2026-10-31
type: automation
pr: "#42"
author: Leonardo Ippolito
---

# The funnel-review automation, evidence half

## What was done
Built `automations/funnel-review/review.py`: it reads four gold tables read-only, compares the latest three mature cohorts with the three before them, finds the stage that moved most and writes a report to `observability/logs/funnel-review-<data date>.md`. Added 23 tests, marked the spec built and ticked its checklist.

## Why
The spec asked for a weekly look at the whole funnel, and the evidence part is deterministic, so it should not depend on a model's mood.

## Result or decision
- Maturity (90 days after the month ends) and the minimum sample (20 qualified deals) are read from `funnel-stages.md` each run, not written in code. The script never recomputes conversion, win rate or time in stage from raw rows: it uses the gold columns.
- **It never states a cause.** The spec wants the likely cause with a confidence, which needs judgment. The report ends with a hand-off to the `funnel-diagnosis` skill (rule out data first, check earlier records, loss reason unavailable) instead of a guess. The agent half has not been run, because no real model has been called.
- It names a constraint only for a conversion drop of at least 5 points, weighted by the deals that reached the step before; failing that, for time in stage growing at least 50% and 3 days. Otherwise it says "No stage changed beyond its normal range." A small sample or fewer than six mature cohorts names nothing. **These thresholds, and the owner team per stage (qualification to sdr, the rest to sales), are my assumptions, not documented rules.** They are marked in the code and should be confirmed.
- Time in stage is compared as a mean of monthly medians weighted by exits, in the same calendar months as the cohorts. That is an approximation of a true median and the report does not claim more.
- It stops with exit code 1 and writes nothing when a table is missing, the snapshot is not a single row, or the data is more than seven days old. If the audit of the same week raised a flag, the report says data may explain the change before the finding.
- **Not scheduled.** The synthetic data has a fixed date, so the seven-day freshness check would stop a weekly run, which is the correct behaviour and the reason it is not added to `weekly-audit.yml`. It was also never run against the real gold tables: the local lakehouse here predates `data_quality_snapshot`. Tests use hand-built tables.

## Rules and context changed
None.

## Follow-ups
Confirm the thresholds and the owner teams. Run it, and the agent half, once a model and fresh data exist.
