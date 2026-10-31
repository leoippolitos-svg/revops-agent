---
id: metrics-revops
title: RevOps metrics
kind: metrics
owner_team: RevOps
status: canonical
last_reviewed: 2026-10-31
related: [area-revops, cross-cutting-rules]
---

# RevOps metrics

## Purpose

The official formula of every metric the RevOps area reports, where each term comes from, its default window and how to read it. The agent reads it before computing any RevOps number, so the same question never gets two numbers. A metric marked "not in gold yet" has no answer from the agent until a gold model exists: that is a data task, never a reason to read silver. Context and process are in [[doc:area-revops]]. RevOps owns it with RevOps and updates it when a formula, a window or a target changes, in the same pull request as the code that changes it.

## Metrics

| Metric | Formula | Source | Status |
|---|---|---|---|
| Deals without a company | count, as of the newest export | [[gold.data_quality_snapshot.deals_without_company]] | in gold |
| Possible duplicate companies | count of flagged company records | [[gold.data_quality_snapshot.possible_duplicate_companies]] | in gold |
| Subscriptions without a deal | count | [[gold.data_quality_snapshot.subscriptions_without_deal]] | in gold |
| Closed won without a subscription | count; includes deals won in the last two weeks | [[gold.data_quality_snapshot.closed_won_without_subscription]] | in gold |
| Jobs healthy | jobs whose last run succeeded on schedule, over jobs in the catalog | the run catalog | outside gold |
| Agent cost per answer | estimated cost of each answer, model and classifier included | the observability log | outside gold |

## Window and grain

- Data-quality counts are a snapshot as of the newest export, not a month. The weekly audit compares them with the previous report.
- Job health and agent cost are per run and per answer.

## Internal benchmark

The previous weekly audit report is the benchmark for each flag.

## Interpretation notes

- A count can move without any business change when a source is corrected, see [[concept:cross-cutting-rules]].
