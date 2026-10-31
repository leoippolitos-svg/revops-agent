# Funnel review

## What it is
A weekly look at the whole funnel: compares the latest mature cohorts with the ones before, names the stage that moved most and hands the cause to the `funnel-diagnosis` skill. It never states a cause itself.

## Where it runs
Locally. Not scheduled, because the fictional data has a fixed date and the seven-day freshness check would stop a weekly run. Spec: `automations/funnel-review/SPEC.md`.

## How to run it
`python automations/funnel-review/review.py` (dry run), `--write` to write the report.

## Rules
`funnel-stages` for maturity and the minimum sample; the thresholds in the code are assumptions, see `memory/decisions/`.

## Owner
RevOps lead.

## Status
Built (2026-10-31), not scheduled.
