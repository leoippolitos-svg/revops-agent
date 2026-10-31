---
id: metrics-marketing
title: Marketing metrics
kind: metrics
owner_team: Marketing
status: canonical
last_reviewed: 2026-10-31
related: [area-marketing, mql]
---

# Marketing metrics

## Purpose

The official formula of every metric the Marketing area reports, where each term comes from, its default window and how to read it. The agent reads it before computing any Marketing number, so the same question never gets two numbers. A metric marked "not in gold yet" has no answer from the agent until a gold model exists: that is a data task, never a reason to read silver. Context and process are in [[doc:area-marketing]]. Marketing owns it with RevOps and updates it when a formula, a window or a target changes, in the same pull request as the code that changes it.

## Metrics

| Metric | Formula | Source | Status |
|---|---|---|---|
| Form submissions | count of submissions in the month | [[gold.mql_monthly.form_submissions]] | in gold |
| Marketing qualified leads | submissions with Marketing's flag | [[gold.mql_monthly.marketing_mqls]] | in gold |
| Sales-accepted share | Sales flags over Marketing flags, same month | [[gold.mql_monthly.sales_mqls]] over [[gold.mql_monthly.marketing_mqls]] | in gold |
| Conflicting flags | submissions where the two flags disagree | [[gold.mql_monthly.conflicting_flags]] | in gold |
| Cost per MQL | campaign budget started in the month over MQLs of those campaigns | [[silver.campaign.budget_usd]], [[silver.form_submission.campaign_id]] | not in gold yet |

## Window and grain

- Default window: the last full calendar month. The month in progress is partial and is never compared with a full month, see [[concept:cross-cutting-rules]].
- Grain: calendar month, first day of the month, as in the gold tables. A question about a quarter sums or averages full months and says which.

## Internal benchmark

The monthly series in [[gold.mql_monthly]] is the benchmark: compare a month with the same month's trailing three-month average, never with one single month.

## Interpretation notes

- Marketing's count is canonical for Marketing reports; Sales' count is shown as "Sales agrees", never added, see [[concept:mql]].
- A rise in conflicting flags is a process problem between teams, not a demand problem.
