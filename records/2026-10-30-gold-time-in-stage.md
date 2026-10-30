---
date: 2026-10-30
type: data
pr: "#27"
author: Leonardo Ippolito
---

# Gold time in stage

## What was done
Added `gold.funnel_time_in_stage_monthly`: for each open stage and each month in which deals left it, the number of deals, the median and average days spent in the stage, and the exits with out-of-order dates. Added descriptions and tests in `gold/schema.yml`, a data test, the rules and gotchas in `funnel-stages.md`, the regenerated catalog, and the matching lines in the `funnel-diagnosis` skill.

## Why
`funnel-diagnosis` looks for the stage whose time grows, but gold had no time figure. The previous PR added conversion; this one adds the second input.

## Result or decision
- A deal leaves a stage when it enters the next one in funnel order, closed won or lost included. Deals still in a stage are not counted.
- The 3 exits with out-of-order dates (all in discovery) are counted apart and kept out of the day figures, instead of producing negative days.
- The context document warns that the median hides stuck deals, and that the CRM has no loss reason, so that question stays unanswerable. This was checked in the data, not assumed.
- Checked: dbt build passes with 8 tests on the model; exits add up to 176, 124, 86 and 47 for the four stages.

## Rules and context changed
`context/concepts/funnel-stages.md`: time-in-stage rule and three gotchas.

## Follow-ups
A loss reason would need a new field in the source, so it is not planned. Scored evals for `funnel-diagnosis` once the agent exists.
