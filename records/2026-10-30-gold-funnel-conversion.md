---
date: 2026-10-30
type: data
pr: "#26"
author: Leonardo Ippolito
---

# Gold funnel conversion by cohort

## What was done
Added `gold.funnel_conversion_monthly`: one row per month in which deals entered qualification, with how many of those deals ever reached discovery, proposal, negotiation, closed won and closed lost, and how many are still open. Added its descriptions and tests in `gold/schema.yml`, a data test in `tests/test_dbt_layers.py`, the conversion and win-rate rules in `funnel-stages.md`, the regenerated catalog, and a note in the `funnel-diagnosis` skill about which tables it can use.

## Why
`funnel-diagnosis` asked for conversion to the next stage, but gold only had entries per stage per month. Dividing one month's entries by the previous month's mixes different deals. A cohort follows the same deals, so the ratio means something.

## Result or decision
- Cohort by qualification month; "reached" means the stage row exists, so out-of-order CRM dates cannot change the counts.
- Win rate leaves open deals out. The context document says so, and warns that the newest cohorts are immature (cohort 2025-12 has 18 of 20 deals still open).
- Median time in stage and loss reason are still not in gold. The skill now says to report them as unavailable.
- Checked: dbt build passes with 9 tests on the new model, and the 17 dbt layer tests pass.

## Rules and context changed
`context/concepts/funnel-stages.md`: cohort conversion, win rate, and three gotchas (no month-over-month ratio, immature cohorts, lost deals that skip stages).

## Follow-ups
Time in stage and loss reason models. Scored evals for `funnel-diagnosis` once the agent exists.
