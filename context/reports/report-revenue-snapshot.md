---
id: report-revenue-snapshot
title: Revenue snapshot report
kind: report
owner_team: RevOps
status: canonical
last_reviewed: 2026-10-31
related: [mrr, active-customer, funnel-stages, mql]
---

# Revenue snapshot report

## Purpose

How every number on the revenue snapshot page is computed, so the agent explains a number from the page without recomputing it another way. The agent reads it when someone asks about "the snapshot", "the Monday page" or a number they saw there. It describes the report, not the code; the code is in `apps/revenue-snapshot/`. RevOps owns it and adds a changelog line whenever a number on the page changes meaning.

## Numbers and how they are computed

| Block | Number | Computed from | Definition |
|---|---|---|---|
| MRR | New, churned and ending MRR per month | [[gold.mrr_monthly.new_mrr_usd]], [[gold.mrr_monthly.churned_mrr_usd]], [[gold.mrr_monthly.ending_mrr_usd]] | [[concept:mrr]] |
| MRR | "Latest full month" line | the last row before the partial month | [[concept:mrr]] |
| Customers | Active customers and active subscriptions per month | [[gold.active_customer_monthly.active_customers]], [[gold.active_customer_monthly.active_subscriptions]] | [[concept:active-customer]] |
| Funnel | Deals that entered each stage in the latest full month | [[gold.funnel_stage_monthly.deals_entered]] | [[concept:funnel-stages]] |
| MQLs | Marketing's count per month, with Sales' count as "Sales agrees" | [[gold.mql_monthly.marketing_mqls]], [[gold.mql_monthly.sales_mqls]] | [[concept:mql]] |

## Filters

None. The page shows every month in gold and labels the newest month "partial". There is no segment, team or date filter, by design: a read-only page with no inputs.

## Gotchas

- The page is built from a file; if the lakehouse is more than two days old, a banner says so, and the numbers are as of that date.
- Customers and subscriptions are two lines: one customer can hold two subscriptions.
- The funnel block counts entries in one month, not a conversion rate.

## Changelog

- 2026-10-31: the report document is written; the page itself was built in an earlier pull request.
