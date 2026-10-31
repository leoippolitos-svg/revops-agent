---
id: metrics-sales
title: Sales metrics
kind: metrics
owner_team: Sales
status: canonical
last_reviewed: 2026-10-31
related: [area-sales, funnel-stages, mrr]
---

# Sales metrics

## Purpose

The official formula of every metric the Sales area reports, where each term comes from, its default window and how to read it. The agent reads it before computing any Sales number, so the same question never gets two numbers. A metric marked "not in gold yet" has no answer from the agent until a gold model exists: that is a data task, never a reason to read silver. Context and process are in [[doc:area-sales]]. Sales owns it with RevOps and updates it when a formula, a window or a target changes, in the same pull request as the code that changes it.

## Metrics

| Metric | Formula | Source | Status |
|---|---|---|---|
| Deals entered per stage | deals that entered the stage in the month | [[gold.funnel_stage_monthly.deals_entered]] | in gold |
| Stage conversion | deals of a cohort that reached a stage over those that reached the previous one | [[gold.funnel_conversion_monthly]] | in gold |
| Win rate | closed won over closed won plus closed lost, mature cohorts only | [[gold.funnel_conversion_monthly.closed_won]], [[gold.funnel_conversion_monthly.closed_lost]] | in gold |
| Time in stage | median days in an open stage, by month of exit | [[gold.funnel_time_in_stage_monthly.median_days_in_stage]] | in gold |
| Bookings | yearly value of deals entering closed won in the month | [[gold.funnel_stage_monthly.amount_usd_entered]] | in gold |
| Open deals per owner | open deals now, per owner | [[gold.owner_workload.open_deals]] | in gold |

## Window and grain

- Default window: the last full calendar month. The month in progress is partial and is never compared with a full month, see [[concept:cross-cutting-rules]].
- Grain: calendar month, first day of the month, as in the gold tables. A question about a quarter sums or averages full months and says which.
- Cohort metrics use the cohort month (entry into qualification) and only cohorts 90 days past their month end, see [[concept:funnel-stages]].

## Internal benchmark

Mature cohorts from 2025-05 to 2025-08 are the ones with 20 qualified deals or more; their win rates range from 18% to 69%. Compare a new mature cohort with that range, not with one cohort.

## Interpretation notes

- Bookings are a sales number; MRR is the revenue number, see [[concept:mrr]].
- With a few deals a month, a rate moves a lot; give the count next to every rate.
