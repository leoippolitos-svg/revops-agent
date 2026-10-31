---
id: area-enterprise
title: Enterprise area
kind: area
owner_team: Sales
status: canonical
last_reviewed: 2026-10-31
related: [metrics-enterprise, funnel-stages, lead-routing]
---

# Enterprise area

## Purpose

How the Enterprise area works at Fernway: what it is for, who is in it, what it is measured on and the words it uses differently. The agent reads it when a question is about Enterprise, after the company and entities documents and before the area's metrics. Formulas live in [[doc:metrics-enterprise]] and CRM fields in [[doc:crm-map]]; neither is repeated here. Sales owns it with RevOps and updates it when the team, its process or its goals change.

## Mission

Win and expand companies of 1,000 employees or more, with longer cycles and bigger deals.

## People

Three account executives, team value `enterprise`. Capacity is 8 open deals each, see [[concept:lead-routing]].

## Objectives

- New MRR from enterprise deals, and enough pipeline to cover the target.

## KPIs

| KPI | Where | Notes |
|---|---|---|
| Open deal value per owner | [[gold.owner_workload.open_amount_usd]] | coverage of the target |
| Deals reaching proposal | [[gold.funnel_stage_monthly]] | the stage where enterprise deals slow down |
| Win rate | [[gold.funnel_conversion_monthly]] | small samples: read with care |

## CRM objects

The same deal pipeline as Sales; the difference is the company segment in [[silver.company.segment]].

## Benchmarks

See [[doc:benchmarks]].

## Frequent questions

- "How much enterprise pipeline do we have?" Open deal value of the enterprise team, from the newest export.

## Anti-confusions

- The enterprise team and the enterprise segment are not the same field, see [[doc:entities]].
- With 3 owners and few deals a month, one deal moves every percentage; the agent gives counts next to rates.
