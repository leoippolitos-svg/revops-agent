---
id: metrics-sdr
title: SDR metrics
kind: metrics
owner_team: Sales
status: canonical
last_reviewed: 2026-10-31
related: [area-sdr, mql]
---

# SDR metrics

## Purpose

The official formula of every metric the SDR area reports, where each term comes from, its default window and how to read it. The agent reads it before computing any SDR number, so the same question never gets two numbers. A metric marked "not in gold yet" has no answer from the agent until a gold model exists: that is a data task, never a reason to read silver. Context and process are in [[doc:area-sdr]]. Sales owns it with RevOps and updates it when a formula, a window or a target changes, in the same pull request as the code that changes it.

## Metrics

| Metric | Formula | Source | Status |
|---|---|---|---|
| Sales-accepted leads | contacts with the Sales flag, by month of submission | [[gold.mql_monthly.sales_mqls]] | in gold |
| MQL to deal | MQLs whose company opened a deal within 30 days, over MQLs; the last 30 days are immature | [[gold.mql_to_deal_monthly.mqls_with_deal_30d]] over [[gold.mql_to_deal_monthly.marketing_mqls]] | in gold |
| Speed to lead | time from submission to first touch | not recorded | not in the data |

## Window and grain

- Default window: the last full calendar month. The month in progress is partial and is never compared with a full month, see [[concept:cross-cutting-rules]].
- Grain: calendar month, first day of the month, as in the gold tables. A question about a quarter sums or averages full months and says which.

## Internal benchmark

None yet: no SDR metric beyond the Sales flag is in gold.

## Interpretation notes

- Without a first-touch time, "speed to lead" cannot be measured; the agent says so instead of using deal creation as a proxy.
