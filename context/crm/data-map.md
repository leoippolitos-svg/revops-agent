---
id: data-map
title: Data map of the gold layer
kind: data-map
owner_team: RevOps
status: canonical
last_reviewed: 2026-10-31
related: [crm-map, cross-cutting-rules]
---

# Data map of the gold layer

## Purpose

The protocol and map for querying the lakehouse: which layer the agent may read, the grain of each gold table, the joins that are safe and the queries that check a result. The agent reads it before writing any SQL. Column descriptions are in the catalog, [docs/catalog.md](../../docs/catalog.md); this document says how to use the tables together. RevOps owns it and updates it with every new or changed gold model.

## Layers and access

- Bronze is the raw daily export, silver the cleaned entities, gold the business grain. The agent, the MCP server, the apps and the automations read **gold only**, through a read-only connection.
- One SELECT per call, no comments, no table functions that read files or the network, a row limit applied by the tool. These are enforced in code, not in this text.
- Before a new query on a table, check its columns with the catalog tool; the real schema wins over this map, and a difference is reported as a pull request to this document.

## Tables and grain

| Table | Grain | Notes |
|---|---|---|
| [[gold.mrr_monthly]] | one row per month | the month in progress is partial |
| [[gold.active_customer_monthly]] | one row per month | customers and subscriptions are separate counts |
| [[gold.funnel_stage_monthly]] | one row per month and stage | a stage with no entries has no row |
| [[gold.funnel_conversion_monthly]] | one row per cohort month | cohorts are immature for 90 days |
| [[gold.funnel_time_in_stage_monthly]] | one row per month of exit and stage | only deals that left the stage |
| [[gold.mql_monthly]] | one row per month | two flags, never added |
| [[gold.owner_workload]] | one row per owner, now | newest export only |
| [[gold.account_health]] | one row per company | the latest health score |
| [[gold.ticket_monthly]] | one row per month, category and priority | a missing combination is zero |
| [[gold.campaign_channel_monthly]] | one row per month and channel | budget by start month, MQLs by submission month |
| [[gold.mql_to_deal_monthly]] | one row per month of the MQL | the last 30 days are immature |
| [[gold.onboarding_progress]] | one row per subscription | milestone dates and the current one |
| [[gold.data_quality_snapshot]] | one row, now | the data date is its as-of day |

## Canonical joins

- Month tables join on the month column: [[gold.mrr_monthly.month]] with [[gold.funnel_stage_monthly.month]] or [[gold.mql_monthly.month]].
- The data date of every answer is [[gold.data_quality_snapshot.as_of]].
- Never join gold to silver in an answer. If a question needs a silver column, that is a data task.

## Model query

New MRR next to the won deals of the same month:

```sql
SELECT m.month, m.new_mrr_usd, f.deals_entered AS deals_won
FROM gold.mrr_monthly m
LEFT JOIN gold.funnel_stage_monthly f
  ON f.month = m.month AND f.stage = 'closed_won'
ORDER BY m.month
```

## Validation queries

- The months connect: starting plus new minus churned equals ending MRR, in every row of [[gold.mrr_monthly]].
- A cohort never reaches a later stage with more deals than an earlier one, in [[gold.funnel_conversion_monthly]].
- The data date is recent: [[gold.data_quality_snapshot.as_of]] is at most a few days old; if not, the answer says the data is stale.

```sql
SELECT count(*) AS broken_months
FROM gold.mrr_monthly
WHERE starting_mrr_usd + new_mrr_usd - churned_mrr_usd <> ending_mrr_usd
```

## Gotchas

- A month with no row is a month with nothing, not missing data, only in the stage table; elsewhere a missing month means the data does not reach it.
- Distinct counts across months cannot be summed: a customer active in three months is one customer, not three.
- A result is returned as a sample with the real total; never present the sample size as the total.
