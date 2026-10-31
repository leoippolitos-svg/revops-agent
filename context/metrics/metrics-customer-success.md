---
id: metrics-customer-success
title: Customer Success metrics
kind: metrics
owner_team: Customer Success
status: canonical
last_reviewed: 2026-10-31
related: [area-customer-success, mrr, active-customer]
---

# Customer Success metrics

## Purpose

The official formula of every metric the Customer Success area reports, where each term comes from, its default window and how to read it. The agent reads it before computing any Customer Success number, so the same question never gets two numbers. A metric marked "not in gold yet" has no answer from the agent until a gold model exists: that is a data task, never a reason to read silver. Context and process are in [[doc:area-customer-success]]. Customer Success owns it with RevOps and updates it when a formula, a window or a target changes, in the same pull request as the code that changes it.

## Metrics

| Metric | Formula | Source | Status |
|---|---|---|---|
| Churned MRR | value of subscriptions that ended in the month | [[gold.mrr_monthly.churned_mrr_usd]] | in gold |
| Monthly MRR churn rate | churned MRR over starting MRR of the month | [[gold.mrr_monthly.churned_mrr_usd]] over [[gold.mrr_monthly.starting_mrr_usd]] | in gold |
| Active customers | companies with a paid subscription in force at month end | [[gold.active_customer_monthly.active_customers]] | in gold |
| Net revenue retention | (starting MRR minus churned MRR plus expansion) over starting MRR | [[gold.mrr_monthly]] | in gold, equals gross retention today |
| Accounts in the red band | companies whose latest score is red | [[silver.health_score.band]] | not in gold yet |

## Window and grain

- Default window: the last full calendar month. The month in progress is partial and is never compared with a full month, see [[concept:cross-cutting-rules]].
- Grain: calendar month, first day of the month, as in the gold tables. A question about a quarter sums or averages full months and says which.

## Internal benchmark

The first churn in the data is in 2025-12 (1.9% of starting MRR). There is no longer history yet.

## Interpretation notes

- A churn rate on a small base swings with one customer; say the count of churned subscriptions next to the rate.
- Fernway has no plan changes, so expansion is zero and net retention equals gross retention; say so whenever net retention is asked.
