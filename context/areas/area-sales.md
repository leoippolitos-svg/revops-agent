---
id: area-sales
title: Sales area
kind: area
owner_team: Sales
status: canonical
last_reviewed: 2026-10-31
related: [metrics-sales, funnel-stages, lead-routing]
---

# Sales area

## Purpose

How the Sales area works at Fernway: what it is for, who is in it, what it is measured on and the words it uses differently. The agent reads it when a question is about Sales, after the company and entities documents and before the area's metrics. Formulas live in [[doc:metrics-sales]] and CRM fields in [[doc:crm-map]]; neither is repeated here. Sales owns it with RevOps and updates it when the team, its process or its goals change.

## Mission

Win SMB and mid-market customers through the new business pipeline.

## People

Five sellers, team value `sales`. Capacity is 30 open deals per seller, see [[concept:lead-routing]].

## Objectives

- Win rate of 40% or more on mature cohorts, and new MRR on target, see [[doc:okrs]].

## KPIs

| KPI | Where | Notes |
|---|---|---|
| Deals entering each stage | [[gold.funnel_stage_monthly.deals_entered]] | volume per month |
| Conversion and win rate | [[gold.funnel_conversion_monthly]] | cohorts, mature only |
| Time in stage | [[gold.funnel_time_in_stage_monthly.median_days_in_stage]] | median, by month of exit |
| Open deals per seller | [[gold.owner_workload.open_deals]] | against the capacity limit |

## CRM objects

Deals ([[silver.deal]]) with stage history ([[silver.deal_stage_history]]), linked to companies and owners.

## Benchmarks

See [[doc:benchmarks]] and the cohort history in gold.

## Frequent questions

- "What is our win rate?" Mature cohorts only, open deals left out, see [[concept:funnel-stages]].
- "Who has room for more leads?" Open deals against the limit, from the newest export.

## Anti-confusions

- Bookings (won deal value) are not MRR, see [[concept:mrr]].
- Entries of one month divided by entries of another month are not a conversion rate; use cohorts.
