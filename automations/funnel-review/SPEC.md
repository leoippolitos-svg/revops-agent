# Weekly funnel review, Spec

Status: specified, not built

## Problem
Nobody looks at the whole funnel every week. A stage can slow down or leak for weeks before someone notices, and a month-by-month number hides it, because the newest deals have not had time to close. The review finds the one stage that limits the funnel and says what to check, before the weekly revenue meeting.

## Trigger
Every Monday morning (UTC), after the weekly data-quality audit (`automations/audits/`), and on demand.

## Inputs
Gold tables only, read-only:
- `gold.funnel_stage_monthly`
- `gold.funnel_conversion_monthly`
- `gold.funnel_time_in_stage_monthly`
- `gold.data_quality_snapshot`

## Rules
- The method is the `funnel-diagnosis` skill: find the constraint stage, rule out data causes first, then name a likely cause with a confidence level.
- Conversion, win rate and time in stage are read as defined in the context document `funnel-stages`. The review never recomputes them.
- Only mature cohorts are compared, and only when both periods have at least 20 qualified deals. Both thresholds are in `funnel-stages`, not in code.
- The two periods are the latest three mature cohorts and the three before them.
- If the weekly audit report of the same week raised a flag, the review states that data may explain the change before it blames the business.
- If no stage changed beyond its normal range, the review says so in one line. It does not invent a bottleneck.
- Time in stage is read together with the open deals of the cohort: a good median can hide stuck deals.
- The review never gives a loss reason. The CRM has none.

## Effects
Writes one report, `observability/logs/funnel-review-<as_of date>.md`, only when run with `--write`. This is the simulated alert channel. Nothing is sent to any external system and no record is changed. The report holds the evidence tables, the constraint stage, the likely cause with its confidence, what would confirm it, and the owner team.

## Failure behavior
If a gold table is missing, or the data is older than the weekly schedule allows, the review stops with an error and writes nothing. An error is never reported as "nothing changed". If the sample is too small it says so and names no constraint.

## Must never
- Write to any data source
- Read from silver or bronze
- Send a message to an external system
- Compare a cohort that is not yet mature
- State a cause without a confidence level
- Name a constraint from fewer than 20 deals

## Dry run
Dry-run is the default: the report is printed and no file is written. `--write` turns the effect on. Running twice for the same data date overwrites the same file, so effects are not duplicated.

## How it would run
The evidence part is deterministic and would be a script like the audit. The reading of the evidence needs judgment, so it is the agent using the skill. ADR-0009 names a scheduled cloud agent as an option for exactly this kind of work, and it stays an option until the agent exists. The agent keeps its four read-only tools; the only file it may write is the report above.

## Security checklist
Standard: `docs/standards/security.md`, automation checklist. Left unticked until the automation is built.

- [ ] Idempotent: running twice does not duplicate effects
- [ ] Retries with backoff, and a cap
- [ ] Respects rate limits of every API it calls
- [ ] Failures are logged and alerted, never swallowed
- [ ] Credentials scoped to the minimum and registered
- [ ] Dry-run mode for anything that would write to an external system
