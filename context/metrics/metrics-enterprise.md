---
id: metrics-enterprise
title: Enterprise metrics
kind: metrics
owner_team: Sales
status: canonical
last_reviewed: 2026-10-31
related: [area-enterprise, funnel-stages]
---

# Enterprise metrics

## Purpose

The official formula of every metric the Enterprise area reports, where each term comes from, its default window and how to read it. The agent reads it before computing any Enterprise number, so the same question never gets two numbers. A metric marked "not in gold yet" has no answer from the agent until a gold model exists: that is a data task, never a reason to read silver. Context and process are in [[doc:area-enterprise]]. Sales owns it with RevOps and updates it when a formula, a window or a target changes, in the same pull request as the code that changes it.

## Metrics

| Metric | Formula | Source | Status |
|---|---|---|---|
| Open pipeline value | open deal value of enterprise owners | [[gold.owner_workload.open_amount_usd]] | in gold |
| Open deals per owner | open deals of enterprise owners, against the limit of 8 | [[gold.owner_workload.open_deals]] | in gold |
| Enterprise win rate | win rate of deals of enterprise-segment companies | needs the segment in the cohort table | not in gold yet |

## Window and grain

- Default window: the last full calendar month. The month in progress is partial and is never compared with a full month, see [[concept:cross-cutting-rules]].
- Grain: calendar month, first day of the month, as in the gold tables. A question about a quarter sums or averages full months and says which.

## Internal benchmark

None yet by segment; the funnel benchmarks in [[doc:metrics-sales]] mix all segments.

## Interpretation notes

- Coverage is open pipeline over the remaining target; say the target used, from [[doc:okrs]].
