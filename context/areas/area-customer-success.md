---
id: area-customer-success
title: Customer Success area
kind: area
owner_team: Customer Success
status: canonical
last_reviewed: 2026-10-31
related: [metrics-customer-success, active-customer, mrr]
---

# Customer Success area

## Purpose

How the Customer Success area works at Fernway: what it is for, who is in it, what it is measured on and the words it uses differently. The agent reads it when a question is about Customer Success, after the company and entities documents and before the area's metrics. Formulas live in [[doc:metrics-customer-success]] and CRM fields in [[doc:crm-map]]; neither is repeated here. Customer Success owns it with RevOps and updates it when the team, its process or its goals change.

## Mission

Keep customers healthy, renew them and grow them.

## People

Four customer success managers, team value `customer_success`.

## Objectives

- Churned MRR below 2% of starting MRR every month, see [[doc:okrs]].

## KPIs

| KPI | Where | Notes |
|---|---|---|
| Churned MRR | [[gold.mrr_monthly.churned_mrr_usd]] | value of subscriptions that ended |
| Active customers | [[gold.active_customer_monthly.active_customers]] | paid subscription in force |
| Health band | not in gold yet | from [[silver.health_score.band]] |
| Tickets by category | not in gold yet | from [[silver.ticket]] |

## CRM objects

Health scores ([[silver.health_score]]): a score from 0 to 100 and a band, red below 40, yellow from 40 to 69, green from 70. Tickets ([[silver.ticket]]) with a category (billing, bug, feature request, how-to, integration) and a priority.

## Benchmarks

See [[doc:benchmarks]].

## Frequent questions

- "How many customers churned?" Churned subscriptions and churned MRR, from billing. A red band is a risk, not a churn.
- "Which accounts are at risk?" Red band and open high-priority tickets; that needs gold models, so today it is a data task.

## Anti-confusions

- "Customer" for Sales is a CRM stage; for Customer Success it is a paid subscription, see [[concept:active-customer]].
- There is no expansion or contraction in the data, so net revenue retention equals gross revenue retention today.
